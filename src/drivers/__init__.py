"""
RunZero Runner Drivers Package
Defines the abstract RunnerDriver interface and driver discovery/factory mechanisms.
"""

import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from github_api import create_registration_token

ImageEventCallback = Callable[[dict[str, Any]], None]

# Spawn inputs end up in runner names, `docker run` labels and VM bootstrap scripts, so they are
# validated against GitHub's own naming rules before any driver uses them (and quoted anyway).
_OWNER = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})"
_REPO_RE = re.compile(rf"^{_OWNER}/[A-Za-z0-9._-]{{1,100}}$")
_ORG_RE = re.compile(rf"^{_OWNER}$")
_LABEL = r"[A-Za-z0-9._:+/ -]{1,100}"
_LABELS_RE = re.compile(rf"^{_LABEL}(?:,{_LABEL})*$")
_ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
# Variables the runner bootstrap owns; extra_env may not override them.
_RESERVED_ENV_KEYS = frozenset({"ACCESS_TOKEN", "RUNNER_TOKEN", "REGISTRATION_TOKEN", "RUNNER_NAME", "RUNNER_LABELS", "REPO", "ORG", "EPHEMERAL"})


def validate_spawn_target(repo: str | None, org: str | None, labels: str | None, extra_env: dict[str, str] | None = None) -> None:
    """Raise ValueError unless `repo`/`org`/`labels`/`extra_env` are well-formed.

    Exactly one of `repo` ("owner/name") or `org` is required; `labels` is an optional
    comma-separated list; `extra_env` keys must be plain identifiers that don't shadow a
    variable the runner bootstrap sets itself, and values must be strings.
    """
    if repo:
        if not isinstance(repo, str) or not _REPO_RE.match(repo):
            raise ValueError(f"invalid repository name: {repo!r}")
    elif org:
        if not isinstance(org, str) or not _ORG_RE.match(org):
            raise ValueError(f"invalid organization name: {org!r}")
    else:
        raise ValueError("either repo or org is required")
    if labels and (not isinstance(labels, str) or not _LABELS_RE.match(labels)):
        raise ValueError(f"invalid runner labels: {labels!r}")
    if extra_env is not None:
        if not isinstance(extra_env, dict):
            raise ValueError("extra_env must be an object")
        for key, value in extra_env.items():
            if not isinstance(key, str) or not _ENV_KEY_RE.match(key) or key.upper() in _RESERVED_ENV_KEYS:
                raise ValueError(f"invalid or reserved extra_env key: {key!r}")
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError(f"invalid extra_env value for {key!r}")


class RunnerInfo:
    """Driver-agnostic snapshot of one ephemeral runner instance, as returned by `list_runners()`."""

    def __init__(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str, created_at: float | None = None):
        """Store the runner's identity, driver-reported status/state, and routing metadata."""
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
        # Unix timestamp, when the driver can report it (currently: Docker only).
        # Lets the reconciler tell "just spawned, GitHub hasn't dispatched to it
        # yet" apart from "been sitting idle for way too long, orphaned".
        self.created_at = created_at

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict (used for the VM bridge's HTTP payloads)."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend,
            "created_at": self.created_at,
        }


class RunnerDriver(ABC):
    """Abstract interface for RunZero execution drivers (Docker containers, OrbStack VMs, WSL2, Multipass)."""

    @abstractmethod
    def name(self) -> str:
        """Return the unique identifier for this driver."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the underlying runtime (docker, orb, wsl, multipass) is available on the host."""

    @abstractmethod
    def spawn_runner(
        self,
        repo: str | None = None,
        org: str | None = None,
        arch: str = "arm64",
        labels: str | None = None,
        access_token: str | None = None,
        cache_mounts: dict[str, str] | None = None,
        proxies_enabled: bool = True,
        extra_env: dict[str, str] | None = None,
        runner_token: str | None = None,
    ) -> str | None:
        """Spawn a fresh ephemeral runner for `repo` (or `org` if `repo` is unset).

        Credentials: `runner_token` is a GitHub runner registration token; when it is absent
        the driver exchanges `access_token` (the admin PAT) for one via
        `_prepare_spawn()`. Only the registration token may reach the runner.

        Must not block the caller for the life of the runner -- registration/execution
        happens out-of-process (background thread, detached subprocess, or remote job).
        Returns the new instance's id/name on success, or None on failure (including a
        deliberate "not ready yet" case, e.g. a VM driver still building its base image).
        """

    @abstractmethod
    def list_runners(self) -> list[RunnerInfo]:
        """Return every runner instance this driver currently manages, regardless of state."""

    @abstractmethod
    def prune_exited(self, runners: list[RunnerInfo]) -> None:
        """Remove any of `runners` (as previously returned by `list_runners()`) that have exited.

        Only acts on entries whose `backend` matches this driver; safe to call with a mixed-backend list.
        """

    @abstractmethod
    def destroy_runner(self, runner_id: str) -> bool:
        """Force-stop and remove one runner by id, regardless of its current state.

        Returns True if the runner was destroyed (or already gone), False on failure.
        """

    @abstractmethod
    def cleanup_all(self) -> None:
        """Destroy every runner this driver manages. Best-effort: swallows per-runner failures."""

    def _prepare_spawn(
        self,
        repo: str | None,
        org: str | None,
        labels: str | None,
        access_token: str | None,
        runner_token: str | None,
        extra_env: dict[str, str] | None = None,
    ) -> str | None:
        """Validate the spawn target and return the registration token to hand the runner.

        Returns None (after logging why) when the inputs are malformed or no registration
        token can be obtained; callers then return None from spawn_runner().
        """
        try:
            validate_spawn_target(repo, org, labels, extra_env)
        except ValueError as exc:
            print(f"[Autoscaler:{self.name()}] Refusing to spawn: {exc}", file=sys.stderr)
            return None
        token = runner_token or create_registration_token(repo, org, access_token)
        if not token:
            print(f"[Autoscaler:{self.name()}] Could not obtain a runner registration token for {repo or org}.", file=sys.stderr)
        return token

    def ensure_runtime_assets(self, arch: str = "arm64") -> bool:
        """Ensure architecture-specific golden artifacts are ready before spawn.

        Drivers that require a prebuilt asset (e.g. Docker runner image, VM base image)
        should override this and return False while preparing it in the background.
        Drivers without such prerequisites can keep this default True behavior.
        """
        return True


# Every accepted RUNNER_BACKEND spelling -> canonical backend name ("auto" picks one).
BACKEND_ALIASES: dict[str, str] = {
    "docker": "docker",
    "container": "docker",
    "orb": "orbstack-vm",
    "orbstack": "orbstack-vm",
    "orbstack-vm": "orbstack-vm",
    "vm-orb": "orbstack-vm",
    "wsl": "wsl2",
    "wsl2": "wsl2",
    "windows": "wsl2",
    "multipass": "multipass",
    "canonical-multipass": "multipass",
    "auto": "auto",
    "hybrid": "auto",
}

# Order in which "auto" prefers backends: Docker is the fast, lightweight baseline.
AUTO_PRIORITY = ("docker", "orbstack-vm", "wsl2", "multipass")


def canonical_backend(name: str) -> str:
    """Resolve a RUNNER_BACKEND alias to its canonical name; ValueError if unknown."""
    canonical = BACKEND_ALIASES.get(name.lower().strip())
    if canonical is None:
        raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")
    return canonical


def _native_factories(on_image_event: ImageEventCallback | None) -> dict[str, Callable[[], RunnerDriver]]:
    """Canonical backend name -> constructor for the host-native driver, in AUTO_PRIORITY order."""
    from .docker_driver import DockerDriver
    from .multipass_driver import MultipassDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver

    return {
        "docker": lambda: DockerDriver(on_image_event=on_image_event),
        "orbstack-vm": lambda: OrbStackVMDriver(on_image_event=on_image_event),
        "wsl2": WSL2Driver,
        "multipass": MultipassDriver,
    }


def _usable_driver(backend: str, on_image_event: ImageEventCallback | None) -> RunnerDriver | None:
    """The native driver if available, else a reachable Host VM Bridge proxy for it, else None."""
    from .bridge_driver import BridgeVMDriver

    native = _native_factories(on_image_event)[backend]()
    if native.is_available():
        return native
    bridge = BridgeVMDriver(backend)
    return bridge if bridge.is_available() else None


def get_available_drivers(on_image_event: ImageEventCallback | None = None) -> dict[str, RunnerDriver]:
    """Discover every usable backend (native, or via the Host VM Bridge) as a name -> driver registry.

    The autoscaler builds this ONCE per process and takes its default driver from it (see
    `select_default_driver`): per-instance state such as golden-image build locks and
    spawn cooldowns must not be split across duplicate driver objects.

    `on_image_event`, when given, is forwarded to drivers that build golden images (currently
    Docker and OrbStack VM) so they can report structured build-status events (see
    `dashboard.state.DashboardState.report_image_build`) instead of only printing to stdout/stderr.
    """
    drivers: dict[str, RunnerDriver] = {}
    for backend in AUTO_PRIORITY:
        driver = _usable_driver(backend, on_image_event)
        if driver is not None:
            drivers[backend] = driver
    return drivers


def select_default_driver(drivers: dict[str, RunnerDriver], backend: str, on_image_event: ImageEventCallback | None = None) -> RunnerDriver:
    """Return the default driver for RUNNER_BACKEND, taken from the `drivers` registry.

    "auto" picks the first available backend in AUTO_PRIORITY. When the requested backend
    isn't in the registry (unavailable), its native driver is created and ADDED to the
    registry, so the process still holds exactly one instance per backend (it will fail to
    spawn and log why, as before). With an empty registry "auto" falls back to Docker.
    """
    canonical = canonical_backend(backend)
    if canonical == "auto":
        canonical = next((name for name in AUTO_PRIORITY if name in drivers), "docker")
    if canonical not in drivers:
        drivers[canonical] = _native_factories(on_image_event)[canonical]()
    return drivers[canonical]


def get_driver(name: str = "auto", on_image_event: ImageEventCallback | None = None) -> RunnerDriver:
    """Build one driver for `name` outside any registry (used by the VM bridge and build scripts).

    Explicit backends return the native driver if available, else a reachable bridge proxy,
    else the native driver anyway ("docker" is returned without probing). "auto" follows
    AUTO_PRIORITY. Raises ValueError for an unknown backend name.
    """
    canonical = canonical_backend(name)
    if canonical == "auto":
        # Stop at the first usable backend -- no need to probe the rest. Docker is only
        # considered natively here; the Host VM Bridge exists for the VM backends.
        docker = _native_factories(on_image_event)["docker"]()
        if docker.is_available():
            return docker
        for backend in AUTO_PRIORITY[1:]:
            driver = _usable_driver(backend, on_image_event)
            if driver is not None:
                return driver
        return docker
    if canonical == "docker":
        return _native_factories(on_image_event)["docker"]()
    return _usable_driver(canonical, on_image_event) or _native_factories(on_image_event)[canonical]()
