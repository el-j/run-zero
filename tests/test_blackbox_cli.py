"""
Blackbox / process-boundary contract tests for the Makefile/CLI surface (issue #18).

Same three-layer split documented in tests/test_blackbox_dashboard.py's module
docstring: unlike every other test in this suite, these invoke a real `make`
target as an actual subprocess (`subprocess.run(["make", ...])`, from the real
repo root) and assert on real stdout/exit code -- the way an operator running
`make info` at a terminal actually experiences it. Nothing here imports `src/`
or mocks anything; the process boundary under test is the Makefile itself.

Targets are chosen deliberately for being side-effect-free and fast (no
docker/orbctl requirement to pass, since `make info`/`make cache-size`/
`make help` all degrade gracefully via `2>/dev/null || echo ...` fallbacks
when those tools aren't on the host) so this file runs unconditionally in CI
and in the container `make test-suite` runs in, without needing real
Docker/OrbStack/GitHub access.
"""

import os
import subprocess
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestMakeCLIBlackboxContract(unittest.TestCase):
    """Shells out to the real `make` binary against the real Makefile at the repo root."""

    def _run_make(self, *targets, timeout=60):
        return subprocess.run(
            ["make", *targets],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def test_make_info_runs_and_reports_every_managed_resource_section(self):
        res = self._run_make("info")
        self.assertEqual(res.returncode, 0, f"`make info` failed:\nstdout={res.stdout}\nstderr={res.stderr}")
        for heading in (
            "Host Package/Tool Cache",
            "Proxy Cache Volumes",
            "Runner Images",
            "OrbStack VMs",
            "Ephemeral Runner Containers",
        ):
            self.assertIn(heading, res.stdout, f"`make info` output missing expected section: {heading!r}")

    def test_make_cache_size_runs_and_reports_disk_usage(self):
        res = self._run_make("cache-size")
        self.assertEqual(res.returncode, 0, f"`make cache-size` failed:\nstdout={res.stdout}\nstderr={res.stderr}")
        self.assertIn("Local Runner Cache Disk Usage", res.stdout)

    def test_make_help_lists_real_targets(self):
        # `make help` (also the .DEFAULT_GOAL, so `make` with no args hits the
        # same path) greps its own Makefile for documented targets -- this
        # both proves the CLI entrypoint works AND that the ones this file
        # itself depends on (info, cache-size) are still real, documented
        # targets, not renamed/removed out from under these tests.
        res = self._run_make("help")
        self.assertEqual(res.returncode, 0, f"`make help` failed:\nstdout={res.stdout}\nstderr={res.stderr}")
        self.assertIn("Usage:", res.stdout)
        for target in ("info", "cache-size", "dashboard", "bridge-start", "test-suite"):
            self.assertIn(target, res.stdout, f"`make help` output missing documented target: {target!r}")

    def test_make_with_unknown_target_fails_with_nonzero_exit(self):
        # Contract check on the failure path too: an operator's typo in a
        # target name must not silently succeed.
        res = self._run_make("this-target-does-not-exist")
        self.assertNotEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
