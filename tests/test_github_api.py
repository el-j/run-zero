"""
Unit tests for GitHub REST API client and job queue inspector.
"""

import unittest
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

from github_api import get_queued_job_details, get_workflow_text_for_run, github_request


class TestGitHubApi(unittest.TestCase):
    def setUp(self):
        # _workflow_text_cache is module-level and keyed by run_id -- several
        # tests reuse run_id 101, so a hit cached by one test would silently
        # skip the HTTP call (and its mock) in the next unless cleared.
        import github_api
        github_api._workflow_text_cache.clear()

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

    @patch("github_api.get_workflow_text_for_run")
    @patch("github_api.github_request")
    def test_get_queued_job_details(self, mock_gh, mock_workflow_text):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"jobs": [{"id": 201, "name": "e2e-chrome", "status": "queued", "labels": ["self-hosted", "browser"]}]}
        ]
        mock_workflow_text.return_value = None  # workflow lookup unresolved -> declares_services is None
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 201)
        self.assertEqual(jobs[0]["name"], "e2e-chrome")
        self.assertEqual(jobs[0]["run_id"], 101)
        self.assertIn("browser", jobs[0]["labels"])
        self.assertIsNone(jobs[0]["declares_services"])

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

    @patch("github_api.get_workflow_text_for_run")
    @patch("github_api.github_request")
    def test_get_queued_job_details_mixed_batch_only_returns_self_hosted(self, mock_gh, mock_workflow_text):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"jobs": [
                {"id": 201, "name": "hosted-job", "status": "queued", "labels": ["ubuntu-latest"]},
                {"id": 202, "name": "local-job", "status": "queued", "labels": ["self-hosted", "local"]},
            ]}
        ]
        mock_workflow_text.return_value = None
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 202)

    @patch("github_api.get_workflow_text_for_run")
    @patch("github_api.github_request")
    def test_get_queued_job_details_resolves_declares_services_from_workflow(self, mock_gh, mock_workflow_text):
        # Regression test for the "API — Tests" bug: a job with no
        # postgres/service/db keyword in its name or labels must still come
        # back with declares_services=True when the workflow file it belongs
        # to actually has a `services:` block for that job.
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 555, "head_branch": "feat/x", "event": "pull_request"}]},
            {"jobs": [{"id": 301, "name": "API — Tests", "status": "queued", "labels": ["self-hosted", "amd64"]}]}
        ]
        mock_workflow_text.return_value = (
            "jobs:\n"
            "  api-test:\n"
            "    name: API — Tests\n"
            "    services:\n"
            "      postgres:\n"
            "        image: postgres:16\n"
        )
        jobs = get_queued_job_details("el-j/herbful", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertTrue(jobs[0]["declares_services"])

    @patch("github_api.github_request")
    def test_get_workflow_text_for_run_fetches_and_decodes(self, mock_gh):
        import base64
        raw_yaml = "jobs:\n  x:\n    name: X\n"
        mock_gh.side_effect = [
            {"path": ".github/workflows/ci.yml", "head_sha": "abc123"},
            {"encoding": "base64", "content": base64.b64encode(raw_yaml.encode()).decode()},
        ]
        text = get_workflow_text_for_run("el-j/herbful", 999, access_token="token")
        self.assertEqual(text, raw_yaml)

    @patch("github_api.github_request")
    def test_get_workflow_text_for_run_caches_by_run_id(self, mock_gh):
        import base64
        raw_yaml = "jobs:\n  x:\n    name: X\n"
        mock_gh.side_effect = [
            {"path": ".github/workflows/ci.yml", "head_sha": "abc123"},
            {"encoding": "base64", "content": base64.b64encode(raw_yaml.encode()).decode()},
        ]
        first = get_workflow_text_for_run("el-j/herbful", 12345, access_token="token")
        second = get_workflow_text_for_run("el-j/herbful", 12345, access_token="token")
        self.assertEqual(first, second)
        self.assertEqual(mock_gh.call_count, 2)  # not re-fetched on the second call

    @patch("github_api.github_request")
    def test_get_workflow_text_for_run_missing_run_returns_none(self, mock_gh):
        mock_gh.return_value = None
        text = get_workflow_text_for_run("el-j/herbful", 1, access_token="token")
        self.assertIsNone(text)


if __name__ == "__main__":
    unittest.main()
