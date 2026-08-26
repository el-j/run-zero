"""
Shell script generation templates for OrbStack Linux VM provisioning.
"""

from typing import Dict, Optional


def cache_mount_snippet(cache_mounts: Optional[Dict[str, str]]) -> str:
    """Generate a shell snippet that bind-mounts host-backed package caches into this VM.

    A Docker container shares the host's mount namespace, so `DockerDriver` can turn
    `cache_mounts` (host path -> container path) directly into `-v host:container` bind
    mounts. An OrbStack VM is a real, separate guest filesystem -- there's no `-v` flag --
    but every non-isolated OrbStack VM (the kind this driver creates; `--isolated`/`--mount`
    is a different, opt-in mode) automatically virtiofs-shares the ENTIRE host macOS
    filesystem into the guest at a fixed path, `/mnt/mac<absolute-macOS-path>`. Confirmed
    live (2026-08-26): a file written from inside a VM under `/mnt/mac/Users/...` appears
    immediately, with matching ownership, at the real `/Users/...` path on the host and vice
    versa, and `mount --bind /mnt/mac/<path> <container-style-path>` inside the guest
    transparently round-trips writes to real host disk -- see docs/README caching section.
    That makes a real, kernel-level bind mount possible without any extra OrbStack
    configuration: bind the `/mnt/mac`-relative source onto the destination path so package
    managers see an ordinary local directory that happens to persist on the real host disk
    across every VM cloned from this golden image.

    Returns "" when `cache_mounts` is empty/None (matches `if cache_mounts:` guards
    elsewhere in the codebase -- no snippet, no bind mounts, VM behaves as before).
    """
    if not cache_mounts:
        return ""

    lines = [
        "# Bind-mount host-backed package caches via OrbStack's automatic /mnt/mac host share",
        "# (see cache_mount_snippet() in orbstack_templates.py for why this works).",
    ]
    for host_path, container_path in cache_mounts.items():
        mac_path = f"/mnt/mac{host_path}"
        lines.append(f'sudo mkdir -p "{container_path}"')
        lines.append(
            f'if [ -d "{mac_path}" ]; then\n'
            f'  sudo mount --bind "{mac_path}" "{container_path}" || '
            f'echo "Warning: cache bind mount failed for {container_path}" >&2\n'
            f"else\n"
            f'  echo "Warning: host cache dir {mac_path} not visible via OrbStack mac share -- '
            f'skipping mount for {container_path}" >&2\n'
            f"fi"
        )
    return "\n".join(lines)


def docker_engine_snippet() -> str:
    """Generate shell snippet for installing full Docker daemon inside the VM."""
    return """
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/docker.asc
sudo install -m 0644 /tmp/docker.asc /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \\
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker runner

# Docker's default cgroup driver on Ubuntu 24.04 is "systemd" -- it asks the
# guest's systemd to create a transient scope unit (via dbus) for every
# container it starts. That works on a real kernel, but this VM is itself an
# OrbStack "scon" (an LXC-style container running inside one shared master
# VM, not independent hardware virtualization -- see OrbStack's own
# architecture). In that nested setup, systemd's kernel-thread check for the
# new scope's cgroup.procs entries fails against the guest's /proc with
# ENOTTY, which reads as: "Failed to determine whether process N is a kernel
# thread: Inappropriate ioctl for device", and every `docker start` (incl.
# GitHub Actions service containers like postgres) fails immediately.
# cgroupfs manages the same cgroup v2 hierarchy directly, bypassing
# systemd-managed scope units entirely, and needs no such kernel support.
# Reproduced and confirmed live in this exact VM image (2026-08-26): systemd
# driver reliably fails `docker start`; cgroupfs starts the same container
# cleanly.
#
# registry-mirrors points every `docker pull`/`docker create` at the stack's
# own pull-through cache (docker-compose.yml's "docker-mirror" service, a
# registry:2 proxying registry-1.docker.io) instead of Docker Hub directly.
# Without this, every image pull -- including GitHub Actions service
# containers like postgres, which get pulled fresh on every single ephemeral
# VM -- bypasses the mirror entirely and re-downloads from the internet every
# time (confirmed live 2026-08-26: docker-mirror-storage sat at 0 bytes after
# dozens of pulls this session, while verdaccio/athens/apt-cacher -- which ARE
# wired via env vars -- had real cached data). insecure-registries is
# required alongside it: dockerd refuses a registry-mirrors entry served over
# plain HTTP otherwise, and the local mirror has no TLS cert.
echo '{"exec-opts": ["native.cgroupdriver=cgroupfs"], "registry-mirrors": ["http://host.orb.internal:49502"], "insecure-registries": ["host.orb.internal:49502"]}' | sudo tee /etc/docker/daemon.json > /dev/null
sudo systemctl enable docker
"""


def runner_download_snippet(orb_arch: str, runner_version: str = "2.336.0") -> str:
    """Generate shell snippet for downloading and unpacking the GitHub Actions runner package."""
    return f"""
mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v{runner_version}/actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
rm "./actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
sudo ./bin/installdependencies.sh
"""


def registration_and_run_snippet(
    api_base: str,
    runner_url: str,
    access_token: str,
    vm_name: str,
    runner_labels: str,
    proxy_env_block: str,
    cache_mount_block: str = ""
) -> str:
    """Generate shell snippet for obtaining registration token, registering with config.sh, and executing run.sh.

    `cache_mount_block` (from `cache_mount_snippet()`) runs after the base directory
    chown/chmod pass and before the proxy env vars are exported, so the bind-mounted cache
    directories are in place -- with the right ownership underneath them -- before the job's
    own tooling starts reading/writing to them. Defaults to "" (no-op) so existing callers
    that don't pass it behave exactly as before.
    """
    return f"""
sudo systemctl start docker 2>/dev/null || true
sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
sudo mkdir -p /home/runner/go/bin /home/runner/go/pkg /opt/hostedtoolcache /home/runner/.cache
sudo chown -R runner:runner /home/runner /opt/hostedtoolcache 2>/dev/null || true
sudo chmod -R 777 /home/runner/go /opt/hostedtoolcache /home/runner/.cache 2>/dev/null || true
{cache_mount_block}
{proxy_env_block}
cd /home/runner/actions-runner

echo "Fetching registration token from GitHub API..."
TOKEN_RESPONSE=$(curl -s -X POST \\
  -H "Authorization: Bearer {access_token}" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  "{api_base}/registration-token")
REG_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token // empty')
if [ -z "$REG_TOKEN" ] || [ "$REG_TOKEN" = "null" ]; then
  echo "Error: Failed to obtain registration token. Response: $TOKEN_RESPONSE"
  exit 1
fi

./config.sh --url "{runner_url}" --token "$REG_TOKEN" --name "{vm_name}" --work "_work" \\
  --unattended --replace --ephemeral --labels "{runner_labels}"

echo "Starting runner {vm_name}..."
./run.sh || true

echo "Ephemeral run finished -- powering off so the autoscaler prunes this VM."
sudo systemctl poweroff 2>/dev/null || sudo poweroff 2>/dev/null || sudo shutdown -h now 2>/dev/null || true
"""
