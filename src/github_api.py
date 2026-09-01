"""
GitHub REST API client with adaptive rate-limiting and job queue inspection.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any

from workflow_inspector import job_uses_services_or_container

API_BASE = "https://api.github.com"
rate_limit_remaining: int | None = None
rate_limit_total: int | None = None
rate_limit_used: int | None = None
rate_limit_resource: str | None = None
rate_limit_reset: int | None = None
actions_billing: dict[str, Any] = {}

# A queued run's workflow file is pinned to that run's head_sha, so its content
# never changes for the lifetime of the run -- caching by run_id forever avoids
# re-fetching + re-parsing the same file on every ~10s poll while it's queued.
_workflow_text_cache: dict[int, str | None] = {}


def _update_rate_limit_from_headers(headers: Any) -> None:
    """Best-effort parse of GitHub rate-limit headers from a response object."""
    global rate_limit_remaining, rate_limit_total, rate_limit_used, rate_limit_resource, rate_limit_reset

    if not headers or "x-ratelimit-remaining" not in headers:
        return

    try:
        rate_limit_remaining = int(headers["x-ratelimit-remaining"])
        if "x-ratelimit-limit" in headers:
            rate_limit_total = int(headers["x-ratelimit-limit"])
        if "x-ratelimit-used" in headers:
            rate_limit_used = int(headers["x-ratelimit-used"])
        if "x-ratelimit-resource" in headers:
            rate_limit_resource = str(headers["x-ratelimit-resource"])
        if "x-ratelimit-reset" in headers:
            rate_limit_reset = int(headers["x-ratelimit-reset"])
    except Exception:
        pass


def _update_rate_limit_from_payload(payload: Any) -> None:
    """Best-effort parse from /rate_limit JSON payload (authoritative per token/account)."""
    global rate_limit_remaining, rate_limit_total, rate_limit_used, rate_limit_resource, rate_limit_reset

    if not isinstance(payload, dict):
        return

    resources_obj = payload.get("resources")
    resources = resources_obj if isinstance(resources_obj, dict) else {}
    resource_key = rate_limit_resource if isinstance(rate_limit_resource, str) and rate_limit_resource else "core"
    resource_obj = resources.get(resource_key)
    resource_data = resource_obj if isinstance(resource_obj, dict) else None

    core_obj = resources.get("core")
    if resource_data is None and isinstance(core_obj, dict):
        resource_key = "core"
        resource_data = core_obj

    rate_obj = payload.get("rate")
    if resource_data is None and isinstance(rate_obj, dict):
        resource_data = rate_obj
        if not resource_key:
            resource_key = "core"

    if not isinstance(resource_data, dict):
        return

    try:
        if "remaining" in resource_data:
            rate_limit_remaining = int(resource_data["remaining"])
        if "limit" in resource_data:
            rate_limit_total = int(resource_data["limit"])
        if "used" in resource_data:
            rate_limit_used = int(resource_data["used"])
        if "reset" in resource_data:
            rate_limit_reset = int(resource_data["reset"])
        if resource_key:
            rate_limit_resource = resource_key
    except Exception:
        pass


def refresh_rate_limit(access_token: str | None = None) -> bool:
    """Fetch authoritative rate-limit values for the current token/account."""
    data = github_request("/rate_limit", access_token=access_token)
    if not data:
        return False
    _update_rate_limit_from_payload(data)
    return True


def _normalize_actions_billing(payload: Any, scope_type: str, scope_name: str) -> dict[str, Any] | None:
    """Normalize GitHub Actions billing payload to a stable dashboard shape."""
    if not isinstance(payload, dict):
        return None

    total_minutes_used = payload.get("total_minutes_used")
    total_paid_minutes_used = payload.get("total_paid_minutes_used")
    included_minutes = payload.get("included_minutes")

    def _to_int(v: Any) -> int | None:
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

    used = _to_int(total_minutes_used)
    paid_used = _to_int(total_paid_minutes_used)
    included = _to_int(included_minutes)

    remaining: int | None = None
    if included is not None and paid_used is not None:
        remaining = max(0, included - paid_used)

    return {
        "scope_type": scope_type,
        "scope_name": scope_name,
        "included_minutes": included,
        "total_minutes_used": used,
        "total_paid_minutes_used": paid_used,
        "minutes_remaining": remaining,
        "updated_at": int(time.time()),
        "status": "ok",
        "error": None,
    }


def refresh_actions_billing(
    access_token: str | None = None,
    owner: str | None = None,
    org: str | None = None,
) -> bool:
    """Fetch GitHub Actions minutes usage for the configured org/user scope."""
    global actions_billing

    scope_name = (org or owner or "").strip()
    if not scope_name:
        return False

    # Try explicit org first when configured.
    if org:
        endpoint = f"/orgs/{scope_name}/settings/billing/actions"
        payload = github_request(endpoint, access_token=access_token)
        normalized = _normalize_actions_billing(payload, "org", scope_name)
        if normalized:
            actions_billing = normalized
            return True
        actions_billing = {
            "scope_type": "org",
            "scope_name": scope_name,
            "included_minutes": None,
            "total_minutes_used": None,
            "total_paid_minutes_used": None,
            "minutes_remaining": None,
            "updated_at": int(time.time()),
            "status": "error",
            "error": "Unable to read org Actions billing (permissions or API response).",
        }
        return False

    # For OWNER, try user scope first, then org scope as fallback.
    endpoint_user = f"/users/{scope_name}/settings/billing/actions"
    payload_user = github_request(endpoint_user, access_token=access_token)
    normalized_user = _normalize_actions_billing(payload_user, "user", scope_name)
    if normalized_user:
        actions_billing = normalized_user
        return True

    endpoint_org = f"/orgs/{scope_name}/settings/billing/actions"
    payload_org = github_request(endpoint_org, access_token=access_token)
    normalized_org = _normalize_actions_billing(payload_org, "org", scope_name)
    if normalized_org:
        actions_billing = normalized_org
        return True

    actions_billing = {
        "scope_type": "unknown",
        "scope_name": scope_name,
        "included_minutes": None,
        "total_minutes_used": None,
        "total_paid_minutes_used": None,
        "minutes_remaining": None,
        "updated_at": int(time.time()),
        "status": "error",
        "error": "Unable to read Actions billing (permissions or API response).",
    }
    return False


def github_request(endpoint: str, access_token: str | None = None, method: str = "GET") -> Any:
    """Perform an authenticated GitHub REST API request with rate-limit tracking.

    Returns the parsed JSON body, True for a bodiless success (204/202), or None on failure.
    """
    now = time.time()
    if rate_limit_remaining is not None and rate_limit_reset is not None and rate_limit_remaining <= 10 and now < rate_limit_reset:
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
            _update_rate_limit_from_headers(resp.headers)
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else True
            if endpoint == "/rate_limit" and isinstance(parsed, dict):
                _update_rate_limit_from_payload(parsed)
            return parsed
    except urllib.error.HTTPError as e:
        _update_rate_limit_from_headers(e.headers or {})
        if e.code in (401, 403) and rate_limit_remaining == 0:
            if rate_limit_reset:
                reset_time = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(rate_limit_reset))
            else:
                reset_time = "unknown"
            limit_text = str(rate_limit_total) if rate_limit_total is not None else "unknown"
            print(f"[Autoscaler:API] ❌ Rate limit exceeded (0/{limit_text} remaining). Resets at {reset_time}.")
        elif e.code != 404:
            print(f"[Autoscaler:API] HTTP Error {e.code} for {endpoint}: {e.reason}")
        return None
    except Exception as e:  # noqa: BLE001
        print(f"[Autoscaler:API] Connection error for {endpoint}: {e}")
        return None


def get_workflow_text_for_run(
    repo_full_name: str, run_id: int, access_token: str | None = None
) -> str | None:
    """Fetch the raw workflow YAML that produced a given run, at the exact
    commit it ran against. Returns None (and caches the miss) if the run,
    its workflow path, or the file content can't be resolved -- callers
    must treat that as "unknown", not "no services declared".
    """
    if run_id in _workflow_text_cache:
        return _workflow_text_cache[run_id]

    text: str | None = None
    run_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run_id}", access_token=access_token)
    path = run_data.get("path") if isinstance(run_data, dict) else None
    head_sha = run_data.get("head_sha") if isinstance(run_data, dict) else None

    if path and head_sha:
        contents = github_request(
            f"/repos/{repo_full_name}/contents/{path}?ref={head_sha}", access_token=access_token
        )
        if isinstance(contents, dict) and contents.get("encoding") == "base64" and contents.get("content"):
            try:
                text = base64.b64decode(contents["content"]).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                text = None

    _workflow_text_cache[run_id] = text
    return text


def get_queued_job_details(repo_full_name: str, access_token: str | None = None) -> list[dict[str, Any]]:
    """Retrieve detailed metadata for unclaimed queued jobs in a repository."""
    data = github_request(f"/repos/{repo_full_name}/actions/runs?status=queued", access_token=access_token)
    if not isinstance(data, dict) or "workflow_runs" not in data:
        return []

    queued_runs = data["workflow_runs"]
    if not queued_runs:
        return []

    detailed_jobs: list[dict[str, Any]] = []
    for run in queued_runs:
        run_id = run.get("id")
        if not run_id:
            continue
        jobs_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run_id}/jobs", access_token=access_token)
        if not isinstance(jobs_data, dict) or "jobs" not in jobs_data:
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
                "job_url": job.get("html_url") or (
                    f"https://github.com/{repo_full_name}/actions/runs/{run_id}/job/{job.get('id')}"
                    if run_id and job.get("id") else ""
                ),
                "run_url": run.get("html_url") or (
                    f"https://github.com/{repo_full_name}/actions/runs/{run_id}" if run_id else ""
                ),
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
