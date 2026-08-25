"""
Tests for shell scripts syntax and entrypoint validation.
"""

import unittest
import subprocess
import os


class TestShellScripts(unittest.TestCase):
    def test_start_sh_syntax(self):
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "start.sh"))
        self.assertTrue(os.path.isfile(script_path))
        res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Syntax error in start.sh: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
