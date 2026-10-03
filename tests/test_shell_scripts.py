"""
Tests for shell scripts syntax and entrypoint validation.
"""

import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from cache_manager import init_cache_dirs

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestShellScripts(unittest.TestCase):
    def test_start_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "start.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("docker/start.sh")

        if not os.path.isfile(script_path):
            self.skipTest("start.sh not available in temp sandbox directory")

        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, f"Syntax error in start.sh: {res.stderr}")

    def test_setup_env_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "setup_env.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/setup_env.sh")

        if not os.path.isfile(script_path):
            self.skipTest("setup_env.sh not available in temp sandbox directory")

        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, f"Syntax error in setup_env.sh: {res.stderr}")

    def test_setup_env_sh_non_interactive(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "setup_env.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/setup_env.sh")

        if not os.path.isfile(script_path):
            self.skipTest("setup_env.sh not available in temp sandbox directory")

        env = os.environ.copy()
        env["NON_INTERACTIVE"] = "true"
        res = subprocess.run(["bash", script_path], capture_output=True, text=True, env=env, check=False)
        self.assertEqual(res.returncode, 0, f"Error running setup_env.sh: {res.stderr}")

    def test_pre_commit_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "pre-commit.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/pre-commit.sh")
        if not os.path.isfile(script_path):
            self.skipTest("pre-commit.sh not found")
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, f"Syntax error in pre-commit.sh: {res.stderr}")

    def test_pre_push_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "pre-push.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/pre-push.sh")
        if not os.path.isfile(script_path):
            self.skipTest("pre-push.sh not found")
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, f"Syntax error in pre-push.sh: {res.stderr}")

    def test_provision_toolchain_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "provision-toolchain.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("docker/provision-toolchain.sh")
        if not os.path.isfile(script_path):
            self.skipTest("provision-toolchain.sh not found")
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, f"Syntax error in provision-toolchain.sh: {res.stderr}")

    def test_start_sh_fallback_cache_dirs_match_cache_manager(self):
        # start.sh's CACHE_DIRS fallback (used for a manual `docker run` without
        # the autoscaler, i.e. no CACHE_MOUNT_DESTS env var) must list exactly
        # the same container-side paths cache_manager.py actually mounts.
        # Regression test for the drift that caused a real prod failure: the
        # fallback listed go/pkg/mod (cache_manager mounts go/pkg) and omitted
        # .nuget/packages entirely, so their ancestor dirs never got chowned and
        # GitVersion / `go install` both failed with permission-denied.
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "start.sh"))
        if not os.path.isfile(script_path):
            self.skipTest("start.sh not available in temp sandbox directory")

        with open(script_path) as f:
            content = f.read()

        match = re.search(r"CACHE_DIRS=\((.*?)\)", content, re.DOTALL)
        self.assertIsNotNone(match, "Could not find CACHE_DIRS fallback array in start.sh")
        assert match is not None
        fallback_dirs = set(match.group(1).split())

        expected = init_cache_dirs("/tmp/fake-host-cache", "arm64")
        expected_dirs = {v for v in expected.values() if v != "/opt/hostedtoolcache"}

        self.assertEqual(
            fallback_dirs,
            expected_dirs,
            "start.sh's CACHE_DIRS fallback has drifted from cache_manager.init_cache_dirs() mount destinations — update start.sh to match.",
        )


@unittest.skipUnless(shutil.which("lsof"), "lsof is needed to find the port holder")
class TestBridgeSupervisorPortConflict(unittest.TestCase):
    """#72: a foreign process on the bridge port is named, instead of a silent launchd crash-loop."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="runzero-supervisor-")
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        os.makedirs(os.path.join(self.repo, "scripts"))
        shutil.copy(os.path.join(REPO_ROOT, "scripts", "bridge_supervisor.sh"), os.path.join(self.repo, "scripts"))
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(self.listener.close)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        with open(os.path.join(self.repo, ".env"), "w", encoding="utf-8") as fh:
            fh.write(f"HOST_VM_BRIDGE_PORT={self.listener.getsockname()[1]}\n")

    def test_start_names_the_foreign_process_and_refuses(self):
        env = {**os.environ, "RUNZERO_BRIDGE_NO_LAUNCHD": "1"}
        res = subprocess.run(["bash", "scripts/bridge_supervisor.sh", "start"], cwd=self.repo, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn(f"already in use by PID {os.getpid()}", res.stdout)
        self.assertIn(f"kill {os.getpid()}", res.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".bridge.pid")))


if __name__ == "__main__":
    unittest.main()
