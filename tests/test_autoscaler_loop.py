"""
Unit tests for the autoscaler: pure helpers, one `Scaler` poll cycle at a time, and `main()`.

`Scaler.run_once()` is driven directly with a Config and mock drivers -- no module globals
to patch and no loop to break out of. `main()` tests cover only process wiring: startup
validation, dashboard lifecycle, signal handling and shutdown cleanup.
"""

import dataclasses
import io
import shutil
import signal
import tempfile
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

import autoscaler
from autoscaler import Scaler
from config import Config
from drivers import RunnerInfo


def mock_driver(name: str = "docker", runners: list[RunnerInfo] | None = None, spawn: Any = "runner-1") -> MagicMock:
    driver = MagicMock()
    driver.name.return_value = name
    driver.list_runners.return_value = runners or []
    if callable(spawn):
        driver.spawn_runner.side_effect = spawn
    else:
        driver.spawn_runner.return_value = spawn
    return driver


def unique_ids(**kwargs: Any) -> str:
    """spawn_runner side effect returning a fresh runner id per call."""
    unique_ids.counter += 1  # type: ignore[attr-defined]
    return f"runner-{unique_ids.counter}"  # type: ignore[attr-defined]


unique_ids.counter = 0  # type: ignore[attr-defined]


def running(name: str, target: str, backend: str = "docker") -> RunnerInfo:
    return RunnerInfo(id=name, name=name, status="running", state="running", target_repo=target, target_arch="arm64", backend=backend)


class ScalerTestCase(unittest.TestCase):
    """Base: temp cache dir, offline GitHub/discovery stubs, and a Config factory."""

    def setUp(self):
        self.temp_cache = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_cache, ignore_errors=True)
        cache_patch = patch.object(autoscaler.dashboard_state, "cache_dir", self.temp_cache)
        cache_patch.start()
        self.addCleanup(cache_patch.stop)
        self.stubs: dict[str, MagicMock] = {}
        for name, value in (
            ("refresh_rate_limit", False),
            ("refresh_actions_billing", None),
            ("reconcile_zombie_runners", None),
            ("reconcile_idle_orphans", None),
            ("discover_repositories", ["el-j/run-zero"]),
            ("get_queued_job_details", []),
        ):
            p = patch(f"autoscaler.{name}", return_value=value)
            self.stubs[name] = p.start()
            self.addCleanup(p.stop)
        autoscaler.github_api.shutdown_event.clear()
        self.addCleanup(autoscaler.github_api.shutdown_event.clear)

    def config(self, **overrides: Any) -> Config:
        base = Config(access_token="fake-token", host_cache_dir=self.temp_cache, dashboard_enabled=False)
        return dataclasses.replace(base, **overrides)

    def scaler(self, config: Config | None = None, drivers: dict[str, Any] | None = None, default: Any = None, clock: Any = None) -> Scaler:
        default = default or mock_driver()
        drivers = drivers if drivers is not None else {default.name(): default}
        return Scaler(config or self.config(), drivers, default, clock=clock or (lambda: 1_000_000.0), pause=lambda _s: None)

    def queue(self, *jobs: dict[str, Any]) -> None:
        self.stubs["get_queued_job_details"].return_value = list(jobs)


def job(i: int = 1, *labels: str, **extra: Any) -> dict[str, Any]:
    return {"id": i, "name": f"job-{i}", "labels": ["self-hosted", *labels], **extra}


class TestPureHelpers(unittest.TestCase):
    def test_get_target_architectures(self):
        self.assertEqual(autoscaler.get_target_architectures("both"), ["arm64", "amd64"])
        self.assertEqual(autoscaler.get_target_architectures("amd64"), ["amd64"])
        self.assertEqual(autoscaler.get_target_architectures("arm64"), ["arm64"])

    def test_resolve_job_arch_defaults_to_amd64_like_github_hosted(self):
        # No arch label at all -> must match GitHub-hosted ubuntu-latest (amd64), not the Mac's native arch.
        self.assertEqual(autoscaler.resolve_job_arch([], "both"), "amd64")
        self.assertEqual(autoscaler.resolve_job_arch(["self-hosted", "vm"], "both"), "amd64")

    def test_resolve_job_arch_explicit_arm_label_wins(self):
        for label in ("arm64", "aarch64", "arm"):
            self.assertEqual(autoscaler.resolve_job_arch(["self-hosted", label], "both"), "arm64")

    def test_resolve_job_arch_amd64_label_still_amd64(self):
        self.assertEqual(autoscaler.resolve_job_arch(["amd64"], "both"), "amd64")
        self.assertEqual(autoscaler.resolve_job_arch(["x64"], "both"), "amd64")

    def test_resolve_job_arch_single_arch_override_ignores_labels(self):
        # Operator pinned the whole fleet to one arch -- that wins regardless of job labels.
        self.assertEqual(autoscaler.resolve_job_arch(["arm64"], "amd64"), "amd64")
        self.assertEqual(autoscaler.resolve_job_arch([], "arm64"), "arm64")

    def test_build_cache_scope_is_stable_across_different_runs_of_the_same_job(self):
        # Two runs of the SAME recurring job (new run_id/id every time) must share a scope,
        # or the go-build cache it drives is thrown away on every run.
        job_1 = {"id": 1, "run_id": 100, "workflow_path": ".github/workflows/ci.yml", "name": "test (3.11)"}
        job_2 = {**job_1, "id": 2, "run_id": 200}
        self.assertEqual(autoscaler.build_cache_scope("el-j/run-zero", job_1), autoscaler.build_cache_scope("el-j/run-zero", job_2))

    def test_build_cache_scope_differs_across_different_jobs(self):
        a = autoscaler.build_cache_scope("o/r", {"workflow_path": "ci.yml", "name": "lint"})
        b = autoscaler.build_cache_scope("o/r", {"workflow_path": "ci.yml", "name": "test"})
        c = autoscaler.build_cache_scope("o/r", {"workflow_path": "release.yml", "name": "lint"})
        self.assertEqual(len({a, b, c}), 3)

    def test_build_cache_scope_tolerates_missing_fields(self):
        self.assertEqual(autoscaler.build_cache_scope("el-j/run-zero", {}), "el-j/run-zero")

    def test_ensure_driver_runtime_assets_falls_back_to_positional_arg_on_typeerror(self):
        calls: list[tuple] = []

        def ensure(*args, **kwargs):
            calls.append((args, kwargs))
            if kwargs:
                raise TypeError("no arch kwarg")
            return True

        driver = MagicMock()
        driver.ensure_runtime_assets = ensure
        self.assertTrue(autoscaler.ensure_driver_runtime_assets(driver, "amd64"))
        self.assertEqual(len(calls), 2)

    def test_ensure_driver_runtime_assets_defaults_true_when_driver_has_no_such_method(self):
        class DriverWithoutRuntimeAssets:
            pass

        self.assertTrue(autoscaler.ensure_driver_runtime_assets(DriverWithoutRuntimeAssets(), "amd64"))

    def test_log_print_writes_to_given_file(self):
        buf = io.StringIO()
        autoscaler.log_print("hello world", file=buf)
        self.assertIn("hello world", buf.getvalue())


class TestRepoMode(ScalerTestCase):
    def test_spawns_one_runner_per_queued_job(self):
        self.queue(job())
        driver = mock_driver()
        self.scaler(default=driver).run_once()
        driver.spawn_runner.assert_called_once()
        self.assertEqual(driver.spawn_runner.call_args.kwargs["repo"], "el-j/run-zero")

    def test_passes_the_jobs_runs_on_labels_to_the_driver(self):
        # #46: without them a runs-on: [self-hosted, gpu] job was never dispatched to the runner.
        self.queue(job(1, "gpu", "linux"))
        driver = mock_driver()
        self.scaler(default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_args.kwargs["labels"], "self-hosted,gpu,linux")

    def test_skips_spawn_when_runtime_assets_not_ready(self):
        self.queue(job())
        driver = mock_driver()
        driver.ensure_runtime_assets.return_value = False
        self.scaler(default=driver).run_once()
        driver.spawn_runner.assert_not_called()

    def test_stops_spawning_once_max_runners_reached(self):
        self.queue(job(1), job(2), job(3))
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.config(max_runners=2), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)

    def test_needed_accounts_for_existing_active_runners_for_that_repo(self):
        # 3 queued, 1 already running for this repo, 1 for another repo -> exactly 2 spawns.
        self.queue(job(1), job(2), job(3))
        driver = mock_driver(runners=[running("a", "el-j/run-zero"), running("b", "el-j/other")], spawn=unique_ids)
        self.scaler(config=self.config(max_runners=10), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)

    def test_stops_exactly_when_needed_reaches_zero(self):
        self.queue(job(1), job(2), job(3))
        driver = mock_driver(runners=[running("a", "el-j/run-zero")], spawn=unique_ids)
        self.scaler(config=self.config(max_runners=10), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)

    def test_dispatches_to_the_driver_the_router_selects(self):
        self.queue(job(1, "vm"))
        docker, vm = mock_driver("docker"), mock_driver("orbstack-vm", spawn="vm-1")
        with patch("autoscaler.select_driver_for_job", return_value=(vm, "label:vm")):
            self.scaler(drivers={"docker": docker, "orbstack-vm": vm}, default=docker).run_once()
        vm.spawn_runner.assert_called_once()
        docker.spawn_runner.assert_not_called()

    def test_falls_back_to_default_driver_when_vm_driver_spawn_fails(self):
        self.queue(job(1, "services"))
        docker, vm = mock_driver("docker", spawn="docker-1"), mock_driver("orbstack-vm", spawn=None)
        self.scaler(drivers={"docker": docker, "orbstack-vm": vm}, default=docker).run_once()
        vm.spawn_runner.assert_called_once()
        docker.spawn_runner.assert_called_once()

    def test_no_fallback_to_a_different_instance_of_the_same_backend(self):
        # #43: the fallback compared object identity, so a duplicate instance of the default
        # backend counted as "different" and the same backend was tried twice.
        self.queue(job(1, "services"))
        default, duplicate = mock_driver("docker", spawn=None), mock_driver("docker", spawn=None)
        with patch("autoscaler.select_driver_for_job", return_value=(duplicate, "services")):
            self.scaler(drivers={"docker": default}, default=default).run_once()
        duplicate.spawn_runner.assert_called_once()
        default.spawn_runner.assert_not_called()

    def test_no_fallback_when_default_driver_itself_failed(self):
        self.queue(job())
        driver = mock_driver(spawn=None)
        self.scaler(default=driver).run_once()
        driver.spawn_runner.assert_called_once()

    def test_fallback_skipped_when_default_driver_assets_not_ready(self):
        self.queue(job(1, "services"))
        docker, vm = mock_driver("docker"), mock_driver("orbstack-vm", spawn=None)
        docker.ensure_runtime_assets.return_value = False
        self.scaler(drivers={"docker": docker, "orbstack-vm": vm}, default=docker).run_once()
        vm.spawn_runner.assert_called_once()
        docker.spawn_runner.assert_not_called()

    def test_fallback_that_also_fails_spawns_nothing(self):
        self.queue(job(1, "services"))
        docker, vm = mock_driver("docker", spawn=None), mock_driver("orbstack-vm", spawn=None)
        with patch.object(autoscaler.dashboard_state, "update_fleet") as update:
            self.scaler(drivers={"docker": docker, "orbstack-vm": vm}, default=docker).run_once()
        self.assertEqual(update.call_args.kwargs["runners"], [])

    def test_reconcile_passes_configured_busy_timeout(self):
        self.scaler(config=self.config(busy_timeout_seconds=1234)).run_once()
        self.assertEqual(self.stubs["reconcile_idle_orphans"].call_args.kwargs["busy_timeout_seconds"], 1234)
        self.stubs["reconcile_zombie_runners"].assert_called_once()


class TestJobMetadataAndPublishing(ScalerTestCase):
    def test_job_meta_attaches_to_runner_visible_on_a_later_poll(self):
        # Cycle 1 spawns and records job links; cycle 2's list_runners() reports that runner,
        # and the dashboard entry must carry the links recorded on cycle 1.
        self.stubs["get_queued_job_details"].side_effect = [[job(7, run_id=70, job_url="https://x/job", run_url="https://x/run")], []]
        driver = mock_driver(spawn="local-runner-arm64-1")
        scaler = self.scaler(default=driver)
        scaler.run_once()
        driver.list_runners.return_value = [running("local-runner-arm64-1", "el-j/run-zero")]
        scaler.run_once()
        snapshot = autoscaler.dashboard_state.get_snapshot()
        entry = next((r for r in snapshot["runners"] if r.get("name") == "local-runner-arm64-1"), None)
        assert entry is not None
        self.assertEqual(entry.get("job_url"), "https://x/job")

    def test_job_meta_dropped_once_runner_is_gone(self):
        self.queue(job(7, job_url="https://x/job"))
        scaler = self.scaler(default=mock_driver(spawn="r-7"))
        scaler.run_once()
        self.assertIn("r-7", scaler.runner_job_meta)
        self.queue()
        scaler.run_once()
        self.assertEqual(scaler.runner_job_meta, {})

    def test_queued_jobs_are_published_with_their_repo(self):
        self.queue(job())
        with patch.object(autoscaler.dashboard_state, "update_fleet") as update:
            self.scaler(default=mock_driver(spawn=None)).run_once()
        self.assertEqual(update.call_args.kwargs["queued_jobs"][0]["repo"], "el-j/run-zero")


class TestOrgMode(ScalerTestCase):
    def org_config(self, **kw: Any) -> Config:
        return self.config(org="my-test-org", **kw)

    def test_spawns_min_runners_at_org_scope(self):
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.org_config(min_runners=2), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)
        for call in driver.spawn_runner.call_args_list:
            self.assertEqual(call.kwargs["org"], "my-test-org")
            self.assertNotIn("repo", call.kwargs)

    def test_discovers_org_repos_and_reconciles_at_org_scope(self):
        # #48: ORG mode used to skip discovery, queued jobs and all reconciliation.
        self.stubs["discover_repositories"].return_value = ["my-test-org/api"]
        self.scaler(config=self.org_config()).run_once()
        self.assertEqual(self.stubs["discover_repositories"].call_args.kwargs["owner"], "my-test-org")
        self.assertEqual(self.stubs["reconcile_zombie_runners"].call_args.kwargs["org"], "my-test-org")
        self.assertEqual(self.stubs["reconcile_idle_orphans"].call_args.kwargs["org"], "my-test-org")

    def test_scales_on_queued_org_jobs_with_org_registration(self):
        self.stubs["discover_repositories"].return_value = ["my-test-org/api", "my-test-org/web"]
        self.stubs["get_queued_job_details"].side_effect = [[job(1)], [job(2), job(3)]]
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.org_config(max_runners=10), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 3)
        self.assertTrue(all(c.kwargs["org"] == "my-test-org" for c in driver.spawn_runner.call_args_list))

    def test_org_runners_cover_jobs_from_any_repo(self):
        # Two org runners already exist (any repo's job can go to them) -> 1 of 3 jobs uncovered.
        self.stubs["discover_repositories"].return_value = ["my-test-org/api", "my-test-org/web"]
        self.stubs["get_queued_job_details"].side_effect = [[job(1)], [job(2), job(3)]]
        driver = mock_driver(runners=[running("a", "my-test-org"), running("b", "")], spawn=unique_ids)
        self.scaler(config=self.org_config(max_runners=10), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 1)

    def test_rotates_architectures(self):
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.org_config(min_runners=3), default=driver).run_once()
        self.assertEqual([c.kwargs["arch"] for c in driver.spawn_runner.call_args_list], ["arm64", "amd64", "arm64"])

    def test_skips_spawn_when_runtime_assets_not_ready(self):
        driver = mock_driver()
        driver.ensure_runtime_assets.return_value = False
        self.scaler(config=self.org_config(min_runners=2), default=driver).run_once()
        driver.spawn_runner.assert_not_called()

    def test_no_spawn_when_at_or_above_min_runners(self):
        driver = mock_driver(runners=[running("a", "my-test-org"), running("b", "my-test-org")])
        self.scaler(config=self.org_config(min_runners=2, max_runners=4), default=driver).run_once()
        driver.spawn_runner.assert_not_called()

    def test_no_spawn_when_at_max_runners(self):
        driver = mock_driver(runners=[running("a", "my-test-org"), running("b", "my-test-org")])
        cfg = dataclasses.replace(self.org_config(), min_runners=3, max_runners=2)
        self.scaler(config=cfg, default=driver).run_once()
        driver.spawn_runner.assert_not_called()

    def test_needed_formula_subtracts_active_count(self):
        driver = mock_driver(runners=[running("a", "my-test-org")], spawn=unique_ids)
        self.scaler(config=self.org_config(min_runners=2, max_runners=4), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 1)

    def test_max_runners_caps_even_below_min_runners(self):
        # Config forbids MIN > MAX, so build the (would-be misconfigured) Config directly.
        cfg = dataclasses.replace(self.org_config(), min_runners=5, max_runners=2)
        driver = mock_driver(runners=[running("a", "my-test-org")], spawn=unique_ids)
        self.scaler(config=cfg, default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 1)

    def test_failed_spawn_is_not_counted(self):
        driver = mock_driver(spawn=None)
        self.scaler(config=self.org_config(min_runners=2), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)


class TestRoutingStatistics(ScalerTestCase):
    """#49: counted once per job, after a successful spawn, VM-ness from the driver type."""

    def setUp(self):
        super().setUp()
        p = patch.object(autoscaler.dashboard_state, "record_routing_decision")
        self.record = p.start()
        self.addCleanup(p.stop)

    def test_not_recorded_when_spawn_fails(self):
        self.queue(job())
        self.scaler(default=mock_driver(spawn=None)).run_once()
        self.record.assert_not_called()

    def test_recorded_once_per_job_across_polls(self):
        self.queue(job(42))
        driver = mock_driver(spawn=unique_ids)
        driver.is_vm = False
        scaler = self.scaler(config=self.config(max_runners=10), default=driver)
        scaler.run_once()
        driver.list_runners.return_value = []  # runner vanished; job still queued -> respawn
        scaler.run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)
        self.record.assert_called_once_with(False, "container")

    def test_vm_route_records_driver_is_vm_and_reason(self):
        self.queue(job(1, "browser"))
        docker, vm = mock_driver("docker"), mock_driver("wsl2", spawn="wsl-1")
        vm.is_vm = True
        self.scaler(drivers={"docker": docker, "wsl2": vm}, default=docker).run_once()
        self.record.assert_called_once_with(True, "label:browser")

    def test_fallback_counts_as_container_job(self):
        self.queue(job(1, "services"))
        docker, vm = mock_driver("docker", spawn="d-1"), mock_driver("orbstack-vm", spawn=None)
        docker.is_vm = False
        self.scaler(drivers={"docker": docker, "orbstack-vm": vm}, default=docker).run_once()
        self.record.assert_called_once_with(False, "container")

    def test_memory_of_recorded_jobs_is_bounded(self):
        driver = mock_driver(spawn=unique_ids)
        scaler = self.scaler(default=driver)
        with patch.object(autoscaler, "RECORDED_JOBS_LIMIT", 2):
            for i in range(4):
                scaler._record_routing({"id": i}, driver, "container")
        self.assertEqual(list(scaler._recorded_jobs), [2, 3])
        scaler._record_routing({}, driver, "container")  # no id: counted, not remembered
        self.assertEqual(self.record.call_count, 5)


class TestStandbyInRepoMode(ScalerTestCase):
    """#47: MIN_RUNNERS used to be honoured only in ORG mode."""

    def test_keeps_min_runners_warm_round_robin_across_repos(self):
        self.stubs["discover_repositories"].return_value = ["o/a", "o/b"]
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.config(min_runners=3), default=driver).run_once()
        self.assertEqual([c.kwargs["repo"] for c in driver.spawn_runner.call_args_list], ["o/a", "o/b", "o/a"])

    def test_round_robin_continues_across_cycles(self):
        self.stubs["discover_repositories"].return_value = ["o/a", "o/b"]
        driver = mock_driver(spawn=unique_ids)
        scaler = self.scaler(config=self.config(min_runners=1), default=driver)
        scaler.run_once()
        scaler.run_once()  # list_runners still reports none -> tops up again
        self.assertEqual([c.kwargs["repo"] for c in driver.spawn_runner.call_args_list], ["o/a", "o/b"])

    def test_jobs_get_capacity_before_standby(self):
        self.queue(job(1))
        driver = mock_driver(spawn=unique_ids)
        self.scaler(config=self.config(min_runners=2, max_runners=2), default=driver).run_once()
        self.assertEqual(driver.spawn_runner.call_count, 2)
        self.assertIn("labels", driver.spawn_runner.call_args_list[0].kwargs)  # the job's runner first
        self.assertNotIn("labels", driver.spawn_runner.call_args_list[1].kwargs)

    def test_no_standby_without_tracked_repos(self):
        self.stubs["discover_repositories"].return_value = []
        driver = mock_driver()
        self.scaler(config=self.config(min_runners=2), default=driver).run_once()
        driver.spawn_runner.assert_not_called()

    def test_reconciler_spares_the_standby_pool(self):
        self.scaler(config=self.config(min_runners=2)).run_once()
        self.assertEqual(self.stubs["reconcile_idle_orphans"].call_args.kwargs["standby_count"], 2)


class TestQuotaAndDiscovery(ScalerTestCase):
    def test_billing_owner_derived_from_first_tracked_repo_on_later_poll(self):
        # The owner can only be derived once repos are tracked, i.e. on a later billing refresh.
        times = iter([1_000_000.0, 1_000_400.0])
        scaler = self.scaler(config=self.config(owner=""), clock=lambda: next(times))
        scaler.run_once()
        scaler.run_once()
        billing = self.stubs["refresh_actions_billing"]
        self.assertEqual(billing.call_count, 2)
        self.assertEqual(billing.call_args_list[0].kwargs["owner"], "")
        self.assertEqual(billing.call_args_list[-1].kwargs["owner"], "el-j")

    def test_refresh_intervals_are_respected(self):
        times = iter([1_000_000.0, 1_000_005.0])
        scaler = self.scaler(clock=lambda: next(times))
        scaler.run_once()
        scaler.run_once()
        self.assertEqual(self.stubs["refresh_rate_limit"].call_count, 1)
        self.assertEqual(self.stubs["discover_repositories"].call_count, 1)

    def test_empty_discovery_keeps_previous_repos(self):
        times = iter([1_000_000.0, 1_010_000.0])
        scaler = self.scaler(clock=lambda: next(times))
        scaler.run_once()
        self.stubs["discover_repositories"].return_value = []
        scaler.run_once()
        self.assertEqual(self.stubs["discover_repositories"].call_count, 2)
        self.assertEqual(scaler.tracked_repos, ["el-j/run-zero"])

    def test_no_repos_means_no_reconciliation(self):
        self.stubs["discover_repositories"].return_value = []
        self.scaler().run_once()
        self.stubs["reconcile_zombie_runners"].assert_not_called()
        self.stubs["reconcile_idle_orphans"].assert_not_called()

    def _quota_lines(self, remaining: Any, total: Any) -> list[str]:
        with (
            patch.object(autoscaler.github_api, "rate_limit_remaining", remaining),
            patch.object(autoscaler.github_api, "rate_limit_total", total),
            patch.object(autoscaler.github_api, "rate_limit_resource", "core"),
            patch("autoscaler.log_print") as log,
        ):
            self.scaler().run_once()
        return [c.args[0] for c in log.call_args_list if "Quota remaining" in c.args[0]]

    def test_prints_quota_when_rate_limit_known(self):
        self.assertEqual(self._quota_lines(4999, 5000), ["[Autoscaler] GitHub API Quota remaining: 4999/5000 (core)"])

    def test_prints_quota_unknown_when_only_one_value_is_known(self):
        self.assertEqual(self._quota_lines(4999, None), ["[Autoscaler] GitHub API Quota remaining: unknown/unknown"])
        self.assertEqual(self._quota_lines(None, 5000), ["[Autoscaler] GitHub API Quota remaining: unknown/unknown"])


class TestCollectAndShutdown(ScalerTestCase):
    def test_prunes_and_stops_base_images(self):
        driver = mock_driver()
        self.scaler(default=driver).collect()
        driver.prune_exited.assert_called_once()
        driver.ensure_base_images_stopped.assert_called_once()

    def test_driver_without_base_images_is_fine(self):
        driver = mock_driver()
        del driver.ensure_base_images_stopped
        self.assertEqual(self.scaler(default=driver).collect(), [])

    def test_shutdown_cleans_every_driver(self):
        a, b = mock_driver("docker"), mock_driver("orbstack-vm")
        self.scaler(drivers={"docker": a, "orbstack-vm": b}, default=a).shutdown()
        a.cleanup_all.assert_called_once()
        b.cleanup_all.assert_called_once()


class TestMain(ScalerTestCase):
    """Process wiring only: one cycle, then shutdown via the shared event."""

    def run_main(self, config: Config | None, driver: MagicMock | None = None, on_signal: Any = None) -> MagicMock:
        driver = driver or mock_driver()
        with (
            patch("autoscaler.get_available_drivers", return_value={driver.name(): driver}),
            patch.object(Scaler, "run_once", autospec=True, side_effect=lambda _s: autoscaler.github_api.shutdown_event.set()),
            patch("autoscaler.signal.signal", side_effect=on_signal),
        ):
            autoscaler.main(config)
        return driver

    def test_default_driver_is_taken_from_the_single_registry(self):
        # #43: main() used to build the default driver separately from the registry, so the
        # process held two instances of the same backend with independent build locks.
        docker, vm = mock_driver("docker"), mock_driver("orbstack-vm")
        registry = {"docker": docker, "orbstack-vm": vm}
        built: list[Scaler] = []

        def record_and_stop(scaler: Scaler) -> None:
            built.append(scaler)
            autoscaler.github_api.shutdown_event.set()

        with (
            patch("autoscaler.get_available_drivers", return_value=registry),
            patch.object(Scaler, "run_once", autospec=True, side_effect=record_and_stop),
            patch("autoscaler.signal.signal"),
        ):
            autoscaler.main(self.config(runner_backend="orbstack-vm"))
        self.assertIs(built[0].default_driver, registry["orbstack-vm"])
        self.assertIs(built[0].drivers, registry)

    def test_dashboard_gets_the_scalers_driver_registry(self):
        with patch("autoscaler.DashboardServer") as server_cls:
            driver = self.run_main(self.config(dashboard_enabled=True))
        self.assertEqual(server_cls.call_args.kwargs["drivers"], {"docker": driver})

    def test_runs_until_shutdown_then_cleans_up(self):
        self.run_main(self.config()).cleanup_all.assert_called_once()

    def test_loads_config_from_environment_when_none_given(self):
        with patch("autoscaler.load_config", return_value=self.config()) as load:
            self.run_main(None)
        load.assert_called_once()

    def test_exits_when_access_token_missing(self):
        with self.assertRaises(SystemExit) as cm, patch("sys.stderr"):
            autoscaler.main(self.config(access_token=None))
        self.assertEqual(cm.exception.code, 1)

    def test_exits_when_cache_enabled_without_host_cache_dir(self):
        with self.assertRaises(SystemExit) as cm, patch("sys.stderr"):
            autoscaler.main(self.config(cache_enabled=True, host_cache_dir=""))
        self.assertEqual(cm.exception.code, 1)

    def test_exits_on_invalid_environment(self):
        with patch.dict("os.environ", {"MAX_RUNNERS": "four"}), patch("autoscaler.log_print") as log, self.assertRaises(SystemExit) as cm:
            autoscaler.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("MAX_RUNNERS='four' is not an integer", log.call_args.args[0])

    def test_starts_and_stops_dashboard_server_on_success(self):
        with patch("autoscaler.DashboardServer") as server_cls:
            self.run_main(self.config(dashboard_enabled=True))
        server_cls.assert_called_once()
        server_cls.return_value.start.assert_called_once_with(blocking=False)
        server_cls.return_value.stop.assert_called_once()

    def test_logs_warning_when_dashboard_fails_to_start(self):
        with patch("autoscaler.DashboardServer", side_effect=OSError("port in use")), patch("autoscaler.log_print") as log:
            driver = self.run_main(self.config(dashboard_enabled=True))
        self.assertTrue(any("Could not start Dashboard server" in str(c.args[0]) for c in log.call_args_list))
        driver.cleanup_all.assert_called_once()

    def test_registers_signal_handlers_that_request_shutdown(self):
        captured: dict[int, Any] = {}
        self.run_main(self.config(), on_signal=lambda sig, handler: captured.__setitem__(sig, handler))
        self.assertEqual(set(captured), {signal.SIGINT, signal.SIGTERM})
        autoscaler.github_api.shutdown_event.clear()
        captured[signal.SIGTERM](signal.SIGTERM, None)
        # #44: the handler wakes the poll wait and any in-progress rate-limit throttle.
        self.assertTrue(autoscaler.github_api.shutdown_event.is_set())


if __name__ == "__main__":
    unittest.main()
