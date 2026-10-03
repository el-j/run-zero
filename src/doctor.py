"""
`make doctor` / `runzero doctor`: verify the cache wiring from inside a fresh runner (#73).

Every cache fix in el-j/run-zero#76 was found by hand, from inside a live job. This does
the same in a minute and without a GitHub token: it checks the host side (proxies, cache
directories, load, sizing, bridge/autoscaler versions), then starts a throwaway runner per
backend -- a `docker run --rm` of the runner image, or an OrbStack clone of the golden image
-- with exactly the environment and mounts a job gets, and asks the tools what they resolve.

Exit status is 1 when any check fails, so it can gate scripts and CI.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from arch_override import normalize_host_arch
from cache_manager import init_cache_dirs
from dashboard.state import cache_categories
from drivers.runner_env import PLAYWRIGHT_BROWSERS, PNPM_STORE, TOOL_CACHE, cache_env, export_block
from drivers.sizing import orbstack_capacity, resolve_sizing
from version import build_info, version_drift

OK, WARN, FAIL, SKIP = "ok", "warn", "fail", "skip"

# Host-published proxy health endpoints (docker-compose.yml).
PROXIES = {
    "verdaccio (npm/pnpm/yarn)": "http://127.0.0.1:49501/-/ping",
    "apt-cacher-ng": "http://127.0.0.1:49503/acng-report.html",
    "athens (Go)": "http://127.0.0.1:49500/healthz",
    "docker-mirror": "http://127.0.0.1:49502/v2/",
    "devpi (pip/uv)": "http://127.0.0.1:49507/+api",
    "kellnr (cargo)": "http://127.0.0.1:49506/",
}
SLOW_PROXY_SECONDS = 1.0

# Runs inside the runner as a login shell (nvm's node/pnpm on PATH), prints KEY=VALUE lines.
PROBE_SCRIPT = r"""
cd /tmp
p() { printf '%s=%s\n' "$1" "$2"; }
mounted() { mountpoint -q "$1" 2>/dev/null && echo 1 || echo 0; }
p RUNZERO "${RUNZERO:-}"
p RUNNER_TOOL_CACHE "${RUNNER_TOOL_CACHE:-}"
p TOOLCACHE_MOUNTED "$(mounted /opt/hostedtoolcache)"
p PLAYWRIGHT_BROWSERS_PATH "${PLAYWRIGHT_BROWSERS_PATH:-}"
p PLAYWRIGHT_MOUNTED "$(mounted "${PLAYWRIGHT_BROWSERS_PATH:-/nonexistent}")"
p EXPECTED_REGISTRY "${npm_config_registry:-}"
p NPM_REGISTRY "$(npm config get registry 2>/dev/null)"
p YARN_REGISTRY "$(yarn config get registry 2>/dev/null)"
for v in 10 11; do
  p "PNPM${v}_REGISTRY" "$(npx -y "pnpm@${v}" config get registry 2>/dev/null)"
  p "PNPM${v}_STORE" "$(npx -y "pnpm@${v}" config get store-dir 2>/dev/null)"
done
p REGISTRY_SECONDS "$(curl -fsS -o /dev/null -m 10 -w '%{time_total}' "${npm_config_registry:-http://invalid.invalid}" 2>/dev/null)"
"""


@dataclass(frozen=True)
class Check:
    """One line of the doctor report."""

    name: str
    status: str
    detail: str = ""


# -- host checks ------------------------------------------------------------------------


def _http_get(url: str, timeout: float = 3.0) -> tuple[bool, float, bytes]:
    """(reachable, seconds, body) for a GET of `url`; any HTTP status counts as reachable."""
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read()
        return True, time.monotonic() - start, body
    except urllib.error.HTTPError as e:
        return True, time.monotonic() - start, e.read() if e.fp else b""
    except (urllib.error.URLError, OSError, ValueError):
        return False, time.monotonic() - start, b""


def check_proxies(proxies_enabled: bool, get: Callable[[str], tuple[bool, float, bytes]] | None = None) -> list[Check]:
    """Each caching proxy answers, and fast enough not to be the bottleneck."""
    get = get or _http_get
    if not proxies_enabled:
        return [Check("proxies", SKIP, "PROXIES_ENABLED=false")]
    checks = []
    for name, url in PROXIES.items():
        reachable, seconds, _ = get(url)
        if not reachable:
            checks.append(Check(f"proxy {name}", FAIL, f"unreachable at {url} (`make start`?)"))
        elif seconds > SLOW_PROXY_SECONDS:
            checks.append(Check(f"proxy {name}", WARN, f"slow: {seconds * 1000:.0f} ms"))
        else:
            checks.append(Check(f"proxy {name}", OK, f"{seconds * 1000:.0f} ms"))
    return checks


def _dir_bytes(path: str) -> int:
    """Total size of the regular files under `path` (0 if missing)."""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            if not os.path.islink(fp):
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    continue
    return total


def check_cache_dir(cache_dir: str, cache_enabled: bool, size_of: Callable[[str], int] = _dir_bytes) -> list[Check]:
    """The host cache directory exists, with each category's size (an empty one never got a hit)."""
    if not cache_enabled:
        return [Check("host cache", SKIP, "CACHE_ENABLED=false")]
    if not cache_dir or not os.path.isdir(cache_dir):
        return [Check("host cache", FAIL, f"HOST_CACHE_DIR {cache_dir!r} does not exist (`make init-cache`)")]
    checks = [Check("host cache", OK, cache_dir)]
    for name, path in cache_categories(cache_dir).items():
        size = size_of(path) if os.path.isdir(path) else 0
        checks.append(Check(f"cache {name}", OK if size else WARN, f"{size / 2**20:.0f} MiB" if size else "empty"))
    return checks


def check_load(loadavg: Callable[[], tuple[float, float, float]] = os.getloadavg, cpus: int | None = None) -> Check:
    """The host isn't already oversubscribed (1-minute load above the core count)."""
    cpus = cpus or os.cpu_count() or 1
    load = loadavg()[0]
    status = WARN if load > cpus else OK
    return Check("host load", status, f"1-min load {load:.1f} on {cpus} CPUs")


def check_sizing(env: dict[str, str], backend: str) -> list[Check]:
    """Per-runner CPU/memory sizing, flagged when MAX_RUNNERS x size exceeds the host (#71)."""
    sizing = resolve_sizing(env, orbstack_capacity if backend == "orbstack-vm" else None)
    checks = [Check("runner sizing", OK, sizing.describe())]
    checks.extend(Check("runner sizing", WARN, w) for w in sizing.warnings)
    return checks


def check_versions(bridge_url: str, dashboard_url: str, get: Callable[[str], tuple[bool, float, bytes]] | None = None) -> list[Check]:
    """The bridge and the autoscaler run the code of this checkout (#72)."""
    # /health enumerates every driver, and a hung `docker info` alone takes its 5s timeout.
    get = get or (lambda url: _http_get(url, timeout=10.0))
    local = build_info()
    checks = []
    for name, url in (("Host VM Bridge", f"{bridge_url}/health"), ("autoscaler", f"{dashboard_url}/api/status")):
        reachable, _, body = get(url)
        if not reachable:
            checks.append(Check(f"{name} version", WARN, f"not reachable at {url}"))
            continue
        try:
            remote = json.loads(body or b"{}")
        except ValueError:
            remote = {}
        drift = version_drift(local, remote if isinstance(remote, dict) else {}, remote_name=name)
        status = WARN if drift else OK
        checks.append(Check(f"{name} version", status, drift or f"{remote.get('version')} ({remote.get('git_sha') or 'no sha'})"))
    return checks


# -- in-runner probe --------------------------------------------------------------------


def parse_probe(output: str) -> dict[str, str]:
    """KEY=VALUE lines printed by PROBE_SCRIPT (other lines, e.g. npx noise, are ignored)."""
    values = {}
    for line in output.splitlines():
        key, sep, value = line.partition("=")
        if sep and key.isupper() and key.replace("_", "").isalnum():
            values[key] = value.strip()
    return values


def _same_url(a: str, b: str) -> bool:
    """Registry URLs equal up to a trailing slash."""
    return a.rstrip("/") == b.rstrip("/")


def _registry_checks(backend: str, values: dict[str, str], proxies_enabled: bool) -> list[Check]:
    """npm, yarn and pnpm 10/11 all resolve the registry the runner advertises."""
    expected = values.get("EXPECTED_REGISTRY", "")
    if not proxies_enabled:
        return [Check(f"{backend}: registry", SKIP, "PROXIES_ENABLED=false")]
    if not expected:
        return [Check(f"{backend}: registry", FAIL, "npm_config_registry is not set in the runner")]
    checks = []
    for tool in ("NPM", "YARN", "PNPM10", "PNPM11"):
        got = values.get(f"{tool}_REGISTRY", "")
        label = f"{backend}: {tool.lower().replace('pnpm1', 'pnpm 1')} registry"
        if not got:
            checks.append(Check(label, WARN, "could not ask the tool (not installed, or npx failed)"))
        else:
            checks.append(Check(label, OK if _same_url(got, expected) else FAIL, got))
    seconds = values.get("REGISTRY_SECONDS", "")
    checks.append(Check(f"{backend}: registry reachable", OK if seconds else FAIL, f"{float(seconds) * 1000:.0f} ms" if seconds else f"{expected} unreachable"))
    return checks


def _cache_checks(backend: str, values: dict[str, str], caches_mounted: bool) -> list[Check]:
    """Tool cache, pnpm store and Playwright browsers point at (mounted) host caches."""
    checks = [
        Check(f"{backend}: RUNNER_TOOL_CACHE", OK if values.get("RUNNER_TOOL_CACHE") == TOOL_CACHE else FAIL, values.get("RUNNER_TOOL_CACHE") or "unset"),
    ]
    if not caches_mounted:
        return checks
    checks.append(Check(f"{backend}: tool cache mounted", OK if values.get("TOOLCACHE_MOUNTED") == "1" else FAIL, TOOL_CACHE))
    browsers = values.get("PLAYWRIGHT_BROWSERS_PATH", "")
    browsers_ok = browsers.endswith(PLAYWRIGHT_BROWSERS[len("/home/runner") :]) and values.get("PLAYWRIGHT_MOUNTED") == "1"
    checks.append(Check(f"{backend}: Playwright browsers", OK if browsers_ok else FAIL, f"{browsers or 'unset'} (mounted: {values.get('PLAYWRIGHT_MOUNTED')})"))
    for version in ("10", "11"):
        store = values.get(f"PNPM{version}_STORE", "")
        if store:
            ok = store.endswith(PNPM_STORE[len("/home/runner") :])
            checks.append(Check(f"{backend}: pnpm {version} store", OK if ok else FAIL, store))
    return checks


def evaluate_probe(backend: str, values: dict[str, str], caches_mounted: bool, proxies_enabled: bool) -> list[Check]:
    """Turn a runner's probe output into checks."""
    if values.get("RUNZERO") != "1":
        return [Check(f"{backend}: runner env", FAIL, "RUNZERO=1 is not exported -- the runner environment is not applied")]
    return [
        Check(f"{backend}: runner env", OK, "RUNZERO=1"),
        *_cache_checks(backend, values, caches_mounted),
        *_registry_checks(backend, values, proxies_enabled),
    ]


def probe_docker(arch: str, cache_mounts: dict[str, str], proxies_enabled: bool, timeout: int = 300) -> str | None:
    """Run PROBE_SCRIPT in a throwaway container with a job's env and mounts; its output, or None.

    The image's entrypoint (start.sh: registration, runtime proxy detection) is bypassed, so
    this checks what the driver passes in, which is what every job step inherits.
    """
    from drivers.docker_driver import DockerDriver

    driver = DockerDriver()
    if not driver.is_available() or not driver._image_exists(arch):
        return None
    cmd = ["docker", "run", "--rm", "--platform", f"linux/{driver._normalize_arch(arch)}", "--network", driver.network, "--entrypoint", "bash"]
    cmd += [arg for k, v in cache_env(bool(cache_mounts)).items() for arg in ("-e", f"{k}={v}")]
    if proxies_enabled:
        cmd += driver._build_proxy_env_args()
    cmd += driver._build_cache_mount_args(cache_mounts)
    cmd += [driver._image_tag_for_arch(arch), "-lc", PROBE_SCRIPT]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def probe_orbstack(arch: str, cache_mounts: dict[str, str], proxies_enabled: bool, timeout: int = 300) -> str | None:
    """Run PROBE_SCRIPT in a throwaway clone of the golden image, set up like a job VM; its output, or None."""
    from drivers.orbstack_templates import cache_mount_snippet
    from drivers.orbstack_vm_driver import OrbStackVMDriver

    driver = OrbStackVMDriver()
    if not driver.is_available() or not driver.base_image_exists(arch):
        return None
    vm = f"runzero-doctor-{arch}-{uuid.uuid4().hex[:6]}"
    script = "\n".join(
        [
            driver.proxy_env_block() if proxies_enabled else "",
            cache_mount_snippet(cache_mounts),
            export_block(cache_env(bool(cache_mounts))),
            PROBE_SCRIPT,
        ]
    )
    try:
        subprocess.run(["orbctl", "clone", driver.base_image_name(arch), vm], check=True, capture_output=True, timeout=120)
        driver.images.apply_limits(vm)
        return subprocess.run(["orb", "-m", vm, "-u", "runner", "bash", "-lc", script], capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        subprocess.run(["orbctl", "delete", "-f", vm], capture_output=True, timeout=120)


PROBES: dict[str, Callable[[str, dict[str, str], bool], str | None]] = {"docker": probe_docker, "orbstack-vm": probe_orbstack}


def check_runner(backend: str, arch: str, cache_dir: str, cache_enabled: bool, proxies_enabled: bool) -> list[Check]:
    """Start a throwaway runner on `backend` and check what its tools resolve."""
    probe = PROBES.get(backend)
    if probe is None:
        return [Check(f"{backend}: runner probe", SKIP, "not supported by doctor for this backend yet")]
    mounts = init_cache_dirs(cache_dir, arch, cache_enabled) if cache_enabled and cache_dir else {}
    output = probe(arch, mounts, proxies_enabled)
    if output is None:
        return [Check(f"{backend}: runner probe", SKIP, f"backend unavailable or no {arch} runner image yet")]
    return evaluate_probe(backend, parse_probe(output), bool(mounts), proxies_enabled)


# -- report -----------------------------------------------------------------------------

_ICONS = {OK: "✅", WARN: "⚠️ ", FAIL: "❌", SKIP: "⏭️ "}


def render(checks: Iterable[Check]) -> str:
    """Human report, one check per line."""
    return "\n".join(f"{_ICONS[c.status]} {c.name}: {c.detail}" if c.detail else f"{_ICONS[c.status]} {c.name}" for c in checks)


def _truthy(value: str | None, default: bool) -> bool:
    """Parse a boolean env value the way config.py does (unknown -> default)."""
    if value is None or not value.strip():
        return default
    return value.strip().lower() in ("true", "1", "yes", "on")


def run_checks(args: argparse.Namespace, env: dict[str, str]) -> list[Check]:
    """Every host check, then the in-runner probe for each requested backend."""
    cache_enabled = _truthy(env.get("CACHE_ENABLED"), True)
    proxies_enabled = _truthy(env.get("PROXIES_ENABLED"), True)
    cache_dir = env.get("HOST_CACHE_DIR", "")
    checks = [
        *check_proxies(proxies_enabled),
        *check_cache_dir(cache_dir, cache_enabled),
        check_load(),
        *check_versions(f"http://127.0.0.1:{env.get('HOST_VM_BRIDGE_PORT') or 49504}", f"http://127.0.0.1:{env.get('DASHBOARD_PORT') or 49505}"),
    ]
    for backend in args.backend:
        checks.extend(check_sizing(env, backend))
        if not args.no_spawn:
            checks.extend(check_runner(backend, args.arch, cache_dir, cache_enabled, proxies_enabled))
    return checks


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """CLI: which backends to probe, which arch, and whether to start runners at all."""
    parser = argparse.ArgumentParser(prog="runzero doctor", description="Verify RunZero's cache wiring from inside a fresh runner.")
    parser.add_argument("--backend", action="append", choices=sorted(PROBES), help="backend to probe (repeatable; default: docker and orbstack-vm)")
    parser.add_argument("--arch", default=normalize_host_arch(platform.machine()), help="runner architecture (default: this host's)")
    parser.add_argument("--no-spawn", action="store_true", help="host checks only; don't start throwaway runners")
    args = parser.parse_args(argv)
    args.backend = args.backend or sorted(PROBES)
    return args


def main(argv: list[str] | None = None, env: dict[str, Any] | None = None) -> int:
    """Print the report; exit status 1 if any check failed."""
    checks = run_checks(parse_args(argv), dict(os.environ if env is None else env))
    print(render(checks))
    failed = [c for c in checks if c.status == FAIL]
    print(f"\n{len(failed)} failed, {sum(c.status == WARN for c in checks)} warnings, {len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover -- CLI entrypoint guard
    sys.exit(main())
