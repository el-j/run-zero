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
from drivers import RunnerInfo


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

    def test_build_cache_scope_is_stable_across_different_runs_of_the_same_job(self):
        # The whole point of this scope key: two separate runs of the SAME recurring job
        # (different run_id/job id every time, as real GitHub runs always are) must produce
        # the SAME scope, or the go-build cache directory it drives is thrown away and
        # rebuilt from empty on every single run.
        job_run_1 = {"id": 201, "run_id": 1001, "name": "test", "workflow_path": ".github/workflows/ci.yml"}
        job_run_2 = {"id": 555, "run_id": 9999, "name": "test", "workflow_path": ".github/workflows/ci.yml"}
        scope_1 = autoscaler.build_cache_scope("el-j/run-zero", job_run_1)
        scope_2 = autoscaler.build_cache_scope("el-j/run-zero", job_run_2)
        self.assertEqual(scope_1, scope_2)

    def test_build_cache_scope_differs_across_different_jobs(self):
        job_a = {"name": "test", "workflow_path": ".github/workflows/ci.yml"}
        job_b = {"name": "build", "workflow_path": ".github/workflows/ci.yml"}
        job_c = {"name": "test", "workflow_path": ".github/workflows/release.yml"}
        scope_a = autoscaler.build_cache_scope("el-j/run-zero", job_a)
        scope_b = autoscaler.build_cache_scope("el-j/run-zero", job_b)
        scope_c = autoscaler.build_cache_scope("el-j/run-zero", job_c)
        self.assertNotEqual(scope_a, scope_b)
        self.assertNotEqual(scope_a, scope_c)
        self.assertNotEqual(scope_b, scope_c)

    def test_build_cache_scope_tolerates_missing_fields(self):
        self.assertEqual(autoscaler.build_cache_scope("el-j/run-zero", {}), "el-j/run-zero")

    def test_ensure_driver_runtime_assets_falls_back_to_positional_arg_on_typeerror(self):
        # Some driver stand-ins (e.g. certain bridge/mocked drivers) may expose
        # ensure_runtime_assets() without accepting the `arch=` keyword -- must still work.
        driver = MagicMock()

        def _positional_only(arch):
            return arch == "amd64"

        driver.ensure_runtime_assets.side_effect = TypeError("no kwarg")
        # Replace with a callable that raises TypeError only for the kwarg call form,
        # then succeeds positionally -- simulate via a small wrapper.
        calls = []

        def _ensure(*args, **kwargs):
            calls.append((args, kwargs))
            if kwargs:
                raise TypeError("unexpected keyword argument 'arch'")
            return _positional_only(*args)

        driver.ensure_runtime_assets = _ensure
        self.assertTrue(autoscaler.ensure_driver_runtime_assets(driver, "amd64"))
        self.assertEqual(len(calls), 2)  # first the kwarg attempt, then the positional fallback

    def test_ensure_driver_runtime_assets_defaults_true_when_driver_has_no_such_method(self):
        class DriverWithoutRuntimeAssets:
            pass

        self.assertTrue(autoscaler.ensure_driver_runtime_assets(DriverWithoutRuntimeAssets(), "amd64"))

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

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 1)
    @patch("autoscaler.MAX_RUNNERS", 4)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_organization_mode_skips_spawn_when_runtime_assets_not_ready(self, mock_sleep):
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
            mock_driver.ensure_runtime_assets.return_value = False  # golden image still building
            mock_driver.spawn_runner.return_value = "local-runner-org-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.spawn_runner.assert_not_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repository_mode_skips_spawn_when_runtime_assets_not_ready(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
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
            mock_driver.ensure_runtime_assets.return_value = False  # golden image still building
            mock_driver.spawn_runner.return_value = "local-runner-arm64-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.spawn_runner.assert_not_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_falls_back_to_default_driver_when_vm_driver_spawn_fails(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # A "services"-labeled job routes to the VM driver (router.VM_TRIGGER_LABELS).
        # When that driver's spawn_runner() fails, main() must retry with the default
        # (docker) driver rather than just dropping the job.
        mock_jobs.side_effect = [[{"id": 1, "name": "integration-test", "labels": ["self-hosted", "services"]}], []]

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            docker_driver = MagicMock()
            docker_driver.name.return_value = "docker"
            docker_driver.list_runners.return_value = []
            docker_driver.spawn_runner.return_value = "local-runner-arm64-fallback"

            vm_driver = MagicMock()
            vm_driver.name.return_value = "orbstack-vm"
            vm_driver.list_runners.return_value = []
            vm_driver.spawn_runner.return_value = None  # VM spawn fails

            mock_get_driver.return_value = docker_driver
            mock_avail.return_value = {"docker": docker_driver, "orbstack-vm": vm_driver}

            autoscaler.running = True
            autoscaler.main()

            vm_driver.spawn_runner.assert_called_once()
            docker_driver.spawn_runner.assert_called_once()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details", return_value=[])
    @patch("autoscaler.refresh_actions_billing")
    @patch("autoscaler.refresh_rate_limit")
    @patch("autoscaler.time.time")
    @patch("autoscaler.time.sleep")
    def test_main_loop_derives_billing_owner_from_first_tracked_repo_on_later_poll(
        self, mock_sleep, mock_time, mock_rate_limit, mock_billing, mock_jobs, mock_reconcile, mock_discover
    ):
        # billing_owner is only derived from tracked_repos on a poll where the
        # ACTIONS_BILLING_REFRESH_INTERVAL gate (floor: 30 real seconds) actually
        # fires again -- which by definition is never the very first poll, since
        # discovery (which populates tracked_repos) runs later in that same
        # iteration. Two ticks, 35 simulated seconds apart, with OWNER/ORG both
        # unset, exercises the real "derive from tracked_repos[0]" fallback path.
        # A strictly-increasing clock that jumps forward a lot on every single call, so
        # every interval gate (rate limit/billing/discovery) fires on every poll no
        # matter how many *other*, unrelated time.time() calls happen in between (e.g.
        # dashboard_state.update_fleet()'s own internal one) -- exact call-count
        # bookkeeping across the whole call graph would be far too brittle to hand-track.
        clock = {"t": 1_000_000.0}

        def _tick_clock():
            clock["t"] += 100.0
            return clock["t"]

        mock_time.side_effect = _tick_clock
        mock_rate_limit.return_value = True

        tick_count = {"n": 0}

        def _stop_after_second_poll_wait(*args, **kwargs):
            # time.sleep() is also called for the unrelated per-repo 0.1s API throttle
            # inside the queued-jobs loop -- only the real end-of-poll wait (sleep(1),
            # from `for _ in range(POLL_INTERVAL): time.sleep(1)`) should count as a tick.
            if args and args[0] == 1:
                tick_count["n"] += 1
                if tick_count["n"] >= 2:
                    autoscaler.running = False

        mock_sleep.side_effect = _stop_after_second_poll_wait

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch.object(autoscaler, "POLL_INTERVAL", 1),
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

        self.assertGreaterEqual(mock_billing.call_count, 2)
        self.assertEqual(mock_billing.call_args_list[-1].kwargs["owner"], "el-j")

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_prints_quota_when_rate_limit_known(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        mock_jobs.return_value = []

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        def _fake_refresh_rate_limit(access_token=None):
            autoscaler.github_api.rate_limit_remaining = 4999
            autoscaler.github_api.rate_limit_total = 5000
            autoscaler.github_api.rate_limit_resource = "core"
            return True

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
            patch("autoscaler.refresh_rate_limit", side_effect=_fake_refresh_rate_limit),
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            with patch("autoscaler.log_print") as mock_log:
                autoscaler.main()

        quota_calls = [c for c in mock_log.call_args_list if c.args and "Quota remaining: 4999/5000" in c.args[0]]
        self.assertEqual(len(quota_calls), 1)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_attaches_job_meta_to_runner_visible_on_a_later_poll(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # Iteration 1 spawns a runner and records its job metadata (job_url/run_url) in
        # runner_job_meta, keyed by the spawned runner's name -- that dict lives outside
        # the poll loop. Iteration 2's list_runners() now reports that same runner as
        # active; the dashboard payload construction must attach its remembered metadata.
        mock_jobs.side_effect = [
            [{"id": 1, "name": "unit-test", "labels": ["self-hosted"], "run_id": 55, "job_url": "https://x/job", "run_url": "https://x/run"}],
            [],
        ]

        tick_count = {"n": 0}

        def _stop_after_second_tick(*args, **kwargs):
            # Only the real end-of-poll wait (sleep(1)) marks a tick boundary -- the
            # per-repo 0.1s API throttle inside the queued-jobs loop also calls
            # time.sleep() and must not be counted as one.
            if args and args[0] == 1:
                tick_count["n"] += 1
                if tick_count["n"] >= 2:
                    autoscaler.running = False

        mock_sleep.side_effect = _stop_after_second_tick

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch.object(autoscaler, "POLL_INTERVAL", 1),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.spawn_runner.return_value = "local-runner-arm64-1"
            running_runner = RunnerInfo(
                id="local-runner-arm64-1",
                name="local-runner-arm64-1",
                status="running",
                state="running",
                target_repo="el-j/run-zero",
                target_arch="arm64",
                backend="docker",
            )
            # list_runners() is called twice per driver per poll (once for prune_exited(),
            # once to build all_runners) -- two ticks means four calls total.
            mock_driver.list_runners.side_effect = [[], [], [running_runner], [running_runner]]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

        snapshot = autoscaler.dashboard_state.get_snapshot()
        runner_entry = next((r for r in snapshot["runners"] if r.get("name") == "local-runner-arm64-1"), None)
        self.assertIsNotNone(runner_entry)
        self.assertEqual(runner_entry.get("job_url"), "https://x/job")

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

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 2)
    @patch("autoscaler.MAX_RUNNERS", 5)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_org_mode_does_not_spawn_when_already_above_min_runners(self, mock_sleep):
        # Documents the intended behavior of the `active_count < MIN_RUNNERS and
        # active_count < MAX_RUNNERS` gate: MAX_RUNNERS is a hard cap, not a spawn
        # *target* -- once active_count is at/above MIN_RUNNERS, no more scaling should
        # be attempted no matter how far below MAX_RUNNERS it still is. (Note: mutating
        # this gate's `and` to `or` is a verified-equivalent mutant, not a real gap --
        # whenever the two conditions disagree, active_count >= MIN_RUNNERS, which makes
        # `needed = min(MIN_RUNNERS - active_count, ...)` <= 0 regardless, so the
        # `for i in range(needed)` loop is empty either way. See docker_driver.py's
        # equivalent-mutant note in the mutation-triage report for the same pattern.)
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
            mock_driver.list_runners.return_value = [
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
            ]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.spawn_runner.assert_not_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 3)
    @patch("autoscaler.MAX_RUNNERS", 10)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_org_mode_needed_formula_subtracts_active_count(self, mock_sleep):
        # Mutation-prone: `needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)`
        # had its first term's sign flippable to `MIN_RUNNERS + active_count` with zero
        # detection, because every other test starts from active_count == 0 (where a sign
        # flip on a zero term is invisible). With 2 already active and MIN_RUNNERS=3, the
        # correct formula needs exactly 1 more; the mutant would try to spawn 5.
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
            mock_driver.list_runners.return_value = [
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
            ]
            mock_driver.spawn_runner.return_value = "runner-new"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 1)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 8)
    @patch("autoscaler.MAX_RUNNERS", 3)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.time.sleep")
    def test_main_loop_org_mode_max_runners_caps_even_below_misconfigured_min_runners(self, mock_sleep):
        # Mutation-prone: the second `min()` term's sign flip (`MAX_RUNNERS + active_count`
        # instead of `- active_count`) is only observable when BOTH MAX_RUNNERS < MIN_RUNNERS
        # (a real operator misconfiguration) AND active_count > 0 (a `- 0`/`+ 0` sign flip is
        # invisible). With MIN=8, MAX=3, and 2 already active, the correct `needed` is
        # min(8-2, 3-2) = 1; the `+`-flipped mutant computes min(6, 5) = 5 instead.
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
            mock_driver.list_runners.return_value = [
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
                MagicMock(state="running", target_repo="my-test-org", backend="docker"),
            ]
            mock_driver.spawn_runner.side_effect = [f"runner-{i}" for i in range(10)]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 1)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.MAX_RUNNERS", 10)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repo_mode_needed_accounts_for_existing_active_runners_for_that_repo(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # Mutation-prone: `active_for_repo = sum(1 for r in active_runners if
        # r.target_repo == repo)` had its `==` flippable to `!=` and its `1` flippable
        # to `2` with zero detection -- every existing test starts with zero pre-existing
        # runners for the target repo, so `active_for_repo` was always 0 regardless of
        # which mutant ran. With 1 already-active runner and 3 queued jobs, the correct
        # `needed = len(jobs) - active_for_repo` is 2; a `!=`-flipped mutant would instead
        # compute active_for_repo=0 (needed=3, one extra spawn), and a weight-flipped
        # (`sum(2 for ...)`) mutant would compute active_for_repo=2 (needed=1, one fewer).
        mock_jobs.return_value = [
            {"id": 1, "name": "job-1", "labels": ["self-hosted"]},
            {"id": 2, "name": "job-2", "labels": ["self-hosted"]},
            {"id": 3, "name": "job-3", "labels": ["self-hosted"]},
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
            mock_driver.list_runners.return_value = [
                RunnerInfo(
                    id="existing-1",
                    name="existing-1",
                    status="running",
                    state="running",
                    target_repo="el-j/run-zero",
                    target_arch="arm64",
                    backend="docker",
                ),
            ]
            mock_driver.spawn_runner.side_effect = ["new-runner-1", "new-runner-2", "new-runner-3"]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 2)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.MAX_RUNNERS", 10)
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repo_mode_stops_exactly_when_needed_reaches_zero(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # Mutation-prone: `if len(active_runners) >= MAX_RUNNERS or needed <= 0: break`
        # mutated to `needed < 0` would let the loop spawn one job PAST the point where
        # `needed` naturally reaches exactly zero. 3 queued jobs, 1 already-active for
        # the repo -> needed starts at 2 -> exactly 2 spawns should happen, not 3.
        mock_jobs.return_value = [
            {"id": 1, "name": "job-1", "labels": ["self-hosted"]},
            {"id": 2, "name": "job-2", "labels": ["self-hosted"]},
            {"id": 3, "name": "job-3", "labels": ["self-hosted"]},
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
            mock_driver.list_runners.return_value = [
                RunnerInfo(
                    id="existing-1",
                    name="existing-1",
                    status="running",
                    state="running",
                    target_repo="el-j/run-zero",
                    target_arch="arm64",
                    backend="docker",
                ),
            ]
            mock_driver.spawn_runner.side_effect = ["new-runner-1", "new-runner-2", "new-runner-3"]

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 2)

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.DASHBOARD_ENABLED", False)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_prints_quota_unknown_when_only_one_value_is_known(self, mock_sleep, mock_jobs, mock_reconcile, mock_discover):
        # Mutation-prone: `if quota_remaining is None or quota_total is None:` mutated
        # to `and` would only fall back to "unknown/unknown" when BOTH values are None
        # simultaneously -- a partial API failure/race leaving just one of the two set
        # would instead try to format a real number against a None partner.
        mock_jobs.return_value = []

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        def _fake_refresh_rate_limit(access_token=None):
            autoscaler.github_api.rate_limit_remaining = 4999
            autoscaler.github_api.rate_limit_total = None  # partial data
            autoscaler.github_api.rate_limit_resource = "core"
            return True

        with (
            patch.object(autoscaler, "HOST_CACHE_DIR", self.temp_cache),
            patch("autoscaler.get_driver") as mock_get_driver,
            patch("autoscaler.get_available_drivers") as mock_avail,
            patch("autoscaler.refresh_rate_limit", side_effect=_fake_refresh_rate_limit),
        ):
            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            with patch("autoscaler.log_print") as mock_log:
                autoscaler.main()

        unknown_calls = [c for c in mock_log.call_args_list if c.args and "unknown/unknown" in c.args[0]]
        self.assertEqual(len(unknown_calls), 1)


if __name__ == "__main__":
    unittest.main()
