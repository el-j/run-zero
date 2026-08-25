"""
RunZero Runner Drivers Package
Defines the abstract RunnerDriver interface and driver discovery/factory mechanisms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁRunnerInfoǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁRunnerInfoǁto_dict__mutmut: MutantDict = {}  # type: ignore


class RunnerInfo:
    @_mutmut_mutated(mutants_xǁRunnerInfoǁ__init____mutmut)
    def __init__(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_orig(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_1(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = None
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_2(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = None
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_3(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = None
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_4(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = None
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_5(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = None
        self.target_arch = target_arch
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_6(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = None
        self.backend = backend
    def xǁRunnerInfoǁ__init____mutmut_7(self, id: str, name: str, status: str, state: str, target_repo: str, target_arch: str, backend: str):
        self.id = id
        self.name = name
        self.status = status
        self.state = state
        self.target_repo = target_repo
        self.target_arch = target_arch
        self.backend = None

    @_mutmut_mutated(mutants_xǁRunnerInfoǁto_dict__mutmut)
    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_orig(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_1(self) -> Dict[str, str]:
        return {
            "XXidXX": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_2(self) -> Dict[str, str]:
        return {
            "ID": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_3(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "XXnameXX": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_4(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "NAME": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_5(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "XXstatusXX": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_6(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "STATUS": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_7(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "XXstateXX": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_8(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "STATE": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_9(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "XXtarget_repoXX": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_10(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "TARGET_REPO": self.target_repo,
            "target_arch": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_11(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "XXtarget_archXX": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_12(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "TARGET_ARCH": self.target_arch,
            "backend": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_13(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "XXbackendXX": self.backend
        }

    def xǁRunnerInfoǁto_dict__mutmut_14(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "state": self.state,
            "target_repo": self.target_repo,
            "target_arch": self.target_arch,
            "BACKEND": self.backend
        }

mutants_xǁRunnerInfoǁ__init____mutmut['_mutmut_orig'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_1'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_2'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_3'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_4'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_5'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_6'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁ__init____mutmut['xǁRunnerInfoǁ__init____mutmut_7'] = RunnerInfo.xǁRunnerInfoǁ__init____mutmut_7 # type: ignore # mutmut generated

mutants_xǁRunnerInfoǁto_dict__mutmut['_mutmut_orig'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_orig # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_1'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_1 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_2'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_2 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_3'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_3 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_4'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_4 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_5'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_5 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_6'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_6 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_7'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_7 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_8'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_8 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_9'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_9 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_10'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_10 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_11'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_11 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_12'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_12 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_13'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_13 # type: ignore # mutmut generated
mutants_xǁRunnerInfoǁto_dict__mutmut['xǁRunnerInfoǁto_dict__mutmut_14'] = RunnerInfo.xǁRunnerInfoǁto_dict__mutmut_14 # type: ignore # mutmut generated


class RunnerDriver(ABC):
    """Abstract interface for RunZero execution drivers (Docker containers, OrbStack VMs, WSL2, Multipass)."""

    @abstractmethod
    def name(self) -> str:
        """Return the unique identifier for this driver."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the underlying runtime (docker, orb, wsl, multipass) is available on the host."""
        pass

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
        """Spawn a fresh ephemeral runner instance. Returns instance identifier/name."""
        pass

    @abstractmethod
    def list_runners(self) -> List[RunnerInfo]:
        """List all runner instances currently managed by this driver."""
        pass

    @abstractmethod
    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        """Remove stopped or dead runner instances."""
        pass

    @abstractmethod
    def destroy_runner(self, runner_id: str) -> bool:
        """Force destroy and clean up a specific runner instance."""
        pass

    @abstractmethod
    def cleanup_all(self) -> None:
        """Clean up all managed runner instances during shutdown."""
        pass
mutants_x_get_available_drivers__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_available_drivers__mutmut)
def get_available_drivers() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

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

    return drivers


def x_get_available_drivers__mutmut_orig() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

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

    return drivers


def x_get_available_drivers__mutmut_1() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    drivers = None
    candidates = [
        DockerDriver(),
        OrbStackVMDriver(),
        WSL2Driver(),
        MultipassDriver()
    ]

    for d in candidates:
        if d.is_available():
            drivers[d.name()] = d

    return drivers


def x_get_available_drivers__mutmut_2() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    drivers = {}
    candidates = None

    for d in candidates:
        if d.is_available():
            drivers[d.name()] = d

    return drivers


def x_get_available_drivers__mutmut_3() -> Dict[str, RunnerDriver]:
    """Discover and return all drivers available on the host system."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    drivers = {}
    candidates = [
        DockerDriver(),
        OrbStackVMDriver(),
        WSL2Driver(),
        MultipassDriver()
    ]

    for d in candidates:
        if d.is_available():
            drivers[d.name()] = None

    return drivers

mutants_x_get_available_drivers__mutmut['_mutmut_orig'] = x_get_available_drivers__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_available_drivers__mutmut['x_get_available_drivers__mutmut_1'] = x_get_available_drivers__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_available_drivers__mutmut['x_get_available_drivers__mutmut_2'] = x_get_available_drivers__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_available_drivers__mutmut['x_get_available_drivers__mutmut_3'] = x_get_available_drivers__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_driver__mutmut)
def get_driver(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_orig(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_1(name: str = "XXautoXX") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_2(name: str = "AUTO") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_3(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = None

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_4(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.upper().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_5(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name not in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_6(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("XXdockerXX", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_7(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("DOCKER", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_8(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "XXcontainerXX"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_9(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "CONTAINER"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_10(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name not in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_11(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("XXorbXX", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_12(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("ORB", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_13(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "XXorbstackXX", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_14(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "ORBSTACK", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_15(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "XXorbstack-vmXX", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_16(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "ORBSTACK-VM", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_17(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "XXvm-orbXX"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_18(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "VM-ORB"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_19(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name not in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_20(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("XXwslXX", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_21(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("WSL", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_22(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "XXwsl2XX", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_23(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "WSL2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_24(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "XXwindowsXX"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_25(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "WINDOWS"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_26(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name not in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_27(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("XXmultipassXX", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_28(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("MULTIPASS", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_29(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "XXcanonical-multipassXX"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_30(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "CANONICAL-MULTIPASS"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_31(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name not in ("auto", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_32(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("XXautoXX", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_33(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("AUTO", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_34(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("auto", "XXhybridXX"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_35(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("auto", "HYBRID"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_36(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("auto", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = None
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = OrbStackVMDriver()
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_37(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
    elif name in ("auto", "hybrid"):
        # Auto-selection priority:
        # 1. Docker (fastest, lightweight baseline)
        docker_driver = DockerDriver()
        if docker_driver.is_available():
            return docker_driver

        # 2. OrbStack VM (if on macOS without docker daemon)
        orb_driver = None
        if orb_driver.is_available():
            return orb_driver

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_38(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = None
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_39(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = None
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(f"Unknown runner backend driver: '{name}'. Valid options: docker, orbstack-vm, wsl2, multipass, auto")


def x_get_driver__mutmut_40(name: str = "auto") -> RunnerDriver:
    """Instantiate and return the requested driver or auto-select best available."""
    from .docker_driver import DockerDriver
    from .orbstack_vm_driver import OrbStackVMDriver
    from .wsl_driver import WSL2Driver
    from .multipass_driver import MultipassDriver

    name = name.lower().strip()

    if name in ("docker", "container"):
        return DockerDriver()
    elif name in ("orb", "orbstack", "orbstack-vm", "vm-orb"):
        return OrbStackVMDriver()
    elif name in ("wsl", "wsl2", "windows"):
        return WSL2Driver()
    elif name in ("multipass", "canonical-multipass"):
        return MultipassDriver()
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

        # 3. WSL2 (if on Windows)
        wsl_driver = WSL2Driver()
        if wsl_driver.is_available():
            return wsl_driver

        # 4. Multipass
        multipass_driver = MultipassDriver()
        if multipass_driver.is_available():
            return multipass_driver

        # Fallback to Docker driver
        return docker_driver

    raise ValueError(None)

mutants_x_get_driver__mutmut['_mutmut_orig'] = x_get_driver__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_1'] = x_get_driver__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_2'] = x_get_driver__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_3'] = x_get_driver__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_4'] = x_get_driver__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_5'] = x_get_driver__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_6'] = x_get_driver__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_7'] = x_get_driver__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_8'] = x_get_driver__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_9'] = x_get_driver__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_10'] = x_get_driver__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_11'] = x_get_driver__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_12'] = x_get_driver__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_13'] = x_get_driver__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_14'] = x_get_driver__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_15'] = x_get_driver__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_16'] = x_get_driver__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_17'] = x_get_driver__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_18'] = x_get_driver__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_19'] = x_get_driver__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_20'] = x_get_driver__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_21'] = x_get_driver__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_22'] = x_get_driver__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_23'] = x_get_driver__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_24'] = x_get_driver__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_25'] = x_get_driver__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_26'] = x_get_driver__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_27'] = x_get_driver__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_28'] = x_get_driver__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_29'] = x_get_driver__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_30'] = x_get_driver__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_31'] = x_get_driver__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_32'] = x_get_driver__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_33'] = x_get_driver__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_34'] = x_get_driver__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_35'] = x_get_driver__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_36'] = x_get_driver__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_37'] = x_get_driver__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_38'] = x_get_driver__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_39'] = x_get_driver__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_driver__mutmut['x_get_driver__mutmut_40'] = x_get_driver__mutmut_40 # type: ignore # mutmut generated
