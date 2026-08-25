"""
Tests for shell scripts syntax and entrypoint validation.
"""

import unittest
import subprocess
import os


class TestShellScripts(unittest.TestCase):
    def test_start_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "start.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("docker/start.sh")

        if not os.path.isfile(script_path):
            self.skipTest("start.sh not available in temp sandbox directory")

        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Syntax error in start.sh: {res.stderr}")

    def test_setup_env_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "setup_env.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/setup_env.sh")

        if not os.path.isfile(script_path):
            self.skipTest("setup_env.sh not available in temp sandbox directory")

        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Syntax error in setup_env.sh: {res.stderr}")

    def test_setup_env_sh_non_interactive(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "setup_env.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/setup_env.sh")

        if not os.path.isfile(script_path):
            self.skipTest("setup_env.sh not available in temp sandbox directory")

        env = os.environ.copy()
        env["NON_INTERACTIVE"] = "true"
        res = subprocess.run(["bash", script_path], capture_output=True, text=True, env=env)
        self.assertEqual(res.returncode, 0, f"Error running setup_env.sh: {res.stderr}")

    def test_pre_commit_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "pre-commit.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("scripts/pre-commit.sh")
        if not os.path.isfile(script_path):
            self.skipTest("pre-commit.sh not found")
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Syntax error in pre-commit.sh: {res.stderr}")

    def test_provision_toolchain_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "provision-toolchain.sh"))
        if not os.path.isfile(script_path):
            script_path = os.path.abspath("docker/provision-toolchain.sh")
        if not os.path.isfile(script_path):
            self.skipTest("provision-toolchain.sh not found")
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Syntax error in provision-toolchain.sh: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
