#!/usr/bin/env python3
"""
⚡ RunZero — Local GitHub Actions Runner Autoscaler
Dual-Engine Fleet supporting ultra-fast Docker containers and dedicated Virtual Machines
(OrbStack macOS Linux Machines, Windows WSL2, Canonical Multipass).
Includes persistent multi-language package caching, proxy registries, and adaptive rate-limiting.
"""

import os
import signal
import sys
import time
from typing import Any, Dict, List

from cache_manager import init_cache_dirs
from discovery import discover_repositories
from drivers import RunnerInfo, get_available_drivers, get_driver
from github_api import get_queued_job_details, rate_limit_remaining
from reconciler import reconcile_idle_orphans, reconcile_zombie_runners
from router import select_driver_for_job

# Configuration from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("OWNER", "").strip()
ORG = os.getenv("ORG", "").strip()
REPOS_CONFIG = os.getenv("REPOS") or os.getenv("REPO", "") or ""
AUTO_DISCOVER = os.getenv("AUTO_DISCOVER_REPOS", "true").lower() in ("true", "1", "yes")
ACTIVE_DAYS = int(os.getenv("ACTIVE_REPO_DAYS", "60"))
DISCOVERY_INTERVAL = int(os.getenv("DISCOVERY_INTERVAL", "900"))

# Driver & Architecture configuration
RUNNER_BACKEND = os.getenv("RUNNER_BACKEND", "auto").strip().lower()
AUTO_ROUTE_VM = os.getenv("AUTO_ROUTE_VM", "true").lower() in ("true", "1", "yes")
RUNNER_ARCH = os.getenv("RUNNER_ARCH", "both").strip().lower()
PROXIES_ENABLED = os.getenv("PROXIES_ENABLED", "true").lower() in ("true", "1", "yes")

# Concurrency & Cache settings
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
HOST_CACHE_DIR = os.getenv("HOST_CACHE_DIR", "")
MIN_RUNNERS = int(os.getenv("MIN_RUNNERS", "0"))
MAX_RUNNERS = int(os.getenv("MAX_RUNNERS", "4"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))

running = True


def get_target_architectures() -> List[str]:
    """Determine list of architectures to rotate through for pool."""
    if RUNNER_ARCH == "both":
        return ["arm64", "amd64"]
    elif RUNNER_ARCH in ("amd64", "x64", "x86_64"):
        return ["amd64"]
    else:
        return ["arm64"]


def main():
    if not ACCESS_TOKEN:
        print("[Autoscaler] Error: ACCESS_TOKEN is required for autoscaling.", file=sys.stderr)
        sys.exit(1)

    if CACHE_ENABLED and not HOST_CACHE_DIR:
        print(
            "[Autoscaler] Error: CACHE_ENABLED=true but HOST_CACHE_DIR is not set. "
            "It must be a real path on the Docker HOST (not a path inside this "
            "container) -- e.g. HOST_CACHE_DIR=/Users/you/.local-github-runner/cache "
            "on macOS. Set it in .env, or set CACHE_ENABLED=false to run without "
            "persistent caching.",
            file=sys.stderr,
        )
        sys.exit(1)

    available_drivers = get_available_drivers()
    default_driver = get_driver(RUNNER_BACKEND)
    architectures = get_target_architectures()

    try:
        from version import __version__
    except ImportError:
        __version__ = "0.0.1"

    print("=" * 65)
    print(f" ⚡ RunZero v{__version__} — Dual-Engine Local GitHub Runner Autoscaler")
    print(f" Default Engine:   {default_driver.name().upper()}")
    print(f" Available Drivers: {', '.join([k.upper() for k in available_drivers.keys()])}")
    print(f" Hybrid Routing:   {'Enabled (Auto-detecting VM vs Container jobs)' if AUTO_ROUTE_VM else 'Disabled'}")
    print(f" Architectures:    {', '.join([a.upper() for a in architectures])}")
    print(f" Cache Directory:  {HOST_CACHE_DIR} ({'Enabled' if CACHE_ENABLED else 'Disabled'})")
    print(f" Max Concurrency:  {MAX_RUNNERS} | Min Runners: {MIN_RUNNERS}")
    print(f" Active Filter:    Pushed within last {ACTIVE_DAYS} days")
    print("=" * 65)

    def signal_handler(signum, frame):
        global running
        print("\n[Autoscaler] Received shutdown signal. Cleaning up...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    tracked_repos: List[str] = []
    last_discovery_time = 0.0

    while running:
        now = time.time()
        # Refresh tracked repositories periodically
        if not ORG and (now - last_discovery_time > DISCOVERY_INTERVAL or not tracked_repos):
            discovered = discover_repositories(
                owner=OWNER,
                active_days=ACTIVE_DAYS,
                auto_discover=AUTO_DISCOVER,
                repos_config=REPOS_CONFIG,
                access_token=ACCESS_TOKEN
            )
            last_discovery_time = now
            if discovered:
                tracked_repos = discovered
                print(f"[Autoscaler] Monitoring {len(tracked_repos)} active repository(ies):")
                for r in tracked_repos:
                    print(f"  • {r}")
                print(f"[Autoscaler] GitHub API Quota remaining: {rate_limit_remaining}/5000")

            if tracked_repos:
                reconcile_zombie_runners(tracked_repos, access_token=ACCESS_TOKEN)

        # Collect active runners across all drivers
        all_runners: List[RunnerInfo] = []
        for d in available_drivers.values():
            runners = d.list_runners()
            d.prune_exited(runners)
            all_runners.extend(d.list_runners())

        if tracked_repos and not ORG:
            # No-ops (zero API calls) unless a runner is actually old enough and
            # still idle to be worth checking -- cheap to call every poll.
            reconcile_idle_orphans(tracked_repos, all_runners, available_drivers, access_token=ACCESS_TOKEN)

        # "pending" (creating/provisioning/created) counts as active too -- a VM/
        # container that's still booting hasn't hit GitHub's "claimed" state yet
        # either, so undercounting it here caused a duplicate spawn for the same
        # job on the very next poll, every time, before the fix.
        active_runners = [r for r in all_runners if r.state in ("running", "pending")]
        active_count = len(active_runners)

        if ORG:
            # For organizations: scale based on MIN_RUNNERS
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    default_driver.spawn_runner(
                        org=ORG,
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=init_cache_dirs(HOST_CACHE_DIR, arch, CACHE_ENABLED),
                        proxies_enabled=PROXIES_ENABLED
                    )
        else:
            # For repositories: check queued jobs with hybrid routing
            queued_jobs_by_repo: Dict[str, List[Dict[str, Any]]] = {}
            total_queued = 0

            for repo in tracked_repos:
                jobs = get_queued_job_details(repo, access_token=ACCESS_TOKEN)
                if jobs:
                    queued_jobs_by_repo[repo] = jobs
                    total_queued += len(jobs)
                time.sleep(0.1)

            if total_queued > 0:
                print(f"[Autoscaler] Detected {total_queued} queued unclaimed job(s) across repos.")

            for repo, jobs in queued_jobs_by_repo.items():
                active_for_repo = sum(1 for r in active_runners if r.target_repo == repo)
                needed = len(jobs) - active_for_repo

                for job in jobs:
                    if len(active_runners) >= MAX_RUNNERS or needed <= 0:
                        break

                    driver_to_use, mode = select_driver_for_job(job, default_driver, available_drivers, AUTO_ROUTE_VM)
                    arch = architectures[0]
                    if "amd64" in job.get("labels", []) or "x64" in job.get("labels", []):
                        arch = "amd64"

                    spawned_id = driver_to_use.spawn_runner(
                        repo=repo,
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=init_cache_dirs(HOST_CACHE_DIR, arch, CACHE_ENABLED),
                        proxies_enabled=PROXIES_ENABLED
                    )
                    if spawned_id:
                        needed -= 1
                        active_runners.append(RunnerInfo(
                            id=spawned_id,
                            name=spawned_id,
                            status="running",
                            state="running",
                            target_repo=repo,
                            target_arch=arch,
                            backend=driver_to_use.name()
                        ))

        # Sleep before next poll loop
        for _ in range(POLL_INTERVAL):
            if not running:
                break
            time.sleep(1)

    print("[Autoscaler] Stopping managed runners on shutdown...")
    for d in available_drivers.values():
        d.cleanup_all()
    print("[Autoscaler] Shutdown complete.")


if __name__ == "__main__":
    main()
