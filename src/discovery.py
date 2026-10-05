"""
Repository auto-discovery with activity date cutoffs and owner filtering.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from github_api import github_request


def _parse_timestamp(value: str) -> datetime | None:
    """Parse a GitHub ISO-8601 timestamp (``...Z``), returning None when it is malformed."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError):
        return None


USER_REPOS_ENDPOINT = "/user/repos?affiliation=owner&sort=pushed&direction=desc"


def _repo_listing_endpoint(owner: str, access_token: str | None) -> str:
    """Return the repo-listing endpoint for `owner`, most recently pushed first.

    `/user/repos?affiliation=owner` only lists repos the token's *user* owns, so an
    organization OWNER discovered nothing. When `owner` is an organization, its own
    `/orgs/{owner}/repos` listing is used instead.
    """
    if owner:
        account = github_request(f"/users/{owner}", access_token=access_token)
        if isinstance(account, dict) and account.get("type") == "Organization":
            return f"/orgs/{owner}/repos?type=all&sort=pushed&direction=desc"
    return USER_REPOS_ENDPOINT


def _filter_repo_item(item: Any, owner: str, cutoff_date: datetime) -> tuple[str | None, bool]:
    """Inspect a repository record, returning (repo_name_or_none, stop_pagination)."""
    if not isinstance(item, dict) or item.get("archived", False):
        return None, False

    full_name = item.get("full_name", "")
    if owner and not full_name.startswith(f"{owner}/"):
        return None, False

    pushed_at_str = item.get("pushed_at")
    if pushed_at_str:
        pushed_at = _parse_timestamp(pushed_at_str)
        # An unparseable timestamp keeps the repo (fail open): dropping a repo
        # silently would stop its queued jobs from ever being scaled for.
        if pushed_at is not None and pushed_at < cutoff_date:
            return None, True

    return full_name, False


def _paginate_repositories(endpoint: str, owner: str, cutoff_date: datetime, access_token: str | None) -> set[str]:
    """Iterate through paginated GitHub repos endpoint until cutoff or end."""
    repos: set[str] = set()
    page = 1
    while True:
        data = github_request(f"{endpoint}&per_page=100&page={page}", access_token=access_token)
        if not isinstance(data, list) or not data:
            break

        stop_pagination = False
        for item in data:
            name, stop = _filter_repo_item(item, owner, cutoff_date)
            if stop:
                stop_pagination = True
                break
            if name:
                repos.add(name)

        if stop_pagination or len(data) < 100:
            break
        page += 1
    return repos


def discover_repositories(
    owner: str = "", active_days: int = 60, auto_discover: bool = True, repos_config: str = "", access_token: str | None = None
) -> list[str]:
    """Discover list of active repositories to monitor."""
    repos: set[str] = set()

    if repos_config:
        for r in repos_config.split(","):
            r = r.strip()
            if r:
                repos.add(r)
        return sorted(repos)

    if auto_discover and access_token:
        cutoff_date = datetime.now(UTC) - timedelta(days=active_days)
        endpoint = _repo_listing_endpoint(owner, access_token)
        repos = _paginate_repositories(endpoint, owner, cutoff_date, access_token)

    return sorted(repos)
