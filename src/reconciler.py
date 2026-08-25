"""
Self-healing zombie runner detection and queue unsticking.
"""

import sys
from typing import List, Optional
from github_api import github_request

# Prefixes used by docker_driver.py and orbstack_vm_driver.py
MANAGED_RUNNER_PREFIXES = ("local-runner-", "runzero-vm-")


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
