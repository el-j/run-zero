"""
Tests for drivers.backoff.BuildBackoff: per-key build dedup and exponential cooldown.
"""

import threading
import unittest
from unittest.mock import patch

from drivers.backoff import MAX_COOLDOWN_SECONDS, BuildBackoff, cooldown_for


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class TestCooldownFor(unittest.TestCase):
    def test_doubles_from_30s_and_caps_at_900s(self):
        self.assertEqual([cooldown_for(n) for n in range(1, 8)], [30, 60, 120, 240, 480, 900, 900])
        self.assertEqual(cooldown_for(50), MAX_COOLDOWN_SECONDS)


class TestBuildBackoff(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.backoff = BuildBackoff(clock=self.clock)

    def test_dedupes_concurrent_builds_per_key(self):
        self.assertTrue(self.backoff.try_begin("arm64"))
        self.assertFalse(self.backoff.try_begin("arm64"))
        self.assertTrue(self.backoff.try_begin("amd64"))

    def test_failure_starts_cooldown_success_resets(self):
        self.backoff.try_begin("arm64")
        self.assertEqual(self.backoff.finish("arm64", ok=False), (1, 30))
        self.assertEqual(self.backoff.remaining("arm64"), 30.0)
        self.assertFalse(self.backoff.try_begin("arm64"))
        self.clock.now += 31
        self.assertTrue(self.backoff.try_begin("arm64"))
        self.assertEqual(self.backoff.finish("arm64", ok=False), (2, 60))
        self.clock.now += 61
        self.backoff.try_begin("arm64")
        self.assertIsNone(self.backoff.finish("arm64", ok=True))
        self.assertEqual(self.backoff.failure_counts["arm64"], 0)
        self.assertEqual(self.backoff.remaining("arm64"), 0.0)

    def _run(self, build, key="arm64"):
        failures: list[tuple[int, int]] = []
        started = self.backoff.run_async(key, build, f"runzero-build-test-{key}", lambda f, c: failures.append((f, c)), "[test]")
        self.assertTrue(self.backoff.join(timeout=5.0))
        return started, failures

    def test_run_async_success(self):
        started, failures = self._run(lambda: True)
        self.assertTrue(started)
        self.assertEqual(failures, [])
        self.assertNotIn("arm64", self.backoff.in_progress)

    def test_run_async_failure_reports_backoff(self):
        _, failures = self._run(lambda: False)
        self.assertEqual(failures, [(1, 30)])

    def test_run_async_crash_counts_as_failure_and_is_logged(self):
        def boom() -> bool:
            raise RuntimeError("kaboom")

        with patch("sys.stderr") as err:
            _, failures = self._run(boom)
        self.assertEqual(failures, [(1, 30)])
        self.assertIn("kaboom", "".join(str(c.args[0]) for c in err.write.call_args_list))

    def test_run_async_refuses_while_building_or_cooling_down(self):
        gate = threading.Event()
        self.assertTrue(self.backoff.run_async("arm64", lambda: gate.wait(5) and False, "runzero-build-test", lambda f, c: None, "[test]"))
        self.assertFalse(self.backoff.run_async("arm64", lambda: True, "runzero-build-test", lambda f, c: None, "[test]"))
        gate.set()
        self.assertTrue(self.backoff.join(timeout=5.0))
        self.assertFalse(self.backoff.run_async("arm64", lambda: True, "runzero-build-test", lambda f, c: None, "[test]"))  # cooling down

    def test_join_reports_threads_still_running(self):
        gate = threading.Event()
        self.backoff.run_async("arm64", lambda: gate.wait(5), "runzero-build-test", lambda f, c: None, "[test]")
        self.assertFalse(self.backoff.join(timeout=0.01))
        gate.set()
        self.assertTrue(self.backoff.join(timeout=5.0))


if __name__ == "__main__":
    unittest.main()
