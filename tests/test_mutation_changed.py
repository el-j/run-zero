"""Unit tests for differential mutation testing runner (scripts/mutation_changed.py)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys_path_entry = str(REPO_ROOT / "scripts")
if sys_path_entry not in sys.path:
    sys.path.insert(0, sys_path_entry)

import mutation_changed  # noqa: E402


class TestDifferentialMutationRunner(unittest.TestCase):
    """Test suite for mutation_changed.py logic."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test-mut-changed-")
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_filter_mutatable_files_filters_non_src_and_excluded(self):
        src_dir = self.temp_path / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "valid_module.py").write_text("x = 1\n", encoding="utf-8")
        (src_dir / "version.py").write_text("VERSION = '1.0'\n", encoding="utf-8")
        (src_dir / "other.txt").write_text("text\n", encoding="utf-8")

        candidates = [
            "src/valid_module.py",
            "src/version.py",
            "src/other.txt",
            "tests/test_foo.py",
            "nonexistent/file.py",
        ]

        result = mutation_changed.filter_mutatable_files(candidates, cwd=self.temp_path)
        self.assertEqual(result, ["src/valid_module.py"])

    def test_read_do_not_mutate_from_pyproject_fallback_when_missing(self):
        with patch.object(mutation_changed, "PYPROJECT_PATH", self.temp_path / "nonexistent.toml"):
            excluded = mutation_changed.read_do_not_mutate_from_pyproject()
            self.assertTrue("src/version.py" in excluded)

    def test_read_default_source_paths_from_pyproject(self):
        dummy_toml = self.temp_path / "pyproject.toml"
        dummy_toml.write_text('source_paths = ["src/foo.py", "src/bar.py"]\n', encoding="utf-8")
        with patch.object(mutation_changed, "PYPROJECT_PATH", dummy_toml):
            paths = mutation_changed.read_default_source_paths()
            self.assertEqual(paths, ["src/foo.py", "src/bar.py"])

    def test_read_default_source_paths_fallback_when_missing(self):
        with patch.object(mutation_changed, "PYPROJECT_PATH", self.temp_path / "nonexistent.toml"):
            paths = mutation_changed.read_default_source_paths()
            self.assertEqual(paths, ["src/dashboard/state.py"])

    def test_scoped_pyproject_config_context_manager(self):
        dummy_toml = self.temp_path / "pyproject.toml"
        original = '[tool.mutmut]\nsource_paths = ["src/dashboard/state.py"]\nother = 123\n'
        dummy_toml.write_text(original, encoding="utf-8")

        with mutation_changed.ScopedPyprojectMutmutConfig(["src/reconciler.py"], pyproject_path=dummy_toml):
            modified = dummy_toml.read_text(encoding="utf-8")
            self.assertIn('source_paths = ["src/reconciler.py"]', modified)
            self.assertIn("other = 123", modified)

        restored = dummy_toml.read_text(encoding="utf-8")
        self.assertEqual(restored, original)

    def test_get_git_diff_files_handles_process_error(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            files = mutation_changed.get_git_diff_files(["--cached"], cwd=self.temp_path)
            self.assertEqual(files, [])

    def test_resolve_base_ref_finds_available_ref(self):
        def fake_run(cmd, **kwargs):
            ref = cmd[3]
            res = MagicMock()
            res.returncode = 0 if ref == "main" else 1
            return res

        with patch("subprocess.run", side_effect=fake_run):
            base = mutation_changed.resolve_base_ref(cwd=self.temp_path)
            self.assertEqual(base, "main")

    def test_resolve_base_ref_none_when_unresolved(self):
        res = MagicMock()
        res.returncode = 1
        with patch("subprocess.run", return_value=res):
            base = mutation_changed.resolve_base_ref(cwd=self.temp_path)
            self.assertIsNone(base)

    def test_detect_changed_source_files_staged_only(self):
        with (
            patch.object(mutation_changed, "get_git_diff_files", return_value=["src/foo.py"]),
            patch.object(mutation_changed, "filter_mutatable_files", return_value=["src/foo.py"]),
        ):
            res = mutation_changed.detect_changed_source_files(staged_only=True, cwd=self.temp_path)
            self.assertEqual(res, ["src/foo.py"])

    def test_detect_changed_source_files_working_only(self):
        with (
            patch.object(mutation_changed, "get_git_diff_files", return_value=["src/bar.py"]),
            patch.object(mutation_changed, "filter_mutatable_files", return_value=["src/bar.py"]),
        ):
            res = mutation_changed.detect_changed_source_files(working_only=True, cwd=self.temp_path)
            self.assertEqual(res, ["src/bar.py"])

    def test_detect_changed_source_files_falls_back_to_base_ref(self):
        def fake_diff(args, cwd):
            if args == ["--cached"] or args == []:
                return []
            if args == ["main...HEAD"]:
                return ["src/branch_mod.py"]
            return []

        with (
            patch.object(mutation_changed, "get_git_diff_files", side_effect=fake_diff),
            patch.object(mutation_changed, "filter_mutatable_files", side_effect=lambda files, cwd: files),
        ):
            res = mutation_changed.detect_changed_source_files(base_ref="main", cwd=self.temp_path)
            self.assertEqual(res, ["src/branch_mod.py"])

    def test_detect_changed_source_files_returns_empty_when_no_changes(self):
        with (
            patch.object(mutation_changed, "get_git_diff_files", return_value=[]),
            patch.object(mutation_changed, "resolve_base_ref", return_value=None),
        ):
            res = mutation_changed.detect_changed_source_files(cwd=self.temp_path)
            self.assertEqual(res, [])

    def test_run_mutation_on_files_invokes_mutmut(self):
        run_res = MagicMock()
        run_res.returncode = 0
        with patch("subprocess.run", return_value=run_res) as mock_run:
            ret = mutation_changed.run_mutation_on_files(["src/test.py"], cwd=self.temp_path)
            self.assertEqual(ret, 0)
            self.assertEqual(mock_run.call_count, 3)

    def test_main_cli_clean_returns_zero(self):
        with patch.object(mutation_changed, "detect_changed_source_files", return_value=[]):
            code = mutation_changed.main([])
            self.assertEqual(code, 0)

    def test_main_cli_files_flag(self):
        with (
            patch.object(mutation_changed, "filter_mutatable_files", return_value=["src/custom.py"]),
            patch.object(mutation_changed, "run_mutation_on_files", return_value=0) as mock_run,
        ):
            code = mutation_changed.main(["--files", "src/custom.py"])
            self.assertEqual(code, 0)
            mock_run.assert_called_once_with(["src/custom.py"])

    def test_main_cli_all_flag(self):
        with (
            patch.object(mutation_changed, "read_default_source_paths", return_value=["src/dashboard/state.py"]),
            patch.object(mutation_changed, "run_mutation_on_files", return_value=0) as mock_run,
        ):
            code = mutation_changed.main(["--all"])
            self.assertEqual(code, 0)
            mock_run.assert_called_once_with(["src/dashboard/state.py"])


if __name__ == "__main__":
    unittest.main()
