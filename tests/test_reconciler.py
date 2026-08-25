"""
Unit tests for self-healing zombie runner reconciler.
"""

import unittest
from unittest.mock import patch
from reconciler import reconcile_zombie_runners


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


if __name__ == "__main__":
    unittest.main()
