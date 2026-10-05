"""Unit tests for dashboard workflow_service module."""

from __future__ import annotations

import io
import unittest
import urllib.error
from email.message import Message
from unittest.mock import MagicMock, patch

from dashboard.workflow_service import execute_workflow_action


class TestWorkflowService(unittest.TestCase):
    """Test suite for workflow actions execution via GitHub REST API."""

    def test_validation_errors(self):
        with self.assertRaises(ValueError):
            execute_workflow_action("", 123, "cancel", "token")

        with self.assertRaises(ValueError):
            execute_workflow_action("invalid-repo-without-slash", 123, "cancel", "token")

        with self.assertRaises(ValueError):
            execute_workflow_action("owner/repo", 0, "cancel", "token")

        with self.assertRaises(ValueError):
            execute_workflow_action("owner/repo", 123, "invalid-action", "token")

        with self.assertRaises(ValueError):
            execute_workflow_action("owner/repo", 123, "cancel", None)

    @patch("urllib.request.urlopen")
    def test_execute_workflow_action_success(self, mock_urlopen: MagicMock):
        mock_resp = MagicMock()
        mock_resp.status = 202
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = execute_workflow_action("owner/repo", 456, "cancel", "fake-token")
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], 202)

        res_rerun = execute_workflow_action("owner/repo", 456, "rerun", "fake-token")
        self.assertTrue(res_rerun["ok"])

        res_failed = execute_workflow_action("owner/repo", 456, "rerun-failed", "fake-token")
        self.assertTrue(res_failed["ok"])

    @patch("urllib.request.urlopen")
    def test_execute_workflow_action_http_error(self, mock_urlopen: MagicMock):
        fp = io.BytesIO(b'{"message": "Run is not in progress"}')
        err = urllib.error.HTTPError("http://api.github.com", 422, "Unprocessable", Message(), fp)
        mock_urlopen.side_effect = err

        with self.assertRaises(RuntimeError) as cm:
            execute_workflow_action("owner/repo", 123, "cancel", "fake-token")
        self.assertIn("Run is not in progress", str(cm.exception))

    @patch("urllib.request.urlopen")
    def test_execute_workflow_action_http_error_non_json(self, mock_urlopen: MagicMock):
        fp = io.BytesIO(b"Internal Server Error HTML")
        err = urllib.error.HTTPError("http://api.github.com", 500, "Internal Server Error", Message(), fp)
        mock_urlopen.side_effect = err

        with self.assertRaises(RuntimeError) as cm:
            execute_workflow_action("owner/repo", 123, "cancel", "fake-token")
        self.assertIn("Internal Server Error HTML", str(cm.exception))

    @patch("urllib.request.urlopen")
    def test_execute_workflow_action_network_error(self, mock_urlopen: MagicMock):
        err = urllib.error.URLError("DNS resolution failed")
        mock_urlopen.side_effect = err

        with self.assertRaises(RuntimeError) as cm:
            execute_workflow_action("owner/repo", 123, "cancel", "fake-token")
        self.assertIn("Network error", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
