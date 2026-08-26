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
            {
                "workflow_runs": [
                    {"id": 999, "run_number": 42}
                ]
            },
            # 3. /repos/el-j/run-zero/actions/runs/999/jobs
            {
                "jobs": [
                    {"runner_name": "local-runner-arm64-1", "name": "build"}
                ]
            },
            # 4. Cancel run 999
            True,
            # 5. Delete runner 10
            True,
        ]

        reconcile_zombie_runners(["el-j/run-zero"], access_token="token")
        self.assertEqual(mock_gh.call_count, 5)

    def _runner(self, name="local-runner-arm64-el-j-run-zero-abc123", age_seconds=700, state="running"):
        return RunnerInfo(
            id="container123", name=name, status="Up", state=state,
            target_repo="el-j/run-zero", target_arch="arm64", backend="docker",
            created_at=1_000_000.0 - age_seconds
        )

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_skips_when_nothing_old_enough(self, mock_gh):
        # Regression guard for the real bug this fixes: a queued ubuntu-latest
        # job still spawned a local container that then sat idle forever with
        # nothing ever reaping it. A runner younger than the timeout must never
        # trigger any API calls at all -- this also has to stay near-zero-cost
        # on every 10s poll loop tick in the common case.
        driver = MagicMock()
        reconcile_idle_orphans(
            ["el-j/run-zero"],
            [self._runner(age_seconds=5)],
            {"docker": driver},
            access_token="token",
            now=1_000_000.0
        )
        mock_gh.assert_not_called()
        driver.destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_destroys_never_dispatched_runner(self, mock_gh):
        mock_gh.side_effect = [
            {"runners": [{"id": 55, "name": "local-runner-arm64-el-j-run-zero-abc123", "busy": False}]},
            True,  # DELETE runner registration
        ]
        driver = MagicMock()
        reconcile_idle_orphans(
            ["el-j/run-zero"],
            [self._runner(age_seconds=700)],
            {"docker": driver},
            access_token="token",
            now=1_000_000.0
        )
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
            now=1_000_000.0
        )
        driver.destroy_runner.assert_not_called()

    @patch("reconciler.github_request")
    def test_reconcile_idle_orphans_destroys_even_if_never_registered(self, mock_gh):
        # The container came up but the runner process never made it into
        # GitHub's runner list at all -- still an orphan, not a reason to skip.
        mock_gh.return_value = {"runners": []}
        driver = MagicMock()
        reconcile_idle_orphans(
            ["el-j/run-zero"],
            [self._runner(age_seconds=700)],
            {"docker": driver},
            access_token="token",
            now=1_000_000.0
        )
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
            created_at=1_000_000.0 - 250  # 250s old (> 180s unregistered threshold)
        )
        reconcile_idle_orphans(
            ["el-j/herbful"],
            [vm_runner],
            {"orbstack-vm": driver},
            access_token="token",
            now=1_000_000.0
        )
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
        reconcile_idle_orphans(
            ["el-j/run-zero", "el-j/other"],
            [runner],
            {"docker": driver},
            access_token="token",
            now=1_000_000.0
        )
        driver.destroy_runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
