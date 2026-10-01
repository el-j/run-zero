"""
Golden-image build deduplication and exponential backoff, shared by the Docker and OrbStack drivers.

Both drivers build a per-arch "golden" artifact (runner image / base VM) on a background thread
so the poll loop never blocks. `BuildBackoff` guarantees at most one build per key at a time and,
after a failure, refuses new attempts for an exponentially growing cooldown
(30s, 60s, 120s ... capped at 900s) so a non-transient failure isn't retried every poll tick.
"""

import sys
import threading
import time
from collections.abc import Callable

BASE_COOLDOWN_SECONDS = 30
MAX_COOLDOWN_SECONDS = 900


def cooldown_for(failures: int) -> int:
    """Cooldown after `failures` consecutive failed builds: 30s doubling per failure, capped at 900s."""
    return int(min(BASE_COOLDOWN_SECONDS * (2 ** (failures - 1)), MAX_COOLDOWN_SECONDS))


class BuildBackoff:
    """Per-key (arch) build state: in-progress set, consecutive failures and retry deadlines."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        """Start with no builds running and no failures recorded."""
        self.lock = threading.Lock()
        self.in_progress: set[str] = set()
        self.failure_counts: dict[str, int] = {}
        self.retry_after: dict[str, float] = {}
        self.threads: dict[str, threading.Thread] = {}
        self._clock = clock

    def remaining(self, key: str) -> float:
        """Seconds left before `key` may be built again (0.0 when not cooling down)."""
        return max(0.0, self.retry_after.get(key, 0.0) - self._clock())

    def try_begin(self, key: str) -> bool:
        """Claim `key` for a build; False if it is already building or cooling down."""
        with self.lock:
            if key in self.in_progress or self.remaining(key) > 0:
                return False
            self.in_progress.add(key)
            return True

    def finish(self, key: str, ok: bool) -> tuple[int, int] | None:
        """Release `key`. On success reset its failures; on failure return (failures, cooldown_seconds)."""
        with self.lock:
            self.in_progress.discard(key)
            if ok:
                self.failure_counts[key] = 0
                self.retry_after.pop(key, None)
                return None
            failures = self.failure_counts.get(key, 0) + 1
            self.failure_counts[key] = failures
            cooldown = cooldown_for(failures)
            self.retry_after[key] = self._clock() + cooldown
            return failures, cooldown

    def run_async(self, key: str, build: Callable[[], bool], thread_name: str, on_failure: Callable[[int, int], None], log_prefix: str) -> bool:
        """Run `build` on a daemon thread if `key` can be claimed; returns whether a build started.

        A crash inside `build` counts as a failure (logged, then backoff) instead of escaping as
        an unhandled thread exception. `on_failure(failures, cooldown)` reports the backoff.
        """
        if not self.try_begin(key):
            return False

        def _run() -> None:
            """Execute build in background thread and report failure or backoff upon completion."""
            ok = False
            try:
                ok = build()
            except Exception as exc:
                print(f"{log_prefix} Golden image build for '{key}' crashed: {exc}", file=sys.stderr)
            finally:
                outcome = self.finish(key, ok)
                if outcome is not None:
                    on_failure(*outcome)

        thread = threading.Thread(target=_run, name=thread_name, daemon=True)
        self.threads[key] = thread
        thread.start()
        return True

    def join(self, timeout: float = 10.0) -> bool:
        """Wait for every started build thread; True if all finished within `timeout` each."""
        for thread in list(self.threads.values()):
            thread.join(timeout=timeout)
        return not any(t.is_alive() for t in self.threads.values())
