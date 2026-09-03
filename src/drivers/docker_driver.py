"""
Docker Container Execution Driver for RunZero
Spawns and manages ephemeral runner containers with host or bridge networking.
"""

import os
import shutil
import subprocess
import sys
import threading
import time
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
        self._building_lock = threading.Lock()
        self._building_arches: set = set()
        self._build_failure_counts: Dict[str, int] = {}
        self._build_retry_after: Dict[str, float] = {}

    @staticmethod
    def _normalize_arch(arch: str) -> str:
        if arch in ("amd64", "x64", "x86_64"):
            return "amd64"
        return "arm64"

    def _image_tag_for_arch(self, arch: str) -> str:
        return f"{self.runner_image_prefix}:{self._normalize_arch(arch)}"

    def _image_exists(self, arch: str) -> bool:
        image_tag = self._image_tag_for_arch(arch)
        try:
            res = subprocess.run(["docker", "image", "inspect", image_tag], capture_output=True)
            return res.returncode == 0
        except Exception:
            return False

    def _resolve_build_context_dir(self) -> Optional[str]:
        candidates = []

        env_dir = os.getenv("RUNNER_IMAGE_DOCKER_DIR", "").strip()
        if env_dir:
            candidates.append(env_dir)

        module_relative = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docker")
        )
        candidates.append(module_relative)
        candidates.append("/workspace/docker")
        candidates.append(os.path.abspath(os.path.join(os.getcwd(), "docker")))

        for path in candidates:
            dockerfile = os.path.join(path, "Dockerfile")
            provision_script = os.path.join(path, "provision-toolchain.sh")
            start_script = os.path.join(path, "start.sh")
            if os.path.isfile(dockerfile) and os.path.isfile(provision_script) and os.path.isfile(start_script):
                return path
        return None

    def _build_cooldown_remaining(self, arch: str) -> float:
        return max(0.0, self._build_retry_after.get(arch, 0.0) - time.monotonic())

    def _build_runner_image(self, arch: str) -> bool:
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)

        if self._image_exists(normalized_arch):
            print(f"[Autoscaler:Docker] Golden runner image '{image_tag}' already exists -- skipping build.")
            return True

        build_context_dir = self._resolve_build_context_dir()
        if not build_context_dir:
            print(
                "[Autoscaler:Docker] Error: runner image build context not found. "
                "Expected a docker directory with Dockerfile/provision-toolchain.sh/start.sh. "
                "Set RUNNER_IMAGE_DOCKER_DIR or mount the repo into /workspace.",
                file=sys.stderr,
            )
            return False

        print(
            f"[Autoscaler:Docker] 🏗️  Building missing golden runner image '{image_tag}' "
            f"from '{build_context_dir}'..."
        )

        # Cross-platform builds (e.g. linux/amd64 on Apple Silicon hosts)
        # require BuildKit/buildx. Falling back to legacy `docker build`
        # here produces misleading platform errors and never yields a usable
        # tag for the requested architecture.
        has_buildx = subprocess.run(["docker", "buildx", "version"], capture_output=True).returncode == 0
        if not has_buildx:
            print(
                "[Autoscaler:Docker] Error: docker buildx is not available in the autoscaler runtime. "
                "Install docker-buildx-plugin in the autoscaler image so missing runner images can be "
                "built automatically for the requested platform.",
                file=sys.stderr,
            )
            return False

        try:
            subprocess.run(
                [
                    "docker", "buildx", "build",
                    "--load",
                    "--platform", f"linux/{normalized_arch}",
                    "--build-arg", f"TARGETARCH={normalized_arch}",
                    "-t", image_tag,
                    "-f", os.path.join(build_context_dir, "Dockerfile"),
                    build_context_dir,
                ],
                check=True,
                capture_output=True,
            )
            print(f"[Autoscaler:Docker] ✅ Golden runner image '{image_tag}' is ready.")
            return True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
            print(
                f"[Autoscaler:Docker] Error building golden runner image '{image_tag}': {stderr}",
                file=sys.stderr,
            )
            return False

    def _build_runner_image_async(self, arch: str) -> None:
        normalized_arch = self._normalize_arch(arch)
        with self._building_lock:
            if normalized_arch in self._building_arches:
                return
            if self._build_cooldown_remaining(normalized_arch) > 0:
                return
            self._building_arches.add(normalized_arch)

        def _run() -> None:
            ok = False
            try:
                ok = self._build_runner_image(normalized_arch)
            finally:
                with self._building_lock:
                    self._building_arches.discard(normalized_arch)
                    if ok:
                        self._build_failure_counts[normalized_arch] = 0
                        self._build_retry_after.pop(normalized_arch, None)
                    else:
                        failures = self._build_failure_counts.get(normalized_arch, 0) + 1
                        self._build_failure_counts[normalized_arch] = failures
                        cooldown = min(30 * (2 ** (failures - 1)), 900)
                        self._build_retry_after[normalized_arch] = time.monotonic() + cooldown
                        print(
                            f"[Autoscaler:Docker] Golden runner image build for '{normalized_arch}' "
                            f"failed {failures} time(s). Backing off {cooldown}s before retry.",
                            file=sys.stderr,
                        )

        threading.Thread(target=_run, name=f"runzero-build-docker-{normalized_arch}", daemon=True).start()

    def ensure_runtime_assets(self, arch: str = "arm64") -> bool:
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)
        if self._image_exists(normalized_arch):
            return True

        with self._building_lock:
            already_building = normalized_arch in self._building_arches
            cooldown_remaining = self._build_cooldown_remaining(normalized_arch)

        if already_building:
            print(
                f"[Autoscaler:Docker] Golden runner image '{image_tag}' is currently building. "
                "This queued job will be retried on the next poll."
            )
            return False

        if cooldown_remaining > 0:
            print(
                f"[Autoscaler:Docker] Golden runner image '{image_tag}' is missing, but build retry is "
                f"cooling down for {int(cooldown_remaining)}s after a previous failure.",
                file=sys.stderr,
            )
            return False

        print(
            f"[Autoscaler:Docker] Golden runner image '{image_tag}' is missing. "
            "Starting automatic background build now; this job will be retried once ready."
        )
        self._build_runner_image_async(normalized_arch)
        return False

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
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)
        platform_flag = f"linux/{normalized_arch}"

        if not self.ensure_runtime_assets(normalized_arch):
            return None

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
            stderr_text = e.stderr.decode(errors="replace") if e.stderr else str(e)
            if "Unable to find image" in stderr_text or "pull access denied" in stderr_text:
                print(
                    f"[Autoscaler:Docker] Launch failed because image '{image_tag}' is unavailable. "
                    "Triggering automatic background build and retrying on next poll.",
                    file=sys.stderr,
                )
                self._build_runner_image_async(normalized_arch)
            print(f"[Autoscaler:Docker] Error launching container: {stderr_text}", file=sys.stderr)
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
