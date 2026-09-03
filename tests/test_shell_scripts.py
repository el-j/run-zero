"""
Tests for shell scripts syntax and entrypoint validation.
"""

import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from cache_manager import init_cache_dirs


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
        fallback_dirs = set(match.group(1).split())

        expected = init_cache_dirs("/tmp/fake-host-cache", "arm64")
        expected_dirs = {v for v in expected.values() if v != "/opt/hostedtoolcache"}

        self.assertEqual(
            fallback_dirs,
            expected_dirs,
            "start.sh's CACHE_DIRS fallback has drifted from cache_manager.init_cache_dirs() "
            "mount destinations — update start.sh to match.",
        )


if __name__ == "__main__":
    unittest.main()
