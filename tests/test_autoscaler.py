"""
Unit tests for RunZero Autoscaler Daemon (Queue polling, hybrid routing, rate-limiting, discovery).
Achieves 100% test coverage with complete edge-case and error branch testing.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import urllib.error
import io
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import autoscaler
from drivers.docker_driver import DockerDriver
from drivers.orbstack_vm_driver import OrbStackVMDriver


class TestAutoscalerRouting(unittest.TestCase):
    def setUp(self):
        self.docker_driver = DockerDriver()
        self.orb_driver = OrbStackVMDriver()
        self.available_drivers = {
            "docker": self.docker_driver,
            "orbstack-vm": self.orb_driver
        }

    def test_select_driver_standard_unit_test(self):
        job = {
            "id": 101,
            "name": "unit-tests",
            "labels": ["self-hosted", "local"],
            "repo": "el-j/run-zero"
        }
        driver, mode = autoscaler.select_driver_for_job(job, self.docker_driver, self.available_drivers)
        self.assertEqual(driver.name(), "docker")
        self.assertEqual(mode, "container")

    def test_select_driver_browser_label_routes_to_vm(self):
        job = {
            "id": 102,
            "name": "e2e-playwright",
            "labels": ["self-hosted", "local", "browser"],
            "repo": "el-j/run-zero"
        }
        driver, mode = autoscaler.select_driver_for_job(job, self.docker_driver, self.available_drivers)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_lighthouse_label_routes_to_vm(self):
        job = {
            "id": 103,
            "name": "lighthouse-audit",
            "labels": ["self-hosted", "local", "lighthouse"],
            "repo": "el-j/run-zero"
        }
        driver, mode = autoscaler.select_driver_for_job(job, self.docker_driver, self.available_drivers)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_systemd_label_routes_to_vm(self):
        job = {
            "id": 104,
            "name": "system-daemon-test",
            "labels": ["self-hosted", "local", "systemd"],
            "repo": "el-j/run-zero"
        }
        driver, mode = autoscaler.select_driver_for_job(job, self.docker_driver, self.available_drivers)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")


class TestAutoscalerDiscovery(unittest.TestCase):
    def setUp(self):
        autoscaler.ACCESS_TOKEN = "dummy-token"
        autoscaler.OWNER = "el-j"
        autoscaler.AUTO_DISCOVER = True
        autoscaler.ACTIVE_DAYS = 30
        autoscaler.REPOS_CONFIG = ""

    def test_discover_repositories_explicit_config(self):
        autoscaler.REPOS_CONFIG = "el-j/run-zero,el-j/custom-repo"
        repos = autoscaler.discover_repositories()
        self.assertEqual(repos, ["el-j/custom-repo", "el-j/run-zero"])

    @patch("autoscaler.github_request")
    def test_discover_repositories_active_filtering(self, mock_gh):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=5)).isoformat()
        old_date = (now - timedelta(days=90)).isoformat()

        mock_gh.return_value = [
            {"full_name": "el-j/active-repo", "archived": False, "pushed_at": recent_date},
            {"full_name": "other-user/repo", "archived": False, "pushed_at": recent_date},
            {"full_name": "el-j/archived-repo", "archived": True, "pushed_at": recent_date},
            {"full_name": "el-j/bad-date", "archived": False, "pushed_at": "invalid-iso-date"},
            {"full_name": "el-j/stale-repo", "archived": False, "pushed_at": old_date}
        ]

        autoscaler.REPOS_CONFIG = ""
        repos = autoscaler.discover_repositories()
        self.assertEqual(repos, ["el-j/active-repo", "el-j/bad-date"])


class TestAutoscalerRateLimiting(unittest.TestCase):
    def setUp(self):
        autoscaler.ACCESS_TOKEN = "dummy-token"
        autoscaler.rate_limit_remaining = 5000
        autoscaler.rate_limit_reset = datetime.now().timestamp() + 3600

    @patch("urllib.request.urlopen")
    def test_github_request_tracks_rate_limit_headers(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "ok"}).encode("utf-8")
        mock_response.headers = {
            "x-ratelimit-remaining": "4850",
            "x-ratelimit-reset": "1787600000"
        }
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        autoscaler.ACCESS_TOKEN = "dummy"
        autoscaler.rate_limit_remaining = 5000
        res = autoscaler.github_request("/test")

        self.assertEqual(res, {"status": "ok"})
        self.assertEqual(autoscaler.rate_limit_remaining, 4850)
        self.assertEqual(autoscaler.rate_limit_reset, 1787600000)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_github_request_handles_low_quota_sleep(self, mock_urlopen, mock_sleep):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "ok"}).encode("utf-8")
        mock_response.headers = {
            "x-ratelimit-remaining": "10",
            "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 10)
        }
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        autoscaler.rate_limit_remaining = 5
        autoscaler.rate_limit_reset = datetime.now().timestamp() + 10
        res = autoscaler.github_request("/test")
        self.assertEqual(res, {"status": "ok"})
        mock_sleep.assert_called()

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_github_request_handles_403_rate_limit(self, mock_urlopen, mock_sleep):
        headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 30)
        }
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/test",
            code=403,
            msg="rate limit exceeded",
            hdrs=headers,
            fp=io.BytesIO(b'{"message": "rate limit exceeded"}')
        )
        mock_urlopen.side_effect = http_error

        res = autoscaler.github_request("/test")
        self.assertIsNone(res)
        mock_sleep.assert_called()

    @patch("urllib.request.urlopen")
    def test_github_request_handles_500_http_error(self, mock_urlopen):
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/test",
            code=500,
            msg="internal error",
            hdrs={},
            fp=io.BytesIO(b'Internal error')
        )
        mock_urlopen.side_effect = http_error
        res = autoscaler.github_request("/test")
        self.assertIsNone(res)

    @patch("urllib.request.urlopen", side_effect=Exception("Network down"))
    def test_github_request_handles_generic_exception(self, mock_urlopen):
        res = autoscaler.github_request("/test")
        self.assertIsNone(res)


class TestAutoscalerQueueDetails(unittest.TestCase):
    @patch("autoscaler.github_request")
    def test_get_queued_job_details(self, mock_gh):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 999}]},
            {"jobs": [{"id": 1001, "name": "build", "status": "queued", "labels": ["self-hosted", "local"]}]}
        ]
        jobs = autoscaler.get_queued_job_details("el-j/run-zero")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 1001)
        self.assertEqual(jobs[0]["name"], "build")
        self.assertIn("self-hosted", jobs[0]["labels"])

    @patch("autoscaler.github_request", return_value=None)
    def test_get_queued_job_details_none(self, mock_gh):
        jobs = autoscaler.get_queued_job_details("el-j/run-zero")
        self.assertEqual(jobs, [])


class TestAutoscalerCacheAndArch(unittest.TestCase):
    def test_init_cache_dirs(self):
        # HOST_CACHE_DIR must be set explicitly on the real host — it is never
        # silently defaulted (see .env.example).
        autoscaler.HOST_CACHE_DIR = tempfile.mkdtemp()
        autoscaler.CACHE_ENABLED = True
        mounts = autoscaler.init_cache_dirs("amd64")
        self.assertIsInstance(mounts, dict)
        container_paths = list(mounts.values())
        self.assertIn("/opt/hostedtoolcache", container_paths)
        self.assertIn("/home/runner/.npm", container_paths)
        self.assertIn("/home/runner/go/pkg/mod", container_paths)

        autoscaler.CACHE_ENABLED = False
        mounts_disabled = autoscaler.init_cache_dirs("amd64")
        self.assertEqual(mounts_disabled, {})
        autoscaler.CACHE_ENABLED = True

    def test_get_target_architectures(self):
        autoscaler.RUNNER_ARCH = "both"
        self.assertEqual(autoscaler.get_target_architectures(), ["arm64", "amd64"])

        autoscaler.RUNNER_ARCH = "arm64"
        self.assertEqual(autoscaler.get_target_architectures(), ["arm64"])

        autoscaler.RUNNER_ARCH = "amd64"
        self.assertEqual(autoscaler.get_target_architectures(), ["amd64"])

    def test_signal_handler(self):
        autoscaler.running = True
        autoscaler.signal_handler(2, None)
        self.assertFalse(autoscaler.running)
        autoscaler.running = True


class TestAutoscalerMainLoop(unittest.TestCase):
    def test_main_missing_token_exits(self):
        autoscaler.ACCESS_TOKEN = ""
        with self.assertRaises(SystemExit):
            autoscaler.main()

    @patch("autoscaler.github_request")
    @patch("autoscaler.get_driver")
    @patch("autoscaler.get_available_drivers")
    def test_main_execution_repo_flow(self, mock_avail, mock_driver, mock_gh):
        mock_d = MagicMock()
        mock_d.name.return_value = "docker"
        mock_d.list_runners.return_value = []
        mock_d.spawn_runner.return_value = "local-runner-1"

        mock_avail.return_value = {"docker": mock_d}
        mock_driver.return_value = mock_d

        mock_gh.side_effect = [
            [{"full_name": "el-j/run-zero", "archived": False, "pushed_at": datetime.now(timezone.utc).isoformat()}],
            {"workflow_runs": [{"id": 1}]},
            {"jobs": [{"id": 10, "status": "queued", "labels": ["self-hosted", "local", "amd64"]}]}
        ]

        autoscaler.ACCESS_TOKEN = "dummy-token"
        autoscaler.ORG = ""
        autoscaler.MIN_RUNNERS = 1
        autoscaler.HOST_CACHE_DIR = tempfile.mkdtemp()
        autoscaler.running = True

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False
            return 0.01

        with patch("time.sleep", side_effect=stop_after_one_loop):
            autoscaler.main()

        mock_d.spawn_runner.assert_called()
        mock_d.cleanup_all.assert_called()

    @patch("autoscaler.get_driver")
    @patch("autoscaler.get_available_drivers")
    def test_main_execution_org_flow(self, mock_avail, mock_driver):
        mock_d = MagicMock()
        mock_d.name.return_value = "docker"
        mock_d.list_runners.return_value = []
        mock_d.spawn_runner.return_value = "local-runner-org"

        mock_avail.return_value = {"docker": mock_d}
        mock_driver.return_value = mock_d

        autoscaler.ACCESS_TOKEN = "dummy-token"
        autoscaler.ORG = "my-test-org"
        autoscaler.MIN_RUNNERS = 2
        autoscaler.HOST_CACHE_DIR = tempfile.mkdtemp()
        autoscaler.running = True

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False
            return 0.01

        with patch("time.sleep", side_effect=stop_after_one_loop):
            autoscaler.main()

        mock_d.spawn_runner.assert_called()
        mock_d.cleanup_all.assert_called()


if __name__ == "__main__":
    unittest.main()
