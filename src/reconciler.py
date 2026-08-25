"""
Self-healing zombie runner detection and queue unsticking.
"""

import sys
import time
from typing import Dict, List, Optional

from drivers import RunnerDriver, RunnerInfo
from github_api import github_request

# Prefixes used by docker_driver.py and orbstack_vm_driver.py
MANAGED_RUNNER_PREFIXES = ("local-runner-", "runzero-vm-")

# How long a spawned runner is allowed to sit without GitHub ever marking it
# busy before it's considered orphaned and torn down. Generous: real jobs are
# normally claimed within seconds once a matching runner registers.
IDLE_ORPHAN_TIMEOUT_SECONDS = 600


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
    now: Optional[float] = None
) -> None:
    """Destroy our own runners that GitHub never dispatched a job to.

    A local container/VM can end up permanently unused for reasons other than
    the zombie case above -- a mislabeled workflow, a race between our poll and
    GitHub's own dispatch, an API hiccup. Whatever the cause, an unused runner
    that sits registered and idle forever is exactly the "created a container
    for nothing" failure mode this fleet must never leave unattended. Runners
    GitHub marks busy are never touched here, however long they've run --
    that's a real in-progress job, not an orphan.
    """
    now = now if now is not None else time.time()

    managed = [
        r for r in local_runners
        if r.state == "running"
        and r.created_at is not None
        and str(r.name).startswith(MANAGED_RUNNER_PREFIXES)
        and now - r.created_at > idle_timeout_seconds
    ]
    if not managed:
        return

    gh_runners_by_repo: Dict[str, List[Dict]] = {}
    for repo in repos:
        data = github_request(f"/repos/{repo}/actions/runners", access_token=access_token)
        gh_runners_by_repo[repo] = (data or {}).get("runners", [])

    for runner in managed:
        gh_runners = gh_runners_by_repo.get(runner.target_repo, [])
        gh_match = next((r for r in gh_runners if r.get("name") == runner.name), None)

        # A busy runner is doing real work no matter how long it's been alive.
        if gh_match and gh_match.get("busy"):
            continue

        assert runner.created_at is not None  # guaranteed by the `managed` filter above
        age_minutes = int((now - runner.created_at) / 60)
        print(
            f"[Autoscaler] 🧹 Orphaned runner detected: {runner.name} "
            f"(idle {age_minutes}m, GitHub never dispatched a job to it) — tearing down...",
            file=sys.stderr
        )

        driver = drivers.get(runner.backend)
        if driver:
            driver.destroy_runner(runner.id)

        if gh_match:
            github_request(f"/repos/{runner.target_repo}/actions/runners/{gh_match['id']}", access_token=access_token, method="DELETE")
