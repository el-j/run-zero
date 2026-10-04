"""
GitHub REST API client with adaptive rate-limiting and job queue inspection.
"""

from __future__ import annotations

import base64
import json
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from typing import Any

from workflow_inspector import job_uses_services_or_container

API_BASE = "https://api.github.com"
rate_limit_remaining: int | None = None
rate_limit_total: int | None = None
rate_limit_used: int | None = None
rate_limit_resource: str | None = None
rate_limit_reset: int | None = None
actions_billing: dict[str, Any] = {}

# Set by the autoscaler's signal handler. Every wait in this module (the rate-limit throttle)
# wakes on it, so a SIGTERM during a throttle stops promptly instead of sleeping up to an hour
# while `docker stop` escalates to SIGKILL and runner cleanup never runs.
shutdown_event = threading.Event()

# Longest single throttle wait. If the limit still hasn't reset afterwards, the request is
# skipped (returns None) rather than spending the last few calls; the caller retries next poll.
MAX_THROTTLE_WAIT_SECONDS = 60

# Hard ceiling on pages fetched by github_paginate(): 10 x 100 items. Bounds the API cost of a
# single call; hitting it is logged, never silent.
MAX_PAGES = 10
PAGE_SIZE = 100

# A queued run's workflow file is pinned to that run's head_sha, so its content
# never changes for the lifetime of the run -- caching by run_id avoids re-fetching +
# re-parsing the same file on every poll while it's queued. Bounded (LRU, least recently
# used run evicted first) so a long-running daemon doesn't grow it without limit.
WORKFLOW_TEXT_CACHE_SIZE = 512
_workflow_text_cache: OrderedDict[int, str | None] = OrderedDict()


def _update_rate_limit_from_headers(headers: Any) -> None:
    """Best-effort parse of GitHub rate-limit headers from a response object."""
    global rate_limit_remaining, rate_limit_total, rate_limit_used, rate_limit_resource, rate_limit_reset

    if not headers or "x-ratelimit-remaining" not in headers:
        return

    # Malformed header values stop the update at the first bad field (earlier fields are kept),
    # matching GitHub's own all-or-nothing header set in practice.
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
    except (TypeError, ValueError):
        return


def _resolve_rate_limit_resource(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Find the most relevant rate limit resource dictionary and its name in a /rate_limit response."""
    resources_obj = payload.get("resources")
    resources = resources_obj if isinstance(resources_obj, dict) else {}
    resource_key = rate_limit_resource if isinstance(rate_limit_resource, str) and rate_limit_resource else "core"
    resource_obj = resources.get(resource_key)
    if isinstance(resource_obj, dict):
        return resource_obj, resource_key

    core_obj = resources.get("core")
    if isinstance(core_obj, dict):
        return core_obj, "core"

    rate_obj = payload.get("rate")
    if isinstance(rate_obj, dict):
        return rate_obj, resource_key

    return None, resource_key


def _update_rate_limit_from_payload(payload: Any) -> None:
    """Best-effort parse from /rate_limit JSON payload (authoritative per token/account)."""
    global rate_limit_remaining, rate_limit_total, rate_limit_used, rate_limit_resource, rate_limit_reset

    if not isinstance(payload, dict):
        return

    resource_data, resource_key = _resolve_rate_limit_resource(payload)
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
    except (TypeError, ValueError):
        return


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
        """Convert a value to integer, returning None if absent or invalid."""
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
    When the rate limit is nearly exhausted, waits (interruptibly, at most
    MAX_THROTTLE_WAIT_SECONDS) for the reset, and returns None without calling GitHub if
    shutdown was requested or the limit still hasn't reset.
    """
    now = time.time()
    if rate_limit_remaining is not None and rate_limit_reset is not None and rate_limit_remaining <= 10 and now < rate_limit_reset:
        wait_seconds = min(int(rate_limit_reset - now) + 1, MAX_THROTTLE_WAIT_SECONDS)
        print(f"[Autoscaler:API] ⚠️ Rate limit nearly exhausted. Throttling for {wait_seconds}s...")
        if shutdown_event.wait(wait_seconds) or time.time() < rate_limit_reset:
            return None

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
            reset_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(rate_limit_reset)) if rate_limit_reset else "unknown"
            limit_text = str(rate_limit_total) if rate_limit_total is not None else "unknown"
            print(f"[Autoscaler:API] ❌ Rate limit exceeded (0/{limit_text} remaining). Resets at {reset_time}.")
        elif e.code != 404:
            print(f"[Autoscaler:API] HTTP Error {e.code} for {endpoint}: {e.reason}")
        return None
    except Exception as e:
        print(f"[Autoscaler:API] Connection error for {endpoint}: {e}")
        return None


def create_registration_token(repo: str | None, org: str | None, access_token: str | None) -> str | None:
    """Exchange the admin PAT for a short-lived (1 hour) runner registration token.

    Runners only ever receive this token -- never the PAT -- so a job running on them
    cannot reuse the autoscaler's credentials. `repo` wins over `org` when both are set.
    Returns None when there is no PAT/target or GitHub refuses the request.
    """
    if not access_token or not (repo or org):
        return None
    scope = f"/repos/{repo}" if repo else f"/orgs/{org}"
    data = github_request(f"{scope}/actions/runners/registration-token", access_token=access_token, method="POST")
    token = data.get("token") if isinstance(data, dict) else None
    return token if isinstance(token, str) and token else None


def github_paginate(
    endpoint: str, key: str, access_token: str | None = None, max_pages: int = MAX_PAGES, allow_truncated: bool = True
) -> list[dict[str, Any]] | None:
    """Fetch every page of a GitHub list endpoint and return the concatenated `key` items.

    GitHub list endpoints default to 30 items per page; without this, a matrix of more than
    30 jobs or a repo with more than 30 runners is silently truncated. Requests
    `per_page=100` and follows pages until a short page, up to `max_pages` (a truncation
    warning is printed if the cap is hit).

    Returns None if ANY page fails or is malformed: a partial list would be mistaken for the
    complete set (e.g. "these are all the registered runners") by callers. For the same
    reason, callers that treat the result as exhaustive pass `allow_truncated=False` to get
    None instead of a capped list.
    """
    sep = "&" if "?" in endpoint else "?"
    items: list[dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        data = github_request(f"{endpoint}{sep}per_page={PAGE_SIZE}&page={page}", access_token=access_token)
        batch = data.get(key) if isinstance(data, dict) else None
        if not isinstance(batch, list):
            return None
        items.extend(item for item in batch if isinstance(item, dict))
        if len(batch) < PAGE_SIZE:
            return items
    print(f"[Autoscaler:API] ⚠️ {endpoint} has more than {max_pages * PAGE_SIZE} {key}; only the first {max_pages * PAGE_SIZE} were read.")
    return items if allow_truncated else None


def get_workflow_text_for_run(repo_full_name: str, run_id: int, access_token: str | None = None) -> str | None:
    """Fetch the raw workflow YAML that produced a given run, at the exact
    commit it ran against. Returns None (and caches the miss) if the run,
    its workflow path, or the file content can't be resolved -- callers
    must treat that as "unknown", not "no services declared".
    """
    if run_id in _workflow_text_cache:
        _workflow_text_cache.move_to_end(run_id)
        return _workflow_text_cache[run_id]

    text: str | None = None
    run_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run_id}", access_token=access_token)
    path = run_data.get("path") if isinstance(run_data, dict) else None
    head_sha = run_data.get("head_sha") if isinstance(run_data, dict) else None

    if path and head_sha:
        contents = github_request(f"/repos/{repo_full_name}/contents/{path}?ref={head_sha}", access_token=access_token)
        if isinstance(contents, dict) and contents.get("encoding") == "base64" and contents.get("content"):
            try:
                text = base64.b64decode(contents["content"]).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                text = None

    _workflow_text_cache[run_id] = text
    while len(_workflow_text_cache) > WORKFLOW_TEXT_CACHE_SIZE:
        _workflow_text_cache.popitem(last=False)
    return text


def get_queued_job_details(
    repo_full_name: str,
    access_token: str | None = None,
    include_in_progress: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve detailed metadata for unclaimed queued (and optionally in-progress) jobs in a repository.

    Queued jobs live in `queued` runs and in `in_progress` ones: as soon as any job of a run
    starts, or is skipped (a re-run marks its skipped jobs as started at once), the whole run
    is `in_progress`, while its later jobs still wait. Listing only `queued` runs hid those
    jobs, so they got a runner only if one spawned for another job happened to take them
    (an el-j/herbful E2E re-run waited 17 minutes this way, 2026-10-04).
    """
    queued_runs: list[dict[str, Any]] = []
    seen_run_ids = set()
    for status in ("queued", "in_progress"):
        for run in github_paginate(f"/repos/{repo_full_name}/actions/runs?status={status}", "workflow_runs", access_token=access_token) or []:
            if run.get("id") not in seen_run_ids:
                seen_run_ids.add(run.get("id"))
                queued_runs.append(run)
    if not queued_runs:
        return []

    target_statuses = ("queued", "in_progress") if include_in_progress else ("queued",)
    detailed_jobs: list[dict[str, Any]] = []
    for run in queued_runs:
        run_id = run.get("id")
        if not run_id:
            continue
        jobs = github_paginate(f"/repos/{repo_full_name}/actions/runs/{run_id}/jobs", "jobs", access_token=access_token)
        if jobs is None:
            continue

        # GitHub only ever dispatches a job to one of our runners if its
        # `runs-on:` requested the literal "self-hosted" label (every
        # self-hosted-targeting workflow in this fleet's convention
        # includes it explicitly, e.g. `["self-hosted", "local"]`) --
        # without this check, a queued `ubuntu-latest` job (which will
        # never be assigned to us) still causes a container/VM spawn
        # that then sits registered and idle forever, since GitHub
        # dispatches it to its own hosted fleet instead.
        qualifying_jobs = [job for job in jobs if job.get("status") in target_statuses and "self-hosted" in job.get("labels", [])]
        if not qualifying_jobs:
            continue

        # Fetched once per run (not per job) and cached forever by run_id --
        # a run can have dozens of jobs sharing the same workflow file.
        workflow_text = get_workflow_text_for_run(repo_full_name, run_id, access_token=access_token)

        for job in qualifying_jobs:
            declares_services = job_uses_services_or_container(workflow_text, job.get("name", "")) if workflow_text is not None else None
            detailed_jobs.append(
                {
                    "id": job.get("id"),
                    "name": job.get("name", ""),
                    "run_id": run_id,
                    "status": job.get("status", "queued"),
                    "run_attempt": job.get("run_attempt") or run.get("run_attempt") or 1,
                    # The workflow FILE path (e.g. ".github/workflows/ci.yml"), stable across every
                    # run of this workflow -- unlike run_id/id, which are unique per execution and
                    # therefore useless as a cache scope key (see build_cache_scope() in
                    # autoscaler.py: it's combined with the job name for a stable, reusable
                    # per-job build-cache directory instead of one that's thrown away every run).
                    "workflow_path": run.get("path", ""),
                    "workflow_name": run.get("name") or (run.get("path", "").rsplit("/", 1)[-1] if run.get("path") else ""),
                    "job_url": job.get("html_url")
                    or (f"https://github.com/{repo_full_name}/actions/runs/{run_id}/job/{job.get('id')}" if run_id and job.get("id") else ""),
                    "run_url": run.get("html_url") or (f"https://github.com/{repo_full_name}/actions/runs/{run_id}" if run_id else ""),
                    "labels": job.get("labels", []),
                    "head_branch": run.get("head_branch", ""),
                    "event": run.get("event", ""),
                    "created_at": job.get("created_at") or job.get("started_at") or run.get("run_started_at") or run.get("created_at") or "",
                    "started_at": job.get("started_at") or "",
                    # True/False when the workflow file could be located and
                    # parsed and the job matched by name; None ("unknown") if
                    # not -- router.py must fall back to its name/label
                    # heuristic rather than treat None as "no services".
                    "declares_services": declares_services,
                }
            )
    return detailed_jobs
