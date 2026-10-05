"""
Unit tests for GitHub REST API client and job queue inspector.
"""

import unittest
import urllib.error
from email.message import Message
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch

import github_api
from github_api import get_queued_job_details, get_workflow_text_for_run, github_request


def _headers(values: dict[str, str]) -> Message:
    """Build the header mapping urllib.error.HTTPError expects (``hdrs``) from a plain dict."""
    msg = Message()
    for key, value in values.items():
        msg[key] = value
    return msg


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
        mock_resp.headers = {"x-ratelimit-remaining": "4990", "x-ratelimit-limit": "5432", "x-ratelimit-reset": "1700000000"}
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(github_api.rate_limit_remaining, 4990)
        self.assertEqual(github_api.rate_limit_total, 5432)

    @patch("urllib.request.urlopen")
    def test_github_request_http_error(self, mock_urlopen):
        error = urllib.error.HTTPError(
            url="/test",
            code=403,
            msg="Forbidden",
            hdrs=_headers({"x-ratelimit-remaining": "0", "x-ratelimit-limit": "7777", "x-ratelimit-reset": "1700000000"}),
            fp=BytesIO(b""),
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)
        self.assertEqual(github_api.rate_limit_total, 7777)

    @patch("urllib.request.urlopen")
    def test_refresh_rate_limit_uses_rate_limit_payload(self, mock_urlopen):
        from github_api import refresh_rate_limit

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"resources":{"core":{"limit":9999,"remaining":8765,"used":1234,"reset":1700001111}}}'
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
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push", "path": ".github/workflows/ci.yml"}]},
            {"workflow_runs": []},  # in_progress runs
            {"jobs": [{"id": 201, "name": "e2e-chrome", "status": "queued", "labels": ["self-hosted", "browser"]}]},
        ]
        mock_workflow_text.return_value = None  # workflow lookup unresolved -> declares_services is None
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 201)
        self.assertEqual(jobs[0]["name"], "e2e-chrome")
        self.assertEqual(jobs[0]["run_id"], 101)
        self.assertEqual(jobs[0]["workflow_path"], ".github/workflows/ci.yml")
        self.assertIn("browser", jobs[0]["labels"])
        self.assertIsNone(jobs[0]["declares_services"])
        self.assertEqual(jobs[0]["run_url"], "https://github.com/el-j/run-zero/actions/runs/101")
        self.assertEqual(jobs[0]["job_url"], "https://github.com/el-j/run-zero/actions/runs/101/job/201")

    @patch("github_api.get_workflow_text_for_run", return_value=None)
    @patch("github_api.github_request")
    def test_get_queued_job_details_finds_queued_jobs_of_in_progress_runs(self, mock_gh, _workflow_text):
        # A run whose first job already started (or whose skipped jobs count as started) is
        # in_progress while later jobs still wait; those must be seen too.
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101}]},
            {"workflow_runs": [{"id": 101}, {"id": 102}]},  # 101 shows up in both listings
            {"jobs": [{"id": 201, "name": "build", "status": "queued", "labels": ["self-hosted"]}]},
            {
                "jobs": [
                    {"id": 301, "name": "detect", "status": "completed", "labels": ["self-hosted"]},
                    {"id": 302, "name": "e2e", "status": "queued", "labels": ["self-hosted"]},
                ]
            },
        ]
        jobs = get_queued_job_details("el-j/herbful", access_token="token")
        self.assertEqual([j["id"] for j in jobs], [201, 302])
        urls = [c.args[0] for c in mock_gh.call_args_list]
        self.assertIn("status=in_progress", urls[1])
        self.assertEqual(sum("/runs/101/jobs" in u for u in urls), 1)

    @patch("github_api.get_workflow_text_for_run", return_value=None)
    @patch("github_api.github_request")
    def test_get_queued_job_details_include_in_progress(self, mock_gh, _workflow_text):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "name": "CI", "path": ".github/workflows/ci.yml", "run_attempt": 2, "head_branch": "feat/x"}]},
            {"workflow_runs": []},
            {
                "jobs": [
                    {
                        "id": 201,
                        "name": "unit-test",
                        "status": "in_progress",
                        "labels": ["self-hosted"],
                        "run_attempt": 2,
                        "created_at": "2026-10-04T20:00:00Z",
                        "started_at": "2026-10-04T20:01:00Z",
                    },
                    {
                        "id": 202,
                        "name": "e2e-test",
                        "status": "queued",
                        "labels": ["self-hosted"],
                        "created_at": "2026-10-04T20:02:00Z",
                    },
                ]
            },
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token", include_in_progress=True)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["id"], 201)
        self.assertEqual(jobs[0]["status"], "in_progress")
        self.assertEqual(jobs[0]["run_attempt"], 2)
        self.assertEqual(jobs[0]["workflow_name"], "CI")
        self.assertEqual(jobs[0]["created_at"], "2026-10-04T20:00:00Z")
        self.assertEqual(jobs[0]["started_at"], "2026-10-04T20:01:00Z")

        self.assertEqual(jobs[1]["id"], 202)
        self.assertEqual(jobs[1]["status"], "queued")
        self.assertEqual(jobs[1]["workflow_name"], "CI")

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
            {"workflow_runs": []},  # in_progress runs
            {"jobs": [{"id": 201, "name": "Python Lint", "status": "queued", "labels": ["ubuntu-latest"]}]},
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])

    @patch("github_api.get_workflow_text_for_run")
    @patch("github_api.github_request")
    def test_get_queued_job_details_mixed_batch_only_returns_self_hosted(self, mock_gh, mock_workflow_text):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"workflow_runs": []},  # in_progress runs
            {
                "jobs": [
                    {"id": 201, "name": "hosted-job", "status": "queued", "labels": ["ubuntu-latest"]},
                    {"id": 202, "name": "local-job", "status": "queued", "labels": ["self-hosted", "local"]},
                ]
            },
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
            {"workflow_runs": []},  # in_progress runs
            {"jobs": [{"id": 301, "name": "API — Tests", "status": "queued", "labels": ["self-hosted", "amd64"]}]},
        ]
        mock_workflow_text.return_value = "jobs:\n  api-test:\n    name: API — Tests\n    services:\n      postgres:\n        image: postgres:16\n"
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

    def _ok_response(self) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"status": "ok"}'
        mock_resp.headers = {"x-ratelimit-remaining": "4990", "x-ratelimit-reset": "1700000000"}
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    @patch("urllib.request.urlopen")
    def test_github_request_throttles_then_proceeds_once_limit_resets(self, mock_urlopen):
        import github_api

        mock_urlopen.return_value = self._ok_response()
        event = MagicMock()
        event.wait.return_value = False  # no shutdown during the wait
        with (
            patch.object(github_api, "rate_limit_remaining", 5),
            patch.object(github_api, "rate_limit_reset", 1_000_010),
            patch.object(github_api, "shutdown_event", event),
            patch("github_api.time.time", side_effect=[1_000_000, 1_000_011]),
            patch("builtins.print"),
        ):
            result = github_request("/test", access_token="secret")
        self.assertEqual(result, {"status": "ok"})
        event.wait.assert_called_once_with(11)

    @patch("urllib.request.urlopen")
    def test_github_request_throttle_is_capped_and_skips_request_if_not_reset(self, mock_urlopen):
        # #44: the wait used to be time.sleep(reset - now) -- up to an hour on the main thread.
        import github_api

        event = MagicMock()
        event.wait.return_value = False
        with (
            patch.object(github_api, "rate_limit_remaining", 5),
            patch.object(github_api, "rate_limit_reset", 1_003_600),
            patch.object(github_api, "shutdown_event", event),
            patch("github_api.time.time", side_effect=[1_000_000, 1_000_060]),
            patch("builtins.print"),
        ):
            self.assertIsNone(github_request("/test", access_token="secret"))
        event.wait.assert_called_once_with(github_api.MAX_THROTTLE_WAIT_SECONDS)
        mock_urlopen.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_shutdown_signalled_mid_throttle_wakes_the_waiting_request(self, mock_urlopen):
        import github_api

        event = github_api.threading.Event()
        timer = github_api.threading.Timer(0.2, event.set)
        with (
            patch.object(github_api, "rate_limit_remaining", 0),
            patch.object(github_api, "rate_limit_reset", 9_999_999_999),
            patch.object(github_api, "shutdown_event", event),
            patch("builtins.print"),
        ):
            started = github_api.time.monotonic()
            timer.start()
            self.assertIsNone(github_request("/test", access_token="secret"))
            elapsed = github_api.time.monotonic() - started
        timer.join()
        self.assertGreaterEqual(elapsed, 0.15)
        self.assertLess(elapsed, 5.0)  # vs. up to MAX_THROTTLE_WAIT_SECONDS without the event
        mock_urlopen.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_github_request_throttle_returns_promptly_on_shutdown(self, mock_urlopen):
        import github_api

        event = github_api.threading.Event()
        event.set()
        with (
            patch.object(github_api, "rate_limit_remaining", 0),
            patch.object(github_api, "rate_limit_reset", 9_999_999_999),
            patch.object(github_api, "shutdown_event", event),
            patch("builtins.print"),
        ):
            started = github_api.time.monotonic()
            self.assertIsNone(github_request("/test", access_token="secret"))
            self.assertLess(github_api.time.monotonic() - started, 1.0)
        mock_urlopen.assert_not_called()

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
            url="/test", code=500, msg="Server Error", hdrs=_headers({"x-ratelimit-remaining": "garbage", "x-ratelimit-reset": "garbage"}), fp=BytesIO(b"")
        )
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_github_request_http_error_non_rate_limit_prints_and_returns_none(self, mock_urlopen):
        # A 500 (or any code other than 401/403-with-exhausted-quota or 404)
        # must hit the generic "HTTP Error" logging branch.
        error = urllib.error.HTTPError(url="/test", code=500, msg="Internal Server Error", hdrs=_headers({}), fp=BytesIO(b""))
        mock_urlopen.side_effect = error
        result = github_request("/test", access_token="secret")
        self.assertIsNone(result)

    def test_update_rate_limit_from_headers_captures_used_and_resource(self):
        github_api._update_rate_limit_from_headers(
            {
                "x-ratelimit-remaining": "10",
                "x-ratelimit-limit": "100",
                "x-ratelimit-used": "90",
                "x-ratelimit-resource": "search",
                "x-ratelimit-reset": "1700001234",
            }
        )
        self.assertEqual(github_api.rate_limit_used, 90)
        self.assertEqual(github_api.rate_limit_resource, "search")

    def test_update_rate_limit_from_payload_handles_non_dict_and_invalid_resource(self):
        github_api._update_rate_limit_from_payload(["not", "a", "dict"])
        self.assertIsNone(github_api.rate_limit_remaining)

        github_api._update_rate_limit_from_payload({"resources": {"core": "oops"}})
        self.assertIsNone(github_api.rate_limit_total)

    def test_update_rate_limit_from_payload_falls_back_to_core_and_rate(self):
        github_api.rate_limit_resource = "search"
        github_api._update_rate_limit_from_payload({"resources": {"core": {"limit": 999, "remaining": 333, "used": 666, "reset": 1700002222}}})
        self.assertEqual(github_api.rate_limit_resource, "core")
        self.assertEqual(github_api.rate_limit_remaining, 333)

        github_api.rate_limit_resource = "search"
        github_api._update_rate_limit_from_payload(
            {
                "resources": {},
                "rate": {"limit": 5000, "remaining": 4900, "used": 100, "reset": 1700003333},
            }
        )
        self.assertEqual(github_api.rate_limit_remaining, 4900)
        self.assertEqual(github_api.rate_limit_used, 100)

    def test_update_rate_limit_from_payload_tolerates_bad_numeric_values(self):
        github_api._update_rate_limit_from_payload({"resources": {"core": {"limit": "bad", "remaining": "bad", "used": "bad", "reset": "bad"}}})
        self.assertIsNone(github_api.rate_limit_total)

    def test_normalize_actions_billing_tolerates_non_numeric_values(self):
        normalized = github_api._normalize_actions_billing(
            {"total_minutes_used": "x", "total_paid_minutes_used": "y", "included_minutes": "z"},
            "user",
            "el-j",
        )
        self.assertIsNotNone(normalized)
        assert normalized is not None
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
        error = urllib.error.HTTPError(url="/test", code=403, msg="Forbidden", hdrs=_headers({"x-ratelimit-remaining": "0"}), fp=BytesIO(b""))
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
        # Only the queued and in_progress run listings happen -- no jobs lookup
        # for a run with no id.
        self.assertEqual(mock_gh.call_count, 2)

    @patch("github_api.github_request")
    def test_get_queued_job_details_missing_jobs_data_is_skipped(self, mock_gh):
        mock_gh.side_effect = [
            {"workflow_runs": [{"id": 101, "head_branch": "main", "event": "push"}]},
            {"workflow_runs": []},  # in_progress runs
            None,  # jobs lookup fails
        ]
        jobs = get_queued_job_details("el-j/run-zero", access_token="token")
        self.assertEqual(jobs, [])


if __name__ == "__main__":
    unittest.main()


class TestGithubPaginate(unittest.TestCase):
    """github_paginate(): follows pages, never returns a partial list on failure (#45)."""

    def _pages(self, pages: list[Any]) -> tuple[MagicMock, Any]:
        mock = MagicMock(side_effect=pages)
        return mock, patch("github_api.github_request", mock)

    def test_follows_pages_until_a_short_page(self):
        full = {"jobs": [{"id": i} for i in range(github_api.PAGE_SIZE)]}
        mock, p = self._pages([full, {"jobs": [{"id": "last"}, "not-a-dict"]}])
        with p:
            items = github_api.github_paginate("/repos/o/r/actions/runs/1/jobs", "jobs", access_token="t")
        assert items is not None
        self.assertEqual(len(items), github_api.PAGE_SIZE + 1)
        urls = [c.args[0] for c in mock.call_args_list]
        self.assertEqual(urls, ["/repos/o/r/actions/runs/1/jobs?per_page=100&page=1", "/repos/o/r/actions/runs/1/jobs?per_page=100&page=2"])

    def test_existing_query_string_uses_ampersand(self):
        mock, p = self._pages([{"workflow_runs": []}])
        with p:
            self.assertEqual(github_api.github_paginate("/x?status=queued", "workflow_runs"), [])
        self.assertEqual(mock.call_args.args[0], "/x?status=queued&per_page=100&page=1")

    def test_failure_or_malformed_page_is_none(self):
        full = {"runners": [{"id": i} for i in range(github_api.PAGE_SIZE)]}
        seconds: tuple[Any, ...] = (None, {"runners": "x"}, [], True)
        for second in seconds:
            with self.subTest(second=second):
                _, p = self._pages([full, second])
                with p:
                    self.assertIsNone(github_api.github_paginate("/x", "runners"))

    def test_page_cap(self):
        full = {"runners": [{"id": i} for i in range(github_api.PAGE_SIZE)]}
        for allow, expected_len in ((True, 2 * github_api.PAGE_SIZE), (False, None)):
            with self.subTest(allow=allow):
                mock, p = self._pages([full] * 5)
                with p, patch("builtins.print") as printed:
                    items = github_api.github_paginate("/x", "runners", max_pages=2, allow_truncated=allow)
                self.assertEqual(mock.call_count, 2)
                self.assertEqual(None if items is None else len(items), expected_len)
                self.assertIn("only the first 200", printed.call_args.args[0])


class TestWorkflowTextCacheBound(unittest.TestCase):
    """#51: the per-run workflow cache is an LRU, not an ever-growing dict."""

    def setUp(self):
        github_api._workflow_text_cache.clear()
        self.addCleanup(github_api._workflow_text_cache.clear)

    def test_evicts_least_recently_used(self):
        with patch.object(github_api, "WORKFLOW_TEXT_CACHE_SIZE", 2), patch("github_api.github_request", return_value=None) as req:
            get_workflow_text_for_run("o/r", 1)
            get_workflow_text_for_run("o/r", 2)
            get_workflow_text_for_run("o/r", 1)  # hit: 1 becomes most recent
            get_workflow_text_for_run("o/r", 3)  # evicts 2
            self.assertEqual(list(github_api._workflow_text_cache), [1, 3])
            calls = req.call_count
            get_workflow_text_for_run("o/r", 1)
            self.assertEqual(req.call_count, calls)  # still cached


class TestRefreshGuards(unittest.TestCase):
    """Refresh helpers must report failure without raising (previously only hit via real 401s)."""

    def test_refresh_rate_limit_false_when_fetch_fails(self):
        with patch("github_api.github_request", return_value=None):
            self.assertFalse(github_api.refresh_rate_limit("t"))

    def test_refresh_actions_billing_false_without_scope(self):
        with patch("github_api.github_request") as req:
            self.assertFalse(github_api.refresh_actions_billing("t", owner="  ", org=None))
        req.assert_not_called()
