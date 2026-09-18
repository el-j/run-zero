"""
Host cache directory initialization and mount mapping manager.
"""

import os
import shutil
from typing import Dict


def _sanitize_scope(scope: str) -> str:
    """Sanitize scope string to a safe directory name."""
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in scope).strip("_")


def clean_build_cache(host_cache_dir: str, scope: str = "") -> None:
    """Clean the build cache directory on host to remove corrupted files or stale locks."""
    if not host_cache_dir:
        return
    if scope:
        safe_scope = _sanitize_scope(scope)
        target_dir = os.path.join(host_cache_dir, "build-cache", safe_scope, "go-build")
    else:
        target_dir = os.path.join(host_cache_dir, "go-build")

    if os.path.exists(target_dir):
        try:
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    try:
                        os.remove(item_path)
                    except OSError:
                        pass
        except OSError:
            pass
    os.makedirs(target_dir, exist_ok=True)
    try:
        os.chmod(target_dir, 0o777)
    except OSError:
        pass


def init_cache_dirs(
    host_cache_dir: str,
    arch: str,
    cache_enabled: bool = True,
    scope: str = "",
) -> Dict[str, str]:
    """Ensure host cache directories exist with strict permissions and return volume mounts.

    `scope` isolates mutable compilation build caches (such as `go-build`) per workflow/job
    so independent concurrent workflows never collide or lock the same build cache directory,
    while shared package download caches (npm, pip, go-pkg, toolcache) remain shared.
    """
    if not cache_enabled or not host_cache_dir:
        return {}

    subdirs = [
        "npm", "pnpm", "yarn", "pip", "uv", "go-pkg",
        "dotnet", "rust", "hostedtoolcache", "apt"
    ]

    for sub in subdirs:
        p = os.path.join(host_cache_dir, sub)
        os.makedirs(p, exist_ok=True)
        try:
            os.chmod(p, 0o777)
        except OSError:
            pass

    arch_toolcache = os.path.join(host_cache_dir, "hostedtoolcache", arch)
    os.makedirs(arch_toolcache, exist_ok=True)
    try:
        os.chmod(arch_toolcache, 0o777)
    except OSError:
        pass

    # Build cache isolation:
    # If scope is provided, place go-build under build-cache/<scope>/go-build so concurrent
    # builds from independent workflows/jobs do not collide or lock the same directory.
    if scope:
        safe_scope = _sanitize_scope(scope)
        go_build_dir = os.path.join(host_cache_dir, "build-cache", safe_scope, "go-build")
    else:
        go_build_dir = os.path.join(host_cache_dir, "go-build")

    os.makedirs(go_build_dir, exist_ok=True)
    try:
        os.chmod(go_build_dir, 0o777)
    except OSError:
        pass

    mount_mappings = {
        os.path.join(host_cache_dir, "npm"): "/home/runner/.npm",
        os.path.join(host_cache_dir, "pnpm"): "/home/runner/.local/share/pnpm/store",
        os.path.join(host_cache_dir, "yarn"): "/home/runner/.cache/yarn",
        os.path.join(host_cache_dir, "pip"): "/home/runner/.cache/pip",
        os.path.join(host_cache_dir, "uv"): "/home/runner/.cache/uv",
        os.path.join(host_cache_dir, "go-pkg"): "/home/runner/go/pkg",
        go_build_dir: "/home/runner/.cache/go-build",
        os.path.join(host_cache_dir, "dotnet"): "/home/runner/.nuget/packages",
        os.path.join(host_cache_dir, "rust"): "/home/runner/.cargo/registry",
        arch_toolcache: "/opt/hostedtoolcache",
    }
    return mount_mappings
