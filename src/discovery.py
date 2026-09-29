"""
Repository auto-discovery with activity date cutoffs and owner filtering.
"""

from datetime import UTC, datetime, timedelta

from github_api import github_request


def _parse_timestamp(value: str) -> datetime | None:
    """Parse a GitHub ISO-8601 timestamp (``...Z``), returning None when it is malformed."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError):
        return None


def discover_repositories(
    owner: str = "", active_days: int = 60, auto_discover: bool = True, repos_config: str = "", access_token: str | None = None
) -> list[str]:
    """Discover list of active repositories to monitor."""
    repos = set()

    if repos_config:
        for r in repos_config.split(","):
            r = r.strip()
            if r:
                repos.add(r)
        return sorted(repos)

    if auto_discover and access_token:
        cutoff_date = datetime.now(UTC) - timedelta(days=active_days)
        page = 1
        while True:
            data = github_request(f"/user/repos?per_page=100&affiliation=owner&sort=pushed&direction=desc&page={page}", access_token=access_token)
            if not isinstance(data, list) or not data:
                break

            stop_pagination = False
            for item in data:
                if not isinstance(item, dict) or item.get("archived", False):
                    continue

                full_name = item.get("full_name", "")
                if owner and not full_name.startswith(f"{owner}/"):
                    continue

                pushed_at_str = item.get("pushed_at")
                if pushed_at_str:
                    pushed_at = _parse_timestamp(pushed_at_str)
                    # An unparseable timestamp keeps the repo (fail open): dropping a repo
                    # silently would stop its queued jobs from ever being scaled for.
                    if pushed_at is not None and pushed_at < cutoff_date:
                        stop_pagination = True
                        break

                repos.add(full_name)

            if stop_pagination or len(data) < 100:
                break
            page += 1

    return sorted(repos)
