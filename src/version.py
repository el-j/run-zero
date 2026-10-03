"""
Dynamic Semantic Versioning for RunZero.
Resolved once at import, in this order:
- RUNZERO_VERSION env var, if set (CI and Docker builds pass it explicitly)
- main / master:              0.0.1            (stable release)
- develop:                    0.0.1-beta.1     (integration prerelease)
- feat/*, feature/*, fix/*:   0.0.1-alpha.<N>  (N = commit count on the branch)
- any other branch:           0.0.1-dev.<N>
- git unavailable (e.g. in an image without .git): bare 0.0.1
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
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()

        # Count commits on current branch
        count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()

        if branch in ("main", "master"):
            return BASE_VERSION
        elif branch == "develop":
            return f"{BASE_VERSION}-beta.1"
        elif branch.startswith(("feat/", "feature/", "fix/")):
            return f"{BASE_VERSION}-alpha.{count}"
        else:
            return f"{BASE_VERSION}-dev.{count}"
    except Exception:
        return BASE_VERSION


def get_git_sha() -> str:
    """Short git SHA of the running code: RUNZERO_GIT_SHA (baked into images at build), else git, else ""."""
    env_sha = (os.environ.get("RUNZERO_GIT_SHA") or "").strip()
    if env_sha:
        return env_sha[:12]
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""


__version__ = get_version()
__git_sha__ = get_git_sha()


def build_info() -> dict[str, str]:
    """This process's version and git SHA, as reported on /health and compared across processes."""
    return {"version": __version__, "git_sha": __git_sha__}


def version_drift(local: dict[str, str], remote: dict[str, str], remote_name: str = "bridge") -> str | None:
    """Describe why `remote` runs different code than `local`, or None if no drift is detectable.

    SHAs are authoritative when both sides know theirs. A remote that reports no version at
    all predates version reporting (#72) -- the stale-bridge case this exists to catch.
    """
    if not remote.get("version"):
        return f"The {remote_name} does not report its version, so it runs code older than this autoscaler. Restart it (`make bridge-start`)."
    local_sha, remote_sha = local.get("git_sha"), remote.get("git_sha")
    if local_sha and remote_sha and not (local_sha.startswith(remote_sha) or remote_sha.startswith(local_sha)):
        return (
            f"The {remote_name} runs {remote['version']} ({remote_sha}) but this autoscaler runs "
            f"{local.get('version')} ({local_sha}). Restart it (`make bridge-start`) after updating."
        )
    return None


if __name__ == "__main__":  # pragma: no cover -- CLI entrypoint guard, only runs via `python version.py`
    print(__version__)
