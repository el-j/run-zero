"""
Tests for the OrbStack shell-script templates (drivers.orbstack_templates).
"""

import unittest

from drivers.orbstack_templates import (
    cache_mount_snippet,
    docker_engine_snippet,
    registration_and_run_snippet,
    runner_download_snippet,
)


class TestOrbStackTemplates(unittest.TestCase):
    def test_snippets_generate_valid_bash(self):
        engine = docker_engine_snippet()
        self.assertIn("docker-ce", engine)
        self.assertIn("systemctl enable docker", engine)

    def test_docker_engine_uses_cgroupfs_driver(self):
        # Regression test: Docker's default "systemd" cgroup driver asks the
        # guest's systemd to create a transient scope unit (via dbus) for
        # every container started. The golden VM is itself an OrbStack
        # "scon" (an LXC-style container inside one shared master VM, not
        # independent hardware virtualization), and in that nested setup
        # systemd's kernel-thread check for the new scope fails against the
        # guest's /proc with ENOTTY: "Failed to determine whether process N
        # is a kernel thread: Inappropriate ioctl for device" -- so every
        # `docker start` (including GitHub Actions service containers like
        # postgres) failed immediately. Reproduced live in the actual golden
        # base VM and confirmed the systemd driver fails while cgroupfs
        # (which manages the cgroup v2 hierarchy directly, without asking
        # systemd for a scope unit) starts the same container cleanly.
        engine = docker_engine_snippet()
        self.assertIn('"exec-opts": ["native.cgroupdriver=cgroupfs"]', engine)
        self.assertIn("/etc/docker/daemon.json", engine)

    def test_docker_engine_uses_registry_mirror(self):
        # Regression test: without a registry-mirrors entry, every `docker
        # pull`/`docker create` inside the VM (including GitHub Actions
        # service containers like postgres, pulled fresh on every ephemeral
        # VM) goes straight to Docker Hub, bypassing the stack's own
        # pull-through cache (docker-compose.yml's "docker-mirror" service)
        # entirely. Confirmed live (2026-08-26): docker-mirror-storage sat at
        # 0 bytes after dozens of pulls this session; after adding this
        # config, `docker info` reported the mirror active and a single pull
        # inside a real VM grew the mirror's storage volume from 0 to 3.4M.
        engine = docker_engine_snippet()
        self.assertIn('"registry-mirrors": ["http://host.orb.internal:49502"]', engine)
        # Required alongside it: dockerd refuses a plain-HTTP registry-mirrors
        # entry unless it's also listed in insecure-registries.
        self.assertIn('"insecure-registries": ["host.orb.internal:49502"]', engine)

    def test_other_snippets_generate_valid_bash(self):
        dl = runner_download_snippet("amd64", "2.336.0")
        self.assertIn("actions-runner-linux-${RUNNER_ARCH}-2.336.0.tar.gz", dl)

        reg = registration_and_run_snippet(
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
        )
        # The VM registers with the host-issued registration token; it never calls the
        # registration-token API itself (that would require the PAT inside the VM).
        self.assertNotIn("registration-token", reg)
        self.assertNotIn("Authorization", reg)
        self.assertIn("--token reg-token", reg)
        self.assertIn("./config.sh", reg)
        self.assertIn("./run.sh", reg)
        # Default cache_mount_block is "" -- no bind-mount lines injected when the
        # caller (e.g. an existing test) doesn't pass one.
        self.assertNotIn("mount --bind", reg)

    def test_registration_and_run_snippet_includes_cache_mount_block(self):
        reg = registration_and_run_snippet(
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
            cache_mount_block="sudo mount --bind /mnt/mac/fake /home/runner/.npm",
        )
        # Cache mounts must land before the proxy env vars are exported and before
        # config.sh/run.sh execute, so the directories are ready before the job's own
        # tooling (and the proxy-aware env) starts using them.
        mount_idx = reg.index("mount --bind")
        proxy_idx = reg.index("export PROXY=1")
        config_idx = reg.index("./config.sh")
        self.assertLess(mount_idx, proxy_idx)
        self.assertLess(proxy_idx, config_idx)

    def test_registration_and_run_snippet_includes_network_self_healing(self):
        reg = registration_and_run_snippet(
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
        )
        self.assertIn("DHCP unfulfilled on eth0", reg)
        self.assertIn("192.168.139.1", reg)
        self.assertIn("nameserver 0.250.250.200", reg)
        self.assertIn("nameserver 1.1.1.1", reg)
        self.assertIn("api.github.com reachable", reg)

    def test_cache_mount_snippet_empty_when_no_mounts(self):
        self.assertEqual(cache_mount_snippet(None), "")
        self.assertEqual(cache_mount_snippet({}), "")

    def test_cache_mount_snippet_generates_bind_mount_via_mac_share(self):
        snippet = cache_mount_snippet(
            {
                "/Users/dev/.local-github-runner/cache/npm": "/home/runner/.npm",
                "/Users/dev/.local-github-runner/cache/pip": "/home/runner/.cache/pip",
            }
        )
        # Every host path must be translated to OrbStack's automatic
        # /mnt/mac<absolute-macOS-path> share, and bind-mounted onto the exact
        # container-style destination path cache_manager.py expects.
        self.assertIn("sudo mkdir -p /home/runner/.npm", snippet)
        self.assertIn(
            "sudo mount --bind /mnt/mac/Users/dev/.local-github-runner/cache/npm /home/runner/.npm",
            snippet,
        )
        self.assertIn("sudo mkdir -p /home/runner/.cache/pip", snippet)
        self.assertIn(
            "sudo mount --bind /mnt/mac/Users/dev/.local-github-runner/cache/pip /home/runner/.cache/pip",
            snippet,
        )
        # Must guard against the mac share not (yet) exposing the path rather than
        # blowing up the whole provisioning script.
        self.assertIn("Warning: host cache dir", snippet)
        self.assertIn("Warning: cache bind mount failed", snippet)

    def test_cache_mount_snippet_chowns_runner_ancestor_directories(self):
        snippet = cache_mount_snippet({"/Users/dev/.local-github-runner/cache/rust": "/home/runner/.cargo/registry"})
        self.assertIn("sudo mkdir -p /home/runner/.cargo/registry", snippet)
        self.assertIn('sudo chown runner:runner "$_p"', snippet)
        self.assertIn("sudo chown runner:runner /home/runner/.cargo/registry", snippet)

    def test_cache_mount_snippet_quotes_hostile_paths(self):
        # cache_mounts can arrive over the bridge; a path must never break out of its word.
        snippet = cache_mount_snippet({'/Users/x"; touch /tmp/pwned; "': "/home/runner/$(id)"})
        self.assertNotIn("$(id)\n", snippet.replace("'/home/runner/$(id)'", ""))
        self.assertIn("'/home/runner/$(id)'", snippet)
        self.assertIn("'/mnt/mac/Users/x\"; touch /tmp/pwned; \"'", snippet)


if __name__ == "__main__":
    unittest.main()
