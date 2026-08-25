"""
Canonical Multipass VM Execution Driver for RunZero
Cross-platform VM execution for macOS, Linux, and Windows using lightweight QEMU/Hyper-V/VirtualBox VMs.
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
mutants_xǁMultipassDriverǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁname__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁis_available__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁspawn_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁlist_runners__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁprune_exited__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁdestroy_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁMultipassDriverǁcleanup_all__mutmut: MutantDict = {}  # type: ignore


class MultipassDriver(RunnerDriver):
    @_mutmut_mutated(mutants_xǁMultipassDriverǁ__init____mutmut)
    def __init__(self, image: str = "22.04"):
        self.image = os.getenv("MULTIPASS_IMAGE", image)
    def xǁMultipassDriverǁ__init____mutmut_orig(self, image: str = "22.04"):
        self.image = os.getenv("MULTIPASS_IMAGE", image)
    def xǁMultipassDriverǁ__init____mutmut_1(self, image: str = "XX22.04XX"):
        self.image = os.getenv("MULTIPASS_IMAGE", image)
    def xǁMultipassDriverǁ__init____mutmut_2(self, image: str = "22.04"):
        self.image = None
    def xǁMultipassDriverǁ__init____mutmut_3(self, image: str = "22.04"):
        self.image = os.getenv(None, image)
    def xǁMultipassDriverǁ__init____mutmut_4(self, image: str = "22.04"):
        self.image = os.getenv("MULTIPASS_IMAGE", None)
    def xǁMultipassDriverǁ__init____mutmut_5(self, image: str = "22.04"):
        self.image = os.getenv(image)
    def xǁMultipassDriverǁ__init____mutmut_6(self, image: str = "22.04"):
        self.image = os.getenv("MULTIPASS_IMAGE", )
    def xǁMultipassDriverǁ__init____mutmut_7(self, image: str = "22.04"):
        self.image = os.getenv("XXMULTIPASS_IMAGEXX", image)
    def xǁMultipassDriverǁ__init____mutmut_8(self, image: str = "22.04"):
        self.image = os.getenv("multipass_image", image)

    @_mutmut_mutated(mutants_xǁMultipassDriverǁname__mutmut)
    def name(self) -> str:
        return "multipass"

    def xǁMultipassDriverǁname__mutmut_orig(self) -> str:
        return "multipass"

    def xǁMultipassDriverǁname__mutmut_1(self) -> str:
        return "XXmultipassXX"

    def xǁMultipassDriverǁname__mutmut_2(self) -> str:
        return "MULTIPASS"

    @_mutmut_mutated(mutants_xǁMultipassDriverǁis_available__mutmut)
    def is_available(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_orig(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_1(self) -> bool:
        if shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_2(self) -> bool:
        if not shutil.which(None):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_3(self) -> bool:
        if not shutil.which("XXmultipassXX"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_4(self) -> bool:
        if not shutil.which("MULTIPASS"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_5(self) -> bool:
        if not shutil.which("multipass"):
            return True
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_6(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = None
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_7(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(None, capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_8(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=None, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_9(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=None)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_10(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_11(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_12(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, )
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_13(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["XXmultipassXX", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_14(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["MULTIPASS", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_15(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "XXversionXX"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_16(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "VERSION"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_17(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=False, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_18(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=6)
            return res.returncode == 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_19(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode != 0
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_20(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 1
        except Exception:
            return False

    def xǁMultipassDriverǁis_available__mutmut_21(self) -> bool:
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return True

    @_mutmut_mutated(mutants_xǁMultipassDriverǁspawn_runner__mutmut)
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_orig(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_1(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_2(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_3(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_4(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_5(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_6(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_7(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_8(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_9(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_10(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_11(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_12(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_13(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_14(
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
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_15(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = None

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_16(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(None)

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_17(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = None
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_18(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "XXmultipassXX", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_19(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "MULTIPASS", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_20(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "XXlaunchXX",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_21(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "LAUNCH",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_22(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "XX--nameXX", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_23(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--NAME", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_24(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "XX--cpusXX", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_25(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--CPUS", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_26(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "XX2XX",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_27(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "XX--memoryXX", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_28(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--MEMORY", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_29(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "XX2GXX"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_30(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2g"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_31(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(None, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_32(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=None, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_33(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=None)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_34(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_35(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_36(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, )

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_37(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=False, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_38(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=False)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_39(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = None
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_40(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                None,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_41(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=None,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_42(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=None
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_43(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_44(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_45(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_46(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["XXmultipassXX", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_47(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["MULTIPASS", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_48(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "XXexecXX", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_49(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "EXEC", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_50(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "XX--XX", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_51(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "XXbashXX", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_52(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "BASH", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_53(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "XX-cXX", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_54(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-C", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_55(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(None, file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_56(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=None)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_57(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(file=sys.stderr)
            return None

    def xǁMultipassDriverǁspawn_runner__mutmut_58(
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
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = labels if labels else f"self-hosted,local,multipass,vm,{arch}"

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}'...")

        try:
            # 1. Launch the VM
            launch_cmd = [
                "multipass", "launch",
                self.image,
                "--name", vm_name,
                "--cpus", "2",
                "--memory", "2G"
            ]
            subprocess.run(launch_cmd, check=True, capture_output=True)

            # 2. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
export ACCESS_TOKEN="{access_token}"
nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["multipass", "exec", vm_name, "--", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", )
            return None

    @_mutmut_mutated(mutants_xǁMultipassDriverǁlist_runners__mutmut)
    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_orig(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_1(self) -> List[RunnerInfo]:
        try:
            res = None
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_2(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(None, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_3(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=None, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_4(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=None, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_5(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=None)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_6(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_7(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_8(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_9(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, )
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_10(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["XXmultipassXX", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_11(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["MULTIPASS", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_12(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "XXlistXX", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_13(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "LIST", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_14(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "XX--formatXX", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_15(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--FORMAT", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_16(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "XXjsonXX"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_17(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "JSON"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_18(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=False, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_19(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=False, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_20(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=False)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_21(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = None
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_22(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(None)
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_23(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout and "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_24(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "XX{}XX")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_25(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = None
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_26(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get(None, [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_27(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", None)
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_28(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get([])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_29(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", )
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_30(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("XXlistXX", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_31(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("LIST", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_32(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = None
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_33(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = None
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_34(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get(None, "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_35(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", None)
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_36(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_37(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", )
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_38(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("XXnameXX", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_39(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("NAME", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_40(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "XXXX")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_41(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith(None):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_42(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("XXrunzero-mp-XX"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_43(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("RUNZERO-MP-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_44(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = None
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_45(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get(None, "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_46(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", None)
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_47(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_48(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", )
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_49(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("XXstateXX", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_50(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("STATE", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_51(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "XXRunningXX")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_52(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_53(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "RUNNING")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_54(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = None
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_55(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "XXrunningXX" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_56(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "RUNNING" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_57(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.upper() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_58(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() != "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_59(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "XXrunningXX" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_60(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "RUNNING" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_61(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "XXexitedXX"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_62(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "EXITED"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_63(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(None)
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_64(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=None,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_65(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=None,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_66(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=None,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_67(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=None,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_68(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo=None,
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_69(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=None,
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_70(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend=None
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_71(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_72(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_73(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_74(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        target_repo="",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_75(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_76(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_77(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_78(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="XXXX",
                        target_arch="arm64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_79(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="XXarm64XX",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_80(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="ARM64",
                        backend="multipass"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_81(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="XXmultipassXX"
                    ))
            return runners
        except Exception:
            return []

    def xǁMultipassDriverǁlist_runners__mutmut_82(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch="arm64",
                        backend="MULTIPASS"
                    ))
            return runners
        except Exception:
            return []

    @_mutmut_mutated(mutants_xǁMultipassDriverǁprune_exited__mutmut)
    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_orig(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_1(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" or r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_2(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend != "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_3(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "XXmultipassXX" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_4(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "MULTIPASS" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_5(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state not in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_6(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("XXexitedXX", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_7(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("EXITED", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_8(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "XXstoppedXX", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_9(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "STOPPED", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_10(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "XXdeadXX"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_11(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "DEAD"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_12(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(None)
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_13(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(None, capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_14(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=None)

    def xǁMultipassDriverǁprune_exited__mutmut_15(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_16(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], )

    def xǁMultipassDriverǁprune_exited__mutmut_17(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["XXmultipassXX", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_18(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["MULTIPASS", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_19(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "XXdeleteXX", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_20(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "DELETE", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_21(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "XX--purgeXX", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_22(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--PURGE", r.name], capture_output=True)

    def xǁMultipassDriverǁprune_exited__mutmut_23(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=False)

    @_mutmut_mutated(mutants_xǁMultipassDriverǁdestroy_runner__mutmut)
    def destroy_runner(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_orig(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_1(self, runner_id: str) -> bool:
        res = None
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_2(self, runner_id: str) -> bool:
        res = subprocess.run(None, capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_3(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=None)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_4(self, runner_id: str) -> bool:
        res = subprocess.run(capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_5(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], )
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_6(self, runner_id: str) -> bool:
        res = subprocess.run(["XXmultipassXX", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_7(self, runner_id: str) -> bool:
        res = subprocess.run(["MULTIPASS", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_8(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "XXdeleteXX", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_9(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "DELETE", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_10(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "XX--purgeXX", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_11(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--PURGE", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_12(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=False)
        return res.returncode == 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_13(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode != 0

    def xǁMultipassDriverǁdestroy_runner__mutmut_14(self, runner_id: str) -> bool:
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 1

    @_mutmut_mutated(mutants_xǁMultipassDriverǁcleanup_all__mutmut)
    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_orig(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_1(self) -> None:
        runners = None
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_2(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend != "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_3(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "XXmultipassXX":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_4(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "MULTIPASS":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_5(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(None, capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_6(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=None)

    def xǁMultipassDriverǁcleanup_all__mutmut_7(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_8(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], )

    def xǁMultipassDriverǁcleanup_all__mutmut_9(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["XXmultipassXX", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_10(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["MULTIPASS", "delete", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_11(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "XXdeleteXX", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_12(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "DELETE", "--purge", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_13(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "XX--purgeXX", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_14(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--PURGE", r.name], capture_output=True)

    def xǁMultipassDriverǁcleanup_all__mutmut_15(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=False)

mutants_xǁMultipassDriverǁ__init____mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_1'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_2'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_3'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_4'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_5'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_6'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_7'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁ__init____mutmut['xǁMultipassDriverǁ__init____mutmut_8'] = MultipassDriver.xǁMultipassDriverǁ__init____mutmut_8 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁname__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁname__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁname__mutmut['xǁMultipassDriverǁname__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁname__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁname__mutmut['xǁMultipassDriverǁname__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁname__mutmut_2 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁis_available__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_14 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_15'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_15 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_16'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_16 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_17'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_17 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_18'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_18 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_19'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_19 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_20'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_20 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁis_available__mutmut['xǁMultipassDriverǁis_available__mutmut_21'] = MultipassDriver.xǁMultipassDriverǁis_available__mutmut_21 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁspawn_runner__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_14 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_15'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_15 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_16'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_16 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_17'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_17 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_18'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_18 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_19'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_19 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_20'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_20 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_21'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_21 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_22'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_22 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_23'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_23 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_24'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_24 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_25'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_25 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_26'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_26 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_27'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_27 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_28'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_28 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_29'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_29 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_30'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_30 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_31'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_31 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_32'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_32 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_33'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_33 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_34'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_34 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_35'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_35 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_36'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_36 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_37'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_37 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_38'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_38 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_39'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_39 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_40'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_40 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_41'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_41 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_42'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_42 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_43'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_43 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_44'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_44 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_45'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_45 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_46'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_46 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_47'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_47 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_48'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_48 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_49'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_49 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_50'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_50 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_51'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_51 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_52'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_52 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_53'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_53 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_54'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_54 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_55'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_55 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_56'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_56 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_57'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_57 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁspawn_runner__mutmut['xǁMultipassDriverǁspawn_runner__mutmut_58'] = MultipassDriver.xǁMultipassDriverǁspawn_runner__mutmut_58 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁlist_runners__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_14 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_15'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_15 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_16'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_16 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_17'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_17 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_18'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_18 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_19'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_19 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_20'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_20 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_21'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_21 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_22'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_22 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_23'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_23 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_24'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_24 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_25'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_25 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_26'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_26 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_27'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_27 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_28'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_28 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_29'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_29 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_30'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_30 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_31'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_31 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_32'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_32 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_33'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_33 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_34'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_34 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_35'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_35 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_36'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_36 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_37'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_37 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_38'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_38 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_39'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_39 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_40'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_40 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_41'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_41 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_42'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_42 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_43'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_43 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_44'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_44 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_45'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_45 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_46'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_46 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_47'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_47 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_48'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_48 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_49'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_49 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_50'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_50 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_51'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_51 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_52'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_52 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_53'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_53 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_54'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_54 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_55'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_55 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_56'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_56 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_57'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_57 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_58'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_58 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_59'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_59 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_60'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_60 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_61'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_61 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_62'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_62 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_63'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_63 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_64'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_64 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_65'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_65 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_66'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_66 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_67'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_67 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_68'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_68 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_69'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_69 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_70'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_70 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_71'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_71 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_72'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_72 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_73'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_73 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_74'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_74 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_75'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_75 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_76'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_76 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_77'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_77 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_78'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_78 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_79'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_79 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_80'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_80 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_81'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_81 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁlist_runners__mutmut['xǁMultipassDriverǁlist_runners__mutmut_82'] = MultipassDriver.xǁMultipassDriverǁlist_runners__mutmut_82 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁprune_exited__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_14 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_15'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_15 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_16'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_16 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_17'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_17 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_18'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_18 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_19'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_19 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_20'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_20 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_21'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_21 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_22'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_22 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁprune_exited__mutmut['xǁMultipassDriverǁprune_exited__mutmut_23'] = MultipassDriver.xǁMultipassDriverǁprune_exited__mutmut_23 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁdestroy_runner__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁdestroy_runner__mutmut['xǁMultipassDriverǁdestroy_runner__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁdestroy_runner__mutmut_14 # type: ignore # mutmut generated

mutants_xǁMultipassDriverǁcleanup_all__mutmut['_mutmut_orig'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_orig # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_1'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_1 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_2'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_2 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_3'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_3 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_4'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_4 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_5'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_5 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_6'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_6 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_7'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_7 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_8'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_8 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_9'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_9 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_10'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_10 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_11'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_11 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_12'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_12 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_13'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_13 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_14'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_14 # type: ignore # mutmut generated
mutants_xǁMultipassDriverǁcleanup_all__mutmut['xǁMultipassDriverǁcleanup_all__mutmut_15'] = MultipassDriver.xǁMultipassDriverǁcleanup_all__mutmut_15 # type: ignore # mutmut generated
