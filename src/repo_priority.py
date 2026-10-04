"""
Repository Priority and Pause State Manager.

Maintains operator-defined repository priority order and paused status.
Free runner slots are allocated to queued jobs of higher-priority repositories first.
Repositories marked as paused have runner allocation suspended while jobs remain queued.
State is seeded from REPO_PRIORITY and persisted to disk in the state directory so it
survives autoscaler restarts.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import threading
from collections.abc import Sequence
from typing import Any

from drivers.instance_store import default_state_dir

REPO_PRIORITY_FILE = "repo-priority.json"


def parse_repo_priority_env(val: str | None) -> list[str]:
    """Parse comma-separated repository names from REPO_PRIORITY string.

    Trims whitespace and omits empty entries while preserving order and uniqueness.
    """
    if not val:
        return []
    seen: set[str] = set()
    result: list[str] = []
    for item in val.split(","):
        cleaned = item.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


class RepoPriorityManager:
    """Thread-safe manager for repository priority order and paused state.

    Persists configuration changes to disk and resolves priority lists for
    tracked repositories.
    """

    def __init__(
        self,
        state_file: str | None = None,
        initial_priority: Sequence[str] | None = None,
        initial_paused: Sequence[str] | None = None,
    ) -> None:
        """Initialize priority manager with optional custom state file and defaults."""
        self._state_file = state_file or os.path.join(default_state_dir(), REPO_PRIORITY_FILE)
        self._lock = threading.Lock()
        self._priority: list[str] = []
        self._paused: set[str] = set()

        # Load from disk if file exists; otherwise seed from initial defaults
        if not self._load():
            if initial_priority:
                self._priority = self._clean_list(initial_priority)
            if initial_paused:
                self._paused = set(self._clean_list(initial_paused))
            if self._priority or self._paused:
                self._save()

    @staticmethod
    def _clean_list(items: Sequence[str]) -> list[str]:
        """Normalize sequence of repository names, stripping whitespace and removing duplicates."""
        seen: set[str] = set()
        cleaned: list[str] = []
        for it in items:
            if isinstance(it, str):
                val = it.strip()
                if val and val not in seen:
                    seen.add(val)
                    cleaned.append(val)
        return cleaned

    def _load(self) -> bool:
        """Attempt to read and parse persisted priority and paused state from disk."""
        if not os.path.isfile(self._state_file):
            return False
        try:
            with open(self._state_file, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                raw_prio = data.get("priority", [])
                raw_paused = data.get("paused", [])
                if isinstance(raw_prio, list):
                    self._priority = self._clean_list(raw_prio)
                if isinstance(raw_paused, list):
                    self._paused = set(self._clean_list(raw_paused))
                return True
        except (OSError, ValueError):
            pass
        return False

    def _save(self) -> None:
        """Atomically persist priority and paused state to disk."""
        directory = os.path.dirname(self._state_file) or "."
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        data = {
            "priority": self._priority,
            "paused": sorted(self._paused),
        }
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            os.replace(tmp, self._state_file)
        except OSError:
            with contextlib.suppress(OSError):
                os.remove(tmp)
            raise

    def get_priority_list(self, repositories: Sequence[str]) -> list[str]:
        """Order tracked repositories according to configured priority.

        Repositories explicitly in the priority list appear first in their defined order.
        Any repositories in `repositories` not explicitly prioritized appear after,
        preserving their original sequence.
        """
        with self._lock:
            prio_order = list(self._priority)

        repo_set = set(repositories)
        result: list[str] = []
        # First add known prioritized repositories that are among tracked repositories
        for repo in prio_order:
            if repo in repo_set and repo not in result:
                result.append(repo)
        # Then append remaining tracked repositories in their given sequence
        for repo in repositories:
            if repo not in result:
                result.append(repo)
        return result

    def is_paused(self, repo: str) -> bool:
        """Check if runner allocation for a repository is currently paused."""
        with self._lock:
            return repo in self._paused

    def set_priority(self, priority: Sequence[str]) -> None:
        """Set new repository priority order and persist to disk."""
        cleaned = self._clean_list(priority)
        with self._lock:
            self._priority = cleaned
            self._save()

    def set_paused(self, repo: str, paused: bool) -> None:
        """Set pause state for a single repository and persist to disk."""
        clean_repo = repo.strip()
        if not clean_repo:
            return
        with self._lock:
            if paused:
                self._paused.add(clean_repo)
            else:
                self._paused.discard(clean_repo)
            self._save()

    def update(self, priority: Sequence[str] | None = None, paused: Sequence[str] | None = None) -> None:
        """Atomically update both priority order and paused list and persist to disk."""
        with self._lock:
            if priority is not None:
                self._priority = self._clean_list(priority)
            if paused is not None:
                self._paused = set(self._clean_list(paused))
            self._save()

    def get_state(self) -> dict[str, Any]:
        """Return a snapshot dictionary containing priority and paused repository lists."""
        with self._lock:
            return {
                "priority": list(self._priority),
                "paused": sorted(self._paused),
            }
