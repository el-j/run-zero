"""
Unit tests for repository auto-discovery.
"""

import unittest
from typing import Any
from unittest.mock import patch

import discovery
from discovery import _repo_listing_endpoint, discover_repositories


class TestDiscovery(unittest.TestCase):
    def setUp(self):
        # These tests drive the listing loop; account-type detection is covered separately.
        endpoint = patch("discovery._repo_listing_endpoint", return_value=discovery.USER_REPOS_ENDPOINT)
        endpoint.start()
        self.addCleanup(endpoint.stop)

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
            [],  # Page 2 empty
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
        full_page = [{"full_name": f"el-j/repo-{i}", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"} for i in range(100)]
        mock_gh.side_effect = [full_page, []]
        repos = discover_repositories(owner="el-j", active_days=60, auto_discover=True, access_token="token")
        self.assertEqual(len(repos), 100)
        self.assertEqual(mock_gh.call_count, 2)


class TestOrgOwnerDiscovery(unittest.TestCase):
    """#51: an organization OWNER used to discover nothing via /user/repos."""

    @patch("discovery.github_request")
    def test_organization_owner_uses_org_listing(self, mock_gh):
        mock_gh.return_value = {"login": "acme", "type": "Organization"}
        self.assertEqual(_repo_listing_endpoint("acme", "t"), "/orgs/acme/repos?type=all&sort=pushed&direction=desc")
        mock_gh.assert_called_once_with("/users/acme", access_token="t")

    @patch("discovery.github_request")
    def test_user_owner_or_failed_lookup_uses_user_listing(self, mock_gh):
        accounts: tuple[Any, ...] = ({"type": "User"}, None, [])
        for account in accounts:
            with self.subTest(account=account):
                mock_gh.return_value = account
                self.assertEqual(_repo_listing_endpoint("el-j", "t"), discovery.USER_REPOS_ENDPOINT)

    @patch("discovery.github_request")
    def test_no_owner_skips_lookup(self, mock_gh):
        self.assertEqual(_repo_listing_endpoint("", "t"), discovery.USER_REPOS_ENDPOINT)
        mock_gh.assert_not_called()

    @patch("discovery.github_request")
    def test_end_to_end_org_discovery(self, mock_gh):
        def route(endpoint, access_token=None):
            if endpoint == "/users/acme":
                return {"type": "Organization"}
            if endpoint.startswith("/orgs/acme/repos?") and endpoint.endswith("&page=1"):
                return [{"full_name": "acme/api", "archived": False, "pushed_at": "2099-01-01T00:00:00Z"}]
            return []

        mock_gh.side_effect = route
        self.assertEqual(discover_repositories(owner="acme", access_token="t"), ["acme/api"])


if __name__ == "__main__":
    unittest.main()
