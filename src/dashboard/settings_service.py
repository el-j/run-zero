"""Live dynamic runtime settings service for the RunZero dashboard.

Provides real-time inspection and hot-reloading of configuration variables,
updating the running Config dataclass in memory and persisting updates to .env.
"""

from __future__ import annotations

import dataclasses
import os
import tempfile
from typing import Any

import arch_override
from config import ARCH_ALIASES, ARCHES, BACKENDS, Config, ConfigError


def get_live_settings(config: Config) -> dict[str, Any]:
    """Return JSON-serializable live runtime settings with secrets safely masked."""
    return {
        "access_token_configured": bool(config.access_token),
        "owner": config.owner,
        "org": config.org,
        "auto_discover": config.auto_discover,
        "active_days": config.active_days,
        "runner_backend": config.runner_backend,
        "auto_route_vm": config.auto_route_vm,
        "runner_arch": config.runner_arch,
        "min_runners": config.min_runners,
        "max_runners": config.max_runners,
        "poll_interval": config.poll_interval,
        "discovery_interval": config.discovery_interval,
        "proxies_enabled": config.proxies_enabled,
        "cache_enabled": config.cache_enabled,
        "host_cache_dir": config.host_cache_dir,
        "native_arch_override": config.native_arch_override,
    }


def _update_env_file(env_path: str, updates: dict[str, str]) -> None:
    """Atomically update or append key-value pairs in the specified .env file."""
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in updates.items():
                f.write(f"{k}={v}\n")
        return

    with open(env_path, encoding="utf-8") as f:
        lines = f.readlines()

    seen_keys: set[str] = set()
    new_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}\n")
                seen_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in updates.items():
        if k not in seen_keys:
            new_lines.append(f"{k}={v}\n")

    dir_name = os.path.dirname(os.path.abspath(env_path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".env_tmp_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    os.replace(tmp_path, env_path)


def _parse_runner_limits(body: dict[str, Any], current: Config) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse and validate MAX_RUNNERS and MIN_RUNNERS."""
    overrides: dict[str, Any] = {}
    env_updates: dict[str, str] = {}
    if "max_runners" in body:
        val = int(body["max_runners"])
        if val < 1:
            raise ConfigError("MAX_RUNNERS must be >= 1")
        overrides["max_runners"] = val
        env_updates["MAX_RUNNERS"] = str(val)

    if "min_runners" in body:
        val = int(body["min_runners"])
        if val < 0:
            raise ConfigError("MIN_RUNNERS must be >= 0")
        overrides["min_runners"] = val
        env_updates["MIN_RUNNERS"] = str(val)

    new_max = overrides.get("max_runners", current.max_runners)
    new_min = overrides.get("min_runners", current.min_runners)
    if new_min > new_max:
        raise ConfigError(f"MIN_RUNNERS={new_min} cannot exceed MAX_RUNNERS={new_max}")
    return overrides, env_updates


def _parse_intervals(body: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse and validate polling and discovery intervals."""
    overrides: dict[str, Any] = {}
    env_updates: dict[str, str] = {}
    if "poll_interval" in body:
        val = int(body["poll_interval"])
        if val < 1 or val > 3600:
            raise ConfigError("POLL_INTERVAL must be between 1 and 3600")
        overrides["poll_interval"] = val
        env_updates["POLL_INTERVAL"] = str(val)

    if "discovery_interval" in body:
        val = int(body["discovery_interval"])
        if val < 30 or val > 7200:
            raise ConfigError("DISCOVERY_INTERVAL must be between 30 and 7200")
        overrides["discovery_interval"] = val
        env_updates["DISCOVERY_INTERVAL"] = str(val)
    return overrides, env_updates


def _parse_engine_settings(body: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse and validate runner backend, architecture, and native override."""
    overrides: dict[str, Any] = {}
    env_updates: dict[str, str] = {}
    if "runner_backend" in body:
        backend = str(body["runner_backend"]).strip().lower()
        if backend not in BACKENDS:
            raise ConfigError(f"RUNNER_BACKEND must be one of: {', '.join(BACKENDS)}")
        overrides["runner_backend"] = backend
        env_updates["RUNNER_BACKEND"] = backend

    if "runner_arch" in body:
        arch = str(body["runner_arch"]).strip().lower()
        if arch not in ARCHES:
            raise ConfigError(f"RUNNER_ARCH must be one of: {', '.join(ARCHES)}")
        resolved = ARCH_ALIASES[arch]
        overrides["runner_arch"] = resolved
        env_updates["RUNNER_ARCH"] = resolved

    if "native_arch_override" in body:
        raw_override = str(body["native_arch_override"]).strip().lower()
        err = arch_override.validate(raw_override)
        if err:
            raise ConfigError(err)
        overrides["native_arch_override"] = raw_override
        env_updates["NATIVE_ARCH_OVERRIDE"] = raw_override
    return overrides, env_updates


def _parse_feature_toggles(body: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse and validate auth token, auto-route, caching, proxies, and host cache dir."""
    overrides: dict[str, Any] = {}
    env_updates: dict[str, str] = {}
    if body.get("access_token"):
        token = str(body["access_token"]).strip()
        overrides["access_token"] = token
        env_updates["ACCESS_TOKEN"] = token

    for key, env_key in (
        ("auto_route_vm", "AUTO_ROUTE_VM"),
        ("cache_enabled", "CACHE_ENABLED"),
        ("proxies_enabled", "PROXIES_ENABLED"),
    ):
        if key in body:
            b = bool(body[key])
            overrides[key] = b
            env_updates[env_key] = "true" if b else "false"

    if "host_cache_dir" in body:
        dir_val = str(body["host_cache_dir"]).strip()
        overrides["host_cache_dir"] = dir_val
        env_updates["HOST_CACHE_DIR"] = dir_val
    return overrides, env_updates


def update_live_settings(
    body: dict[str, Any],
    current: Config,
    env_path: str = ".env",
) -> tuple[Config, dict[str, Any]]:
    """Validate and apply live configuration mutations, writing updates to env_path."""
    overrides: dict[str, Any] = {}
    env_updates: dict[str, str] = {}

    for parser in (
        lambda: _parse_runner_limits(body, current),
        lambda: _parse_intervals(body),
        lambda: _parse_engine_settings(body),
        lambda: _parse_feature_toggles(body),
    ):
        p_overrides, p_env = parser()
        overrides.update(p_overrides)
        env_updates.update(p_env)

    updated_config = dataclasses.replace(current, **overrides)
    if env_updates:
        _update_env_file(env_path, env_updates)

    return updated_config, get_live_settings(updated_config)
