"""Workflow run action service for the RunZero dashboard.

Provides handlers for cancelling, re-running, and re-running failed GitHub Actions
workflow runs directly from the dashboard via the GitHub REST API.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def execute_workflow_action(
    repo: str,
    run_id: int,
    action: str,
    access_token: str | None,
) -> dict[str, Any]:
    """Execute a workflow run control action (cancel, rerun, or rerun-failed) on GitHub."""
    if not repo or "/" not in repo:
        raise ValueError(f"Invalid repository: '{repo}'. Must be in 'owner/repo' format.")
    if run_id <= 0:
        raise ValueError(f"Invalid run_id: {run_id}. Must be a positive integer.")

    normalized_action = action.lower().strip()
    action_endpoints: dict[str, str] = {
        "cancel": "cancel",
        "rerun": "rerun",
        "rerun-failed": "rerun-failed-jobs",
    }

    sub_path = action_endpoints.get(normalized_action)
    if not sub_path:
        valid = ", ".join(action_endpoints.keys())
        raise ValueError(f"Invalid action: '{action}'. Must be one of: {valid}")

    if not access_token:
        raise ValueError("GitHub access token is required to execute workflow actions.")

    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/{sub_path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "RunZero-Autoscaler",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            status_code = resp.status
            return {
                "ok": True,
                "status": status_code,
                "message": f"Successfully triggered '{normalized_action}' on {repo} run #{run_id}.",
            }
    except urllib.error.HTTPError as e:
        raw_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw_body)
            msg = parsed.get("message", raw_body)
        except Exception:
            msg = raw_body or str(e)
        raise RuntimeError(f"GitHub API error ({e.code}): {msg}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error contacting GitHub API: {e.reason}") from e
