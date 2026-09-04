"""
Unit tests for self-healing zombie runner reconciler.
"""

import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from reconciler import reconcile_idle_orphans, reconcile_zombie_runners


class TestReconciler(unittest.TestCase):
    @patch("reconciler.github_request")
    def test_reconcile_zombie_runners(self, mock_gh):
        mock_gh.side_effect = [
            # 1. /repos/el-j/run-zero/actions/runners
            {
                "runners": [
                    {"id": 10, "name": "local-runner-arm64-1", "status": "offline", "busy": True},
                    {"id": 20, "name": "local-runner-arm64-2", "status": "online", "busy": True},
                    {"id": 30, "name": "external-self-hosted", "status": "offline", "busy": True},
                ]
            },
            # 2. /repos/el-j/run-zero/actions/runs?status=in_progress&per_page=20
            {"workflow_runs": [{"id": 999, "run_number": 42}]},
            # 3. /repos/el-j/run-zero/actions/runs/999/jobs
            {"jobs": [{"runner_name": "local-runner-arm64-1", "name": "build"}]},
            # 4. Cancel run 999
            True,
            # 5. Delete runner 10
            True,
        ]

        reconcile_zombie_runners(["el-j/run-zero"], access_token="token")
        self.assertEqual(mock_gh.call_count, 5)

    def _runner(self, name="local-runner-arm64-el-j-run-zero-abc123", age_seconds=700, state="running"):
        return RunnerInfo(
            id="container123",
            name=name,
            status="Up",
            state=state,
            target_repo="el-j/run-zero",
            target_arch="arm64",
            backend="docker",
            created_at=1_000_000.0 - age_seconds,
        )

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_skips_when_nothing_old_enough(self, mock_gh):
        # Regression guard for the real bug this fixes: a queued ubuntu-latest
        # job still spawned a local container that then sat idle forever with
        # nothing ever reaping it. A runner younger than the timeout must never
        # trigger any API calls at all -- this also has to stay near-zero-cost
        # on every 10s poll loop tick in the common case.
        driver = MagicMock()
        reconcile_idle_orphans(["el-j/run-zero"], [self._runner(age_seconds=5)], {"docker": driver}, access_token="token", now=1_000_000.0)
        mock_gh.assert_not_called()
        driver.destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_destroys_never_dispatched_runner(self, mock_gh):
        mock_gh.side_effect = [
            {"runners": [{"id": 55, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": False}]},
            True,  # DELETE runner registration
        ]
        driver = MagicMock()
        reconcile_idle_orphans(["el-j/run-zero"], [self._runner(age_seconds=700)], {"docker": driver}, access_token="token", now=1_000_000.0)
        driver.destroy_runner.assert_called_once_with("container123")
        self.assertEqual(mock_gh.call_count, 2)

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_never_touches_busy_runner(self, mock_gh):
        mock_gh.return_value = {"runners": [{"id": 55, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": True}]}
        driver = MagicMock()
        reconcile_idle_orphans(
            ["el-j/run-zero"],
            [self._runner(age_seconds=3600)],  # an hour old, but actively busy
            {"docker": driver},
            access_token="token",
            now=1_000_000.0,
        )
        driver.destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_destroys_even_if_never_registered(self, mock_gh):
        # The container came up but the runner process never made it into
        # GitHub's runner list at all -- still an orphan, not a reason to skip.
        mock_gh.return_value = {"runners": []}
        driver = MagicMock()
        reconcile_idle_orphans(["el-j/run-zero"], [self._runner(age_seconds=700)], {"docker": driver}, access_token="token", now=1_000_000.0)
        driver.destroy_runner.assert_called_once_with("container123")

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_destroys_finished_vm_runner(self, mock_gh):
        # Ephemeral VM finished running action in el-j/herbful and was unregistered from GitHub,
        # but the VM remained running. Reconciler detects it's not in GitHub and reaps it.
        mock_gh.return_value = {"runners": []}
        driver = MagicMock()
        vm_runner = RunnerInfo(
            id="runzero-vm-amd64-el-j-herbful-8e8a72",
            name="runzero-vm-amd64-el-j-herbful-8e8a72",
            status="running",
            state="running",
            target_repo="el-j-herbful",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=1_000_000.0 - 250,  # 250s old (> 180s unregistered threshold)
        )
        reconcile_idle_orphans(["el-j/herbful"], [vm_runner], {"orbstack-vm": driver}, access_token="token", now=1_000_000.0)
        driver.destroy_runner.assert_called_once_with("runzero-vm-amd64-el-j-herbful-8e8a72")

    @patch("reconciler.github_request")
    def test_reconcile_zombie_runners_no_runners_key_skips_repo(self, mock_gh):
        # data present but missing the "runners" key entirely (e.g. an
        # unexpected API shape) must be treated like "nothing to do" for
        # that repo, not raise.
        mock_gh.return_value = {}
        reconcile_zombie_runners(["el-j/run-zero"], access_token="token")
        self.assertEqual(mock_gh.call_count, 1)

    @patch("reconciler.github_request")
    def test_reconcile_zombie_runners_no_zombies_found(self, mock_gh):
        mock_gh.return_value = {
            "runners": [
                {"id": 20, "name": "local-runner-arm64-2", "status": "online", "busy": True},
            ]
        }
        reconcile_zombie_runners(["el-j/run-zero"], access_token="token")
        # Only the initial runners lookup should happen -- no in_progress
        # runs lookup, no cancel, no delete, since there's nothing to reconcile.
        self.assertEqual(mock_gh.call_count, 1)

    @patch("reconciler.github_request")
    def test_reconcile_zombie_runners_delete_failure_logs_and_continues(self, mock_gh):
        # When the DELETE call comes back falsy (run cancellation likely
        # still in flight), reconcile_zombie_runners must not raise -- it
        # just retries next cycle.
        mock_gh.side_effect = [
            {
                "runners": [
                    {"id": 10, "name": "local-runner-arm64-1", "status": "offline", "busy": True},
                ]
            },
            {"workflow_runs": []},
            None,  # DELETE runner 10 fails
        ]
        reconcile_zombie_runners(["el-j/run-zero"], access_token="token")
        self.assertEqual(mock_gh.call_count, 3)

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_finds_runner_via_fallback_repo_search(self, mock_gh):
        # Regression test: a runner's own target_repo doesn't match any key
        # in gh_runners_by_repo (e.g. repo naming drift), but the runner's
        # name IS found under a different tracked repo's runner list --
        # reconcile_idle_orphans must still find that match via the
        # fallback search across all tracked repos, and treat it as busy
        # (so it must NOT be destroyed).
        mock_gh.side_effect = [
            {"runners": []},  # el-j/run-zero: no match by target_repo
            {"runners": [{"id": 99, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": True}]},  # el-j/other
        ]
        driver = MagicMock()
        runner = self._runner(age_seconds=700)
        runner.target_repo = "el-j/nonexistent"
        reconcile_idle_orphans(["el-j/run-zero", "el-j/other"], [runner], {"docker": driver}, access_token="token", now=1_000_000.0)
        driver.destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_zombie_runners_requires_both_offline_and_busy_flags(self, mock_gh):
        # Mutation target: both "offline" AND "busy" must be True (not OR)
        repos = ["test/repo"]

        # Test 1: offline=True, busy=False (should NOT be zombie)
        mock_gh.return_value = {"runners": [{"id": 1, "name": "local-runner-test-1", "status": "offline", "busy": False}]}

        with patch("reconciler.print"):
            reconcile_zombie_runners(repos, access_token="token")

        # Should not try to delete because busy=False
        self.assertEqual(mock_gh.call_count, 1)

        # Reset mocks
        mock_gh.reset_mock()

        # Test 2: offline=False, busy=True (should NOT be zombie)
        mock_gh.return_value = {"runners": [{"id": 1, "name": "local-runner-test-1", "status": "online", "busy": True}]}

        with patch("reconciler.print"):
            reconcile_zombie_runners(repos, access_token="token")

        # Should not try to delete because status != "offline"
        self.assertEqual(mock_gh.call_count, 1)

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_timeout_comparison_not_equal(self, mock_gh):
        # Mutation target: age_seconds > timeout (not >=, not <)
        import time

        from drivers import RunnerInfo

        now = time.time()
        created_at = now - 600  # Exactly 600 seconds old (IDLE_ORPHAN_TIMEOUT_SECONDS)

        runners = [
            RunnerInfo(
                id="runner-1",
                name="local-runner-test-1",
                status="online",
                state="running",
                target_repo="test/repo",
                target_arch="arm64",
                backend="docker",
                created_at=created_at,
            )
        ]

        # Ensure runner is registered in GitHub so idle_timeout comparison is used.
        mock_gh.return_value = {
            "runners": [
                {"id": 99, "name": "local-runner-test-1", "busy": False}
            ]
        }
        drivers = {"docker": MagicMock()}

        with patch("reconciler.print"):
            # With now - created_at = 600 exactly and idle_timeout = 600,
            # condition must be FALSE (strict >), so NO destroy.
            reconcile_idle_orphans(["test/repo"], runners, drivers, idle_timeout_seconds=600, unregistered_timeout_seconds=180, now=now)

        # Verify destroy was NOT called (runner is exactly at timeout, not over it)
        drivers["docker"].destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_age_seconds_must_exceed_timeout(self, mock_gh):
        # Mutation target: age_seconds > timeout must be strictly greater
        import time

        from drivers import RunnerInfo

        now = time.time()
        created_at = now - 601  # 601 seconds old (exceeds IDLE_ORPHAN_TIMEOUT_SECONDS of 600)

        runners = [
            RunnerInfo(
                id="runner-1",
                name="local-runner-test-1",
                status="online",
                state="running",
                target_repo="test/repo",
                target_arch="arm64",
                backend="docker",
                created_at=created_at,
            )
        ]

        mock_gh.return_value = {
            "runners": []  # Not found in GitHub, so will check unregistered timeout
        }
        drivers = {"docker": MagicMock()}

        with patch("reconciler.print"):
            # Runner is 601 seconds old, exceeds 600s timeout
            reconcile_idle_orphans(["test/repo"], runners, drivers, idle_timeout_seconds=600, unregistered_timeout_seconds=180, now=now)

        # Verify destroy WAS called (runner exceeds timeout)
        drivers["docker"].destroy_runner.assert_called_once()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_skips_runner_not_in_managed_prefixes(self, mock_gh):
        # Mutation target: startswith(MANAGED_RUNNER_PREFIXES) check
        import time

        from drivers import RunnerInfo

        now = time.time()
        created_at = now - 700  # Well over timeout

        runners = [
            RunnerInfo(
                id="runner-1",
                name="some-random-runner",  # Doesn't start with managed prefix
                status="online",
                state="running",
                target_repo="test/repo",
                target_arch="arm64",
                backend="docker",
                created_at=created_at,
            )
        ]

        mock_gh.return_value = {"runners": []}
        drivers = {"docker": MagicMock()}

        with patch("reconciler.print"):
            reconcile_idle_orphans(["test/repo"], runners, drivers, idle_timeout_seconds=600, unregistered_timeout_seconds=180, now=now)

        # Should NOT destroy because runner name doesn't start with managed prefix
        drivers["docker"].destroy_runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
