"""
Host cache directory initialization and mount mapping manager.
"""

import contextlib
import os

from drivers.runner_env import PLAYWRIGHT_BROWSERS, PNPM_STORE, TOOL_CACHE


def _sanitize_scope(scope: str) -> str:
    """Sanitize scope string to a safe directory name."""
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in scope).strip("_")


def _make_arch_dir(host_cache_dir: str, name: str, arch: str) -> str:
    """Create the world-writable per-arch cache directory `<host_cache_dir>/<name>/<arch>`."""
    path = os.path.join(host_cache_dir, name, arch)
    os.makedirs(path, exist_ok=True)
    for p in (os.path.dirname(path), path):
        with contextlib.suppress(OSError):
            os.chmod(p, 0o777)
    return path


def init_cache_dirs(
    host_cache_dir: str,
    arch: str,
    cache_enabled: bool = True,
    scope: str = "",
) -> dict[str, str]:
    """Ensure host cache directories exist and return host-path -> runner-path volume mounts.

    Directories are made world-writable (0o777) on purpose: they are bind-mounted into
    containers and VMs whose `runner` user has a different uid than the host user that
    owns them, and the runner must be able to write its package caches. This is a shared,
    trusted cache -- see SECURITY.md ("Proxy caches") for the implications.

    `scope` isolates mutable compilation build caches (such as `go-build`) per workflow/job
    so independent concurrent workflows never collide or lock the same build cache directory,
    while shared package download caches (npm, pip, go-pkg, toolcache) remain shared.
    """
    if not cache_enabled or not host_cache_dir:
        return {}

    # apt is deliberately absent: .deb caching goes through the apt-cacher-ng proxy, not a mount.
    subdirs = ["npm", "pnpm", "yarn", "pip", "uv", "go-pkg", "dotnet", "rust", "hostedtoolcache"]

    for sub in subdirs:
        p = os.path.join(host_cache_dir, sub)
        os.makedirs(p, exist_ok=True)
        with contextlib.suppress(OSError):
            os.chmod(p, 0o777)

    # Per-arch: tool cache entries and Playwright browsers are native binaries.
    arch_toolcache = _make_arch_dir(host_cache_dir, "hostedtoolcache", arch)
    arch_playwright = _make_arch_dir(host_cache_dir, "ms-playwright", arch)

    # Build cache isolation:
    # If scope is provided, place go-build under build-cache/<scope>/go-build so concurrent
    # builds from independent workflows/jobs do not collide or lock the same directory.
    if scope:
        safe_scope = _sanitize_scope(scope)
        go_build_dir = os.path.join(host_cache_dir, "build-cache", safe_scope, "go-build")
    else:
        go_build_dir = os.path.join(host_cache_dir, "go-build")

    os.makedirs(go_build_dir, exist_ok=True)
    with contextlib.suppress(OSError):
        os.chmod(go_build_dir, 0o777)

    mount_mappings = {
        os.path.join(host_cache_dir, "npm"): "/home/runner/.npm",
        os.path.join(host_cache_dir, "pnpm"): PNPM_STORE,
        os.path.join(host_cache_dir, "yarn"): "/home/runner/.cache/yarn",
        os.path.join(host_cache_dir, "pip"): "/home/runner/.cache/pip",
        os.path.join(host_cache_dir, "uv"): "/home/runner/.cache/uv",
        os.path.join(host_cache_dir, "go-pkg"): "/home/runner/go/pkg",
        go_build_dir: "/home/runner/.cache/go-build",
        os.path.join(host_cache_dir, "dotnet"): "/home/runner/.nuget/packages",
        os.path.join(host_cache_dir, "rust"): "/home/runner/.cargo/registry",
        arch_toolcache: TOOL_CACHE,
        arch_playwright: PLAYWRIGHT_BROWSERS,
    }
    return mount_mappings
