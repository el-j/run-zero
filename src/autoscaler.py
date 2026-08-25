#!/usr/bin/env python3
"""
⚡ RunZero — Local GitHub Actions Runner Autoscaler
Dual-Engine Fleet supporting ultra-fast Docker containers and dedicated Virtual Machines
(OrbStack macOS Linux Machines, Windows WSL2, Canonical Multipass).
Includes persistent multi-language package caching, proxy registries, and adaptive rate-limiting.
"""

import os
import sys
import time
import signal
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Any

from drivers import get_driver, get_available_drivers, RunnerDriver, RunnerInfo

# Configuration from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("OWNER", "").strip()
ORG = os.getenv("ORG", "").strip()
REPOS_CONFIG = os.getenv("REPOS") or os.getenv("REPO", "")
AUTO_DISCOVER = os.getenv("AUTO_DISCOVER_REPOS", "true").lower() in ("true", "1", "yes")
ACTIVE_DAYS = int(os.getenv("ACTIVE_REPO_DAYS", "60"))
DISCOVERY_INTERVAL = int(os.getenv("DISCOVERY_INTERVAL", "900"))

# Driver & Architecture configuration
RUNNER_BACKEND = os.getenv("RUNNER_BACKEND", "auto").lower().strip()
RUNNER_ARCH = os.getenv("RUNNER_ARCH", "both").lower().strip()
RUNNER_LABELS_CUSTOM = os.getenv("RUNNER_LABELS", "").strip()

# Hybrid Auto-Routing settings
AUTO_ROUTE_VM = os.getenv("AUTO_ROUTE_VM", "true").lower() in ("true", "1", "yes")
VM_TRIGGER_LABELS = [
    label.strip().lower()
    for label in os.getenv("VM_TRIGGER_LABELS", "vm,browser,e2e,lighthouse,systemd,gui,unconfined").split(",")
    if label.strip()
]

MIN_RUNNERS = int(os.getenv("MIN_RUNNERS", "0"))
MAX_RUNNERS = int(os.getenv("MAX_RUNNERS", "4"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
DOCKER_SOCK = os.getenv("DOCKER_SOCK", "/var/run/docker.sock")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "host")

# Persistent Cache & Proxy Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
PROXIES_ENABLED = os.getenv("PROXIES_ENABLED", "true").lower() in ("true", "1", "yes")
HOST_CACHE_DIR = os.getenv("HOST_CACHE_DIR") or os.path.expanduser("~/.local-github-runner/cache")

API_BASE = "https://api.github.com"
running = True

# Rate-limiting state
rate_limit_remaining = 5000
rate_limit_reset = time.time() + 3600


def signal_handler(signum, frame):
    global running
    print("\n[Autoscaler] Received shutdown signal. Cleaning up...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def init_cache_dirs():
    """Ensure host cache directories exist."""
    if not CACHE_ENABLED:
        return {}

    subdirs = {
        "toolcache": "/opt/hostedtoolcache",
        "npm": "/home/runner/.npm",
        "yarn": "/home/runner/.cache/yarn",
        "pnpm": "/home/runner/.local/share/pnpm/store",
        "pip": "/home/runner/.cache/pip",
        "uv": "/home/runner/.cache/uv",
        "go-mod": "/home/runner/go/pkg/mod",
        "go-build": "/home/runner/.cache/go-build",
        "cargo-registry": "/home/runner/.cargo/registry"
    }

    os.makedirs(HOST_CACHE_DIR, exist_ok=True)
    mount_mappings = {}
    for key, container_path in subdirs.items():
        host_path = os.path.join(HOST_CACHE_DIR, key)
        os.makedirs(host_path, exist_ok=True)
        mount_mappings[host_path] = container_path

    return mount_mappings


def github_request(endpoint):
    """Perform authenticated GitHub REST API GET request with rate-limit tracking."""
    global rate_limit_remaining, rate_limit_reset

    now = time.time()
    if rate_limit_remaining < 15 and now < rate_limit_reset:
        wait_seconds = max(5, int(rate_limit_reset - now) + 2)
        print(f"[Autoscaler] ⚠️ API rate limit low ({rate_limit_remaining} remaining). Backing off for {wait_seconds}s...", file=sys.stderr)
        time.sleep(wait_seconds)

    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "RunZero-Autoscaler")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = resp.headers
            if "x-ratelimit-remaining" in headers:
                try:
                    rate_limit_remaining = int(headers["x-ratelimit-remaining"])
                    rate_limit_reset = int(headers["x-ratelimit-reset"])
                except Exception:
                    pass
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        headers = e.headers or {}
        if "x-ratelimit-remaining" in headers:
            try:
                rate_limit_remaining = int(headers["x-ratelimit-remaining"])
                rate_limit_reset = int(headers["x-ratelimit-reset"])
            except Exception:
                pass

        if e.code in (403, 429):
            wait_seconds = max(10, int(rate_limit_reset - time.time()) + 2) if rate_limit_reset > time.time() else 60
            print(f"[Autoscaler] ⛔ GitHub API rate limit reached ({e.code}). Pausing for {wait_seconds}s...", file=sys.stderr)
            time.sleep(min(wait_seconds, 300))
        else:
            body = e.read().decode("utf-8") if e.fp else ""
            print(f"[Autoscaler] API Error ({e.code}) for {endpoint}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[Autoscaler] Request Error for {endpoint}: {e}", file=sys.stderr)
        return None


def discover_repositories():
    """Discover list of active repositories to monitor."""
    repos = set()

    if REPOS_CONFIG:
        for r in REPOS_CONFIG.split(","):
            r = r.strip()
            if r:
                repos.add(r)
        return sorted(list(repos))

    if AUTO_DISCOVER and ACCESS_TOKEN:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=ACTIVE_DAYS)
        page = 1
        while True:
            data = github_request(f"/user/repos?per_page=100&affiliation=owner&sort=pushed&direction=desc&page={page}")
            if not isinstance(data, list) or not data:
                break

            stop_pagination = False
            for item in data:
                if not isinstance(item, dict) or item.get("archived", False):
                    continue

                full_name = item.get("full_name", "")
                if OWNER and not full_name.startswith(f"{OWNER}/"):
                    continue

                pushed_at_str = item.get("pushed_at")
                if pushed_at_str:
                    try:
                        pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
                        if pushed_at < cutoff_date:
                            stop_pagination = True
                            break
                    except Exception:
                        pass

                repos.add(full_name)

            if stop_pagination or len(data) < 100:
                break
            page += 1

    return sorted(list(repos))


def get_queued_job_details(repo_full_name: str) -> List[Dict[str, Any]]:
    """Inspect queued workflow runs and extract job labels for hybrid routing."""
    data = github_request(f"/repos/{repo_full_name}/actions/runs?status=queued")
    if not data or "workflow_runs" not in data:
        return []

    queued_jobs = []
    for run in data["workflow_runs"]:
        jobs_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run['id']}/jobs?filter=latest")
        if jobs_data and "jobs" in jobs_data:
            for job in jobs_data["jobs"]:
                if job.get("status") == "queued":
                    labels = [lbl.lower() for lbl in job.get("labels", [])]
                    queued_jobs.append({
                        "id": job.get("id"),
                        "name": job.get("name"),
                        "labels": labels,
                        "repo": repo_full_name
                    })
    return queued_jobs


def select_driver_for_job(
    job: Dict[str, Any],
    default_driver: RunnerDriver,
    available_drivers: Dict[str, RunnerDriver]
) -> Tuple[RunnerDriver, str]:
    """Determine whether a job requires a VM driver or a standard container driver."""
    job_labels = job.get("labels", [])

    # Check if job specifically requests a VM or features requiring full OS sandbox
    needs_vm = any(trigger in job_labels for trigger in VM_TRIGGER_LABELS)

    if needs_vm and AUTO_ROUTE_VM:
        # Prefer VM backends: orbstack-vm -> wsl2 -> multipass
        for vm_name in ("orbstack-vm", "wsl2", "multipass"):
            if vm_name in available_drivers:
                return available_drivers[vm_name], "vm"

    return default_driver, "container"


def get_target_architectures():
    """Return list of architectures to spin up."""
    if RUNNER_ARCH in ("both", "all", "dual"):
        return ["arm64", "amd64"]
    elif RUNNER_ARCH in ("amd64", "x86_64", "x64"):
        return ["amd64"]
    else:
        return ["arm64"]


def main():
    if not ACCESS_TOKEN:
        print("[Autoscaler] Error: ACCESS_TOKEN is required for autoscaling.", file=sys.stderr)
        sys.exit(1)

    available_drivers = get_available_drivers()
    default_driver = get_driver(RUNNER_BACKEND)
    architectures = get_target_architectures()
    cache_mounts = init_cache_dirs()

    print("=" * 65)
    print(" ⚡ RunZero — Dual-Engine Local GitHub Runner Autoscaler")
    print(f" Default Engine:   {default_driver.name().upper()}")
    print(f" Available Drivers: {', '.join([k.upper() for k in available_drivers.keys()])}")
    print(f" Hybrid Routing:   {'Enabled (Auto-detecting VM vs Container jobs)' if AUTO_ROUTE_VM else 'Disabled'}")
    print(f" Architectures:    {', '.join([a.upper() for a in architectures])}")
    print(f" Cache Directory:  {HOST_CACHE_DIR} ({'Enabled' if CACHE_ENABLED else 'Disabled'})")
    print(f" Max Concurrency:  {MAX_RUNNERS} | Min Runners: {MIN_RUNNERS}")
    print(f" Active Filter:    Pushed within last {ACTIVE_DAYS} days")
    print("=" * 65)

    last_discovery_time: float = 0.0
    tracked_repos: List[str] = []

    while running:
        now = time.time()
        # Refresh tracked repositories periodically
        if not ORG and (now - last_discovery_time > DISCOVERY_INTERVAL or not tracked_repos):
            discovered = discover_repositories()
            last_discovery_time = now
            if discovered:
                tracked_repos = discovered
                print(f"[Autoscaler] Monitoring {len(tracked_repos)} active repository(ies):")
                for r in tracked_repos:
                    print(f"  • {r}")
                print(f"[Autoscaler] GitHub API Quota remaining: {rate_limit_remaining}/5000")

        # Collect active runners across all drivers
        all_runners: List[RunnerInfo] = []
        for d in available_drivers.values():
            runners = d.list_runners()
            d.prune_exited(runners)
            all_runners.extend(d.list_runners())

        active_runners = [r for r in all_runners if r.state == "running"]
        active_count = len(active_runners)

        if ORG:
            # For organizations
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    default_driver.spawn_runner(
                        org=ORG,
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=cache_mounts,
                        proxies_enabled=PROXIES_ENABLED
                    )
        else:
            # For repositories: check queued jobs with hybrid routing
            queued_jobs_by_repo: Dict[str, List[Dict[str, Any]]] = {}
            total_queued = 0

            for repo in tracked_repos:
                jobs = get_queued_job_details(repo)
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

                    driver_to_use, mode = select_driver_for_job(job, default_driver, available_drivers)
                    arch = architectures[0]
                    if "amd64" in job.get("labels", []) or "x64" in job.get("labels", []):
                        arch = "amd64"

                    spawned_id = driver_to_use.spawn_runner(
                        repo=repo,
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=cache_mounts,
                        proxies_enabled=PROXIES_ENABLED
                    )
                    if spawned_id:
                        active_runners.append(RunnerInfo(
                            id=spawned_id,
                            name=spawned_id,
                            status="running",
                            state="running",
                            target_repo=repo,
                            target_arch=arch,
                            backend=driver_to_use.name()
                        ))
                        needed -= 1

            # Maintain MIN_RUNNERS if configured
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS and tracked_repos:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    default_driver.spawn_runner(
                        repo=tracked_repos[0],
                        arch=arch,
                        access_token=ACCESS_TOKEN,
                        cache_mounts=cache_mounts,
                        proxies_enabled=PROXIES_ENABLED
                    )

        # Adaptive sleep pacing
        sleep_duration = max(POLL_INTERVAL, int(len(tracked_repos) * 0.5))
        time.sleep(sleep_duration)

    # Cleanup remaining runners across all drivers on shutdown
    print("[Autoscaler] Stopping managed runners on shutdown...")
    for d in available_drivers.values():
        d.cleanup_all()
    print("[Autoscaler] Shutdown complete.")


if __name__ == "__main__":
    main()
