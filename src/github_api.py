"""
GitHub REST API client with adaptive rate-limiting and job queue inspection.
"""

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from workflow_inspector import job_uses_services_or_container

API_BASE = "https://api.github.com"
rate_limit_remaining = 5000
rate_limit_reset = 0

# A queued run's workflow file is pinned to that run's head_sha, so its content
# never changes for the lifetime of the run -- caching by run_id forever avoids
# re-fetching + re-parsing the same file on every ~10s poll while it's queued.
_workflow_text_cache: Dict[int, Optional[str]] = {}


def github_request(endpoint: str, access_token: Optional[str] = None, method: str = "GET") -> Any:
    """Perform an authenticated GitHub REST API request with rate-limit tracking.

    Returns the parsed JSON body, True for a bodiless success (204/202), or None on failure.
    """
    global rate_limit_remaining, rate_limit_reset

    now = time.time()
    if rate_limit_remaining <= 10 and now < rate_limit_reset:
        wait_seconds = int(rate_limit_reset - now) + 1
        print(f"[Autoscaler:API] ⚠️ Rate limit nearly exhausted. Throttling for {wait_seconds}s...")
        time.sleep(wait_seconds)

    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url, method=method)
    if access_token:
        req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = resp.headers
            if "x-ratelimit-remaining" in headers:
                try:
                    rate_limit_remaining = int(headers["x-ratelimit-remaining"])
                    rate_limit_reset = int(headers["x-ratelimit-reset"])
                except Exception:
                    pass
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else True
    except urllib.error.HTTPError as e:
        headers = e.headers or {}
        if "x-ratelimit-remaining" in headers:
            try:
                rate_limit_remaining = int(headers["x-ratelimit-remaining"])
                rate_limit_reset = int(headers["x-ratelimit-reset"])
            except Exception:
                pass
        if e.code in (401, 403) and rate_limit_remaining == 0:
            reset_time = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(rate_limit_reset))
            print(f"[Autoscaler:API] ❌ Rate limit exceeded (0/5000 remaining). Resets at {reset_time}.")
        elif e.code != 404:
            print(f"[Autoscaler:API] HTTP Error {e.code} for {endpoint}: {e.reason}")
        return None
    except Exception as e:
        print(f"[Autoscaler:API] Connection error for {endpoint}: {e}")
        return None


def get_workflow_text_for_run(
    repo_full_name: str, run_id: int, access_token: Optional[str] = None
) -> Optional[str]:
    """Fetch the raw workflow YAML that produced a given run, at the exact
    commit it ran against. Returns None (and caches the miss) if the run,
    its workflow path, or the file content can't be resolved -- callers
    must treat that as "unknown", not "no services declared".
    """
    if run_id in _workflow_text_cache:
        return _workflow_text_cache[run_id]

    text: Optional[str] = None
    run_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run_id}", access_token=access_token)
    path = run_data.get("path") if run_data else None
    head_sha = run_data.get("head_sha") if run_data else None

    if path and head_sha:
        contents = github_request(
            f"/repos/{repo_full_name}/contents/{path}?ref={head_sha}", access_token=access_token
        )
        if contents and contents.get("encoding") == "base64" and contents.get("content"):
            try:
                text = base64.b64decode(contents["content"]).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                text = None

    _workflow_text_cache[run_id] = text
    return text


def get_queued_job_details(repo_full_name: str, access_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve detailed metadata for unclaimed queued jobs in a repository."""
    data = github_request(f"/repos/{repo_full_name}/actions/runs?status=queued", access_token=access_token)
    if not data or "workflow_runs" not in data:
        return []

    queued_runs = data["workflow_runs"]
    if not queued_runs:
        return []

    detailed_jobs: List[Dict[str, Any]] = []
    for run in queued_runs:
        run_id = run.get("id")
        if not run_id:
            continue
        jobs_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run_id}/jobs", access_token=access_token)
        if not jobs_data or "jobs" not in jobs_data:
            continue

        # GitHub only ever dispatches a job to one of our runners if its
        # `runs-on:` requested the literal "self-hosted" label (every
        # self-hosted-targeting workflow in this fleet's convention
        # includes it explicitly, e.g. `["self-hosted", "local"]`) --
        # without this check, a queued `ubuntu-latest` job (which will
        # never be assigned to us) still causes a container/VM spawn
        # that then sits registered and idle forever, since GitHub
        # dispatches it to its own hosted fleet instead.
        qualifying_jobs = [
            job for job in jobs_data["jobs"]
            if job.get("status") == "queued" and "self-hosted" in job.get("labels", [])
        ]
        if not qualifying_jobs:
            continue

        # Fetched once per run (not per job) and cached forever by run_id --
        # a run can have dozens of jobs sharing the same workflow file.
        workflow_text = get_workflow_text_for_run(repo_full_name, run_id, access_token=access_token)

        for job in qualifying_jobs:
            declares_services = (
                job_uses_services_or_container(workflow_text, job.get("name", ""))
                if workflow_text is not None else None
            )
            detailed_jobs.append({
                "id": job.get("id"),
                "name": job.get("name", ""),
                "run_id": run_id,
                "labels": job.get("labels", []),
                "head_branch": run.get("head_branch", ""),
                "event": run.get("event", ""),
                # True/False when the workflow file could be located and
                # parsed and the job matched by name; None ("unknown") if
                # not -- router.py must fall back to its name/label
                # heuristic rather than treat None as "no services".
                "declares_services": declares_services,
            })
    return detailed_jobs
