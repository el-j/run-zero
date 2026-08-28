"""
Docker Container Execution Driver for RunZero
Spawns and manages ephemeral runner containers with host or bridge networking.
"""

import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from . import RunnerDriver, RunnerInfo


class DockerDriver(RunnerDriver):
    """Runs ephemeral GitHub Actions runners as Docker containers -- the fastest, lightest-weight backend."""

    def __init__(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner"
    ):
        """Configure the Docker socket path, container network mode, and runner image tag prefix.

        `docker_sock`/`network` fall back to DOCKER_SOCK/DOCKER_NETWORK env vars if set.
        """
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix

    def name(self) -> str:
        """Return this driver's backend identifier: "docker"."""
        return "docker"

    def is_available(self) -> bool:
        """True if the `docker` CLI is on PATH and `docker info` succeeds (daemon reachable)."""
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
        """Launch a detached, ephemeral runner container via `docker run -d` and return its name.

        Returns None (and prints to stderr) if the `docker run` invocation itself fails;
        registration/execution then happens asynchronously inside the container's own entrypoint.
        """
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
            # Headless Chrome (Lighthouse CI, Playwright) needs to create its own
            # user/PID namespace for its internal sandbox, which Docker blocks by
            # default. GitHub-hosted runners never hit this because they're full
            # VMs, not containers. Jobs only skip this container path when their
            # own `runs-on:` labels match a VM_TRIGGER_LABELS entry and a VM
            # driver is available (see select_driver_for_job in autoscaler.py) —
            # every other job, including browser-driven ones, lands here.
            "--cap-add", "SYS_ADMIN",
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
            # devpi's default "root/pypi" index is a real pull-through PyPI mirror out of the
            # box; pip and uv both honor PIP_INDEX_URL, and uv additionally reads UV_INDEX_URL.
            pip_host = "localhost:49507" if self.network == "host" else "devpi:3141"
            pip_index_url = f"http://{pip_host}/root/pypi/+simple/"
            cmd.extend([
                "-e", f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                "-e", f"YARN_REGISTRY={verdaccio_url}",
                "-e", f"GOPROXY={athens_url}",
                "-e", f"PIP_INDEX_URL={pip_index_url}",
                "-e", f"UV_INDEX_URL={pip_index_url}"
            ])
            if self.network != "host":
                # pip implicitly trusts "localhost"/"127.0.0.1" for plain-HTTP indexes but
                # refuses anything else -- verified live (2026-08-26): pointing pip at a
                # plain-HTTP non-localhost host without this produced "is not a trusted or
                # secure host" and pip silently found zero packages, exit 0, no error. uv
                # does not have this restriction (verified: identical install succeeds with
                # no equivalent flag), so this is pip/PIP_TRUSTED_HOST-only.
                cmd.extend(["-e", "PIP_TRUSTED_HOST=devpi"])
            # kellnr's crates.io proxy is a real sparse-index mirror, but unlike pip/Go it
            # has no single "point at this URL" env var: verified live (2026-08-26) that
            # cargo silently ignores CARGO_SOURCE_<name>_* env vars for a dynamic/custom
            # [source.*] table (a real cargo limitation, not a typo) -- only a real
            # ~/.cargo/config.toml source-replacement block works. `docker/start.sh`
            # (this image's own entrypoint) writes that file at container start when it
            # detects kellnr is reachable, so no extra `-e`/`-v` is threaded through here.

        if cache_mounts:
            for host_p, cont_p in cache_mounts.items():
                cmd.extend(["-v", f"{host_p}:{cont_p}"])
            # start.sh needs the exact set of container-side mount destinations to
            # fix their ancestor-directory ownership (Docker/OrbStack create bind
            # mount ancestors as root). Passing it from here — the same dict that
            # drives the -v flags above — means start.sh can never drift out of
            # sync with the actual mounts the way a second hardcoded list did.
            cmd.extend(["-e", f"CACHE_MOUNT_DESTS={':'.join(cache_mounts.values())}"])

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
        """List containers labeled `managed-by=local-autoscaler` via `docker ps -a`.

        Returns an empty list (and prints to stderr) if the `docker ps` call itself fails.
        """
        try:
            res = subprocess.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "label=managed-by=local-autoscaler",
                    "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}|{{.Label \"backend\"}}|{{.CreatedAt}}"
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
                    created_at = self._parse_created_at(parts[7]) if len(parts) > 7 else None
                    # Docker's raw state, normalized so main()'s active-runner tally
                    # (state == "running"/"pending") doesn't undercount a container
                    # that's created but hasn't flipped to "running" yet -- narrow
                    # window for Docker (near-instant) but same bug class as the VM
                    # driver's "creating"/"provisioning" misclassification.
                    raw_state = parts[3]
                    if raw_state == "running":
                        state = "running"
                    elif raw_state in ("created", "restarting"):
                        state = "pending"
                    else:
                        state = raw_state
                    runners.append(RunnerInfo(
                        id=parts[0],
                        status=parts[1],
                        name=parts[2],
                        state=state,
                        target_repo=parts[4],
                        target_arch=parts[5],
                        backend=backend,
                        created_at=created_at
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    @staticmethod
    def _parse_created_at(raw: str) -> Optional[float]:
        # Docker's `--format {{.CreatedAt}}` is e.g. "2026-08-25 14:38:53 +0200
        # CEST" -- the trailing zone abbreviation isn't reliably parseable by
        # strptime's %Z across platforms/locales, but the numeric UTC offset
        # right before it is, so only the first three tokens are used.
        try:
            date_part, time_part, offset, *_ = raw.strip().split()
            return datetime.strptime(f"{date_part} {time_part} {offset}", "%Y-%m-%d %H:%M:%S %z").timestamp()
        except (ValueError, IndexError):
            return None

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        """Force-remove any `runners` entries that are Docker-backed and in "exited"/"dead" state."""
        for r in runners:
            if r.backend == "docker" and r.state in ("exited", "dead"):
                print(f"[Autoscaler:Docker] Removing finished container: {r.name} ({r.id})")
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)

    def destroy_runner(self, runner_id: str) -> bool:
        """Force-remove the container with this id/name via `docker rm -f`."""
        res = subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def cleanup_all(self) -> None:
        """Stop and force-remove every container this driver manages (used on autoscaler shutdown)."""
        runners = self.list_runners()
        for r in runners:
            if r.backend == "docker":
                subprocess.run(["docker", "stop", r.id], capture_output=True)
                subprocess.run(["docker", "rm", "-f", r.id], capture_output=True)
