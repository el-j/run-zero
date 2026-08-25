"""
Host cache directory initialization and mount mapping manager.
"""

import os
from typing import Dict


def init_cache_dirs(host_cache_dir: str, arch: str, cache_enabled: bool = True) -> Dict[str, str]:
    """Ensure host cache directories exist with strict permissions and return volume mounts."""
    if not cache_enabled or not host_cache_dir:
        return {}

    subdirs = [
        "npm", "pnpm", "yarn", "pip", "uv", "go-pkg", "go-build",
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

    mount_mappings = {
        os.path.join(host_cache_dir, "npm"): "/home/runner/.npm",
        os.path.join(host_cache_dir, "pnpm"): "/home/runner/.local/share/pnpm/store",
        os.path.join(host_cache_dir, "yarn"): "/home/runner/.cache/yarn",
        os.path.join(host_cache_dir, "pip"): "/home/runner/.cache/pip",
        os.path.join(host_cache_dir, "uv"): "/home/runner/.cache/uv",
        os.path.join(host_cache_dir, "go-pkg"): "/home/runner/go/pkg",
        os.path.join(host_cache_dir, "go-build"): "/home/runner/.cache/go-build",
        os.path.join(host_cache_dir, "dotnet"): "/home/runner/.nuget/packages",
        os.path.join(host_cache_dir, "rust"): "/home/runner/.cargo/registry",
        arch_toolcache: "/opt/hostedtoolcache",
    }
    return mount_mappings
