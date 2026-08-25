"""
Docker Container Execution Driver for RunZero
Spawns and manages ephemeral runner containers with host or bridge networking.
"""

import os
import sys
import uuid
import shutil
import subprocess
from typing import List, Dict, Optional
from . import RunnerDriver, RunnerInfo


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_xǁDockerDriverǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁname__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁis_available__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁspawn_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁlist_runners__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁprune_exited__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁdestroy_runner__mutmut: MutantDict = {}  # type: ignore
mutants_xǁDockerDriverǁcleanup_all__mutmut: MutantDict = {}  # type: ignore


class DockerDriver(RunnerDriver):
    @_mutmut_mutated(mutants_xǁDockerDriverǁ__init____mutmut)
    def __init__(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_orig(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_1(
        self,
        docker_sock: str = "XX/var/run/docker.sockXX",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_2(
        self,
        docker_sock: str = "/VAR/RUN/DOCKER.SOCK",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_3(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "XXhostXX",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_4(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "HOST",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_5(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "XXlocal-github-runnerXX"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_6(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "LOCAL-GITHUB-RUNNER"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_7(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = None
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_8(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv(None, docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_9(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", None)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_10(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv(docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_11(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", )
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_12(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("XXDOCKER_SOCKXX", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_13(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("docker_sock", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_14(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = None
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_15(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv(None, network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_16(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", None)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_17(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv(network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_18(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", )
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_19(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("XXDOCKER_NETWORKXX", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_20(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("docker_network", network)
        self.runner_image_prefix = runner_image_prefix
    def xǁDockerDriverǁ__init____mutmut_21(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = None

    @_mutmut_mutated(mutants_xǁDockerDriverǁname__mutmut)
    def name(self) -> str:
        return "docker"

    def xǁDockerDriverǁname__mutmut_orig(self) -> str:
        return "docker"

    def xǁDockerDriverǁname__mutmut_1(self) -> str:
        return "XXdockerXX"

    def xǁDockerDriverǁname__mutmut_2(self) -> str:
        return "DOCKER"

    @_mutmut_mutated(mutants_xǁDockerDriverǁis_available__mutmut)
    def is_available(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_orig(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_1(self) -> bool:
        if shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_2(self) -> bool:
        if not shutil.which(None):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_3(self) -> bool:
        if not shutil.which("XXdockerXX"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_4(self) -> bool:
        if not shutil.which("DOCKER"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_5(self) -> bool:
        if not shutil.which("docker"):
            return True
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_6(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = None
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_7(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(None, capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_8(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=None, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_9(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=None)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_10(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_11(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_12(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, )
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_13(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["XXdockerXX", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_14(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["DOCKER", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_15(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "XXinfoXX"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_16(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "INFO"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_17(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=False, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_18(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=6)
            return res.returncode == 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_19(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode != 0
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_20(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 1
        except Exception:
            return False

    def xǁDockerDriverǁis_available__mutmut_21(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return True

    @_mutmut_mutated(mutants_xǁDockerDriverǁspawn_runner__mutmut)
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_orig(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_1(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_2(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_3(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_4(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_5(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_6(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_7(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_8(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_9(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_10(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_11(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_12(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_13(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_14(
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
        container_name = None
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_15(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = None
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_16(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = None

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_17(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = None
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_18(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch not in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_19(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("XXamd64XX", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_20(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("AMD64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_21(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "XXx64XX", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_22(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "X64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_23(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "XXx86_64XX"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_24(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "X86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_25(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = None

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_26(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "XXself-hosted,local,x64,amd64XX"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_27(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "SELF-HOSTED,LOCAL,X64,AMD64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_28(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = None

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_29(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = None

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_30(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "XXdockerXX", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_31(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "DOCKER", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_32(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "XXrunXX", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_33(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "RUN", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_34(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "XX-dXX",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_35(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-D",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_36(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "XX--nameXX", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_37(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--NAME", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_38(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "XX--platformXX", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_39(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--PLATFORM", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_40(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "XX--networkXX", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_41(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--NETWORK", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_42(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "XX--labelXX", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_43(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--LABEL", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_44(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "XXmanaged-by=local-autoscalerXX",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_45(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "MANAGED-BY=LOCAL-AUTOSCALER",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_46(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "XX--labelXX", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_47(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--LABEL", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_48(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "XXbackend=dockerXX",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_49(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "BACKEND=DOCKER",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_50(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "XX--labelXX", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_51(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--LABEL", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_52(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo and ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_53(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or 'XXXX'}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_54(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "XX--labelXX", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_55(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--LABEL", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_56(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "XX-eXX", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_57(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-E", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_58(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "XX-eXX", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_59(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-E", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_60(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "XX-eXX", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_61(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-E", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_62(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "XX-eXX", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_63(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-E", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_64(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "XXEPHEMERAL=trueXX",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_65(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "ephemeral=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_66(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=TRUE",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_67(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "XX-eXX", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_68(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-E", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_69(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "XXRUNNER_WORKDIR=_workXX",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_70(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "runner_workdir=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_71(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_WORK",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_72(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "XX-eXX", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_73(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-E", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_74(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "XXRUNNER_TOOL_CACHE=/opt/hostedtoolcacheXX",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_75(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "runner_tool_cache=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_76(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/OPT/HOSTEDTOOLCACHE",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_77(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "XX-vXX", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_78(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-V", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_79(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = None
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_80(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "XXhttp://localhost:49501/XX" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_81(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "HTTP://LOCALHOST:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_82(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network != "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_83(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "XXhostXX" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_84(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "HOST" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_85(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "XXhttp://verdaccio:4873/XX"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_86(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "HTTP://VERDACCIO:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_87(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = None
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_88(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "XXhttp://localhost:49500,https://proxy.golang.org,directXX" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_89(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "HTTP://LOCALHOST:49500,HTTPS://PROXY.GOLANG.ORG,DIRECT" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_90(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network != "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_91(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "XXhostXX" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_92(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "HOST" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_93(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "XXhttp://athens:3000,https://proxy.golang.org,directXX"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_94(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "HTTP://ATHENS:3000,HTTPS://PROXY.GOLANG.ORG,DIRECT"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_95(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend(None)

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_96(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "XX-eXX", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_97(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-E", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_98(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "XX-eXX", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_99(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-E", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_100(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(None)

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_101(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["XX-vXX", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_102(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-V", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_103(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(None)
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_104(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["XX-eXX", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_105(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-E", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_106(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(None)

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_107(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["XX-eXX", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_108(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-E", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_109(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(None)

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_110(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["XX-eXX", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_111(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-E", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_112(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(None)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_113(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = None
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_114(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(None)

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_115(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.lower()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_116(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo and org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_117(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(None, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_118(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=None, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_119(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=None)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_120(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_121(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_122(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, )
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_123(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=False, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_124(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=False)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_125(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(None, file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_126(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", file=None)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_127(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(file=sys.stderr)
            return None

    def xǁDockerDriverǁspawn_runner__mutmut_128(
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
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        image_tag = f"{self.runner_image_prefix}:{arch}"
        platform_flag = f"linux/{arch}"

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = labels if labels else default_labels

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--platform", platform_flag,
            "--network", self.network,
            "--label", "managed-by=local-autoscaler",
            "--label", "backend=docker",
            "--label", f"target-repo={repo or ''}",
            "--label", f"target-arch={arch}",
            "-e", f"ACCESS_TOKEN={access_token}",
            "-e", f"RUNNER_NAME={container_name}",
            "-e", f"RUNNER_LABELS={runner_labels}",
            "-e", "EPHEMERAL=true",
            "-e", "RUNNER_WORKDIR=_work",
            "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v", f"{self.docker_sock}:/var/run/docker.sock"
        ]

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}"
            ])

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])

        if repo:
            cmd.extend(["-e", f"REPO={repo}"])
        elif org:
            cmd.extend(["-e", f"ORG={org}"])

        if extra_env:
            for k, v in extra_env.items():
                cmd.extend(["-e", f"{k}={v}"])

        cmd.append(image_tag)

        network_desc = f"{self.network} network"
        print(f"[Autoscaler:Docker] 🚀 Spawning ephemeral [{arch.upper()}] container {container_name} ({network_desc}) for {repo or org}...")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return container_name
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Docker] Error launching container: {e.stderr.decode()}", )
            return None

    @_mutmut_mutated(mutants_xǁDockerDriverǁlist_runners__mutmut)
    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_orig(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_1(self) -> List[RunnerInfo]:
        try:
            res = None
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_2(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                None,
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_3(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=None,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_4(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=None,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_5(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=None
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_6(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_7(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_8(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_9(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_10(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "XXdockerXX", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_11(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "DOCKER", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_12(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "XXpsXX", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_13(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "PS", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_14(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "XX-aXX",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_15(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-A",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_16(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "XX--filterXX", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_17(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--FILTER", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_18(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "XXlabel=managed-by=local-autoscalerXX",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_19(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "LABEL=MANAGED-BY=LOCAL-AUTOSCALER",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_20(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "XX--formatXX", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_21(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--FORMAT", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_22(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "XX{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}XX"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_23(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.id}}|{{.status}}|{{.names}}|{{.state}}|{{.label \"target-repo\"}}|{{.label \"target-arch\"}}|{{.label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_24(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.STATUS}}|{{.NAMES}}|{{.STATE}}|{{.LABEL \"TARGET-REPO\"}}|{{.LABEL \"TARGET-ARCH\"}}|{{.LABEL \"BACKEND\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_25(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=False,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_26(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=False,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_27(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=False
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_28(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = None
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_29(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split(None):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_30(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("XX\nXX"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_31(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_32(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    break
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_33(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = None
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_34(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(None)
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_35(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("XX|XX")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_36(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) > 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_37(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 7:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_38(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = None
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_39(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[7] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_40(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 or parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_41(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) >= 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_42(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 7 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_43(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[7] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_44(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "XXdockerXX"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_45(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "DOCKER"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_46(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(None)
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_47(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=None,
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_48(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=None,
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_49(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=None,
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_50(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=None,
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_51(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=None,
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_52(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=None,
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_53(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=None
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_54(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_55(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_56(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_57(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_58(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_59(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_60(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_61(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[1],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_62(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[2],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_63(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[3],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_64(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[4],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_65(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[5],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_66(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[6],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_67(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(None, file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_68(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=None)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_69(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(file=sys.stderr)
            return []

    def xǁDockerDriverǁlist_runners__mutmut_70(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            runners = []
            for line in res.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    backend = parts[6] if len(parts) > 6 and parts[6] else "docker"
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=parts[3],
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", )
            return []

    @_mutmut_mutated(mutants_xǁDockerDriverǁprune_exited__mutmut)
    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_orig(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_1(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" or r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_2(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend != "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_3(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "XXdockerXX" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_4(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "DOCKER" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_5(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state not in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_6(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("XXexitedXX", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_7(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("EXITED", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_8(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "XXdeadXX"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_9(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "DEAD"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_10(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(None)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_11(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(None, capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_12(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=None)

    def xǁDockerDriverǁprune_exited__mutmut_13(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_14(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], )

    def xǁDockerDriverǁprune_exited__mutmut_15(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["XXdockerXX", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_16(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["DOCKER", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_17(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "XXrmXX", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_18(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "RM", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_19(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "XX-fXX", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_20(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-F", r.id], capture_output=True)

    def xǁDockerDriverǁprune_exited__mutmut_21(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=False)

    @_mutmut_mutated(mutants_xǁDockerDriverǁdestroy_runner__mutmut)
    def destroy_runner(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_orig(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_1(self, runner_id: str) -> bool:
        res = None
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_2(self, runner_id: str) -> bool:
        res = subprocess.run(None, capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_3(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=None)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_4(self, runner_id: str) -> bool:
        res = subprocess.run(capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_5(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], )
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_6(self, runner_id: str) -> bool:
        res = subprocess.run(["XXdockerXX", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_7(self, runner_id: str) -> bool:
        res = subprocess.run(["DOCKER", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_8(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "XXrmXX", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_9(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "RM", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_10(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "XX-fXX", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_11(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-F", runner_id], capture_output=True)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_12(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=False)
        return res.returncode == 0

    def xǁDockerDriverǁdestroy_runner__mutmut_13(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode != 0

    def xǁDockerDriverǁdestroy_runner__mutmut_14(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 1

    @_mutmut_mutated(mutants_xǁDockerDriverǁcleanup_all__mutmut)
    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_orig(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_1(self) -> None:
        runners = None
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_2(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend != "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_3(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "XXdockerXX":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_4(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "DOCKER":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_5(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(None, capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_6(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=None)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_7(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_8(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], )
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_9(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["XXdockerXX", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_10(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["DOCKER", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_11(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "XXstopXX", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_12(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "STOP", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_13(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=False)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_14(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(None, capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_15(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=None)

    def xǁDockerDriverǁcleanup_all__mutmut_16(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_17(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], )

    def xǁDockerDriverǁcleanup_all__mutmut_18(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["XXdockerXX", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_19(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["DOCKER", "rm", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_20(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "XXrmXX", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_21(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "RM", "-f", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_22(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "XX-fXX", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_23(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-F", r.id], capture_output=True)

    def xǁDockerDriverǁcleanup_all__mutmut_24(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=False)

mutants_xǁDockerDriverǁ__init____mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_1'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_2'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_3'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_4'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_5'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_6'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_7'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_8'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_9'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_10'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_11'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_12'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_13'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_14'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_15'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_16'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_17'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_18'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_19'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_20'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁ__init____mutmut['xǁDockerDriverǁ__init____mutmut_21'] = DockerDriver.xǁDockerDriverǁ__init____mutmut_21 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁname__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁname__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁname__mutmut['xǁDockerDriverǁname__mutmut_1'] = DockerDriver.xǁDockerDriverǁname__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁname__mutmut['xǁDockerDriverǁname__mutmut_2'] = DockerDriver.xǁDockerDriverǁname__mutmut_2 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁis_available__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_1'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_2'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_3'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_4'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_5'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_6'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_7'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_8'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_9'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_10'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_11'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_12'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_13'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_14'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_15'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_16'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_17'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_18'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_19'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_20'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁis_available__mutmut['xǁDockerDriverǁis_available__mutmut_21'] = DockerDriver.xǁDockerDriverǁis_available__mutmut_21 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁspawn_runner__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_1'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_2'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_3'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_4'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_5'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_6'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_7'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_8'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_9'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_10'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_11'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_12'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_13'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_14'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_15'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_16'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_17'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_18'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_19'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_20'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_21'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_22'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_23'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_24'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_25'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_26'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_27'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_28'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_29'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_30'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_31'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_32'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_33'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_34'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_35'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_36'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_37'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_38'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_39'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_40'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_41'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_42'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_43'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_44'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_45'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_45 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_46'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_46 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_47'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_47 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_48'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_48 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_49'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_49 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_50'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_50 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_51'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_51 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_52'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_52 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_53'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_53 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_54'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_54 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_55'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_55 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_56'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_56 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_57'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_57 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_58'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_58 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_59'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_59 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_60'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_60 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_61'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_61 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_62'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_62 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_63'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_63 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_64'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_64 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_65'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_65 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_66'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_66 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_67'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_67 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_68'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_68 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_69'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_69 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_70'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_70 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_71'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_71 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_72'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_72 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_73'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_73 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_74'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_74 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_75'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_75 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_76'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_76 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_77'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_77 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_78'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_78 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_79'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_79 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_80'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_80 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_81'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_81 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_82'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_82 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_83'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_83 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_84'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_84 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_85'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_85 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_86'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_86 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_87'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_87 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_88'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_88 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_89'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_89 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_90'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_90 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_91'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_91 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_92'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_92 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_93'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_93 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_94'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_94 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_95'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_95 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_96'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_96 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_97'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_97 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_98'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_98 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_99'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_99 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_100'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_100 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_101'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_101 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_102'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_102 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_103'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_103 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_104'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_104 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_105'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_105 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_106'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_106 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_107'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_107 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_108'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_108 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_109'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_109 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_110'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_110 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_111'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_111 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_112'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_112 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_113'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_113 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_114'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_114 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_115'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_115 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_116'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_116 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_117'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_117 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_118'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_118 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_119'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_119 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_120'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_120 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_121'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_121 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_122'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_122 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_123'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_123 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_124'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_124 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_125'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_125 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_126'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_126 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_127'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_127 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁspawn_runner__mutmut['xǁDockerDriverǁspawn_runner__mutmut_128'] = DockerDriver.xǁDockerDriverǁspawn_runner__mutmut_128 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁlist_runners__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_1'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_2'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_3'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_4'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_5'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_6'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_7'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_8'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_9'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_10'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_11'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_12'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_13'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_14'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_15'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_16'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_17'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_18'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_19'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_20'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_21'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_22'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_23'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_24'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_24 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_25'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_25 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_26'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_26 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_27'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_27 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_28'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_28 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_29'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_29 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_30'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_30 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_31'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_31 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_32'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_32 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_33'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_33 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_34'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_34 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_35'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_35 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_36'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_36 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_37'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_37 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_38'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_38 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_39'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_39 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_40'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_40 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_41'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_41 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_42'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_42 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_43'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_43 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_44'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_44 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_45'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_45 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_46'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_46 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_47'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_47 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_48'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_48 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_49'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_49 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_50'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_50 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_51'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_51 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_52'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_52 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_53'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_53 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_54'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_54 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_55'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_55 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_56'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_56 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_57'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_57 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_58'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_58 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_59'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_59 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_60'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_60 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_61'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_61 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_62'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_62 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_63'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_63 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_64'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_64 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_65'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_65 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_66'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_66 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_67'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_67 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_68'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_68 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_69'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_69 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁlist_runners__mutmut['xǁDockerDriverǁlist_runners__mutmut_70'] = DockerDriver.xǁDockerDriverǁlist_runners__mutmut_70 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁprune_exited__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_1'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_2'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_3'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_4'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_5'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_6'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_7'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_8'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_9'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_10'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_11'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_12'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_13'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_14'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_15'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_16'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_17'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_18'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_19'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_20'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁprune_exited__mutmut['xǁDockerDriverǁprune_exited__mutmut_21'] = DockerDriver.xǁDockerDriverǁprune_exited__mutmut_21 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁdestroy_runner__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_1'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_2'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_3'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_4'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_5'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_6'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_7'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_8'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_9'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_10'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_11'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_12'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_13'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁdestroy_runner__mutmut['xǁDockerDriverǁdestroy_runner__mutmut_14'] = DockerDriver.xǁDockerDriverǁdestroy_runner__mutmut_14 # type: ignore # mutmut generated

mutants_xǁDockerDriverǁcleanup_all__mutmut['_mutmut_orig'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_orig # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_1'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_1 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_2'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_2 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_3'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_3 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_4'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_4 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_5'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_5 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_6'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_6 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_7'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_7 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_8'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_8 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_9'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_9 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_10'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_10 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_11'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_11 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_12'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_12 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_13'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_13 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_14'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_14 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_15'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_15 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_16'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_16 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_17'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_17 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_18'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_18 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_19'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_19 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_20'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_20 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_21'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_21 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_22'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_22 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_23'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_23 # type: ignore # mutmut generated
mutants_xǁDockerDriverǁcleanup_all__mutmut['xǁDockerDriverǁcleanup_all__mutmut_24'] = DockerDriver.xǁDockerDriverǁcleanup_all__mutmut_24 # type: ignore # mutmut generated
