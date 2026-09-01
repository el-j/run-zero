"""
Self-healing zombie runner detection and queue unsticking.
"""

import sys
import time
from typing import Dict, List, Optional

from drivers import RunnerDriver, RunnerInfo
from github_api import github_request

# Prefixes used by all RunZero runner drivers (Docker, OrbStack VM, Multipass, WSL2)
MANAGED_RUNNER_PREFIXES = ("local-runner-", "runzero-vm-", "runzero-mp-", "runzero-wsl-")

# How long a spawned runner is allowed to sit without GitHub ever marking it
# busy before it's considered orphaned and torn down.
IDLE_ORPHAN_TIMEOUT_SECONDS = 600

# Grace period for a runner to boot and register. If a runner is older than this
# and is NOT found in GitHub's active runner list (e.g. ephemeral run already completed
# or failed, or registration failed), it is considered an orphan and reaped.
UNREGISTERED_ORPHAN_TIMEOUT_SECONDS = 180


def _runner_name_matches(local_name: str, gh_name: str) -> bool:
    """Match exact names and legacy suffix variants used by older start.sh images."""
    if not local_name or not gh_name:
        return False
    return gh_name == local_name or gh_name.startswith(f"{local_name}-")


def reconcile_zombie_runners(repos: List[str], access_token: Optional[str] = None) -> None:
    """Find and unstick runners GitHub still thinks are busy but that are actually dead.

    Cancels whatever run is pinned to a dead runner, then removes the stale registration.
    """
    for repo in repos:
        data = github_request(f"/repos/{repo}/actions/runners", access_token=access_token)
        if not data or "runners" not in data:
            continue

        zombies = [
            r for r in data["runners"]
            if r.get("status") == "offline"
            and r.get("busy")
            and str(r.get("name", "")).startswith(MANAGED_RUNNER_PREFIXES)
        ]
        if not zombies:
            continue

        runs_data = github_request(f"/repos/{repo}/actions/runs?status=in_progress&per_page=20", access_token=access_token)
        in_progress_runs = (runs_data or {}).get("workflow_runs", [])

        for zombie in zombies:
            print(f"[Autoscaler] ⚠️  Zombie runner detected: {zombie['name']} (offline but marked busy) — reconciling...", file=sys.stderr)

            for run in in_progress_runs:
                jobs_data = github_request(f"/repos/{repo}/actions/runs/{run['id']}/jobs", access_token=access_token)
                jobs = (jobs_data or {}).get("jobs", [])
                if any(j.get("runner_name") == zombie["name"] for j in jobs):
                    print(f"[Autoscaler] Cancelling run #{run.get('run_number')} ({run['id']}) pinned to dead runner {zombie['name']}", file=sys.stderr)
                    github_request(f"/repos/{repo}/actions/runs/{run['id']}/cancel", access_token=access_token, method="POST")
                    break

            if github_request(f"/repos/{repo}/actions/runners/{zombie['id']}", access_token=access_token, method="DELETE"):
                print(f"[Autoscaler] Removed stale runner registration: {zombie['name']}", file=sys.stderr)
            else:
                print(f"[Autoscaler] Could not remove {zombie['name']} yet (run cancellation likely still in flight) — will retry next cycle", file=sys.stderr)


def reconcile_idle_orphans(
    repos: List[str],
    local_runners: List[RunnerInfo],
    drivers: Dict[str, RunnerDriver],
    access_token: Optional[str] = None,
    idle_timeout_seconds: int = IDLE_ORPHAN_TIMEOUT_SECONDS,
    unregistered_timeout_seconds: int = UNREGISTERED_ORPHAN_TIMEOUT_SECONDS,
    now: Optional[float] = None
) -> None:
    """Destroy our own runners that GitHub never dispatched a job to or that completed their run.

    A local container/VM can end up permanently unused for reasons other than
    the zombie case above -- a completed ephemeral job where the VM didn't power off,
    a mislabeled workflow, a race between our poll and GitHub's dispatch, or an API hiccup.
    """
    now = now if now is not None else time.time()

    min_timeout = min(idle_timeout_seconds, unregistered_timeout_seconds)
    managed = [
        r for r in local_runners
        if r.state == "running"
        and str(r.name).startswith(MANAGED_RUNNER_PREFIXES)
        and (now - (r.created_at if r.created_at is not None else now) > min_timeout)
    ]
    if not managed:
        return

    gh_runners_by_repo: Dict[str, List[Dict]] = {}
    for repo in repos:
        data = github_request(f"/repos/{repo}/actions/runners", access_token=access_token)
        gh_runners_by_repo[repo] = (data or {}).get("runners", [])

    for runner in managed:
        created_at = runner.created_at if runner.created_at is not None else now
        age_seconds = now - created_at

        # Match against GitHub runners across repos, handling owner/repo and owner-repo
        gh_runners = gh_runners_by_repo.get(runner.target_repo, [])
        if not gh_runners and runner.target_repo:
            norm_target = runner.target_repo.replace("/", "-").lower()
            for r_name, r_list in gh_runners_by_repo.items():
                if r_name.replace("/", "-").lower() == norm_target:
                    gh_runners = r_list
                    break

        gh_match = next((r for r in gh_runners if _runner_name_matches(runner.name, str(r.get("name", "")))), None)
        if not gh_match:
            # Fallback search across all tracked repos
            for r_list in gh_runners_by_repo.values():
                m = next((r for r in r_list if _runner_name_matches(runner.name, str(r.get("name", "")))), None)
                if m:
                    gh_match = m
                    break

        # A busy runner is actively running a job
        if gh_match and gh_match.get("busy"):
            continue

        # Case 1: Runner is NOT registered on GitHub (ephemeral run finished or failed to register)
        # Check against unregistered_timeout_seconds (grace period for initial registration)
        if not gh_match and age_seconds > unregistered_timeout_seconds:
            age_minutes = max(1, int(age_seconds / 60))
            print(
                f"[Autoscaler] 🧹 Orphaned runner detected: {runner.name} "
                f"(not registered in GitHub Actions / run finished, alive {age_minutes}m) — tearing down...",
                file=sys.stderr
            )
            driver = drivers.get(runner.backend)
            if driver:
                driver.destroy_runner(runner.id)
            continue

        # Case 2: Runner IS registered on GitHub but sat idle and unclaimed
        if gh_match and age_seconds > idle_timeout_seconds:
            age_minutes = int(age_seconds / 60)
            print(
                f"[Autoscaler] 🧹 Orphaned runner detected: {runner.name} "
                f"(idle {age_minutes}m, GitHub never dispatched a job to it) — tearing down...",
                file=sys.stderr
            )
            driver = drivers.get(runner.backend)
            if driver:
                driver.destroy_runner(runner.id)

            github_request(
                f"/repos/{runner.target_repo}/actions/runners/{gh_match['id']}",
                access_token=access_token,
                method="DELETE"
            )
