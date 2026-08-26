"""
Unit tests for GitHub REST API client and job queue inspector.
"""

import unittest
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

from github_api import get_queued_job_details, github_request


class TestGitHubApi(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_github_request_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.headers = {"x-ratelimit-remaining": "4990", "x-ratelimit-reset": "1700000000"}
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})

    @patch("urllib.request.urlopen")
    def test_github_request_http_error(self, mock_urlopen):
        error = urllib.error.HTTPError(
            url="/test", code=403, msg="Forbidden",
            hdrs={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1700000000"},
            fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_github_request_generic_exception(self, mock_urlopen):
        mock_urlopen.side_effect = ConnectionResetError("Connection reset")
        result = github_request("/test")
        self.assertIsNone(result)

    @patch("github_api.github_request")
    def test_get_queued_job_details(self, mock_gh):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"jobs": [{"id": 201, "name": "e2e-chrome", "status": "queued", "labels": ["self-hosted", "browser"]}]}
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 201)
        self.assertEqual(jobs[0]["name"], "e2e-chrome")
        self.assertEqual(jobs[0]["run_id"], 101)
        self.assertIn("browser", jobs[0]["labels"])

    @patch("github_api.github_request")
    def test_get_queued_job_details_empty(self, mock_gh):
        mock_gh.return_value = {"workflow_runs": []}
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])

    @patch("github_api.github_request")
    def test_get_queued_job_details_ignores_github_hosted_jobs(self, mock_gh):
        # Regression test: a queued job that will never be dispatched to us
        # (runs-on: ubuntu-latest, no "self-hosted" label) must never trigger a
        # spawn. Before this filter existed, get_queued_job_details returned
        # every queued job regardless of labels, so the autoscaler spawned a
        # local runner for it anyway -- one that then sat registered and idle
        # forever, since GitHub always dispatches such jobs to its own hosted
        # fleet instead. This happened for real against el-j/run-zero's own
        # ubuntu-latest CI jobs.
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"jobs": [{"id": 201, "name": "Python Lint", "status": "queued", "labels": ["ubuntu-latest"]}]}
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])

    @patch("github_api.github_request")
    def test_get_queued_job_details_mixed_batch_only_returns_self_hosted(self, mock_gh):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"jobs": [
                {"id": 201, "name": "hosted-job", "status": "queued", "labels": ["ubuntu-latest"]},
                {"id": 202, "name": "local-job", "status": "queued", "labels": ["self-hosted", "local"]},
            ]}
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 202)


if __name__ == "__main__":
    unittest.main()
