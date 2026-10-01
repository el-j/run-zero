"""
Docker Container Execution Driver for RunZero
Spawns and manages ephemeral runner containers with host or bridge networking.
"""

import contextlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime

from . import ImageEventCallback, RunnerDriver, RunnerInfo, merge_labels
from .backoff import BuildBackoff

# `docker ps` output columns, `|`-separated; parsed positionally by `list_runners()`.
_PS_FORMAT = "|".join(
    [
        "{{.ID}}",
        "{{.Status}}",
        "{{.Names}}",
        "{{.State}}",
        '{{.Label "target-repo"}}',
        '{{.Label "target-arch"}}',
        '{{.Label "backend"}}',
        "{{.CreatedAt}}",
    ]
)


class DockerDriver(RunnerDriver):
    """Runs ephemeral GitHub Actions runners as Docker containers -- the fastest, lightest-weight backend."""

    def __init__(
        self,
        docker_sock: str = "/var/run/docker.sock",
        network: str = "host",
        runner_image_prefix: str = "local-github-runner",
        on_image_event: ImageEventCallback | None = None,
    ):
        """Configure the Docker socket path, container network mode, and runner image tag prefix.

        `docker_sock`/`network` fall back to DOCKER_SOCK/DOCKER_NETWORK env vars if set.
        `on_image_event`, when given, is called with a structured dict on every golden-image
        build status transition (building/ready/failed/cooldown) -- see `_report_image_event()`.
        """
        self.docker_sock = os.getenv("DOCKER_SOCK", docker_sock)
        self.network = os.getenv("DOCKER_NETWORK", network)
        self.runner_image_prefix = runner_image_prefix
        # Per-container CPU/memory ceiling, forwarded to `docker run` (see spawn_runner()).
        # Left unset by default (unlimited) to preserve existing behavior; without it,
        # MAX_RUNNERS concurrent containers can each claim the full host core/RAM count.
        # A test suite's own worker pool (e.g. vitest/jest auto-sizing to the host's
        # reported CPU count) then oversubscribes actual available CPU by MAX_RUNNERS-x,
        # which is exactly what starved a real CI run's vitest workers into false 20s
        # test timeouts and one outright "Failed to start forks worker" crash (observed
        # 2026-09-22 on el-j/herbful run 35768507392, orbstack-vm engine). Set both once
        # host capacity is known so MAX_RUNNERS * RUNNER_CPUS stays within the host's
        # real core count -- see the same env vars on OrbStackVMDriver.
        self.runner_cpus = os.getenv("RUNNER_CPUS") or None
        self.runner_memory = os.getenv("RUNNER_MEMORY") or None
        self._on_image_event: ImageEventCallback = on_image_event or (lambda event: None)
        # Background runner-image builds: per-arch dedup + exponential backoff (see BuildBackoff).
        self._backoff = BuildBackoff()
        self._registry_mirror_checked = False

    def _report_image_event(self, status: str, arch: str, detail: str, profile: str | None = None) -> None:
        """Emit a structured build-status event alongside the existing stdout/stderr prints.

        Never raises -- a broken/misbehaving callback (e.g. dashboard not yet initialized in a
        test) must not be able to break an actual image build.
        """
        with contextlib.suppress(Exception):
            self._on_image_event(
                {
                    "driver": self.name(),
                    "arch": arch,
                    "profile": profile,
                    "status": status,
                    "detail": detail,
                    "ts": time.time(),
                }
            )

    @staticmethod
    def _normalize_arch(arch: str) -> str:
        """Map architecture aliases (x64, x86_64, amd64) to canonical Docker architectures."""
        if arch in ("amd64", "x64", "x86_64"):
            return "amd64"
        return "arm64"

    def _image_tag_for_arch(self, arch: str) -> str:
        """Return the formatted Docker image tag for the specified architecture."""
        return f"{self.runner_image_prefix}:{self._normalize_arch(arch)}"

    def _image_exists(self, arch: str) -> bool:
        """Check whether the runner Docker image exists locally for the specified architecture."""
        image_tag = self._image_tag_for_arch(arch)
        try:
            res = subprocess.run(["docker", "image", "inspect", image_tag], capture_output=True)
            return res.returncode == 0
        except Exception:
            return False

    def _resolve_build_context_dir(self) -> str | None:
        """Locate the directory containing Dockerfile and runner bootstrap scripts."""
        candidates = []

        env_dir = os.getenv("RUNNER_IMAGE_DOCKER_DIR", "").strip()
        if env_dir:
            candidates.append(env_dir)

        module_relative = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docker"))
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

    def _build_runner_image(self, arch: str) -> bool:
        """Build the runner container image for the specified architecture."""
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)

        if self._image_exists(normalized_arch):
            print(f"[Autoscaler:Docker] Golden runner image '{image_tag}' already exists -- skipping build.")
            self._report_image_event("ready", normalized_arch, "Already built -- skipping.")
            return True

        build_context_dir = self._resolve_build_context_dir()
        if not build_context_dir:
            detail = (
                "Error: runner image build context not found. Expected a docker directory with "
                "Dockerfile/provision-toolchain.sh/start.sh. Set RUNNER_IMAGE_DOCKER_DIR or mount "
                "the repo into /workspace."
            )
            print(f"[Autoscaler:Docker] {detail}", file=sys.stderr)
            self._report_image_event("failed", normalized_arch, detail)
            return False

        print(f"[Autoscaler:Docker] 🏗️  Building missing golden runner image '{image_tag}' from '{build_context_dir}'...")
        self._report_image_event("building", normalized_arch, f"Building from '{build_context_dir}'...")

        # Cross-platform builds (e.g. linux/amd64 on Apple Silicon hosts)
        # require BuildKit/buildx. Falling back to legacy `docker build`
        # here produces misleading platform errors and never yields a usable
        # tag for the requested architecture.
        has_buildx = subprocess.run(["docker", "buildx", "version"], capture_output=True).returncode == 0
        if not has_buildx:
            detail = (
                "Error: docker buildx is not available in the autoscaler runtime. Install "
                "docker-buildx-plugin in the autoscaler image so missing runner images can be "
                "built automatically for the requested platform."
            )
            print(f"[Autoscaler:Docker] {detail}", file=sys.stderr)
            self._report_image_event("failed", normalized_arch, detail)
            return False

        try:
            subprocess.run(
                [
                    "docker",
                    "buildx",
                    "build",
                    "--load",
                    "--platform",
                    f"linux/{normalized_arch}",
                    "--build-arg",
                    f"TARGETARCH={normalized_arch}",
                    "-t",
                    image_tag,
                    "-f",
                    os.path.join(build_context_dir, "Dockerfile"),
                    build_context_dir,
                ],
                check=True,
                capture_output=True,
            )
            print(f"[Autoscaler:Docker] ✅ Golden runner image '{image_tag}' is ready.")
            self._report_image_event("ready", normalized_arch, "Build succeeded.")
            return True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
            print(
                f"[Autoscaler:Docker] Error building golden runner image '{image_tag}': {stderr}",
                file=sys.stderr,
            )
            self._report_image_event("failed", normalized_arch, f"Build failed: {stderr}")
            return False

    def _build_runner_image_async(self, arch: str) -> None:
        """Build the runner image for `arch` on a background thread (deduped, with backoff)."""
        normalized_arch = self._normalize_arch(arch)

        def on_failure(failures: int, cooldown: int) -> None:
            """Record runner image build failure event and log backoff duration."""
            detail = f"Failed {failures} time(s). Backing off {cooldown}s before retry."
            print(f"[Autoscaler:Docker] Golden runner image build for '{normalized_arch}' {detail}", file=sys.stderr)
            self._report_image_event("cooldown", normalized_arch, detail)

        self._backoff.run_async(
            normalized_arch,
            lambda: self._build_runner_image(normalized_arch),
            f"runzero-build-docker-{normalized_arch}",
            on_failure,
            "[Autoscaler:Docker]",
        )

    def ensure_runtime_assets(self, arch: str = "arm64") -> bool:
        """Ensure the runner container image for arch exists, triggering async build if missing."""
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)
        if self._image_exists(normalized_arch):
            return True

        with self._backoff.lock:
            already_building = normalized_arch in self._backoff.in_progress
            cooldown_remaining = self._backoff.remaining(normalized_arch)

        if already_building:
            print(f"[Autoscaler:Docker] Golden runner image '{image_tag}' is currently building. This queued job will be retried on the next poll.")
            return False

        if cooldown_remaining > 0:
            print(
                f"[Autoscaler:Docker] Golden runner image '{image_tag}' is missing, but build retry is "
                f"cooling down for {int(cooldown_remaining)}s after a previous failure.",
                file=sys.stderr,
            )
            return False

        print(
            f"[Autoscaler:Docker] Golden runner image '{image_tag}' is missing. Starting automatic background build now; this job will be retried once ready."
        )
        self._build_runner_image_async(normalized_arch)
        return False

    def _warn_if_registry_mirror_missing(self) -> None:
        """Warn once when host Docker daemon is not configured to use local mirror.

        Docker-backend runners share the host daemon via /var/run/docker.sock, so
        service image pulls and docker build layers inside jobs only hit our
        docker-mirror cache when the host daemon advertises it as a registry mirror.
        """
        if self._registry_mirror_checked:
            return
        self._registry_mirror_checked = True

        try:
            info = subprocess.run(
                ["docker", "info", "--format", "{{json .RegistryConfig.Mirrors}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except Exception:
            return

        if info.returncode != 0:
            return

        raw_stdout = info.stdout if isinstance(info.stdout, str) else ""
        try:
            mirrors = json.loads(raw_stdout.strip() or "[]")
        except (TypeError, json.JSONDecodeError):
            return
        if not isinstance(mirrors, list):
            return

        expected = {
            "http://localhost:49502",
            "https://localhost:49502",
            "http://host.orb.internal:49502",
            "https://host.orb.internal:49502",
        }
        if any(str(m).rstrip("/") in expected for m in mirrors):
            return

        print(
            "[Autoscaler:Docker] ⚠️ Host Docker daemon has no run-zero registry mirror configured "
            "(expected localhost:49502 or host.orb.internal:49502). Docker-backend job pulls may bypass "
            "local cache. Configure daemon.json registry-mirrors/insecure-registries accordingly.",
            file=sys.stderr,
        )

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
        """Launch a detached, ephemeral runner container via `docker run -d` and return its name.

        The container receives only a registration token (RUNNER_TOKEN), never the PAT.
        Returns None (and prints to stderr) if the inputs are invalid, no registration token
        can be obtained, or the `docker run` invocation itself fails; registration/execution
        then happens asynchronously inside the container's own entrypoint.
        """
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
        normalized_arch = self._normalize_arch(arch)
        image_tag = self._image_tag_for_arch(normalized_arch)
        platform_flag = f"linux/{normalized_arch}"

        if not self.ensure_runtime_assets(normalized_arch):
            return None

        registration_token = self._prepare_spawn(repo, org, labels, access_token, runner_token, extra_env)
        if not registration_token:
            return None

        if proxies_enabled:
            self._warn_if_registry_mirror_missing()

        default_labels = f"self-hosted,local,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,x64,amd64"

        runner_labels = merge_labels(default_labels, labels)

        cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--platform",
            platform_flag,
            "--network",
            self.network,
            # Headless Chrome (Lighthouse CI, Playwright) needs to create its own
            # user/PID namespace for its internal sandbox, which Docker blocks by
            # default. GitHub-hosted runners never hit this because they're full
            # VMs, not containers. Jobs only skip this container path when a VM
            # driver is available AND the job needs one -- its workflow declares
            # `services:`/`container:`, or a VM_TRIGGER_LABELS entry appears in its
            # labels or job-name tokens (see router.select_driver_for_job). Every
            # other job, including browser-driven ones, lands here.
            "--cap-add",
            "SYS_ADMIN",
            "--label",
            "managed-by=local-autoscaler",
            "--label",
            "backend=docker",
            "--label",
            f"target-repo={repo or ''}",
            "--label",
            f"target-arch={arch}",
            "-e",
            f"RUNNER_TOKEN={registration_token}",
            "-e",
            f"RUNNER_NAME={container_name}",
            "-e",
            f"RUNNER_LABELS={runner_labels}",
            "-e",
            "EPHEMERAL=true",
            "-e",
            "RUNNER_WORKDIR=_work",
            "-e",
            "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
            "-v",
            f"{self.docker_sock}:/var/run/docker.sock",
        ]

        if self.runner_cpus:
            cmd.extend(["--cpus", self.runner_cpus])
        if self.runner_memory:
            cmd.extend(["--memory", self.runner_memory])

        if proxies_enabled:
            # When on host network, access proxies on published localhost ports
            verdaccio_url = "http://localhost:49501/" if self.network == "host" else "http://verdaccio:4873/"
            athens_url = (
                "http://localhost:49500,https://proxy.golang.org,direct" if self.network == "host" else "http://athens:3000,https://proxy.golang.org,direct"
            )
            # devpi's default "root/pypi" index is a real pull-through PyPI mirror out of the
            # box; pip and uv both honor PIP_INDEX_URL, and uv additionally reads UV_INDEX_URL.
            pip_host = "localhost:49507" if self.network == "host" else "devpi:3141"
            pip_index_url = f"http://{pip_host}/root/pypi/+simple/"
            cmd.extend(
                [
                    "-e",
                    f"NPM_CONFIG_REGISTRY={verdaccio_url}",
                    "-e",
                    f"YARN_REGISTRY={verdaccio_url}",
                    "-e",
                    f"GOPROXY={athens_url}",
                    "-e",
                    f"PIP_INDEX_URL={pip_index_url}",
                    "-e",
                    f"UV_INDEX_URL={pip_index_url}",
                ]
            )
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

    def list_runners(self) -> list[RunnerInfo]:
        """List containers labeled `managed-by=local-autoscaler` via `docker ps -a`.

        Returns an empty list (and prints to stderr) if the `docker ps` call itself fails.
        """
        try:
            res = subprocess.run(
                ["docker", "ps", "-a", "--filter", "label=managed-by=local-autoscaler", "--format", _PS_FORMAT], capture_output=True, text=True, check=True
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
                    runners.append(
                        RunnerInfo(
                            id=parts[0],
                            status=parts[1],
                            name=parts[2],
                            state=state,
                            target_repo=parts[4],
                            target_arch=parts[5],
                            backend=backend,
                            created_at=created_at,
                        )
                    )
            return runners
        except Exception as e:
            print(f"[Autoscaler:Docker] Docker ps error: {e}", file=sys.stderr)
            return []

    @staticmethod
    def _parse_created_at(raw: str) -> float | None:
        """Parse Docker CreatedAt timestamp string into POSIX epoch timestamp."""
        # Docker's `--format {{.CreatedAt}}` is e.g. "2026-08-25 14:38:53 +0200
        # CEST" -- the trailing zone abbreviation isn't reliably parseable by
        # strptime's %Z across platforms/locales, but the numeric UTC offset
        # right before it is, so only the first three tokens are used.
        try:
            date_part, time_part, offset, *_ = raw.strip().split()
            return datetime.strptime(f"{date_part} {time_part} {offset}", "%Y-%m-%d %H:%M:%S %z").timestamp()
        except (ValueError, IndexError):
            return None

    def prune_exited(self, runners: list[RunnerInfo]) -> None:
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
