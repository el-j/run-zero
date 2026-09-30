"""
Unit tests for the self-healing reconciler (zombie runners and idle orphans).

`classify()` is pure and covered table-driven. The executors are driven through a fake
GitHub API that routes by endpoint path (query strings stripped), so tests assert on
*what* was requested, independent of call order or pagination details.
"""

import unittest
from typing import Any, ClassVar
from unittest.mock import MagicMock, patch

from drivers import RunnerDriver, RunnerInfo
from reconciler import (
    Action,
    Registration,
    RunnerRegistry,
    Timeouts,
    _get_in_progress_runner_names,
    _runner_name_matches,
    classify,
    normalize_repo_name,
    reconcile_idle_orphans,
    reconcile_zombie_runners,
    resolve_repo,
)

NOW = 1_000_000.0
FAIL = object()  # route value meaning "this request fails" (github_request -> None)


class FakeGitHub:
    """Routes github_request(endpoint, ..., method) by (method, path-without-query)."""

    def __init__(self, routes: dict[tuple[str, str], Any]):
        self.routes = routes
        self.calls: list[tuple[str, str]] = []

    def __call__(self, endpoint: str, access_token: str | None = None, method: str = "GET") -> Any:
        path = endpoint.split("?", 1)[0]
        self.calls.append((method, path))
        value = self.routes.get((method, path), FAIL)
        return None if value is FAIL else value

    def called(self, method: str, path: str) -> bool:
        return (method, path) in self.calls


def fake_github(routes: dict[tuple[str, str], Any]) -> tuple[FakeGitHub, Any, Any]:
    """Patch both github_request call sites (reconciler + github_api's paginator)."""
    fake = FakeGitHub(routes)
    return fake, patch("reconciler.github_request", fake), patch("github_api.github_request", fake)


def runner(name="local-runner-arm64-el-j-run-zero-abc123", age=700.0, target="el-j/run-zero", backend="docker", state="running", rid="container123"):
    return RunnerInfo(id=rid, name=name, status="Up", state=state, target_repo=target, target_arch="arm64", backend=backend, created_at=NOW - age)


def runners_route(repo: str, runners: list[dict]) -> dict:
    return {("GET", f"/repos/{repo}/actions/runners"): {"runners": runners}}


class TestHelpers(unittest.TestCase):
    def test_runner_name_matches(self):
        self.assertTrue(_runner_name_matches("a", "a"))
        self.assertTrue(_runner_name_matches("a", "a-legacy"))
        self.assertFalse(_runner_name_matches("a", "ab"))
        self.assertFalse(_runner_name_matches("", "some-runner"))
        self.assertFalse(_runner_name_matches("some-runner", ""))

    def test_resolve_repo(self):
        repos = ["el-j/run-zero", "el-j/Herbful"]
        self.assertEqual(resolve_repo("el-j/run-zero", repos), "el-j/run-zero")
        self.assertEqual(resolve_repo("el-j-herbful", repos), "el-j/Herbful")
        self.assertEqual(resolve_repo("el-j/nonexistent", repos), "")
        self.assertEqual(resolve_repo("", repos), "")
        self.assertEqual(normalize_repo_name("A/b"), "a-b")

    def test_registry_conclusiveness(self):
        reg = RunnerRegistry({"repos/a/b": [], "repos/c/d": None})
        self.assertTrue(reg.is_conclusive_for("repos/a/b"))
        self.assertFalse(reg.is_conclusive_for("repos/c/d"))
        self.assertFalse(reg.is_conclusive_for(None))  # unresolved target needs every scope
        self.assertTrue(RunnerRegistry({"repos/a/b": []}).is_conclusive_for(None))

    def test_registry_find_skips_unknown_scopes(self):
        reg = RunnerRegistry({"repos/a/b": None, "repos/c/d": [{"name": "x", "busy": True}]})
        found = reg.find("x")
        assert found is not None
        self.assertEqual(found.scope, "repos/c/d")
        self.assertTrue(found.busy)
        self.assertIsNone(reg.find("y"))


class TestClassify(unittest.TestCase):
    T = Timeouts(idle=600, unregistered=180, busy=7200)

    def test_table(self):
        idle = Registration("repos/a/b", {"busy": False})
        busy = Registration("repos/a/b", {"busy": True})
        cases = [
            # age, registration, conclusive, expected
            (180, None, True, Action.KEEP),  # strictly greater than grace period
            (181, None, True, Action.REAP_UNREGISTERED),
            (10_000, None, False, Action.KEEP),  # registry outage: never reap (#42)
            (600, idle, True, Action.KEEP),
            (601, idle, True, Action.REAP_IDLE),
            (601, idle, False, Action.REAP_IDLE),  # found registration is conclusive by itself
            (7200, busy, True, Action.KEEP),
            (7201, busy, True, Action.CHECK_STALE_BUSY),
        ]
        for age, registration, conclusive, expected in cases:
            with self.subTest(age=age, registration=registration, conclusive=conclusive):
                self.assertIs(classify(age, registration, conclusive, self.T), expected)


class TestReconcileIdleOrphans(unittest.TestCase):
    def run_reconcile(self, routes: dict, runners: list[RunnerInfo], repos=("el-j/run-zero",), **kw) -> tuple[FakeGitHub, MagicMock]:
        fake, p1, p2 = fake_github(routes)
        driver = MagicMock()
        drivers: dict[str, RunnerDriver] = {"docker": driver, "orbstack-vm": driver}
        with p1, p2, patch("sys.stderr"):
            reconcile_idle_orphans(list(repos), runners, drivers, access_token="token", now=NOW, **kw)
        return fake, driver

    def test_no_api_calls_when_nothing_old_enough(self):
        fake, driver = self.run_reconcile({}, [runner(age=5)])
        self.assertEqual(fake.calls, [])
        driver.destroy_runner.assert_not_called()

    def test_runner_without_created_at_is_never_a_candidate(self):
        r = runner()
        r.created_at = None
        fake, _driver = self.run_reconcile({}, [r])
        self.assertEqual(fake.calls, [])

    def test_unmanaged_or_stopped_runners_ignored(self):
        _fake, driver = self.run_reconcile(runners_route("el-j/run-zero", []), [runner(name="some-random-runner"), runner(state="exited")])
        driver.destroy_runner.assert_not_called()

    def test_idle_registered_runner_is_destroyed_and_unregistered(self):
        routes = {
            **runners_route("el-j/run-zero", [{"id": 55, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": False}]),
            ("DELETE", "/repos/el-j/run-zero/actions/runners/55"): True,
        }
        fake, driver = self.run_reconcile(routes, [runner(age=700)])
        driver.destroy_runner.assert_called_once_with("container123")
        self.assertTrue(fake.called("DELETE", "/repos/el-j/run-zero/actions/runners/55"))

    def test_idle_exactly_at_timeout_is_kept(self):
        routes = runners_route("el-j/run-zero", [{"id": 55, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": False}])
        _, driver = self.run_reconcile(routes, [runner(age=600)], idle_timeout_seconds=600)
        driver.destroy_runner.assert_not_called()

    def test_standby_count_spares_idle_registered_runners(self):
        # #47: up to MIN_RUNNERS idle runners are the warm pool, not orphans.
        names = [f"local-runner-arm64-el-j-run-zero-{i}" for i in range(3)]
        routes = {
            **runners_route("el-j/run-zero", [{"id": i, "name": n, "busy": False} for i, n in enumerate(names)]),
            **{("DELETE", f"/repos/el-j/run-zero/actions/runners/{i}"): True for i in range(3)},
        }
        runners = [runner(name=n, rid=n) for n in names]
        _, driver = self.run_reconcile(routes, runners, standby_count=2)
        driver.destroy_runner.assert_called_once_with(names[2])

    def test_standby_never_spares_unregistered_runners(self):
        _, driver = self.run_reconcile(runners_route("el-j/run-zero", []), [runner()], standby_count=5)
        driver.destroy_runner.assert_called_once_with("container123")

    def test_unregistered_runner_is_destroyed(self):
        _, driver = self.run_reconcile(runners_route("el-j/run-zero", []), [runner(age=700)])
        driver.destroy_runner.assert_called_once_with("container123")

    def test_finished_vm_with_legacy_hyphenated_target_is_destroyed(self):
        vm = runner(name="runzero-vm-amd64-el-j-herbful-8e8a72", age=250, target="el-j-herbful", backend="orbstack-vm", rid="vm1")
        _, driver = self.run_reconcile(runners_route("el-j/herbful", []), [vm], repos=("el-j/herbful",))
        driver.destroy_runner.assert_called_once_with("vm1")

    def test_outage_for_one_repo_protects_only_its_runners(self):
        # #42: a failed runner list used to read as "no runners registered", so every managed
        # runner -- including busy ones mid-job -- was destroyed as unregistered.
        routes = runners_route("el-j/healthy", [])  # el-j/down has no route -> request fails
        down = runner(name="local-runner-arm64-el-j-down-1", target="el-j/down", rid="down")
        healthy = runner(name="local-runner-arm64-el-j-healthy-1", target="el-j/healthy", rid="healthy")
        _, driver = self.run_reconcile(routes, [down, healthy], repos=("el-j/down", "el-j/healthy"))
        driver.destroy_runner.assert_called_once_with("healthy")

    def test_outage_protects_runners_with_unresolvable_target(self):
        _, driver = self.run_reconcile(runners_route("el-j/healthy", []), [runner(target="")], repos=("el-j/down", "el-j/healthy"))
        driver.destroy_runner.assert_not_called()

    def test_failure_on_a_later_page_counts_as_outage(self):
        full_page = [{"id": i, "name": f"other-{i}", "busy": False} for i in range(100)]
        fake = FakeGitHub({})

        def route(endpoint, access_token=None, method="GET"):
            fake.calls.append((method, endpoint))
            return {"runners": full_page} if endpoint.endswith("&page=1") else None

        driver = MagicMock()
        with patch("reconciler.github_request", route), patch("github_api.github_request", route), patch("sys.stderr"):
            reconcile_idle_orphans(["el-j/run-zero"], [runner()], {"docker": driver}, access_token="t", now=NOW)
        driver.destroy_runner.assert_not_called()

    def test_truncated_registry_counts_as_outage(self):
        full_page = {"runners": [{"id": i, "name": f"other-{i}", "busy": False} for i in range(100)]}

        def route(endpoint, access_token=None, method="GET"):
            return full_page

        driver = MagicMock()
        with patch("reconciler.github_request", route), patch("github_api.github_request", route), patch("sys.stdout"), patch("sys.stderr"):
            reconcile_idle_orphans(["el-j/run-zero"], [runner()], {"docker": driver}, access_token="t", now=NOW)
        driver.destroy_runner.assert_not_called()

    def test_registration_found_in_another_repo_is_honoured(self):
        routes = {
            **runners_route("el-j/run-zero", []),
            **runners_route("el-j/other", [{"id": 99, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": True}]),
        }
        _, driver = self.run_reconcile(routes, [runner(target="el-j/nonexistent")], repos=("el-j/run-zero", "el-j/other"))
        driver.destroy_runner.assert_not_called()

    def _busy_routes(self, repo="el-j/run-zero", name="local-runner-arm64-el-j-run-zero-abc123", active_names=(), delete_ok=True, runs_ok=True):
        routes: dict = runners_route(repo, [{"id": 55, "name": name, "busy": True}])
        if runs_ok:
            routes[("GET", f"/repos/{repo}/actions/runs")] = {"workflow_runs": [{"id": 999}] if active_names else []}
            routes[("GET", f"/repos/{repo}/actions/runs/999/jobs")] = {"jobs": [{"runner_name": n} for n in active_names]}
        if delete_ok:
            routes[("DELETE", f"/repos/{repo}/actions/runners/55")] = True
        return routes

    def test_busy_runner_within_timeout_is_untouched(self):
        fake, driver = self.run_reconcile(self._busy_routes(), [runner(age=3600)])
        driver.destroy_runner.assert_not_called()
        self.assertFalse(fake.called("GET", "/repos/el-j/run-zero/actions/runs"))

    def test_stale_busy_runner_without_active_job_is_unregistered_then_destroyed(self):
        fake, driver = self.run_reconcile(self._busy_routes(), [runner(age=8000)])
        self.assertTrue(fake.called("DELETE", "/repos/el-j/run-zero/actions/runners/55"))
        driver.destroy_runner.assert_called_once_with("container123")

    def test_stale_busy_runner_with_active_job_is_kept(self):
        fake, driver = self.run_reconcile(self._busy_routes(active_names=("local-runner-arm64-el-j-run-zero-abc123",)), [runner(age=8000)])
        driver.destroy_runner.assert_not_called()
        self.assertFalse(fake.called("DELETE", "/repos/el-j/run-zero/actions/runners/55"))

    def test_stale_busy_runner_kept_when_github_refuses_delete(self):
        _, driver = self.run_reconcile(self._busy_routes(delete_ok=False), [runner(age=8000)])
        driver.destroy_runner.assert_not_called()

    def test_stale_busy_runner_kept_when_run_lookup_fails(self):
        _, driver = self.run_reconcile(self._busy_routes(runs_ok=False), [runner(age=8000)])
        driver.destroy_runner.assert_not_called()

    def test_stale_busy_legacy_target_uses_the_scope_it_is_registered_in(self):
        name = "runzero-vm-amd64-el-j-herbful-stale"
        vm = runner(name=name, age=8000, target="el-j-herbful", backend="orbstack-vm", rid="vm123")
        fake, driver = self.run_reconcile(self._busy_routes(repo="el-j/herbful", name=name), [vm], repos=("el-j/herbful",))
        driver.destroy_runner.assert_called_once_with("vm123")
        self.assertTrue(fake.called("DELETE", "/repos/el-j/herbful/actions/runners/55"))

    def test_org_mode_uses_org_scope_and_searches_all_repos(self):
        name = "local-runner-arm64-acme-1"
        routes = {
            ("GET", "/orgs/acme/actions/runners"): {"runners": [{"id": 7, "name": name, "busy": True}]},
            ("GET", "/repos/acme/a/actions/runs"): {"workflow_runs": []},
            ("GET", "/repos/acme/b/actions/runs"): {"workflow_runs": []},
            ("DELETE", "/orgs/acme/actions/runners/7"): True,
        }
        fake, driver = self.run_reconcile(routes, [runner(name=name, age=8000, target="")], repos=("acme/a", "acme/b"), org="acme")
        self.assertTrue(fake.called("GET", "/repos/acme/b/actions/runs"))
        driver.destroy_runner.assert_called_once_with("container123")


class TestInProgressRunnerNames(unittest.TestCase):
    def names(self, routes: dict):
        _fake, p1, p2 = fake_github(routes)
        with p1, p2:
            return _get_in_progress_runner_names("el-j/run-zero", access_token="t")

    def test_collects_runner_names_and_skips_runs_without_id(self):
        routes = {
            ("GET", "/repos/el-j/run-zero/actions/runs"): {"workflow_runs": [{"status": "in_progress"}, {"id": 5}]},
            ("GET", "/repos/el-j/run-zero/actions/runs/5/jobs"): {"jobs": [{"runner_name": " r1 "}, {"runner_name": None}]},
        }
        self.assertEqual(self.names(routes), {"r1"})

    def test_none_when_jobs_lookup_fails(self):
        self.assertIsNone(self.names({("GET", "/repos/el-j/run-zero/actions/runs"): {"workflow_runs": [{"id": 55}]}}))

    def test_none_when_runs_lookup_fails(self):
        self.assertIsNone(self.names({}))


class TestReconcileZombieRunners(unittest.TestCase):
    def run_zombies(self, routes: dict, **kw) -> FakeGitHub:
        fake, p1, p2 = fake_github(routes)
        with p1, p2, patch("sys.stderr"):
            reconcile_zombie_runners(["el-j/run-zero"], access_token="token", **kw)
        return fake

    RUNNERS: ClassVar[list[dict[str, Any]]] = [
        {"id": 10, "name": "local-runner-arm64-1", "status": "offline", "busy": True},
        {"id": 20, "name": "local-runner-arm64-2", "status": "online", "busy": True},
        {"id": 30, "name": "external-self-hosted", "status": "offline", "busy": True},
        {"id": 40, "name": "local-runner-arm64-4", "status": "offline", "busy": False},
    ]

    def test_cancels_pinned_run_and_removes_only_managed_offline_busy_runner(self):
        routes = {
            **runners_route("el-j/run-zero", self.RUNNERS),
            ("GET", "/repos/el-j/run-zero/actions/runs"): {"workflow_runs": [{"id": 999, "run_number": 42}]},
            ("GET", "/repos/el-j/run-zero/actions/runs/999/jobs"): {"jobs": [{"runner_name": "local-runner-arm64-1"}]},
            ("POST", "/repos/el-j/run-zero/actions/runs/999/cancel"): True,
            ("DELETE", "/repos/el-j/run-zero/actions/runners/10"): True,
        }
        fake = self.run_zombies(routes)
        self.assertTrue(fake.called("POST", "/repos/el-j/run-zero/actions/runs/999/cancel"))
        deletes = [path for method, path in fake.calls if method == "DELETE"]
        self.assertEqual(deletes, ["/repos/el-j/run-zero/actions/runners/10"])

    def test_no_zombies_means_a_single_request(self):
        fake = self.run_zombies(runners_route("el-j/run-zero", self.RUNNERS[1:]))
        self.assertEqual(len(fake.calls), 1)

    def test_failed_or_malformed_runner_list_skips_repo(self):
        cases: tuple[dict[Any, Any], ...] = ({}, {("GET", "/repos/el-j/run-zero/actions/runners"): {}})
        for routes in cases:
            with self.subTest(routes=routes):
                self.assertEqual(len(self.run_zombies(routes).calls), 1)

    def test_delete_failure_does_not_raise(self):
        routes = {**runners_route("el-j/run-zero", self.RUNNERS[:1]), ("GET", "/repos/el-j/run-zero/actions/runs"): {"workflow_runs": []}}
        fake = self.run_zombies(routes)
        self.assertTrue(fake.called("DELETE", "/repos/el-j/run-zero/actions/runners/10"))

    def test_run_lookup_failure_still_removes_registration(self):
        fake = self.run_zombies({**runners_route("el-j/run-zero", self.RUNNERS[:1]), ("DELETE", "/repos/el-j/run-zero/actions/runners/10"): True})
        self.assertFalse(any(m == "POST" for m, _ in fake.calls))
        self.assertTrue(fake.called("DELETE", "/repos/el-j/run-zero/actions/runners/10"))

    def test_org_scope(self):
        routes = {
            ("GET", "/orgs/acme/actions/runners"): {"runners": self.RUNNERS[:1]},
            ("GET", "/repos/el-j/run-zero/actions/runs"): {"workflow_runs": []},
            ("DELETE", "/orgs/acme/actions/runners/10"): True,
        }
        fake = self.run_zombies(routes, org="acme")
        self.assertTrue(fake.called("DELETE", "/orgs/acme/actions/runners/10"))


if __name__ == "__main__":
    unittest.main()
