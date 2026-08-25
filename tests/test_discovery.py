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


if __name__ == "__main__":
    unittest.main()
