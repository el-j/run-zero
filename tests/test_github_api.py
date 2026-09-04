"""
Unit tests for GitHub REST API client and job queue inspector.
"""

import unittest
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import github_api
from github_api import get_queued_job_details, get_workflow_text_for_run, github_request


class TestGitHubApi(unittest.TestCase):
    def setUp(self):
        # _workflow_text_cache is module-level and keyed by run_id -- several
        # tests reuse run_id 101, so a hit cached by one test would silently
        # skip the HTTP call (and its mock) in the next unless cleared.
        github_api._workflow_text_cache.clear()
        github_api.rate_limit_remaining = None
        github_api.rate_limit_total = None
        github_api.rate_limit_used = None
        github_api.rate_limit_resource = None
        github_api.rate_limit_reset = None

    @patch("urllib.request.urlopen")
    def test_github_request_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.headers = {
            "x-ratelimit-remaining": "4990",
            "x-ratelimit-limit": "5432",
            "x-ratelimit-reset": "1700000000"
        }
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(github_api.rate_limit_remaining, 4990)
        self.assertEqual(github_api.rate_limit_total, 5432)

    @patch("urllib.request.urlopen")
    def test_github_request_http_error(self, mock_urlopen):
        error = urllib.error.HTTPError(
            url="/test", code=403, msg="Forbidden",
            hdrs={
                "x-ratelimit-remaining": "0",
                "x-ratelimit-limit": "7777",
                "x-ratelimit-reset": "1700000000"
            },
            fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)
        self.assertEqual(github_api.rate_limit_total, 7777)

    @patch("urllib.request.urlopen")
    def test_refresh_rate_limit_uses_rate_limit_payload(self, mock_urlopen):
        from github_api import refresh_rate_limit

        mock_resp = MagicMock()
        mock_resp.read.return_value = (
            b'{"resources":{"core":{"limit":9999,"remaining":8765,"used":1234,"reset":1700001111}}}'
        )
        mock_resp.headers = {}
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        ok = refresh_rate_limit(access_token="secret")
        self.assertTrue(ok)
        self.assertEqual(github_api.rate_limit_total, 9999)
        self.assertEqual(github_api.rate_limit_remaining, 8765)
        self.assertEqual(github_api.rate_limit_used, 1234)
        self.assertEqual(github_api.rate_limit_reset, 1700001111)
        self.assertEqual(github_api.rate_limit_resource, "core")

    @patch("github_api.github_request")
    def test_refresh_actions_billing_owner_user_scope(self, mock_gh):
        mock_gh.return_value = {
            "total_minutes_used": 400,
            "total_paid_minutes_used": 120,
            "included_minutes": 3000,
        }

        ok = github_api.refresh_actions_billing(access_token="secret", owner="el-j")
        self.assertTrue(ok)
        self.assertEqual(github_api.actions_billing["scope_type"], "user")
        self.assertEqual(github_api.actions_billing["scope_name"], "el-j")
        self.assertEqual(github_api.actions_billing["minutes_remaining"], 2880)

    @patch("github_api.github_request")
    def test_refresh_actions_billing_owner_fallbacks_to_org_scope(self, mock_gh):
        mock_gh.side_effect = [
            None,
            {
                "total_minutes_used": 900,
                "total_paid_minutes_used": 150,
                "included_minutes": 50000,
            },
        ]

        ok = github_api.refresh_actions_billing(access_token="secret", owner="my-org")
        self.assertTrue(ok)
        self.assertEqual(github_api.actions_billing["scope_type"], "org")
        self.assertEqual(github_api.actions_billing["scope_name"], "my-org")

    @patch("github_api.github_request")
    def test_refresh_actions_billing_error_sets_status_error(self, mock_gh):
        mock_gh.return_value = None

        ok = github_api.refresh_actions_billing(access_token="secret", org="my-org")
        self.assertFalse(ok)
        self.assertEqual(github_api.actions_billing["status"], "error")

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
        self.assertEqual(jobs[0]["run_url"], "https://github.com/el-j/run-zero/actions/runs/101")
        self.assertEqual(jobs[0]["job_url"], "https://github.com/el-j/run-zero/actions/runs/101/job/201")

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

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_github_request_throttles_when_rate_limit_nearly_exhausted(self, mock_urlopen, mock_sleep):
        import github_api
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.headers = {"x-ratelimit-remaining": "4990", "x-ratelimit-reset": "1700000000"}
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        with patch.object(github_api, "rate_limit_remaining", 5), \
             patch.object(github_api, "rate_limit_reset", 9_999_999_999):
            result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})
        mock_sleep.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_github_request_success_tolerates_malformed_ratelimit_headers(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.headers = {"x-ratelimit-remaining": "not-a-number", "x-ratelimit-reset": "1700000000"}
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})

    @patch("urllib.request.urlopen")
    def test_github_request_http_error_tolerates_malformed_ratelimit_headers(self, mock_urlopen):
        error = urllib.error.HTTPError(
            url="/test", code=500, msg="Server Error",
            hdrs={"x-ratelimit-remaining": "garbage", "x-ratelimit-reset": "garbage"},
            fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_github_request_http_error_non_rate_limit_prints_and_returns_none(self, mock_urlopen):
        # A 500 (or any code other than 401/403-with-exhausted-quota or 404)
        # must hit the generic "HTTP Error" logging branch.
        error = urllib.error.HTTPError(
            url="/test", code=500, msg="Internal Server Error",
            hdrs={}, fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    def test_update_rate_limit_from_headers_captures_used_and_resource(self):
        github_api._update_rate_limit_from_headers({
            "x-ratelimit-remaining": "10",
            "x-ratelimit-limit": "100",
            "x-ratelimit-used": "90",
            "x-ratelimit-resource": "search",
            "x-ratelimit-reset": "1700001234",
        })
        self.assertEqual(github_api.rate_limit_used, 90)
        self.assertEqual(github_api.rate_limit_resource, "search")

    def test_update_rate_limit_from_payload_handles_non_dict_and_invalid_resource(self):
        github_api._update_rate_limit_from_payload(["not", "a", "dict"])
        self.assertIsNone(github_api.rate_limit_remaining)

        github_api._update_rate_limit_from_payload({"resources": {"core": "oops"}})
        self.assertIsNone(github_api.rate_limit_total)

    def test_update_rate_limit_from_payload_falls_back_to_core_and_rate(self):
        github_api.rate_limit_resource = "search"
        github_api._update_rate_limit_from_payload({
            "resources": {
                "core": {"limit": 999, "remaining": 333, "used": 666, "reset": 1700002222}
            }
        })
        self.assertEqual(github_api.rate_limit_resource, "core")
        self.assertEqual(github_api.rate_limit_remaining, 333)

        github_api.rate_limit_resource = "search"
        github_api._update_rate_limit_from_payload({
            "resources": {},
            "rate": {"limit": 5000, "remaining": 4900, "used": 100, "reset": 1700003333},
        })
        self.assertEqual(github_api.rate_limit_remaining, 4900)
        self.assertEqual(github_api.rate_limit_used, 100)

    def test_update_rate_limit_from_payload_tolerates_bad_numeric_values(self):
        github_api._update_rate_limit_from_payload({
            "resources": {
                "core": {"limit": "bad", "remaining": "bad", "used": "bad", "reset": "bad"}
            }
        })
        self.assertIsNone(github_api.rate_limit_total)

    def test_normalize_actions_billing_tolerates_non_numeric_values(self):
        normalized = github_api._normalize_actions_billing(
            {"total_minutes_used": "x", "total_paid_minutes_used": "y", "included_minutes": "z"},
            "user",
            "el-j",
        )
        self.assertIsNotNone(normalized)
        self.assertIsNone(normalized["included_minutes"])
        self.assertIsNone(normalized["total_minutes_used"])
        self.assertIsNone(normalized["total_paid_minutes_used"])
        self.assertIsNone(normalized["minutes_remaining"])

    @patch("github_api.github_request")
    def test_refresh_actions_billing_org_scope_success(self, mock_gh):
        mock_gh.return_value = {
            "total_minutes_used": 12,
            "total_paid_minutes_used": 4,
            "included_minutes": 3000,
        }
        ok = github_api.refresh_actions_billing(access_token="secret", org="my-org")
        self.assertTrue(ok)
        self.assertEqual(github_api.actions_billing["scope_type"], "org")

    @patch("github_api.github_request")
    def test_refresh_actions_billing_owner_fallback_error_uses_unknown_scope(self, mock_gh):
        mock_gh.side_effect = [None, None]
        ok = github_api.refresh_actions_billing(access_token="secret", owner="owner-only")
        self.assertFalse(ok)
        self.assertEqual(github_api.actions_billing["scope_type"], "unknown")
        self.assertEqual(github_api.actions_billing["scope_name"], "owner-only")

    @patch("urllib.request.urlopen")
    def test_github_request_rate_limit_error_without_reset_uses_unknown_reset_time(self, mock_urlopen):
        error = urllib.error.HTTPError(
            url="/test", code=403, msg="Forbidden", hdrs={"x-ratelimit-remaining": "0"}, fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    @patch("github_api.github_request")
    def test_get_workflow_text_for_run_decode_error_returns_none(self, mock_gh):
        mock_gh.side_effect = [
            {"path": ".github/workflows/ci.yml", "head_sha": "abc123"},
            {"encoding": "base64", "content": "not-valid-base64!!!"},
        ]
        text = get_workflow_text_for_run("el-j/herbful", 2222, access_token="token")
        self.assertIsNone(text)

    @patch("github_api.github_request")
    def test_get_queued_job_details_no_data_returns_empty(self, mock_gh):
        mock_gh.return_value = None
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])

    @patch("github_api.github_request")
    def test_get_queued_job_details_run_without_id_is_skipped(self, mock_gh):
        mock_gh.return_value = {"workflow_runs": [{"head_branch": "main", "event": "push"}]}
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])
        # Only the initial queued-runs lookup should happen -- no jobs lookup
        # for a run with no id.
        self.assertEqual(mock_gh.call_count, 1)

    @patch("github_api.github_request")
    def test_get_queued_job_details_missing_jobs_data_is_skipped(self, mock_gh):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            None,  # jobs lookup fails
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])


if __name__ == "__main__":
    unittest.main()

    @patch("urllib.request.urlopen")
    def test_github_request_rate_limit_10_remaining(self, mock_urlopen):
        # Mutation: rate_limit_remaining <= 10 (boundary)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"data": []}).encode("utf-8")
        now = 1000000000
        mock_response.headers = {
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": str(int(now + 60))
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with patch("github_api.time.time", return_value=now):
            result = github_request(
                "/repos/test/repo/actions/runs", "token", method="GET"
            )
        self.assertEqual(result, {"data": []})

    @patch("urllib.request.urlopen")
    def test_github_request_rate_limit_11_remaining(self, mock_urlopen):
        # Mutation: rate_limit_remaining <= 10 (must NOT trigger with 11)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"data": []}).encode("utf-8")
        now = 1000000000
        mock_response.headers = {
            "X-RateLimit-Remaining": "11",
            "X-RateLimit-Reset": str(int(now + 60))
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        with patch("github_api.time.time", return_value=now):
            result = github_request(
                "/repos/test/repo/actions/runs", "token", method="GET"
            )
        self.assertEqual(result, {"data": []})

    @patch("urllib.request.urlopen")
    def test_github_request_error_401_handled(self, mock_urlopen):
        # Mutation: e.code in (401, 403) - tuple membership
        error = urllib.error.HTTPError(
            "https://api.github.com/repos", 401, "Unauthorized", {}, None
        )
        mock_urlopen.side_effect = error
        result = github_request(
            "/repos/test/repo/actions/runs", "token", method="GET"
        )
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_github_request_error_403_handled(self, mock_urlopen):
        # Mutation: e.code in (401, 403) - tuple membership
        error = urllib.error.HTTPError(
            "https://api.github.com/repos", 403, "Forbidden", {}, None
        )
        mock_urlopen.side_effect = error
        result = github_request(
            "/repos/test/repo/actions/runs", "token", method="GET"
        )
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_github_request_error_500_raises(self, mock_urlopen):
        # Mutation: e.code != 404 - inequality check
        error = urllib.error.HTTPError(
            "https://api.github.com/repos", 500, "Server Error", {}, None
        )
        mock_urlopen.side_effect = error
        with self.assertRaises(urllib.error.HTTPError):
            github_request(
                "/repos/test/repo/actions/runs", "token", method="GET"
            )

    @patch("urllib.request.urlopen")
    def test_github_request_error_404_no_raise(self, mock_urlopen):
        # Mutation: e.code != 404 - inequality check (404 is special)
        error = urllib.error.HTTPError(
            "https://api.github.com/repos", 404, "Not Found", {}, None
        )
        mock_urlopen.side_effect = error
        result = github_request(
            "/repos/test/repo/actions/runs", "token", method="GET"
        )
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_get_queued_job_details_self_hosted_label_filter(self, mock_urlopen):
        # Mutation: "self-hosted" in job.get("labels", [])
        run_response = MagicMock()
        run_response.read.return_value = json.dumps({
            "workflow_runs": [{"id": 1}]
        }).encode("utf-8")
        run_response.headers = {}
        
        jobs_response = MagicMock()
        jobs_response.read.return_value = json.dumps({
            "jobs": [
                {"id": 1, "status": "queued", "name": "job1",
                 "labels": ["self-hosted", "linux"]},
                {"id": 2, "status": "queued", "name": "job2",
                 "labels": ["ubuntu-latest"]}
            ]
        }).encode("utf-8")
        jobs_response.headers = {}
        
        def urlopen_side_effect(req):
            if "runs?status=queued" in req.get_full_url():
                return (run_response.__enter__ for _ in [None]).__next__()
            return (jobs_response.__enter__ for _ in [None]).__next__()
        
        mock_urlopen.return_value.__enter__.side_effect = [
            run_response.read,
            jobs_response.read
        ]
        mock_urlopen.side_effect = None
        mock_urlopen.return_value.__enter__.return_value.read.side_effect = [
            run_response.read.return_value,
            jobs_response.read.return_value
        ]
        
        with patch(
            "github_api.get_workflow_text_for_run", return_value=None
        ):
            result = get_queued_job_details("test/repo", "token")

    @patch("urllib.request.urlopen")
    def test_get_workflow_text_caching_dict_membership(self, mock_urlopen):
        # Mutation: run_id in _workflow_text_cache
        mock_response = MagicMock()
        mock_response.read.return_value = b"workflow yaml"
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        import github_api
        github_api._workflow_text_cache.clear()
        
        result1 = get_workflow_text_for_run("repo", 123, "token")
        call_count_1 = mock_urlopen.call_count
        
        result2 = get_workflow_text_for_run("repo", 123, "token")
        call_count_2 = mock_urlopen.call_count
        
        self.assertEqual(result1, result2)
        self.assertEqual(call_count_1, 2)
        self.assertEqual(call_count_2, 2)

