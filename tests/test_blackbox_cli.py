"""
Blackbox / process-boundary contract tests for the Makefile/CLI surface (issue #18).

Same three-layer split documented in tests/test_blackbox_dashboard.py's module
docstring: unlike every other test in this suite, these invoke a real `make`
target as an actual subprocess (`subprocess.run(["make", ...])`, from the real
repo root) and assert on real stdout/exit code -- the way an operator running
`make info` at a terminal actually experiences it. Nothing here imports `src/`
or mocks anything; the process boundary under test is the Makefile itself.

Targets are chosen for being side-effect-free, and the process is made hermetic: `docker`
and `orbctl` resolve to no-op stubs placed first on PATH, and HOME points at a temp dir. So
`make info` never starts containers against the operator's real volumes or walks their real
~/.local-github-runner cache (on a host with a few GB of proxy caches that alone took over
two minutes), and results don't depend on what happens to be installed or running.
"""

import os
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestMakeCLIBlackboxContract(unittest.TestCase):
    """Shells out to the real `make` binary against the real Makefile at the repo root."""

    _sandbox: str
    _env: dict[str, str]

    @classmethod
    def setUpClass(cls) -> None:
        if shutil.which("make") is None:
            raise unittest.SkipTest("`make` is not available on this test host")
        cls._sandbox = tempfile.mkdtemp(prefix="runzero-cli-")
        stub_bin = os.path.join(cls._sandbox, "bin")
        os.makedirs(stub_bin)
        for tool in ("docker", "orbctl"):
            path = os.path.join(stub_bin, tool)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("#!/bin/sh\nexit 0\n")
            os.chmod(path, 0o755)
        cls._env = {**os.environ, "PATH": f"{stub_bin}{os.pathsep}{os.environ.get('PATH', '')}", "HOME": cls._sandbox}

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls._sandbox, ignore_errors=True)

    def _run_make(self, *targets, timeout=60):
        return subprocess.run(
            ["make", *targets],
            cwd=REPO_ROOT,
            env=self._env,
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
