"""
Unit tests for RepoPriorityManager and parse_repo_priority_env.
"""

import json
import os
import tempfile
import unittest

from repo_priority import RepoPriorityManager, parse_repo_priority_env


class TestParseRepoPriorityEnv(unittest.TestCase):
    """Tests for parse_repo_priority_env helper."""

    def test_empty_or_none(self):
        self.assertEqual(parse_repo_priority_env(None), [])
        self.assertEqual(parse_repo_priority_env(""), [])
        self.assertEqual(parse_repo_priority_env("   "), [])

    def test_single_and_comma_separated(self):
        self.assertEqual(parse_repo_priority_env("el-j/run-zero"), ["el-j/run-zero"])
        self.assertEqual(
            parse_repo_priority_env("el-j/run-zero, el-j/herbful,  el-j/api "),
            ["el-j/run-zero", "el-j/herbful", "el-j/api"],
        )

    def test_deduplicates_and_ignores_empty_chunks(self):
        self.assertEqual(
            parse_repo_priority_env("repo-a, , repo-b, repo-a, repo-c,"),
            ["repo-a", "repo-b", "repo-c"],
        )


class TestRepoPriorityManager(unittest.TestCase):
    """Tests for RepoPriorityManager."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, "repo-priority.json")

    def tearDown(self):
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_defaults_empty(self):
        mgr = RepoPriorityManager(state_file=self.state_file)
        self.assertEqual(mgr.get_state(), {"priority": [], "paused": []})
        self.assertFalse(mgr.is_paused("el-j/run-zero"))

    def test_initial_values_persisted_when_nonempty(self):
        mgr = RepoPriorityManager(
            state_file=self.state_file,
            initial_priority=["repo-b", "repo-a"],
            initial_paused=["repo-c"],
        )
        self.assertTrue(os.path.isfile(self.state_file))
        self.assertEqual(mgr.get_state(), {"priority": ["repo-b", "repo-a"], "paused": ["repo-c"]})
        self.assertTrue(mgr.is_paused("repo-c"))
        self.assertFalse(mgr.is_paused("repo-a"))

    def test_loads_existing_state_file(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump({"priority": ["p1", "p2"], "paused": ["p3"]}, f)
        mgr = RepoPriorityManager(state_file=self.state_file)
        self.assertEqual(mgr.get_state(), {"priority": ["p1", "p2"], "paused": ["p3"]})
        self.assertTrue(mgr.is_paused("p3"))

    def test_loads_corrupt_or_invalid_file_gracefully(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            f.write("not json")
        mgr = RepoPriorityManager(state_file=self.state_file, initial_priority=["fallback"])
        self.assertEqual(mgr.get_state(), {"priority": ["fallback"], "paused": []})

    def test_get_priority_list_orders_known_first_preserves_others(self):
        mgr = RepoPriorityManager(
            state_file=self.state_file,
            initial_priority=["high-priority", "mid-priority"],
        )
        tracked = ["other-1", "mid-priority", "other-2", "high-priority"]
        ordered = mgr.get_priority_list(tracked)
        self.assertEqual(ordered, ["high-priority", "mid-priority", "other-1", "other-2"])

    def test_set_priority_updates_and_persists(self):
        mgr = RepoPriorityManager(state_file=self.state_file)
        mgr.set_priority(["repo-x", "repo-y", " repo-x "])
        self.assertEqual(mgr.get_state()["priority"], ["repo-x", "repo-y"])

        # Reload from disk
        mgr2 = RepoPriorityManager(state_file=self.state_file)
        self.assertEqual(mgr2.get_state()["priority"], ["repo-x", "repo-y"])

    def test_set_paused_toggles_and_persists(self):
        mgr = RepoPriorityManager(state_file=self.state_file)
        mgr.set_paused("repo-1", True)
        self.assertTrue(mgr.is_paused("repo-1"))
        mgr.set_paused("repo-1", False)
        self.assertFalse(mgr.is_paused("repo-1"))

        # Empty repo string is ignored
        mgr.set_paused("   ", True)
        self.assertEqual(mgr.get_state()["paused"], [])

    def test_update_both(self):
        mgr = RepoPriorityManager(state_file=self.state_file)
        mgr.update(priority=["p1", "p2"], paused=["p2"])
        self.assertEqual(mgr.get_state(), {"priority": ["p1", "p2"], "paused": ["p2"]})
        self.assertTrue(mgr.is_paused("p2"))
        self.assertFalse(mgr.is_paused("p1"))

    def test_save_error_cleans_up_temp_file(self):
        from unittest.mock import patch

        mgr = RepoPriorityManager(state_file=self.state_file)
        with patch("os.replace", side_effect=OSError("disk error")), self.assertRaises(OSError):
            mgr.set_priority(["repo-err"])
