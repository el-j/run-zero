"""
True end-to-end test for the Docker engine path (issue #14).

SCOPE -- read this before adding to or relying on this file. This is the ONE
test class in the whole suite that talks to a real, unmocked Docker daemon.
It proves the full REAL container lifecycle that `drivers/docker_driver.py`
itself owns and orchestrates via real `subprocess.run(["docker", ...])`
calls:

  1. real `docker build` of a tiny, disposable test image
  2. real `DockerDriver.spawn_runner()` -> a real `docker run -d` call that
     creates a genuine, running container
  3. a real `docker exec` into that container, proving a command actually
     executes inside it (not a mock, not a dry run)
  4. real `DockerDriver.list_runners()` -> a real `docker ps -a` call,
     parsed, confirming the driver's own view of the fleet matches reality
  5. real `DockerDriver.destroy_runner()` -> a real `docker rm -f` call,
     confirmed by a real `docker inspect` afterwards showing the container
     is actually gone

WHAT THIS DELIBERATELY DOES **NOT** COVER (be honest about the boundary --
see issue #14's own Definition of Done):

  - No real GitHub Actions runner registration token exchange happens. The
    test image's entrypoint is a plain `sleep`, not the real
    `docker/start.sh` -> `config.sh`/`run.sh` registration pipeline that a
    production runner container executes. The `access_token` passed to
    `spawn_runner()` is a throwaway string the image never reads.
  - No real GitHub repo, queued job, or job execution is involved. This
    proves the driver's own container-lifecycle plumbing, not the
    "register -> pick up a real job -> report back" pipeline.
  - The production runner image (`docker/Dockerfile`) is never built or
    exercised here -- that image takes minutes to build and needs its own
    toolchain provisioning; using it would make this test slow and
    environment-dependent for a boundary this test isn't trying to cover
    anyway.

Real GitHub registration was considered and deliberately NOT attempted here:
doing so safely would require a disposable, sandboxed repo with a guaranteed
cleanup path, which isn't available in this environment. Registering even a
short-lived phantom runner against a real project repo risks disrupting its
real CI if cleanup fails for any reason -- not a risk worth taking to widen
this test's scope. See docs/E2E_TESTING.md at the repo root for the manual,
human-run runbook covering what genuinely can't be automated in CI at all:
the OrbStack VM engine, WSL2, and Multipass.

Skipped cleanly (not a hard failure) wherever the `docker` CLI isn't on PATH
or the daemon isn't reachable -- this keeps `make test-suite`'s inner
`python:3.11-slim` container (which has no Docker socket) green, while still
running for real on any CI runner or dev machine that does have Docker
(GitHub-hosted `ubuntu-latest` runners do, out of the box).
"""

import platform
import shutil
import subprocess
import unittest
import uuid

from drivers.docker_driver import DockerDriver

TEST_IMAGE_REPO = "runzero-e2e-test-runner"

_TEST_DOCKERFILE = b"""\
FROM alpine:3.20
CMD ["sleep", "3600"]
"""


def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def _host_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return "amd64"


@unittest.skipUnless(_docker_available(), "Docker daemon not available on this host/CI runner")
class TestDockerEngineEndToEnd(unittest.TestCase):
    """Real, unmocked Docker container lifecycle via DockerDriver's own real subprocess calls."""

    @classmethod
    def setUpClass(cls):
        cls.arch = _host_arch()
        cls.image_tag = f"{TEST_IMAGE_REPO}:{cls.arch}"
        build = subprocess.run(
            ["docker", "build", "--platform", f"linux/{cls.arch}", "-t", cls.image_tag, "-"],
            input=_TEST_DOCKERFILE,
            capture_output=True,
            timeout=120,
        )
        if build.returncode != 0:
            raise unittest.SkipTest(
                f"could not build disposable e2e test image (docker build exited {build.returncode}): "
                f"{build.stderr.decode(errors='replace')}"
            )

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker", "rmi", "-f", cls.image_tag], capture_output=True)

    def test_real_container_create_exec_list_destroy_lifecycle(self):
        driver = DockerDriver(runner_image_prefix=TEST_IMAGE_REPO)
        repo = f"el-j/run-zero-e2e-scratch-{uuid.uuid4().hex[:8]}"

        # 1. Real container creation via the driver's real `docker run -d`.
        runner_id = driver.spawn_runner(
            repo=repo,
            arch=self.arch,
            access_token="e2e-test-token-never-read-by-the-sleep-entrypoint",
            proxies_enabled=False,
        )
        self.assertIsNotNone(runner_id, "spawn_runner() failed to create a real container")
        # Guaranteed real cleanup even if a later assertion fails.
        self.addCleanup(lambda: subprocess.run(["docker", "rm", "-f", runner_id], capture_output=True))

        # 2. Real command execution inside the real container.
        marker = f"real-e2e-exec-{uuid.uuid4().hex[:8]}"
        exec_res = subprocess.run(
            ["docker", "exec", runner_id, "sh", "-c", f"echo {marker}"],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(exec_res.returncode, 0, f"docker exec failed: {exec_res.stderr}")
        self.assertIn(marker, exec_res.stdout)

        # 3. The driver's own real `docker ps -a` parsing must agree the
        #    container it just created is really running.
        runners = driver.list_runners()
        matching = [r for r in runners if r.id.startswith(runner_id[:12]) or r.name == runner_id]
        self.assertTrue(matching, f"list_runners() did not find real container {runner_id}")
        self.assertEqual(matching[0].state, "running")
        self.assertEqual(matching[0].backend, "docker")
        self.assertEqual(matching[0].target_repo, repo)

        # 4. Real teardown via the driver's real `docker rm -f`.
        destroyed = driver.destroy_runner(runner_id)
        self.assertTrue(destroyed)

        # 5. Confirm it is REALLY gone (not just that destroy_runner()
        #    returned True) via a fresh `docker inspect`.
        inspect_res = subprocess.run(["docker", "inspect", runner_id], capture_output=True)
        self.assertNotEqual(inspect_res.returncode, 0, "container still exists after destroy_runner()")


if __name__ == "__main__":
    unittest.main()
