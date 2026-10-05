#!/usr/bin/env python3
"""Differential mutation testing runner for RunZero.

Detects modified Python files in src/ (staged, working tree, or branch diff against
main) and runs mutmut exclusively against those changed files. When no src/ Python
files have changed, it exits immediately with code 0 without wasting any compute.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

DEFAULT_DO_NOT_MUTATE = {
    "src/version.py",
    "src/drivers/orbstack_templates.py",
    "src/__init__.py",
    "src/dashboard/__init__.py",
    "src/drivers/__init__.py",
}


def get_git_diff_files(args: Sequence[str], cwd: Path = REPO_ROOT) -> list[str]:
    """Run git diff with the given arguments and return a list of file paths."""
    try:
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACM", *args]
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def resolve_base_ref(cwd: Path = REPO_ROOT) -> str | None:
    """Find a sensible base branch/commit to diff against."""
    candidates = ["origin/main", "main", "origin/develop", "develop", "HEAD~1"]
    for ref in candidates:
        res = subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return ref
    return None


def read_do_not_mutate_from_pyproject() -> set[str]:
    """Extract do_not_mutate file list from pyproject.toml."""
    if not PYPROJECT_PATH.is_file():
        return set(DEFAULT_DO_NOT_MUTATE)

    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r"do_not_mutate\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not match:
        return set(DEFAULT_DO_NOT_MUTATE)

    raw_items = match.group(1).split(",")
    excluded: set[str] = set()
    for item in raw_items:
        clean = item.strip().strip('"').strip("'")
        if clean:
            excluded.add(clean)
    return excluded.union(DEFAULT_DO_NOT_MUTATE)


def read_default_source_paths() -> list[str]:
    """Extract default source_paths from pyproject.toml."""
    if not PYPROJECT_PATH.is_file():
        return ["src/dashboard/state.py"]

    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r"source_paths\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not match:
        return ["src/dashboard/state.py"]

    raw_items = match.group(1).split(",")
    paths: list[str] = []
    for item in raw_items:
        clean = item.strip().strip('"').strip("'")
        if clean:
            paths.append(clean)
    return paths or ["src/dashboard/state.py"]


def filter_mutatable_files(files: Sequence[str], cwd: Path = REPO_ROOT) -> list[str]:
    """Filter raw file paths to existing mutatable Python files under src/."""
    excluded = read_do_not_mutate_from_pyproject()
    valid_files: list[str] = []
    seen: set[str] = set()

    for rel_path in files:
        norm = os.path.normpath(rel_path).replace("\\", "/")
        if not norm.startswith("src/"):
            continue
        if not norm.endswith(".py"):
            continue
        if norm in excluded:
            continue
        full_path = cwd / norm
        if full_path.is_file() and norm not in seen:
            seen.add(norm)
            valid_files.append(norm)

    return sorted(valid_files)


def detect_changed_source_files(
    *,
    cwd: Path = REPO_ROOT,
    base_ref: str | None = None,
    staged_only: bool = False,
    working_only: bool = False,
) -> list[str]:
    """Detect changed Python source files according to git status/diff."""
    if staged_only:
        raw_files = get_git_diff_files(["--cached"], cwd=cwd)
        return filter_mutatable_files(raw_files, cwd=cwd)

    if working_only:
        raw_files = get_git_diff_files([], cwd=cwd)
        return filter_mutatable_files(raw_files, cwd=cwd)

    # Default heuristic:
    # 1. Staged files
    staged = get_git_diff_files(["--cached"], cwd=cwd)
    # 2. Unstaged changes in working tree
    unstaged = get_git_diff_files([], cwd=cwd)

    combined = list(dict.fromkeys(staged + unstaged))
    mutatable = filter_mutatable_files(combined, cwd=cwd)
    if mutatable:
        return mutatable

    # 3. If working tree is clean, compare current branch to base_ref
    base = base_ref or resolve_base_ref(cwd=cwd)
    if base:
        branch_files = get_git_diff_files([f"{base}...HEAD"], cwd=cwd)
        mutatable = filter_mutatable_files(branch_files, cwd=cwd)
        if mutatable:
            return mutatable

    return []


class ScopedPyprojectMutmutConfig:
    """Context manager to temporarily override mutmut source_paths in pyproject.toml."""

    def __init__(self, target_files: list[str], pyproject_path: Path = PYPROJECT_PATH):
        self.target_files = target_files
        self.pyproject_path = pyproject_path
        self.original_content: str | None = None

    def __enter__(self) -> ScopedPyprojectMutmutConfig:
        if not self.pyproject_path.is_file():
            return self

        self.original_content = self.pyproject_path.read_text(encoding="utf-8")
        paths_str = ", ".join(f'"{f}"' for f in self.target_files)
        new_source_paths_line = f"source_paths = [{paths_str}]"

        modified = re.sub(
            r"source_paths\s*=\s*\[.*?\]",
            new_source_paths_line,
            self.original_content,
            flags=re.DOTALL,
        )

        self.pyproject_path.write_text(modified, encoding="utf-8")
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.restore()

    def restore(self) -> None:
        """Restore original pyproject.toml content."""
        if self.original_content is not None and self.pyproject_path.is_file():
            self.pyproject_path.write_text(self.original_content, encoding="utf-8")
            self.original_content = None


def run_mutation_on_files(target_files: list[str], cwd: Path = REPO_ROOT) -> int:
    """Execute mutmut run scoped strictly to target_files."""
    print(f"\033[1;36m🧬 [RunZero Mutation Testing] Targeting {len(target_files)} changed file(s):\033[0m")
    for f in target_files:
        print(f"   • {f}")
    print()

    scoped_config = ScopedPyprojectMutmutConfig(target_files, pyproject_path=cwd / "pyproject.toml")

    def handle_signal(_signum: int, _frame: object) -> None:
        scoped_config.restore()
        sys.exit(130)

    # Register traps for clean pyproject.toml restoration on interrupt
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    with scoped_config:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        src_path = str(cwd / "src")
        env["PYTHONPATH"] = f"{src_path}:{existing_pythonpath}" if existing_pythonpath else src_path

        py_bin = sys.executable

        run_cmd = [py_bin, "-m", "mutmut", "run"]
        print(f"\033[0;36m==> Running mutmut across {len(target_files)} file(s)...\033[0m")
        run_res = subprocess.run(run_cmd, cwd=cwd, env=env, check=False)

        results_cmd = [py_bin, "-m", "mutmut", "results"]
        subprocess.run(results_cmd, cwd=cwd, env=env, check=False)

        stats_cmd = [py_bin, "-m", "mutmut", "export-cicd-stats"]
        subprocess.run(stats_cmd, cwd=cwd, env=env, check=False)

        return run_res.returncode


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint for differential mutation testing."""
    parser = argparse.ArgumentParser(
        description="Run mutmut mutation testing locally on changed files only to save compute.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run mutation testing on all configured source_paths rather than only changes.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Target only git-staged Python files.",
    )
    parser.add_argument(
        "--working",
        action="store_true",
        help="Target only unstaged working-tree Python changes.",
    )
    parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Base git reference to diff against when working tree is clean.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Explicit file path(s) under src/ to mutate.",
    )

    args = parser.parse_args(argv)

    if args.files:
        targets = filter_mutatable_files(args.files)
    elif args.all:
        targets = read_default_source_paths()
    else:
        targets = detect_changed_source_files(
            base_ref=args.base,
            staged_only=args.staged,
            working_only=args.working,
        )

    if not targets:
        print("\033[1;32m⚡ [RunZero Mutation Testing] No modified Python source files found under src/.\033[0m")
        print("✓ Mutation testing skipped -- 0 compute minutes consumed.")
        return 0

    return run_mutation_on_files(targets)


if __name__ == "__main__":
    sys.exit(main())
