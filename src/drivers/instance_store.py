"""
Host-side metadata for runner instances whose backend can't carry it (Multipass, WSL2).

Neither `multipass list` nor `wsl --list` can report which repository/org a runner serves,
which architecture it runs, or when it was created -- but the autoscaler's per-repo scaling
and the reconciler both depend on those. Instance names can't carry them faithfully either
(both backends restrict instance names to [A-Za-z0-9-]). `InstanceStore` persists them in a
small JSON file next to the host cache, so they also survive a restart of the process that
owns the driver (the Host VM Bridge), unlike in-memory tracking.
"""

import contextlib
import json
import os
import tempfile
import threading
from typing import Any


def default_state_dir() -> str:
    """Directory for driver state: $RUNZERO_STATE_DIR, else ~/.local-github-runner/state."""
    return os.getenv("RUNZERO_STATE_DIR") or os.path.join(os.path.expanduser("~"), ".local-github-runner", "state")


class InstanceStore:
    """A tiny, thread-safe, atomically written name -> metadata JSON map."""

    def __init__(self, path: str):
        """Persist to `path` (created on first write)."""
        self.path = path
        self._lock = threading.Lock()

    def _read(self) -> dict[str, dict[str, Any]]:
        """Read and parse persisted JSON metadata dictionary from disk."""
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return {}
        return {k: v for k, v in data.items() if isinstance(v, dict)} if isinstance(data, dict) else {}

    def _write(self, data: dict[str, dict[str, Any]]) -> None:
        """Atomically persist metadata dictionary to disk via temporary file rename."""
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path) or ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=1, sort_keys=True)
            os.replace(tmp, self.path)
        except OSError:
            with contextlib.suppress(OSError):
                os.remove(tmp)
            raise

    def all(self) -> dict[str, dict[str, Any]]:
        """All recorded instances and their metadata."""
        with self._lock:
            return dict(self._read())

    def get(self, name: str) -> dict[str, Any]:
        """Metadata recorded for `name` ({} if unknown)."""
        with self._lock:
            return dict(self._read().get(name, {}))

    def put(self, name: str, **meta: Any) -> None:
        """Record (replace) metadata for `name`. Best-effort: a write failure is not fatal."""
        with self._lock:
            data = self._read()
            data[name] = meta
            with contextlib.suppress(OSError):
                self._write(data)

    def remove(self, name: str) -> None:
        """Forget `name` (no-op if unknown)."""
        with self._lock:
            data = self._read()
            if data.pop(name, None) is not None:
                with contextlib.suppress(OSError):
                    self._write(data)

    def prune(self, keep: set[str]) -> None:
        """Forget every instance not in `keep` (e.g. deleted outside RunZero)."""
        with self._lock:
            data = self._read()
            stale = set(data) - keep
            if stale:
                with contextlib.suppress(OSError):
                    self._write({k: v for k, v in data.items() if k in keep})
