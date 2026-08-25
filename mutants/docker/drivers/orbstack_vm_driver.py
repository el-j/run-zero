"""
OrbStack Linux VM Execution Driver for RunZero
Spawns and manages dedicated, lightweight Linux Virtual Machines via OrbStack (Apple Virtualization framework).
Provides full systemd, dedicated kernel, internal Docker daemon, and unconfined browser sandboxes.
"""

import os
import sys
import uuid
import json
import shutil
import subprocess
from typing import List, Dict, Optional
from . import RunnerDriver, RunnerInfo


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁOrbStackVMDriverǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁname__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁis_available__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut: MutantDict = {}  # type: ignore


class OrbStackVMDriver(RunnerDriver):
    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁ__init____mutmut)
    def __init__(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_orig(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_1(self, distro: str = "XXubuntu:22.04XX"):
        self.distro = os.getenv("ORB_DISTRO", distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_2(self, distro: str = "UBUNTU:22.04"):
        self.distro = os.getenv("ORB_DISTRO", distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_3(self, distro: str = "ubuntu:22.04"):
        self.distro = None
    def xǁOrbStackVMDriverǁ__init____mutmut_4(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv(None, distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_5(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", None)
    def xǁOrbStackVMDriverǁ__init____mutmut_6(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv(distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_7(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", )
    def xǁOrbStackVMDriverǁ__init____mutmut_8(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("XXORB_DISTROXX", distro)
    def xǁOrbStackVMDriverǁ__init____mutmut_9(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("orb_distro", distro)

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁname__mutmut)
    def name(self) -> str:
        return "orbstack-vm"

    def xǁOrbStackVMDriverǁname__mutmut_orig(self) -> str:
        return "orbstack-vm"

    def xǁOrbStackVMDriverǁname__mutmut_1(self) -> str:
        return "XXorbstack-vmXX"

    def xǁOrbStackVMDriverǁname__mutmut_2(self) -> str:
        return "ORBSTACK-VM"

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁis_available__mutmut)
    def is_available(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_orig(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_1(self) -> bool:
        if (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_2(self) -> bool:
        if not (shutil.which("orbctl") and shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_3(self) -> bool:
        if not (shutil.which(None) or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_4(self) -> bool:
        if not (shutil.which("XXorbctlXX") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_5(self) -> bool:
        if not (shutil.which("ORBCTL") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_6(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which(None)):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_7(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("XXorbXX")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_8(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("ORB")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_9(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return True
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_10(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = None
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_11(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(None, capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_12(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=None, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_13(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=None)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_14(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_15(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_16(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, )
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_17(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["XXorbctlXX", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_18(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["ORBCTL", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_19(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "XXstatusXX"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_20(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "STATUS"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_21(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=False, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_22(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=6)
            return res.returncode == 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_23(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode != 0
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_24(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 1
        except Exception:
            return False

    def xǁOrbStackVMDriverǁis_available__mutmut_25(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return True

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut)
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_orig(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_1(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "XXarm64XX",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_2(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "ARM64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_3(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "arm64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = False,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_4(
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
        unique_id = None
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_5(
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
        unique_id = uuid.uuid4().hex[:7]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_6(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = None
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_7(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace(None, '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_8(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', None)}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_9(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_10(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', )}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_11(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('XX/XX', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_12(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', 'XX-XX')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_13(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "XXXX")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_14(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = None

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_15(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = None
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_16(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch not in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_17(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("XXamd64XX", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_18(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("AMD64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_19(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "XXx64XX", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_20(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "X64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_21(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "XXx86_64XX"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_22(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "X86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_23(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = None

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_24(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "XXself-hosted,local,vm,x64,amd64XX"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_25(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "SELF-HOSTED,LOCAL,VM,X64,AMD64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_26(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = None
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_27(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = None

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_28(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "XXarm64XX" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_29(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "ARM64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_30(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch != "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_31(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "XXarm64XX" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_32(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "ARM64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_33(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "XXamd64XX"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_34(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "AMD64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_35(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(None)

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_36(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.lower()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_37(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = None
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_38(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "XXorbctlXX", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_39(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "ORBCTL", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_40(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "XXcreateXX",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_41(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "CREATE",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_42(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "XX-aXX", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_43(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-A", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_44(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "XX-uXX", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_45(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-U", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_46(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "XXrunnerXX",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_47(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "RUNNER",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_48(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(None, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_49(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=None, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_50(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=None)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_51(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_52(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_53(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, )

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_54(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=False, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_55(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=False)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_56(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = None
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_57(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo and ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_58(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or 'XXXX'}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_59(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org and ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_60(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or 'XXXX'}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_61(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                None,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_62(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=None,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_63(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=None
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_64(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_65(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_66(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_67(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["XXorbXX", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_68(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["ORB", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_69(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "XX-mXX", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_70(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-M", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_71(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "XX-uXX", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_72(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-U", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_73(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "XXrunnerXX", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_74(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "RUNNER", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_75(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "XXbashXX", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_76(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "BASH", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_77(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "XX-cXX", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_78(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-C", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_79(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(None, file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_80(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=None)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_81(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(file=sys.stderr)
            return None

    def xǁOrbStackVMDriverǁspawn_runner__mutmut_82(
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", )
            return None

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁlist_runners__mutmut)
    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_orig(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_1(self) -> List[RunnerInfo]:
        try:
            res = None
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_2(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(None, capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_3(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=None, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_4(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=None, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_5(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=None)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_6(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_7(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_8(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_9(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, )
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_10(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["XXorbctlXX", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_11(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["ORBCTL", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_12(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "XXlistXX", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_13(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "LIST", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_14(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "XX--formatXX", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_15(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--FORMAT", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_16(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "XXjsonXX"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_17(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "JSON"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_18(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=False, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_19(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=False, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_20(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=False)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_21(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = None
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_22(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(None)
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_23(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout and "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_24(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "XX[]XX")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_25(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = None
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_26(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = None
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_27(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get(None, "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_28(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", None)
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_29(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_30(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", )
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_31(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("XXnameXX", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_32(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("NAME", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_33(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "XXXX")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_34(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith(None):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_35(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("XXrunzero-vm-XX"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_36(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("RUNZERO-VM-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_37(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = None
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_38(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get(None, "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_39(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", None)
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_40(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_41(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", )
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_42(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("XXstateXX", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_43(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("STATE", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_44(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "XXrunningXX")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_45(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "RUNNING")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_46(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = None
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_47(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "XXamd64XX" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_48(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "AMD64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_49(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "XXamd64XX" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_50(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "AMD64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_51(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" not in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_52(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "XXarm64XX"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_53(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "ARM64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_54(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = None
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_55(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "XXrunningXX" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_56(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "RUNNING" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_57(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.upper() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_58(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() not in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_59(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("XXrunningXX", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_60(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("RUNNING", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_61(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "XXactiveXX") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_62(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "ACTIVE") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_63(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "XXexitedXX"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_64(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "EXITED"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_65(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(None)
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_66(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=None,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_67(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=None,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_68(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=None,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_69(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=None,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_70(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo=None,
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_71(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=None,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_72(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend=None
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_73(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_74(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_75(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_76(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_77(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_78(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_79(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_80(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="XXXX",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_81(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="XXorbstack-vmXX"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_82(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="ORBSTACK-VM"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_83(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(None, file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_84(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=None)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_85(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(file=sys.stderr)
            return []

    def xǁOrbStackVMDriverǁlist_runners__mutmut_86(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", )
            return []

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁprune_exited__mutmut)
    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_orig(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_1(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" or r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_2(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend != "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_3(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "XXorbstack-vmXX" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_4(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "ORBSTACK-VM" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_5(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state not in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_6(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("XXexitedXX", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_7(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("EXITED", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_8(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "XXdeadXX", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_9(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "DEAD", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_10(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "XXstoppedXX"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_11(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "STOPPED"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_12(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(None)
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_13(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(None, capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_14(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=None)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_15(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_16(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], )

    def xǁOrbStackVMDriverǁprune_exited__mutmut_17(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["XXorbctlXX", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_18(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["ORBCTL", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_19(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "XXdeleteXX", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_20(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "DELETE", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_21(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "XX-fXX", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_22(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-F", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁprune_exited__mutmut_23(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=False)

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut)
    def destroy_runner(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_orig(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_1(self, runner_id: str) -> bool:
        res = None
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_2(self, runner_id: str) -> bool:
        res = subprocess.run(None, capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_3(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=None)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_4(self, runner_id: str) -> bool:
        res = subprocess.run(capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_5(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], )
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_6(self, runner_id: str) -> bool:
        res = subprocess.run(["XXorbctlXX", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_7(self, runner_id: str) -> bool:
        res = subprocess.run(["ORBCTL", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_8(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "XXdeleteXX", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_9(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "DELETE", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_10(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "XX-fXX", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_11(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-F", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_12(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=False)
        return res.returncode == 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_13(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=True)
        return res.returncode != 0

    def xǁOrbStackVMDriverǁdestroy_runner__mutmut_14(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 1

    @_mutmut_mutated(mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut)
    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_orig(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_1(self) -> None:
        runners = None
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_2(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend != "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_3(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "XXorbstack-vmXX":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_4(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "ORBSTACK-VM":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_5(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(None)
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_6(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(None, capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_7(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=None)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_8(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_9(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], )

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_10(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["XXorbctlXX", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_11(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["ORBCTL", "delete", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_12(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "XXdeleteXX", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_13(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "DELETE", "-f", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_14(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "XX-fXX", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_15(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-F", r.name], capture_output=True)

    def xǁOrbStackVMDriverǁcleanup_all__mutmut_16(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=False)

mutants_xǁOrbStackVMDriverǁ__init____mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁ__init____mutmut['xǁOrbStackVMDriverǁ__init____mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁ__init____mutmut_9 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁname__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁname__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁname__mutmut['xǁOrbStackVMDriverǁname__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁname__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁname__mutmut['xǁOrbStackVMDriverǁname__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁname__mutmut_2 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁis_available__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_15'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_16'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_16 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_17'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_17 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_18'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_18 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_19'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_19 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_20'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_20 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_21'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_21 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_22'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_22 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_23'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_23 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_24'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_24 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁis_available__mutmut['xǁOrbStackVMDriverǁis_available__mutmut_25'] = OrbStackVMDriver.xǁOrbStackVMDriverǁis_available__mutmut_25 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_15'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_16'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_16 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_17'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_17 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_18'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_18 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_19'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_19 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_20'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_20 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_21'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_21 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_22'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_22 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_23'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_23 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_24'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_24 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_25'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_25 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_26'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_26 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_27'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_27 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_28'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_28 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_29'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_29 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_30'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_30 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_31'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_31 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_32'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_32 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_33'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_33 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_34'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_34 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_35'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_35 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_36'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_36 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_37'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_37 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_38'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_38 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_39'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_39 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_40'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_40 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_41'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_41 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_42'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_42 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_43'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_43 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_44'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_44 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_45'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_45 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_46'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_46 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_47'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_47 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_48'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_48 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_49'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_49 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_50'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_50 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_51'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_51 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_52'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_52 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_53'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_53 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_54'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_54 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_55'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_55 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_56'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_56 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_57'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_57 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_58'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_58 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_59'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_59 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_60'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_60 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_61'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_61 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_62'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_62 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_63'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_63 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_64'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_64 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_65'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_65 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_66'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_66 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_67'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_67 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_68'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_68 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_69'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_69 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_70'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_70 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_71'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_71 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_72'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_72 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_73'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_73 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_74'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_74 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_75'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_75 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_76'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_76 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_77'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_77 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_78'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_78 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_79'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_79 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_80'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_80 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_81'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_81 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁspawn_runner__mutmut['xǁOrbStackVMDriverǁspawn_runner__mutmut_82'] = OrbStackVMDriver.xǁOrbStackVMDriverǁspawn_runner__mutmut_82 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_15'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_16'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_16 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_17'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_17 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_18'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_18 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_19'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_19 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_20'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_20 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_21'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_21 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_22'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_22 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_23'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_23 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_24'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_24 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_25'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_25 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_26'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_26 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_27'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_27 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_28'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_28 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_29'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_29 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_30'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_30 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_31'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_31 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_32'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_32 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_33'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_33 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_34'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_34 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_35'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_35 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_36'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_36 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_37'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_37 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_38'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_38 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_39'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_39 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_40'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_40 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_41'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_41 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_42'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_42 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_43'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_43 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_44'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_44 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_45'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_45 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_46'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_46 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_47'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_47 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_48'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_48 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_49'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_49 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_50'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_50 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_51'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_51 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_52'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_52 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_53'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_53 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_54'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_54 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_55'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_55 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_56'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_56 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_57'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_57 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_58'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_58 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_59'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_59 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_60'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_60 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_61'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_61 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_62'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_62 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_63'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_63 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_64'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_64 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_65'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_65 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_66'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_66 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_67'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_67 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_68'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_68 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_69'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_69 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_70'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_70 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_71'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_71 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_72'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_72 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_73'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_73 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_74'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_74 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_75'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_75 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_76'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_76 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_77'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_77 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_78'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_78 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_79'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_79 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_80'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_80 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_81'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_81 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_82'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_82 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_83'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_83 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_84'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_84 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_85'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_85 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁlist_runners__mutmut['xǁOrbStackVMDriverǁlist_runners__mutmut_86'] = OrbStackVMDriver.xǁOrbStackVMDriverǁlist_runners__mutmut_86 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_15'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_16'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_16 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_17'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_17 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_18'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_18 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_19'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_19 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_20'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_20 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_21'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_21 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_22'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_22 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁprune_exited__mutmut['xǁOrbStackVMDriverǁprune_exited__mutmut_23'] = OrbStackVMDriver.xǁOrbStackVMDriverǁprune_exited__mutmut_23 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁdestroy_runner__mutmut['xǁOrbStackVMDriverǁdestroy_runner__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁdestroy_runner__mutmut_14 # type: ignore # mutmut generated

mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['_mutmut_orig'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_1'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_2'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_3'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_4'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_4 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_5'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_5 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_6'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_6 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_7'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_7 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_8'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_8 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_9'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_9 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_10'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_11'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_11 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_12'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_12 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_13'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_13 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_14'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_14 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_15'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_15 # type: ignore # mutmut generated
mutants_xǁOrbStackVMDriverǁcleanup_all__mutmut['xǁOrbStackVMDriverǁcleanup_all__mutmut_16'] = OrbStackVMDriver.xǁOrbStackVMDriverǁcleanup_all__mutmut_16 # type: ignore # mutmut generated
