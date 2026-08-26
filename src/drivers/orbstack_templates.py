"""
Shell script generation templates for OrbStack Linux VM provisioning.
"""


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
    proxy_env_block: str
) -> str:
    """Generate shell snippet for obtaining registration token, registering with config.sh, and executing run.sh."""
    return f"""
sudo systemctl start docker 2>/dev/null || true
sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
sudo mkdir -p /home/runner/go/bin /home/runner/go/pkg /opt/hostedtoolcache /home/runner/.cache
sudo chown -R runner:runner /home/runner /opt/hostedtoolcache 2>/dev/null || true
sudo chmod -R 777 /home/runner/go /opt/hostedtoolcache /home/runner/.cache 2>/dev/null || true
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
