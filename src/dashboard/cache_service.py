"""Cache inspection and purging service for the RunZero dashboard.

Provides structured disk usage telemetry across toolchains, package managers,
and test sandboxes, with selective or total eviction controls.
"""

from __future__ import annotations

import os
import shutil
from typing import Any

CACHE_DIRECTORY_MAPPING: dict[str, str] = {
    "hostedtoolcache": "hostedtoolcache",
    "pnpm": "pnpm",
    "npm": "npm",
    "yarn": "yarn",
    "pip": "pip",
    "uv": "uv",
    "go-build": "build-cache",
    "go-pkg": "go-pkg",
    "cargo": "rust",
    "playwright": "ms-playwright",
}


def _format_size(size_bytes: int) -> str:
    """Format bytes into a human-readable metric string."""
    units = ["B", "KB", "MB", "GB", "TB"]
    sz = float(size_bytes)
    for u in units[:-1]:
        if sz < 1024:
            return f"{sz:.1f} {u}" if u != "B" else f"{int(sz)} B"
        sz /= 1024.0
    return f"{sz:.1f} TB"


def _get_path_size(path: str) -> int:
    """Recursively calculate the total byte size of a directory or file."""
    if not os.path.exists(path):
        return 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    try:
        for entry in os.scandir(path):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += _get_path_size(entry.path)
            except OSError:
                continue
    except OSError:
        pass
    return total


def get_cache_stats(cache_root: str) -> dict[str, Any]:
    """Inspect and return categorized disk space statistics under `cache_root`."""
    total_bytes = 0
    categories: list[dict[str, Any]] = []

    if not cache_root or not os.path.isdir(cache_root):
        return {
            "total_bytes": 0,
            "total_human": "0 B",
            "categories": [{"category": cat, "bytes": 0, "human_readable": "0 B"} for cat in CACHE_DIRECTORY_MAPPING],
        }

    for cat_name, sub_path in CACHE_DIRECTORY_MAPPING.items():
        full_path = os.path.join(cache_root, sub_path)
        sz = _get_path_size(full_path)
        total_bytes += sz
        categories.append(
            {
                "category": cat_name,
                "bytes": sz,
                "human_readable": _format_size(sz),
            }
        )

    return {
        "total_bytes": total_bytes,
        "total_human": _format_size(total_bytes),
        "categories": categories,
    }


def purge_cache(
    cache_root: str,
    category: str | None = None,
    repo: str | None = None,
    all_caches: bool = False,
) -> dict[str, Any]:
    """Purge categorized cache directories or the entire host cache directory."""
    if not cache_root or not os.path.isdir(cache_root):
        return {"status": "success", "cleared": []}

    cleared: list[str] = []

    if all_caches or category in ("all", "*"):
        for cat_name, sub_path in CACHE_DIRECTORY_MAPPING.items():
            full_path = os.path.join(cache_root, sub_path)
            if os.path.exists(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
                os.makedirs(full_path, exist_ok=True)
                cleared.append(cat_name)
    elif category:
        cat_key = category.lower().strip()
        target_sub = CACHE_DIRECTORY_MAPPING.get(cat_key)
        if target_sub is not None:
            full_path = os.path.join(cache_root, target_sub)
            if os.path.exists(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
                os.makedirs(full_path, exist_ok=True)
                cleared.append(category)

    return {"status": "success", "cleared": cleared}
