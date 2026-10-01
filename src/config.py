"""
Validated autoscaler configuration, loaded once from the environment.

Every setting is parsed with its type and allowed range, and a bad value fails fast with a
message naming the variable (``MAX_RUNNERS='four' is not an integer``) instead of a bare
``ValueError`` traceback at import time. Defaults here are the single source of truth;
`.env.example` and `docker-compose.yml` mirror them.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

_TRUE = ("true", "1", "yes", "on")
_FALSE = ("false", "0", "no", "off")

# Every alias drivers.get_driver() accepts.
BACKENDS = ("auto", "hybrid", "docker", "container", "orb", "orbstack", "orbstack-vm", "vm-orb", "wsl", "wsl2", "windows", "multipass", "canonical-multipass")
ARCHES = ("both", "arm64", "amd64", "x64", "x86_64", "aarch64")
ARCH_ALIASES = {
    "both": "both",
    "arm64": "arm64",
    "aarch64": "arm64",
    "amd64": "amd64",
    "x64": "amd64",
    "x86_64": "amd64",
}


class ConfigError(ValueError):
    """An environment variable holds a value the autoscaler cannot use."""


def _raw(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    return value.strip() if value is not None and value.strip() != "" else None


def _int(env: Mapping[str, str], name: str, default: int, minimum: int, maximum: int | None = None) -> int:
    raw = _raw(env, name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(f"{name}={raw!r} is not an integer") from None
    if value < minimum or (maximum is not None and value > maximum):
        bound = f">= {minimum}" if maximum is None else f"between {minimum} and {maximum}"
        raise ConfigError(f"{name}={value} must be {bound}")
    return value


def _bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    raw = _raw(env, name)
    if raw is None:
        return default
    if raw.lower() in _TRUE:
        return True
    if raw.lower() in _FALSE:
        return False
    raise ConfigError(f"{name}={raw!r} is not a boolean (use true/false)")


def _choice(env: Mapping[str, str], name: str, default: str, choices: tuple[str, ...]) -> str:
    raw = _raw(env, name)
    if raw is None:
        return default
    value = raw.lower()
    if value not in choices:
        raise ConfigError(f"{name}={raw!r} must be one of: {', '.join(choices)}")
    return value


@dataclass(frozen=True)
class Config:
    """Every setting the autoscaler reads, typed and range-checked."""

    access_token: str | None = None
    owner: str = ""
    org: str = ""
    repos_config: str = ""
    auto_discover: bool = True
    active_days: int = 60
    discovery_interval: int = 900
    runner_backend: str = "auto"
    auto_route_vm: bool = True
    runner_arch: str = "both"
    proxies_enabled: bool = True
    cache_enabled: bool = True
    host_cache_dir: str = ""
    min_runners: int = 0
    max_runners: int = 4
    poll_interval: int = 10
    rate_limit_refresh_interval: int = 60
    actions_billing_refresh_interval: int = 300
    busy_timeout_seconds: int = 7200
    dashboard_enabled: bool = True
    dashboard_port: int = 49505
    dashboard_host: str = "127.0.0.1"


def load_config(env: Mapping[str, str] | None = None) -> Config:
    """Parse and validate the autoscaler configuration from `env` (default: os.environ).

    Raises ConfigError naming the first invalid variable.
    """
    env = os.environ if env is None else env
    config = Config(
        access_token=_raw(env, "ACCESS_TOKEN") or _raw(env, "GITHUB_TOKEN"),
        owner=_raw(env, "OWNER") or "",
        org=_raw(env, "ORG") or "",
        repos_config=_raw(env, "REPOS") or _raw(env, "REPO") or "",
        auto_discover=_bool(env, "AUTO_DISCOVER_REPOS", True),
        active_days=_int(env, "ACTIVE_REPO_DAYS", 60, 1),
        discovery_interval=_int(env, "DISCOVERY_INTERVAL", 900, 60),
        runner_backend=_choice(env, "RUNNER_BACKEND", "auto", BACKENDS),
        auto_route_vm=_bool(env, "AUTO_ROUTE_VM", True),
        runner_arch=ARCH_ALIASES[_choice(env, "RUNNER_ARCH", "both", ARCHES)],
        proxies_enabled=_bool(env, "PROXIES_ENABLED", True),
        cache_enabled=_bool(env, "CACHE_ENABLED", True),
        host_cache_dir=_raw(env, "HOST_CACHE_DIR") or "",
        min_runners=_int(env, "MIN_RUNNERS", 0, 0),
        max_runners=_int(env, "MAX_RUNNERS", 4, 1),
        poll_interval=_int(env, "POLL_INTERVAL", 10, 1, 3600),
        rate_limit_refresh_interval=_int(env, "RATE_LIMIT_REFRESH_INTERVAL", 60, 10),
        actions_billing_refresh_interval=_int(env, "ACTIONS_BILLING_REFRESH_INTERVAL", 300, 30),
        busy_timeout_seconds=_int(env, "RUNNER_BUSY_TIMEOUT_SECONDS", 7200, 60),
        dashboard_enabled=_bool(env, "DASHBOARD_ENABLED", True),
        dashboard_port=_int(env, "DASHBOARD_PORT", 49505, 1, 65535),
        dashboard_host=_raw(env, "DASHBOARD_HOST") or "127.0.0.1",
    )
    if config.min_runners > config.max_runners:
        raise ConfigError(f"MIN_RUNNERS={config.min_runners} cannot exceed MAX_RUNNERS={config.max_runners}")
    return config
