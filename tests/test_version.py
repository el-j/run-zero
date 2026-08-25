"""
Tests for dynamic Semantic Versioning resolver (src/version.py).
"""

import unittest
from unittest.mock import patch
import os
import subprocess

from version import get_version, BASE_VERSION


class TestVersion(unittest.TestCase):
    def test_version_from_env_var(self):
        with patch.dict(os.environ, {"RUNZERO_VERSION": "1.2.3"}):
            self.assertEqual(get_version(), "1.2.3")

    @patch("subprocess.check_output")
    def test_version_main_branch(self, mock_sub):
        mock_sub.side_effect = ["main\n", "10\n"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), "0.0.1")

    @patch("subprocess.check_output")
    def test_version_develop_branch(self, mock_sub):
        mock_sub.side_effect = ["develop\n", "15\n"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), "0.0.1-beta.1")

    @patch("subprocess.check_output")
    def test_version_feature_branch(self, mock_sub):
        mock_sub.side_effect = ["feat/my-feature\n", "22\n"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), "0.0.1-alpha.22")

    @patch("subprocess.check_output")
    def test_version_fix_branch(self, mock_sub):
        mock_sub.side_effect = ["fix/my-bug\n", "7\n"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), "0.0.1-alpha.7")

    @patch("subprocess.check_output")
    def test_version_other_branch(self, mock_sub):
        mock_sub.side_effect = ["staging\n", "5\n"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), "0.0.1-dev.5")

    @patch("subprocess.check_output")
    def test_version_fallback_on_exception(self, mock_sub):
        mock_sub.side_effect = subprocess.CalledProcessError(1, "git")
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_version(), BASE_VERSION)


if __name__ == "__main__":
    unittest.main()
