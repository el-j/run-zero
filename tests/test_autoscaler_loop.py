"""
Unit tests for autoscaler main execution loop and signal handling.
"""

import io
import shutil
import signal
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import autoscaler


class TestAutoscalerLoop(unittest.TestCase):
    def setUp(self):
        self.temp_cache = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_cache, ignore_errors=True)

    def test_get_target_architectures(self):
        with patch.object(autoscaler, "RUNNER_ARCH", "both"):
            self.assertEqual(autoscaler.get_target_architectures(), ["arm64", "amd64"])
        with patch.object(autoscaler, "RUNNER_ARCH", "amd64"):
            self.assertEqual(autoscaler.get_target_architectures(), ["amd64"])
        with patch.object(autoscaler, "RUNNER_ARCH", "arm64"):
            self.assertEqual(autoscaler.get_target_architectures(), ["arm64"])

    def test_resolve_job_arch_defaults_to_amd64_like_github_hosted(self):
        # No arch label at all -> must match what GitHub-hosted ubuntu-latest
        # would use (amd64), not whatever's native to this Mac.
        with patch.object(autoscaler, "RUNNER_ARCH", "both"):
            self.assertEqual(autoscaler.resolve_job_arch([]), "amd64")
            self.assertEqual(autoscaler.resolve_job_arch(["self-hosted", "vm"]), "amd64")

    def test_resolve_job_arch_explicit_arm_label_wins(self):
        with patch.object(autoscaler, "RUNNER_ARCH", "both"):
            self.assertEqual(autoscaler.resolve_job_arch(["self-hosted", "arm64"]), "arm64")
            self.assertEqual(autoscaler.resolve_job_arch(["aarch64"]), "arm64")
            self.assertEqual(autoscaler.resolve_job_arch(["arm"]), "arm64")

    def test_resolve_job_arch_amd64_label_still_amd64(self):
        with patch.object(autoscaler, "RUNNER_ARCH", "both"):
            self.assertEqual(autoscaler.resolve_job_arch(["amd64"]), "amd64")
            self.assertEqual(autoscaler.resolve_job_arch(["x64"]), "amd64")

    def test_resolve_job_arch_single_arch_override_ignores_labels(self):
        # Operator pinned the whole fleet to one arch -- that wins regardless
        # of what an individual job's labels say.
        with patch.object(autoscaler, "RUNNER_ARCH", "amd64"):
            self.assertEqual(autoscaler.resolve_job_arch(["arm64"]), "amd64")
        with patch.object(autoscaler, "RUNNER_ARCH", "arm64"):
            self.assertEqual(autoscaler.resolve_job_arch([]), "arm64")

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero", "el-j/custom-repo"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repository_mode(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # Queue has 1 job for el-j/run-zero
        mock_jobs.side_effect = [[{"id": 1, "name": "unit-test", "labels": ["self-hosted"]}], []]

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.return_value = "local-runner-arm64-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.spawn_runner.assert_called()
            mock_driver.cleanup_all.assert_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 2)
    @patch("autoscaler.MAX_RUNNERS", 4)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_organization_mode(self, mock_sleep):
        def stop_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.return_value = "local-runner-org-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 2)

    def test_log_print_writes_to_given_file(self):
        buf = io.StringIO()
        autoscaler.log_print("hello world", file=buf)
        self.assertIn("hello world", buf.getvalue())

    @patch("autoscaler.ACCESS_TOKEN", "")
    def test_main_exits_when_access_token_missing(self):
        with self.assertRaises(SystemExit) as cm:
            autoscaler.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.HOST_CACHE_DIR", "")
    def test_main_exits_when_cache_enabled_without_host_cache_dir(self):
        with self.assertRaises(SystemExit) as cm:
            autoscaler.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", False)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=[])
    @patch("autoscaler.time.sleep")
    def test_main_falls_back_to_default_version_on_import_error(self, mock_sleep, mock_discover):
        # version.py might not be importable in some deployment contexts
        # (e.g. no .git in a built container image and no fallback module);
        # main() must not crash -- it falls back to a hardcoded "0.1.0".
        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
            patch.dict(sys.modules, {"version": None}),
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

        from dashboard import dashboard_state

        self.assertEqual(dashboard_state.version, "0.1.0")

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", False)
    @patch("autoscaler.DASHBOARD_ENABLED", True)
    @patch("autoscaler.discover_repositories", return_value=[])
    @patch("autoscaler.time.sleep")
    def test_main_logs_warning_when_dashboard_fails_to_start(self, mock_sleep, mock_discover):
        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch("autoscaler.DashboardServer", side_effect=RuntimeError("port already in use")),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.cleanup_all.assert_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", False)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=[])
    @patch("autoscaler.time.sleep")
    @patch("autoscaler.signal.signal")
    def test_main_registers_signal_handler_that_stops_the_loop(self, mock_signal, mock_sleep, mock_discover):
        captured_handlers = {}

        def capture(sig, handler):
            captured_handlers[sig] = handler

        mock_signal.side_effect = capture

        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with patch("autoscaler.get_driver") as mock_get_driver, patch("autoscaler.get_available_drivers") as mock_avail:
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

        self.assertIn(signal.SIGINT, captured_handlers)
        self.assertIn(signal.SIGTERM, captured_handlers)

        # Directly invoke the captured handler to exercise its body (the
        # real OS signal delivery path can't be exercised in a unit test).
        autoscaler.running = True
        captured_handlers[signal.SIGINT](signal.SIGINT, None)
        self.assertFalse(autoscaler.running)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.MAX_RUNNERS", 2)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_stops_spawning_once_max_runners_reached(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # 3 queued jobs but MAX_RUNNERS=2 -- the third job's spawn attempt
        # must hit the "len(active_runners) >= MAX_RUNNERS" break rather
        # than spawning a runner past the concurrency cap.
        mock_jobs.return_value = [
            {"id": 1, "name": "unit-test-1", "labels": ["self-hosted"]},
            {"id": 2, "name": "unit-test-2", "labels": ["self-hosted"]},
            {"id": 3, "name": "unit-test-3", "labels": ["self-hosted"]},
        ]

        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.side_effect = ["local-runner-1", "local-runner-2", "local-runner-3"]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            # Only 2 spawns should have actually happened -- the loop must
            # break before attempting the third.
            self.assertEqual(mock_driver.spawn_runner.call_count, 2)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", False)
    @patch("autoscaler.DASHBOARD_ENABLED", True)
    @patch("autoscaler.discover_repositories", return_value=[])
    @patch("autoscaler.time.sleep")
    def test_main_starts_and_stops_dashboard_server_on_success(self, mock_sleep, mock_discover):
        # Covers the success path of DASHBOARD_ENABLED=True: the dashboard
        # actually starts (mocked, no real socket) and gets stopped again on
        # shutdown -- distinct from test_main_logs_warning_when_dashboard_fails_to_start,
        # which covers the constructor-raises branch instead.
        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        mock_dashboard_instance = MagicMock()
        with (
            patch("autoscaler.DashboardServer", return_value=mock_dashboard_instance) as mock_dashboard_cls,
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

        mock_dashboard_cls.assert_called_once()
        mock_dashboard_instance.start.assert_called_once_with(blocking=False)
        mock_dashboard_instance.stop.assert_called_once()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 3)
    @patch("autoscaler.MAX_RUNNERS", 5)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_org_mode_respects_min_runners_with_rotation(self, mock_sleep):
        # In ORG mode, when no runners exist, MIN_RUNNERS determines how many
        # to spawn. Architecture should rotate (first runner arm64, second amd64, etc.)
        def stop_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch.object(autoscaler, "RUNNER_ARCH", "both"),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.side_effect = ["runner-0", "runner-1", "runner-2"]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            # MIN_RUNNERS=3, so 3 runners should be spawned
            self.assertEqual(mock_driver.spawn_runner.call_count, 3)

            # Verify architecture rotation (both arch available -> arm64, amd64, arm64)
            calls = mock_driver.spawn_runner.call_args_list
            self.assertEqual(calls[0][1]["arch"], "arm64")
            self.assertEqual(calls[1][1]["arch"], "amd64")
            self.assertEqual(calls[2][1]["arch"], "arm64")

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 2)
    @patch("autoscaler.MAX_RUNNERS", 3)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_org_mode_stops_at_max_runners(self, mock_sleep):
        # When MIN_RUNNERS < active_count < MAX_RUNNERS, no additional spawns.
        # When active_count >= MAX_RUNNERS, still no spawns (MAX enforces hard cap).
        def stop_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            # Start with MAX_RUNNERS already running
            mock_driver.list_runners.return_value = [
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
            ]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            # No additional spawns because active_count >= MAX_RUNNERS
            mock_driver.spawn_runner.assert_not_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repo_mode_dispatches_to_correct_driver(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # select_driver_for_job may pick docker or VM driver based on labels;
        # this test verifies the spawned runner gets the correct backend assignment
        mock_jobs.return_value = [
            {"id": 1, "name": "vm-job", "labels": ["self-hosted", "windows"]},
        ]

        def stop_after_one_loop(*a, **kw):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_default_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
            patch("autoscaler.select_driver_for_job") as mock_select,
        ):
            mock_docker_driver = MagicMock()
            mock_docker_driver.name.return_value = "docker"
            mock_docker_driver.list_runners.return_value = []

            mock_vm_driver = MagicMock()
            mock_vm_driver.name.return_value = "orbstack"
            mock_vm_driver.spawn_runner.return_value = "vm-runner-1"

            mock_get_default_driver.return_value = mock_docker_driver
            mock_avail.return_value = {"docker": mock_docker_driver, "orbstack": mock_vm_driver}

            # Simulate select_driver_for_job choosing the VM driver
            mock_select.return_value = (mock_vm_driver, "vm")

            autoscaler.running = True
            autoscaler.main()

            # Verify the VM driver was used for spawn, not the default
            mock_vm_driver.spawn_runner.assert_called_once()
            mock_docker_driver.spawn_runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
