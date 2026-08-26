#!/usr/bin/env bash
# Single source of truth for the CI toolchain shared by BOTH execution engines:
#   - docker/Dockerfile bakes this into the local-github-runner image at build time
#   - src/drivers/orbstack_vm_driver.py runs this once, live, when building the
#     golden `runzero-vm-base-<arch>` VM image that ephemeral job VMs clone from
#
# Keeping this in one file means adding/bumping a tool here fixes it for both
# engines at once -- the previous design had this list duplicated inline in
# orbstack_vm_driver.py's Python f-string, which had already drifted out of
# sync with the Dockerfile by the time this script was written.
#
# Assumes: running as a non-root user with passwordless sudo (true for `runner`
# in both the Dockerfile, after its sudoers step, and the VM). NOT responsible
# for Docker itself -- the container engine needs only the CLI (talks to a
# mounted host socket) while the VM engine needs a full local daemon, and that
# difference is deliberately kept in each caller, not here.
#
ARCH="${1:-${ARCH:-$(dpkg --print-architecture 2>/dev/null || uname -m)}}"
case "${ARCH}" in
  "x86_64") ARCH="amd64" ;;
  "aarch64") ARCH="arm64" ;;
esac
export DEBIAN_FRONTEND=noninteractive

# Route apt through the local apt-cacher-ng proxy (same pattern as Verdaccio/Athens
# for npm/Go) if it's reachable -- caches .deb packages across BOTH engines and
# across repeated runs, so rebuilding the Docker image or the golden VM image after
# an edit here doesn't re-download the same ~3GB of packages from the internet each
# time. `host.orb.internal` resolves from any OrbStack container/VM AND from a
# `docker build` RUN step (OrbStack extends that DNS entry universally); harmless
# no-op if apt-cacher-ng isn't running (`make start` brings it up by default).
if curl -fsS --connect-timeout 2 "http://host.orb.internal:49503/acng-report.html" >/dev/null 2>&1; then
  echo "==> Using local apt-cacher-ng proxy"
  echo 'Acquire::http::Proxy "http://host.orb.internal:49503";' | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
fi

echo "==> Installing base OS packages..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
  ca-certificates curl wget rsync gnupg lsb-release jq git git-lfs tar unzip zip \
  bzip2 zstd xz-utils build-essential cmake pkg-config libssl-dev libffi-dev \
  libicu-dev libsqlite3-dev zlib1g-dev python3 python3-venv python3-dev python3-pip \
  software-properties-common postgresql-client
sudo git lfs install --system --skip-repo 2>/dev/null || true

echo "==> Installing .NET SDK 8.0..."
UBUNTU_VER=$(. /etc/os-release && echo "${VERSION_ID:-24.04}")
curl -fsSL "https://packages.microsoft.com/config/ubuntu/${UBUNTU_VER}/packages-microsoft-prod.deb" -o /tmp/packages-microsoft-prod.deb 2>/dev/null || \
  curl -fsSL "https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb" -o /tmp/packages-microsoft-prod.deb 2>/dev/null || true
if [ -f /tmp/packages-microsoft-prod.deb ]; then
  sudo dpkg -i /tmp/packages-microsoft-prod.deb 2>/dev/null || true
  rm -f /tmp/packages-microsoft-prod.deb
fi
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends dotnet-sdk-8.0

# Google Chrome -- amd64-only, no arm64 build exists (needed by lhci autorun's
# headless browser audits). Playwright-driven jobs still get their own bundled
# Chromium per-job via `playwright install`, this only affects Lighthouse CI.
if [ "$ARCH" = "amd64" ] && [ "$(dpkg --print-architecture)" = "amd64" ]; then
  echo "==> Installing Google Chrome..."
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://dl.google.com/linux/linux_signing_key.pub -o /tmp/google-chrome.asc
  sudo install -m 0644 /tmp/google-chrome.asc /etc/apt/keyrings/google-chrome.asc
  rm -f /tmp/google-chrome.asc
  echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.asc] http://dl.google.com/linux/chrome/deb/ stable main" | \
    sudo tee /etc/apt/sources.list.d/google-chrome.list > /dev/null
  sudo apt-get update -y || true
  sudo apt-get install -y --no-install-recommends google-chrome-stable || true
fi

# Node 20/22/24 via nvm, with yarn + pnpm on each
echo "==> Installing Node 20/22/24 via nvm..."
export NVM_DIR="$HOME/.nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm install 20 && nvm install 22 && nvm install 24
nvm alias default 20
nvm use 20 && npm install -g yarn pnpm
nvm use 22 && npm install -g yarn pnpm
nvm use 24 && npm install -g yarn pnpm
nvm use default

# Playwright OS-level deps (xvfb, GTK, gstreamer, PulseAudio...) so the per-job
# `playwright install --with-deps` step only has to fetch the browser-binary
# delta, not apt-get ~50 packages from scratch every run. GitHub-hosted
# ubuntu-latest images ship these system libs pre-baked already.
echo "==> Pre-baking Playwright OS-level dependencies..."
npx --yes playwright install-deps chromium webkit firefox

echo "==> Toolchain provisioning complete."
