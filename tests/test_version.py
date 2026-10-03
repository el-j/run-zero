"""
Tests for dynamic Semantic Versioning resolver (src/version.py).
"""

import os
import subprocess
import unittest
from typing import ClassVar
from unittest.mock import patch

from version import BASE_VERSION, build_info, get_git_sha, get_version, version_drift


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


class TestBuildInfo(unittest.TestCase):
    def test_git_sha_from_env_is_truncated(self):
        with patch.dict(os.environ, {"RUNZERO_GIT_SHA": "0123456789abcdef"}):
            self.assertEqual(get_git_sha(), "0123456789ab")

    @patch("subprocess.check_output", return_value="abc123\n")
    def test_git_sha_from_git(self, _out):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_git_sha(), "abc123")

    @patch("subprocess.check_output", side_effect=FileNotFoundError)
    def test_git_sha_without_git(self, _out):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_git_sha(), "")

    def test_build_info_keys(self):
        self.assertEqual(set(build_info()), {"version", "git_sha"})


class TestVersionDrift(unittest.TestCase):
    LOCAL: ClassVar[dict[str, str]] = {"version": "0.0.1", "git_sha": "abc123def456"}

    def test_missing_remote_version_is_stale(self):
        self.assertIn("does not report its version", version_drift(self.LOCAL, {"status": "ok"}) or "")

    def test_matching_or_prefix_sha(self):
        self.assertIsNone(version_drift(self.LOCAL, {"version": "0.0.1-beta.1", "git_sha": "abc123def456"}))
        self.assertIsNone(version_drift(self.LOCAL, {"version": "0.0.1-beta.1", "git_sha": "abc123d"}))

    def test_different_sha(self):
        drift = version_drift(self.LOCAL, {"version": "0.0.1-beta.1", "git_sha": "fff000"}, remote_name="Host VM Bridge")
        assert drift is not None
        self.assertIn("Host VM Bridge runs 0.0.1-beta.1 (fff000)", drift)

    def test_unknown_sha_on_either_side_is_not_drift(self):
        self.assertIsNone(version_drift({"version": "0.0.1", "git_sha": ""}, {"version": "0.0.2", "git_sha": "fff000"}))


if __name__ == "__main__":
    unittest.main()
