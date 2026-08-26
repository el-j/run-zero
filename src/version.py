"""
Dynamic Semantic Versioning for RunZero.
Automatically determines version based on current git branch, tags, and environment:
- main: 0.0.1 (Stable release)
- develop: 0.0.1-beta.1 (Integration prerelease)
- feat/*: 0.0.1-alpha.x (Feature branch snapshot)
"""

import os
import subprocess

BASE_VERSION = "0.0.1"


def get_version() -> str:
    """Resolve the running version: RUNZERO_VERSION env var if set, else derived from the git branch.

    Falls back to bare BASE_VERSION if git isn't available or any git call fails (e.g. not a repo,
    such as inside a built container image without a .git directory).
    """
    # Check if RUNZERO_VERSION is explicitly passed (e.g., in CI or Docker build)
    env_ver = os.environ.get("RUNZERO_VERSION")
    if env_ver:
        return env_ver.strip()

    try:
        # Resolve current git branch name
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Count commits on current branch
        count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        if branch in ("main", "master"):
            return BASE_VERSION
        elif branch == "develop":
            return f"{BASE_VERSION}-beta.1"
        elif branch.startswith("feat/") or branch.startswith("feature/") or branch.startswith("fix/"):
            return f"{BASE_VERSION}-alpha.{count}"
        else:
            return f"{BASE_VERSION}-dev.{count}"
    except Exception:
        return BASE_VERSION


__version__ = get_version()

if __name__ == "__main__":  # pragma: no cover -- CLI entrypoint guard, only runs via `python version.py`
    print(__version__)
