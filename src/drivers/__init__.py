"""
RunZero Runner Drivers Package
Defines the abstract RunnerDriver interface and driver discovery/factory mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class RunnerInfo:
    """Driver-agnostic snapshot of one ephemeral runner instance, as returned by `list_runners()`."""

    def __init__(
        self,
        id: str,
        name: str,
        status: str,
        state: str,
        target_repo: str,
        target_arch: str,
        backend: str,
        created_at: Optional[float] = None
    ):
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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict (used for the VM bridge's HTTP payloads)."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend,
            "created_at": self.created_at
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
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "arm64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Spawn a fresh ephemeral runner for `repo` (or `org` if `repo` is unset).

        Must not block the caller for the life of the runner -- registration/execution
        happens out-of-process (background thread, detached subprocess, or remote job).
        Returns the new instance's id/name on success, or None on failure (including a
        deliberate "not ready yet" case, e.g. a VM driver still building its base image).
        """

    @abstractmethod
    def list_runners(self) -> List[RunnerInfo]:
        """Return every runner instance this driver currently manages, regardless of state."""

    @abstractmethod
    def prune_exited(self, runners: List[RunnerInfo]) -> None:
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

    def ensure_runtime_assets(self, arch: str = "arm64") -> bool:
        """Ensure architecture-specific golden artifacts are ready before spawn.

        Drivers that require a prebuilt asset (e.g. Docker runner image, VM base image)
        should override this and return False while preparing it in the background.
        Drivers without such prerequisites can keep this default True behavior.
        """
        return True


def get_available_drivers() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system or via Host VM Bridge."""
    from .bridge_driver import BridgeVMDriver
    from .docker_driver import DockerDriver
    from .multipass_driver import MultipassDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver

    drivers = {}
    candidates = [
        DockerDriver(),
        OrbStackVMDriver(),
        WSL2Driver(),
        MultipassDriver()
    ]

    for d in candidates:
        if d.is_available():
            drivers[d.name()] = d
        else:
            # If native CLI tool is not available (e.g. inside a container), check Host VM Bridge
            bridge_candidate = BridgeVMDriver(d.name())
            if bridge_candidate.is_available():
                drivers[d.name()] = bridge_candidate

    return drivers


def get_driver(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .bridge_driver import BridgeVMDriver
    from .docker_driver import DockerDriver
    from .multipass_driver import MultipassDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        orb_native = OrbStackVMDriver()
        if orb_native.is_available():
            return orb_native
        bridge = BridgeVMDriver("orbstack-vm")
        if bridge.is_available():
            return bridge
        return orb_native
    elif name in ("wsl", "wsl2", "windows"):
        wsl_native = WSL2Driver()
        if wsl_native.is_available():
            return wsl_native
        wsl_bridge = BridgeVMDriver("wsl2")
        if wsl_bridge.is_available():
            return wsl_bridge
        return wsl_native
    elif name in ("multipass", "canonical-multipass"):
        mp_native = MultipassDriver()
        if mp_native.is_available():
            return mp_native
        mp_bridge = BridgeVMDriver("multipass")
        if mp_bridge.is_available():
            return mp_bridge
        return mp_native
    elif name in ("auto", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver
        orb_bridge = BridgeVMDriver("orbstack-vm")
        if orb_bridge.is_available():
            return orb_bridge

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver
        wsl_bridge = BridgeVMDriver("wsl2")
        if wsl_bridge.is_available():
            return wsl_bridge

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver
        mp_bridge = BridgeVMDriver("multipass")
        if mp_bridge.is_available():
            return mp_bridge

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")
