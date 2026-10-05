"""
Shell script generation templates for OrbStack Linux VM provisioning.

Every caller-supplied value interpolated into a script goes through `shlex.quote`.
"""

import shlex
from collections.abc import Callable

from .runner_bootstrap import POWEROFF, register_and_run_snippet, runner_download_snippet

__all__ = ["cache_mount_snippet", "docker_engine_snippet", "registration_and_run_snippet", "runner_download_snippet"]


def cache_mount_snippet(cache_mounts: dict[str, str] | None, host_to_guest: Callable[[str], str] | None = None) -> str:
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

    `host_to_guest` maps a host path to where the guest sees it; the default is OrbStack's
    `/mnt/mac<path>` share (WSL2 passes its `/mnt/<drive>/...` translation instead).

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
        mac = shlex.quote(host_to_guest(host_path) if host_to_guest else f"/mnt/mac{host_path}")
        dest = shlex.quote(container_path)
        lines.append(f"sudo mkdir -p {dest}")
        if container_path.startswith("/home/runner/"):
            lines.append(
                f"_p={dest}\n"
                f'while [ "$_p" != "/home/runner" ] && [ "$_p" != "/" ] && [ "$_p" != "." ]; do\n'
                f'  sudo chown runner:runner "$_p" 2>/dev/null || true\n'
                f'  _p="$(dirname "$_p")"\n'
                f"done\n"
                f"sudo chown runner:runner {dest} 2>/dev/null || true"
            )
        lines.append(
            f"if [ -d {mac} ]; then\n"
            f"  sudo mount --bind {mac} {dest} || "
            f"echo 'Warning: cache bind mount failed for' {dest} >&2\n"
            f"  sudo chmod 777 {dest} 2>/dev/null || true\n"
            f"  sudo chown runner:runner {dest} 2>/dev/null || true\n"
            f"else\n"
            f"  echo 'Warning: host cache dir not visible in the guest, skipping mount:' {mac} {dest} >&2\n"
            f"fi"
        )
    return "\n".join(lines)


def docker_engine_snippet() -> str:
    """Generate shell snippet for installing full Docker daemon inside the VM."""
    return """
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/docker.asc
sudo install -m 0644 /tmp/docker.asc /etc/apt/keyrings/docker.asc
DOCKER_APT_ARCH=$(dpkg --print-architecture)
DOCKER_APT_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
echo "deb [arch=$DOCKER_APT_ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $DOCKER_APT_CODENAME stable" | \\
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
sudo tee /etc/docker/daemon.json > /dev/null <<'DAEMONJSON'
{
  "exec-opts": ["native.cgroupdriver=cgroupfs"],
  "registry-mirrors": ["http://host.orb.internal:49502"],
  "insecure-registries": ["host.orb.internal:49502"]
}
DAEMONJSON
sudo systemctl enable docker
"""


def registration_and_run_snippet(
    runner_url: str,
    registration_token: str,
    vm_name: str,
    runner_labels: str,
    proxy_env_block: str,
    cache_mount_block: str = "",
    runner_env: dict[str, str] | None = None,
) -> str:
    """Generate the shell snippet that registers the runner with config.sh and executes run.sh.

    `registration_token` is the short-lived token the host exchanged the PAT for
    (see `github_api.create_registration_token`); the PAT itself never enters the VM.
    `runner_url`, `registration_token`, `vm_name` and `runner_labels` are shell-quoted.

    `cache_mount_block` (from `cache_mount_snippet()`) runs after the base directory
    chown/chmod pass and before the proxy env vars are exported, so the bind-mounted cache
    directories are in place -- with the right ownership underneath them -- before the job's
    own tooling starts reading/writing to them. Defaults to "" (no-op) so existing callers
    that don't pass it behave exactly as before.

    `runner_env` (see `runner_env.cache_env`) is exported right before `run.sh`.
    """
    return f"""
# --- 1. Ensure IPv4 network connectivity (self-healing for OrbStack DHCP bug #2688) ---
has_ipv4=0
for i in 1 2 3 4 5; do
  if ip -4 addr show dev eth0 2>/dev/null | grep -q "inet "; then
    has_ipv4=1
    break
  fi
  sleep 1
done

if [ "$has_ipv4" -eq 0 ]; then
  echo "[RunZero Network] DHCP unfulfilled on eth0. Finding available IP in 192.168.139.0/23..."
  MAC_LAST=$(cat /sys/class/net/eth0/address 2>/dev/null | awk -F: '{{print $NF}}')
  START_OFF=$(( (16#${{MAC_LAST:-01}} % 150) + 60 ))
  FALLBACK_IP=""
  for off in $(seq $START_OFF 245) $(seq 60 $((START_OFF - 1))); do
    cand="192.168.139.$off"
    if ! ping -c 1 -W 1 "$cand" >/dev/null 2>&1; then
      FALLBACK_IP="$cand"
      break
    fi
  done
  if [ -z "$FALLBACK_IP" ]; then
    FALLBACK_IP="192.168.139.$(( (RANDOM % 150) + 60 ))"
  fi
  echo "[RunZero Network] Assigning fallback IP $FALLBACK_IP/23 (gw 192.168.139.1)..."
  sudo ip addr add "$FALLBACK_IP/23" dev eth0 2>/dev/null || true
  sudo ip route add default via 192.168.139.1 dev eth0 2>/dev/null || true
fi

# Ensure DNS resolution works
if ! curl -s --connect-timeout 2 -I https://api.github.com >/dev/null 2>&1; then
  echo "[RunZero Network] Ensuring resilient DNS..."
  sudo rm -f /etc/resolv.conf
  echo -e "nameserver 0.250.250.200\\nnameserver 1.1.1.1\\nnameserver 8.8.8.8" | sudo tee /etc/resolv.conf >/dev/null
fi

# Wait up to 15s for outbound connectivity to GitHub
for net_check in 1 2 3 4 5 6 7 8; do
  if curl -s --connect-timeout 3 -I https://api.github.com >/dev/null 2>&1; then
    echo "[RunZero Network] Network ready (api.github.com reachable)."
    break
  fi
  echo "[RunZero Network] Waiting for GitHub reachability (check $net_check/8)..."
  sleep 2
done

sudo systemctl start docker 2>/dev/null || true
sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
sudo mkdir -p /home/runner/go/bin /home/runner/go/pkg /opt/hostedtoolcache /home/runner/.cache /home/runner/.cargo /home/runner/.local/bin /home/runner/.nuget
sudo chown -R runner:runner /home/runner /opt/hostedtoolcache 2>/dev/null || true
sudo chmod -R 777 /home/runner/go /opt/hostedtoolcache /home/runner/.cache 2>/dev/null || true
{cache_mount_block}
# -xdev: fix local dirs created around the mounts, but never walk the host-backed caches
# themselves (already runner-owned via virtiofs; ~100k files = seconds per job, #67).
sudo find /home/runner/.cache /home/runner/go /home/runner/.cargo /home/runner/.local /home/runner/.nuget -xdev \\
  -exec chown runner:runner {{}} + 2>/dev/null || true
sudo find /home/runner/.cache /home/runner/go -xdev -exec chmod 777 {{}} + 2>/dev/null || true
mkdir -p /home/runner/.cache/go-build /home/runner/go/pkg 2>/dev/null || true
{proxy_env_block}
{register_and_run_snippet(runner_url, registration_token, vm_name, runner_labels, finish=POWEROFF, env=runner_env)}"""
