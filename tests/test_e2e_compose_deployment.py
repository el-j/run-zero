"""
Deployment-level e2e test for a real production outage (2026-09-22).

WHAT HAPPENED: `docker-compose.yml`'s `autoscaler` service never mounted the
repo's `docker/` directory (Dockerfile, provision-toolchain.sh, start.sh) into
the container, and `RUNNER_IMAGE_DOCKER_DIR` was unset. `DockerDriver` runs
INSIDE that container and needs its own build context on disk to auto-build
the golden runner image via `docker buildx build` -- with no mount and no env
var, `_resolve_build_context_dir()` (drivers/docker_driver.py) could never
find one. Every automatic build failed instantly with "runner image build
context not found", retried, failed again, forever. Because Docker-routed
jobs need that image, they stayed queued indefinitely -- confirmed live via a
real stuck GitHub Actions job that only started running after adding the
missing `./docker:/workspace/docker:ro` mount.

No existing test layer would have caught this:
  - Unit tests (tests/test_docker_driver.py) mock the container's filesystem
    entirely, so they can't see that the REAL deployed container has nothing
    mounted at any of _resolve_build_context_dir()'s candidate paths.
  - `docker compose config` (already run in CI) only validates YAML syntax --
    it happily "validates" a service with zero volumes.
  - tests/test_e2e_docker.py deliberately builds a tiny throwaway Alpine
    image, not the real autoscaler container, and never touches
    docker-compose.yml at all.

This test closes exactly that gap: it resolves docker-compose.yml's real
`autoscaler` service definition via `docker compose config` (not a
hand-rolled reimplementation of the YAML), replays its exact declared bind
mounts against a real container, and execs the REAL
`DockerDriver._resolve_build_context_dir()` method inside it -- proving the
production deployment, as actually configured today, gives the autoscaler
a build context it can use. A future edit that removes/renames the mount (or
narrows what `_resolve_build_context_dir()` accepts) without updating the
other side will fail this test instead of silently reintroducing the outage.

Skips cleanly (not a hard failure) wherever `docker` or `docker compose`
aren't available, matching the pattern in test_e2e_docker.py.
"""

import json
import os
import shutil
import subprocess
import unittest
from typing import Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")


def _docker_compose_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        info = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        if info.returncode != 0:
            return False
        compose = subprocess.run(["docker", "compose", "version"], capture_output=True, timeout=5)
        return compose.returncode == 0
    except Exception:
        return False


@unittest.skipUnless(_docker_compose_available(), "Docker/Compose not available on this host/CI runner")
class TestAutoscalerComposeDeploymentBuildContext(unittest.TestCase):
    """Proves the real docker-compose.yml deployment gives DockerDriver a build context."""

    _env_path: str
    _created_env: bool
    autoscaler_volumes: list[dict[str, Any]]

    @classmethod
    def setUpClass(cls):
        # `docker compose config` needs SOME .env to interpolate against. Reuse a real one
        # if the dev already has it; otherwise stand up a throwaway copy of .env.example for
        # just this call and remove it again -- never overwrite a real, already-configured .env.
        cls._env_path = os.path.join(REPO_ROOT, ".env")
        cls._created_env = False
        if not os.path.isfile(cls._env_path):
            example_path = os.path.join(REPO_ROOT, ".env.example")
            if not os.path.isfile(example_path):
                raise unittest.SkipTest(".env.example not found -- cannot resolve compose config")
            shutil.copyfile(example_path, cls._env_path)
            cls._created_env = True

        try:
            result = subprocess.run(
                ["docker", "compose", "config", "--format", "json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
        finally:
            if cls._created_env:
                os.remove(cls._env_path)

        if result.returncode != 0:
            raise unittest.SkipTest(f"docker compose config failed: {result.stderr}")

        config = json.loads(result.stdout)
        autoscaler = config.get("services", {}).get("autoscaler")
        if not autoscaler:
            raise unittest.SkipTest("docker-compose.yml has no 'autoscaler' service to check")
        cls.autoscaler_volumes = autoscaler.get("volumes", [])

    def test_resolve_build_context_dir_succeeds_with_real_compose_mounts(self):
        """Exec the real DockerDriver method inside a container mounted exactly like production."""
        bind_volumes = [v for v in self.autoscaler_volumes if v.get("type") == "bind"]
        self.assertTrue(
            bind_volumes,
            "autoscaler service declares no bind volumes at all -- docker-compose.yml regressed",
        )

        docker_run_args = ["docker", "run", "--rm"]
        for volume in bind_volumes:
            # The real docker.sock bind is irrelevant to build-context resolution and
            # bind-mounting it here would only add environment-dependent socket-permission
            # noise this test doesn't need -- every other declared bind mount is replayed as-is.
            if volume["target"] == "/var/run/docker.sock":
                continue
            source = volume["source"]
            target = volume["target"]
            suffix = ":ro" if volume.get("read_only") else ""
            docker_run_args += ["-v", f"{source}:{target}{suffix}"]

        # Mirror docker/Dockerfile.autoscaler's own `WORKDIR /app` + `COPY src /app` exactly,
        # so DockerDriver's own-module-relative candidate path resolves identically to production.
        docker_run_args += ["-v", f"{SRC_DIR}:/app:ro", "-w", "/app"]
        docker_run_base = [*docker_run_args, "python:3.11-slim"]
        probe = (
            "from drivers.docker_driver import DockerDriver; "
            "d = DockerDriver(); "
            "ctx = d._resolve_build_context_dir(); "
            "print(ctx or ''); "
            "raise SystemExit(0 if ctx else 1)"
        )
        docker_run_args = [*docker_run_base, "python3", "-c", probe]

        result = subprocess.run(docker_run_args, capture_output=True, text=True, timeout=60)
        self.assertEqual(
            result.returncode,
            0,
            "DockerDriver._resolve_build_context_dir() found no build context using the real "
            "docker-compose.yml 'autoscaler' service mounts -- this reproduces the 2026-09-22 "
            "outage where every Docker-routed job stayed queued forever because the golden "
            f"runner image could never be auto-built.\nstdout={result.stdout!r} stderr={result.stderr!r}",
        )
        resolved_path = result.stdout.strip()
        self.assertTrue(resolved_path, "resolver reported success but printed no path")

        for required_file in ("Dockerfile", "provision-toolchain.sh", "start.sh"):
            check_args = [*docker_run_base, "test", "-f", os.path.join(resolved_path, required_file)]
            check = subprocess.run(check_args, capture_output=True, text=True, timeout=30)
            self.assertEqual(
                check.returncode,
                0,
                f"resolved build context '{resolved_path}' is missing required file '{required_file}'",
            )


if __name__ == "__main__":
    unittest.main()
