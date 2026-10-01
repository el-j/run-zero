"""
Regression tests for scripts/pre-commit.sh re-staging behaviour (#39).

The old hook ran `git add -u` after auto-fixing, which silently swept every
unstaged edit in the working tree -- including unrelated work-in-progress --
into the commit. The rewritten hook must only re-stage files it auto-fixed AND
that had no unstaged edits of their own.

Each test builds a throwaway git repo, copies the real hook into it, and runs
it with RUNZERO_PY pointed at this interpreter (which must have ruff + flake8,
as `make check` / CI guarantee) and tests skipped, so only staging is exercised.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOK = os.path.join(REPO_ROOT, "scripts", "pre-commit.sh")

# Lint-clean once `ruff format` has normalised the quotes.
UNFORMATTED = "x = 'a'\n"
FORMATTED = 'x = "a"\n'


def _tooling_available() -> bool:
    for module in ("ruff", "flake8"):
        res = subprocess.run([sys.executable, "-m", module, "--version"], capture_output=True, check=False)
        if res.returncode != 0:
            return False
    return shutil.which("git") is not None


@unittest.skipUnless(_tooling_available(), "ruff/flake8/git not available to this interpreter")
class TestPreCommitRestaging(unittest.TestCase):
    """Drives the real hook inside an isolated git repository."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="runzero-precommit-")
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "test")
        self._git("config", "commit.gpgsign", "false")
        os.makedirs(os.path.join(self.repo, "scripts"))
        shutil.copy(HOOK, os.path.join(self.repo, "scripts", "pre-commit.sh"))
        for name in ("pyproject.toml", "setup.cfg"):
            shutil.copy(os.path.join(REPO_ROOT, name), os.path.join(self.repo, name))
        self._write("lib.py", FORMATTED)
        self._write("other.py", FORMATTED)
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "init", "--no-verify")

    def _git(self, *args: str) -> str:
        res = subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True)
        return res.stdout

    def _write(self, name: str, content: str) -> None:
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as fh:
            fh.write(content)

    def _run_hook(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "RUNZERO_PY": sys.executable, "RUNZERO_PRECOMMIT_SKIP_TESTS": "1"}
        return subprocess.run(["bash", "scripts/pre-commit.sh"], cwd=self.repo, env=env, capture_output=True, text=True, check=False)

    def _staged(self, name: str) -> str:
        return self._git("show", f":{name}")

    def test_fully_staged_file_is_fixed_and_restaged(self):
        self._write("lib.py", UNFORMATTED)
        self._git("add", "lib.py")

        res = self._run_hook()

        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(self._staged("lib.py"), FORMATTED)
        self.assertEqual(self._git("diff", "--name-only"), "")

    def test_unrelated_unstaged_edit_is_never_swept_into_the_commit(self):
        self._write("lib.py", UNFORMATTED)
        self._git("add", "lib.py")
        self._write("other.py", FORMATTED + "y = 1\n")

        res = self._run_hook()

        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(self._staged("other.py"), FORMATTED)
        self.assertEqual(self._git("diff", "--name-only").split(), ["other.py"])

    def test_partially_staged_file_is_not_rewritten_or_restaged(self):
        self._write("lib.py", FORMATTED + "y = 1\n")
        self._git("add", "lib.py")
        self._write("lib.py", FORMATTED + "y = 1\nz = 'wip'\n")

        res = self._run_hook()

        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("Not auto-fixed", res.stdout)
        self.assertEqual(self._staged("lib.py"), FORMATTED + "y = 1\n")
        with open(os.path.join(self.repo, "lib.py"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), FORMATTED + "y = 1\nz = 'wip'\n")

    def test_partially_staged_file_is_gated_on_its_staged_content(self):
        # Staged blob is unformatted; the working tree happens to be clean. The hook
        # must judge what is being committed, so this has to fail.
        self._write("lib.py", UNFORMATTED)
        self._git("add", "lib.py")
        self._write("lib.py", FORMATTED)

        res = self._run_hook()

        self.assertNotEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(self._staged("lib.py"), UNFORMATTED)

    def test_missing_tooling_fails_hard(self):
        env = {**os.environ, "RUNZERO_PY": "/nonexistent/python", "RUNZERO_PRECOMMIT_SKIP_TESTS": "1"}
        res = subprocess.run(["bash", "scripts/pre-commit.sh"], cwd=self.repo, env=env, capture_output=True, text=True, check=False)

        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Dev tooling not found", res.stdout)


if __name__ == "__main__":
    unittest.main()
