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


class DockerDriver(RunnerDriver):
    def __init__(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix

    def name(self) -> str:
        return "docker"

    def is_available(self) -> bool:
        if not shutil.which("docker"):
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

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

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def destroy_runner(self, runner_id: str) -> bool:
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)
