"""
Unit tests for repository auto-discovery.
"""

import unittest
from unittest.mock import patch

from discovery import discover_repositories


class TestDiscovery(unittest.TestCase):
    def test_explicit_repos_config(self):
        repos = discover_repositories(repos_config="el-j/run-zero, el-j/other-repo")
        self.assertEqual(repos, ["el-j/other-repo", "el-j/run-zero"])

    @patch("discovery.github_request")
    def test_auto_discover_with_pagination_and_cutoff(self, mock_gh):
        mock_gh.side_effect = [
            [
                {"full_name": "el-j/active-1", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"},
                {"full_name": "other/active-2", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"},
                {"full_name": "el-j/archived", "archived": True, "pushed_at": "2099-01-01T00:00:00Z"},
            ],
            []  # Page 2 empty
        ]
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(repos, ["el-j/active-1"])

    @patch("discovery.github_request")
    def test_auto_discover_first_page_empty_stops_immediately(self, mock_gh):
        mock_gh.return_value = []
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(repos, [])
        mock_gh.assert_called_once()

    @patch("discovery.github_request")
    def test_auto_discover_old_repo_stops_pagination(self, mock_gh):
        # A repo pushed before the cutoff date must stop pagination -- repos
        # are sorted by pushed date descending, so anything after it is even
        # older and irrelevant.
        mock_gh.return_value = [
            {"full_name": "el-j/recent", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"},
            {"full_name": "el-j/ancient", "archived": False, "pushed_at": "2000-01-01T00:00:00Z"},
        ]
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(repos, ["el-j/recent"])
        mock_gh.assert_called_once()

    @patch("discovery.github_request")
    def test_auto_discover_malformed_pushed_at_still_includes_repo(self, mock_gh):
        # A repo with a pushed_at that fails to parse must not crash discovery
        # -- the exception is swallowed and the repo is still included (fails
        # open rather than silently dropping a real, active repository).
        mock_gh.return_value = [
            {"full_name": "el-j/weird-date", "archived": False, "pushed_at": "not-a-real-date"},
        ]
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(repos, ["el-j/weird-date"])

    @patch("discovery.github_request")
    def test_auto_discover_continues_to_next_page_on_full_page(self, mock_gh):
        # A first page with exactly 100 items (a full page, none triggering
        # the cutoff) must continue on to page 2 rather than stopping.
        full_page = [
            {"full_name": f"el-j/repo-{i}", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"}
            for i in range(100)
        ]
        mock_gh.side_effect = [full_page, []]
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(len(repos), 100)
        self.assertEqual(mock_gh.call_count, 2)


if __name__ == "__main__":
    unittest.main()
