"""
Unit tests for guest-side runner bootstrap utilities.
"""

import unittest
from unittest.mock import patch

from drivers.runner_bootstrap import (
    POWEROFF,
    host_arch,
    instance_name,
    normalize_arch,
    register_and_run_snippet,
    runner_download_snippet,
    runner_tarball_arch,
    windows_to_wsl_path,
)


class TestRunnerBootstrap(unittest.TestCase):
    def test_normalize_arch(self):
        self.assertEqual(normalize_arch("amd64"), "amd64")
        self.assertEqual(normalize_arch("x64"), "amd64")
        self.assertEqual(normalize_arch("x86_64"), "amd64")
        self.assertEqual(normalize_arch("arm64"), "arm64")
        self.assertEqual(normalize_arch("aarch64"), "arm64")

    def test_host_arch(self):
        with patch("platform.machine", return_value="arm64"):
            self.assertEqual(host_arch(), "arm64")
        with patch("platform.machine", return_value="aarch64"):
            self.assertEqual(host_arch(), "arm64")
        with patch("platform.machine", return_value="x86_64"):
            self.assertEqual(host_arch(), "amd64")
        with patch("platform.machine", return_value="AMD64"):
            self.assertEqual(host_arch(), "amd64")

    def test_runner_tarball_arch(self):
        self.assertEqual(runner_tarball_arch("amd64"), "x64")
        self.assertEqual(runner_tarball_arch("x64"), "x64")
        self.assertEqual(runner_tarball_arch("x86_64"), "x64")
        self.assertEqual(runner_tarball_arch("arm64"), "arm64")

    def test_instance_name(self):
        name = instance_name("runzero-mp-", "arm64", "el-j/run-zero")
        self.assertTrue(name.startswith("runzero-mp-arm64-el-j-run-zero-"))
        self.assertTrue(len(name.split("-")[-1]) == 6)

        # Empty target slug
        name_no_slug = instance_name("runzero-wsl-", "amd64", "")
        self.assertTrue(name_no_slug.startswith("runzero-wsl-amd64-"))

    def test_windows_to_wsl_path(self):
        self.assertEqual(windows_to_wsl_path(r"C:\Users\foo\bar"), "/mnt/c/Users/foo/bar")
        self.assertEqual(windows_to_wsl_path("d:/projects/test"), "/mnt/d/projects/test")
        self.assertEqual(windows_to_wsl_path("/mnt/c/test"), "/mnt/c/test")
        self.assertEqual(windows_to_wsl_path("/host/cache"), "/host/cache")
        self.assertEqual(windows_to_wsl_path("relative/path"), "/mnt/c/relative/path")

    def test_runner_download_snippet(self):
        snippet = runner_download_snippet("arm64", home="/home/ubuntu")
        self.assertIn("RUNNER_ARCH=arm64", snippet)
        self.assertIn("/home/ubuntu/actions-runner", snippet)
        self.assertIn("installdependencies.sh", snippet)

        snippet_x64 = runner_download_snippet("amd64", home="/home/runner")
        self.assertIn("RUNNER_ARCH=x64", snippet_x64)
        self.assertIn("/home/runner/actions-runner", snippet_x64)

    def test_register_and_run_snippet(self):
        snippet = register_and_run_snippet(
            runner_url="https://github.com/el-j/run-zero",
            registration_token="token-123",
            runner_name="runner-1",
            labels="self-hosted,local",
            home="/home/runner",
            finish=POWEROFF,
        )
        self.assertIn("./config.sh --url https://github.com/el-j/run-zero --token token-123", snippet)
        self.assertIn("--name runner-1", snippet)
        self.assertIn("--labels self-hosted,local", snippet)
        self.assertIn("./run.sh || true", snippet)
        self.assertIn("poweroff", snippet)


if __name__ == "__main__":
    unittest.main()
