#!/usr/bin/env python3
"""
⚡ RunZero — Local GitHub Actions Runner Autoscaler
Dual-Engine Fleet supporting ultra-fast Docker containers and dedicated Virtual Machines
(OrbStack macOS Linux Machines, Windows WSL2, Canonical Multipass).
Includes persistent multi-language package caching, proxy registries, real-time observability dashboard, and adaptive rate-limiting.
"""

import os
import signal
import sys
import time
from typing import Any, Dict, List, Optional

from cache_manager import init_cache_dirs
from dashboard import DashboardServer, dashboard_state
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

# Dashboard settings
DASHBOARD_ENABLED = os.getenv("DASHBOARD_ENABLED", "true").lower() in ("true", "1", "yes")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "49505"))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")

running = True


def log_print(msg: str, file: Any = None) -> None:
    """Print message to stdout/stderr and push to dashboard log ring buffer."""
    if file:
        print(msg, file=file)
    else:
        print(msg)
    dashboard_state.append_log(msg)


def get_target_architectures() -> List[str]:
    """Determine list of architectures to rotate through for pool."""
    if RUNNER_ARCH == "both":
        return ["arm64", "amd64"]
    elif RUNNER_ARCH in ("amd64", "x64", "x86_64"):
        return ["amd64"]
    else:
        return ["arm64"]


ARM_LABELS = ("arm64", "aarch64", "arm")


def resolve_job_arch(job_labels: List[str]) -> str:
    """Pick the architecture for a job, mirroring GitHub-hosted runner defaults."""
    if RUNNER_ARCH in ("amd64", "x64", "x86_64"):
        return "amd64"
    if RUNNER_ARCH != "both":
        return "arm64"
    if any(label in job_labels for label in ARM_LABELS):
        return "arm64"
    return "amd64"


def main():
    """Entrypoint: validate config, start the dashboard, then run the poll-scale-reconcile loop forever.

    Exits(1) immediately if ACCESS_TOKEN is missing, or if caching is enabled without a
    HOST_CACHE_DIR. Otherwise blocks until a SIGINT/SIGTERM flips the module-level `running`
    flag, then cleans up every managed runner and stops the dashboard before returning.
    """
    if not ACCESS_TOKEN:
        log_print("[Autoscaler] Error: ACCESS_TOKEN is required for autoscaling.", file=sys.stderr)
        sys.exit(1)

    if CACHE_ENABLED and not HOST_CACHE_DIR:
        log_print(
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
        __version__ = "0.1.0"

    # Initialize dashboard state config
    dashboard_state.version = __version__
    dashboard_state.default_engine = default_driver.name()
    dashboard_state.available_drivers = list(available_drivers.keys())
    dashboard_state.hybrid_routing_enabled = AUTO_ROUTE_VM
    dashboard_state.target_architectures = architectures
    dashboard_state.cache_dir = HOST_CACHE_DIR
    dashboard_state.cache_enabled = CACHE_ENABLED
    dashboard_state.max_concurrency = MAX_RUNNERS
    dashboard_state.min_runners = MIN_RUNNERS

    dashboard_server: Optional[DashboardServer] = None
    if DASHBOARD_ENABLED:
        try:
            dashboard_server = DashboardServer(host=DASHBOARD_HOST, port=DASHBOARD_PORT)
            dashboard_server.start(blocking=False)
        except Exception as e:
            log_print(f"[Autoscaler] Warning: Could not start Dashboard server: {e}", file=sys.stderr)

    log_print("=" * 65)
    log_print(f" ⚡ RunZero v{__version__} — Dual-Engine Local GitHub Runner Autoscaler")
    log_print(f" Default Engine:   {default_driver.name().upper()}")
    log_print(f" Available Drivers: {', '.join([k.upper() for k in available_drivers.keys()])}")
    log_print(f" Hybrid Routing:   {'Enabled (Auto-detecting VM vs Container jobs)' if AUTO_ROUTE_VM else 'Disabled'}")
    log_print(f" Architectures:    {', '.join([a.upper() for a in architectures])}")
    log_print(f" Cache Directory:  {HOST_CACHE_DIR} ({'Enabled' if CACHE_ENABLED else 'Disabled'})")
    log_print(f" Max Concurrency:  {MAX_RUNNERS} | Min Runners: {MIN_RUNNERS}")
    log_print(f" Active Filter:    Pushed within last {ACTIVE_DAYS} days")
    if DASHBOARD_ENABLED:
        log_print(f" Web Dashboard:    http://localhost:{DASHBOARD_PORT}")
    log_print("=" * 65)

    def signal_handler(signum, frame):
        """Flip the module-level `running` flag so the poll loop exits and shutdown cleanup runs."""
        global running
        log_print("\n[Autoscaler] Received shutdown signal. Cleaning up...")
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
                log_print(f"[Autoscaler] Monitoring {len(tracked_repos)} active repository(ies):")
                for r in tracked_repos:
                    log_print(f"  • {r}")
                log_print(f"[Autoscaler] GitHub API Quota remaining: {rate_limit_remaining}/5000")

            if tracked_repos:
                reconcile_zombie_runners(tracked_repos, access_token=ACCESS_TOKEN)

        # Collect active runners across all drivers
        all_runners: List[RunnerInfo] = []
        for d in available_drivers.values():
            runners = d.list_runners()
            d.prune_exited(runners)
            all_runners.extend(d.list_runners())
            ensure_stopped = getattr(d, "ensure_base_images_stopped", None)
            if callable(ensure_stopped):
                ensure_stopped()

        if tracked_repos and not ORG:
            reconcile_idle_orphans(tracked_repos, all_runners, available_drivers, access_token=ACCESS_TOKEN)

        active_runners = [r for r in all_runners if r.state in ("running", "pending")]
        active_count = len(active_runners)

        queued_jobs_by_repo: Dict[str, List[Dict[str, Any]]] = {}
        all_queued_jobs: List[Dict[str, Any]] = []

        if ORG:
            # For organizations: scale based on MIN_RUNNERS
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    spawned_id = default_driver.spawn_runner(
                        org=ORG,
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=init_cache_dirs(HOST_CACHE_DIR, arch, CACHE_ENABLED),
                        proxies_enabled=PROXIES_ENABLED
                    )
                    if spawned_id:
                        active_runners.append(RunnerInfo(
                            id=spawned_id,
                            name=spawned_id,
                            status="running",
                            state="running",
                            target_repo=ORG,
                            target_arch=arch,
                            backend=default_driver.name()
                        ))
        else:
            # For repositories: check queued jobs with hybrid routing
            total_queued = 0

            for repo in tracked_repos:
                jobs = get_queued_job_details(repo, access_token=ACCESS_TOKEN)
                if jobs:
                    queued_jobs_by_repo[repo] = jobs
                    for j in jobs:
                        j_copy = dict(j)
                        j_copy["repo"] = repo
                        all_queued_jobs.append(j_copy)
                    total_queued += len(jobs)
                time.sleep(0.1)

            if total_queued > 0:
                log_print(f"[Autoscaler] Detected {total_queued} queued unclaimed job(s) across repos.")

            for repo, jobs in queued_jobs_by_repo.items():
                active_for_repo = sum(1 for r in active_runners if r.target_repo == repo)
                needed = len(jobs) - active_for_repo

                for job in jobs:
                    if len(active_runners) >= MAX_RUNNERS or needed <= 0:
                        break

                    driver_to_use, mode = select_driver_for_job(job, default_driver, available_drivers, AUTO_ROUTE_VM)
                    arch = resolve_job_arch(job.get("labels", []))

                    dashboard_state.record_routing_decision(driver_to_use.name(), job.get("name", ""))

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

        # Push telemetry update to Dashboard
        dashboard_state.update_fleet(
            runners=all_runners,
            rate_limit=rate_limit_remaining,
            queued_jobs=all_queued_jobs,
            monitored_repos=tracked_repos,
            available_drivers=list(available_drivers.keys()),
            default_engine=default_driver.name(),
            version=__version__
        )

        # Sleep before next poll loop
        for _ in range(POLL_INTERVAL):
            if not running:
                break
            time.sleep(1)

    log_print("[Autoscaler] Stopping managed runners on shutdown...")
    for d in available_drivers.values():
        d.cleanup_all()
    if dashboard_server:
        dashboard_server.stop()
    log_print("[Autoscaler] Shutdown complete.")


if __name__ == "__main__":
    main()
