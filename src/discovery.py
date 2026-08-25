"""
Repository auto-discovery with activity date cutoffs and owner filtering.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from github_api import github_request


def discover_repositories(
    owner: str = "",
    active_days: int = 60,
    auto_discover: bool = True,
    repos_config: str = "",
    access_token: Optional[str] = None
) -> List[str]:
    """Discover list of active repositories to monitor."""
    repos = set()

    if repos_config:
        for r in repos_config.split(","):
            r = r.strip()
            if r:
                repos.add(r)
        return sorted(list(repos))

    if auto_discover and access_token:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=active_days)
        page = 1
        while True:
            data = github_request(
                f"/user/repos?per_page=100&affiliation=owner&sort=pushed&direction=desc&page={page}",
                access_token=access_token
            )
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
