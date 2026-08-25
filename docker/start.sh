#!/bin/bash
set -e

# Ensure Docker socket permissions if mounted
if [ -S /var/run/docker.sock ]; then
  sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

# Ensure toolcache permissions if mounted
if [ -d /opt/hostedtoolcache ]; then
  sudo chown -R runner:runner /opt/hostedtoolcache 2>/dev/null || true
fi

# Ensure package-manager cache mount permissions if mounted — OrbStack presents
# bind-mounted host dirs as root-owned regardless of the container user. Docker
# also auto-creates the *ancestor* path components of a bind mount as root (e.g.
# mounting .../go/pkg still leaves .../go itself root-owned), so a sibling dir a
# tool tries to mkdir later (like go/bin next to go/pkg) fails too — every
# ancestor from /home/runner down needs chowning, not just the mount leaf.
#
# CACHE_MOUNT_DESTS (set by docker_driver.py, colon-separated) carries the exact
# container-side paths cache_manager.py just mounted with -v — the same source
# of truth, so this can't silently drift out of sync with the real mounts again
# the way a second hand-maintained list did (.nuget/packages was missing here
# entirely, and go/pkg/mod didn't match the actual go/pkg mount so its ancestor
# was never chowned — see run-zero PR fixing cache-mount-ownership-drift).
# Falls back to a fixed copy of cache_manager.py's destinations for a manual/
# standalone `docker run` without the autoscaler.
if [ -n "${CACHE_MOUNT_DESTS:-}" ]; then
  IFS=':' read -ra CACHE_DIRS <<< "${CACHE_MOUNT_DESTS}"
else
  CACHE_DIRS=(
    /home/runner/.npm
    /home/runner/.local/share/pnpm/store
    /home/runner/.cache/yarn
    /home/runner/.cache/pip
    /home/runner/.cache/uv
    /home/runner/go/pkg
    /home/runner/.cache/go-build
    /home/runner/.nuget/packages
    /home/runner/.cargo/registry
  )
fi

for cache_dir in "${CACHE_DIRS[@]}"; do
  if [ -d "${cache_dir}" ]; then
    path="/home/runner"
    rel="${cache_dir#/home/runner/}"
    IFS='/' read -ra parts <<< "${rel}"
    for part in "${parts[@]}"; do
      path="${path}/${part}"
      sudo chown runner:runner "${path}" 2>/dev/null || true
    done
    sudo chown -R runner:runner "${cache_dir}" 2>/dev/null || true
  fi
done

# Detect architecture for automatic labels
ARCH=$(uname -m)
case "${ARCH}" in
  "aarch64"|"arm64") ARCH_LABEL="arm64" ;;
  "x86_64"|"amd64") ARCH_LABEL="x64,amd64" ;;
  *) ARCH_LABEL="${ARCH}" ;;
esac

# Proxy Registry auto-detection (Verdaccio for NPM & Athens for Go). Uses
# localhost, not container names — the runner runs with --network host (needed
# for GitHub Actions `services:` containers to be reachable at localhost), so
# there's no container-name DNS between the runner and these proxy containers,
# only whatever ports they publish to the host.
if curl -s --connect-timeout 1 http://localhost:49501/ >/dev/null 2>&1; then
  export NPM_CONFIG_REGISTRY="http://localhost:49501/"
  npm config set registry http://localhost:49501/ --global 2>/dev/null || true
  echo "⚡ Verdaccio NPM proxy connected: http://localhost:49501/"
fi

if curl -s --connect-timeout 1 http://localhost:49500/ >/dev/null 2>&1; then
  export GOPROXY="http://localhost:49500,https://proxy.golang.org,direct"
  echo "⚡ Athens Go proxy connected: http://localhost:49500"
fi

# apt-cacher-ng only gets wired into the image if it happened to be running at
# `docker build` time (see provision-toolchain.sh) -- a real container built
# on a machine where it wasn't up starts with no apt proxy config at all, and
# even when it WAS baked in, that only sped up the one-time image build, never
# an actual job's own `sudo apt-get install ...` step, since nothing re-checked
# at container start. Doing it here, same as npm/Go above, means the proxy
# works for user workflows too, regardless of build-time luck.
if curl -fsS --connect-timeout 1 http://localhost:49503/acng-report.html >/dev/null 2>&1; then
  echo 'Acquire::http::Proxy "http://localhost:49503";' | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
  echo "⚡ apt-cacher-ng proxy connected: http://localhost:49503"
fi

# Fallback/alias for environment variable names
REPO="${REPO:-${REPOSITORY}}"
ORG="${ORG:-${ORGANIZATION}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-${TOKEN:-${PAT_TOKEN:-${GITHUB_TOKEN}}}}"
RUNNER_TOKEN="${RUNNER_TOKEN:-${REGISTRATION_TOKEN}}"
BASE_RUNNER_NAME="${RUNNER_NAME:-runner-${ARCH_LABEL%%,*}}"
RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
RUNNER_GROUP="${RUNNER_GROUP:-}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,local,${ARCH_LABEL}}"
EPHEMERAL="${EPHEMERAL:-false}"
DISABLE_AUTO_UPDATE="${DISABLE_AUTO_UPDATE:-true}"

# Ensure unique runner name to avoid collisions when scaling
RAND_ID=$(head /dev/urandom | LC_ALL=C tr -dc 'a-z0-9' | head -c 6 || echo "${RANDOM}")
RUNNER_NAME="${BASE_RUNNER_NAME}-${RAND_ID}"

if [ -z "${REPO}" ] && [ -z "${ORG}" ]; then
  echo "Error: You must set either REPO (e.g. owner/repo) or ORG (e.g. my-org) environment variable."
  exit 1
fi

if [ -n "${REPO}" ]; then
  RUNNER_URL="https://github.com/${REPO}"
  API_URL="https://api.github.com/repos/${REPO}/actions/runners"
elif [ -n "${ORG}" ]; then
  RUNNER_URL="https://github.com/${ORG}"
  API_URL="https://api.github.com/orgs/${ORG}/actions/runners"
fi

echo "=========================================="
echo "Target URL:    ${RUNNER_URL}"
echo "Runner Name:   ${RUNNER_NAME}"
echo "Architecture:  ${ARCH} (${ARCH_LABEL})"
echo "Labels:        ${RUNNER_LABELS}"
echo "Ephemeral:     ${EPHEMERAL}"
echo "NPM Registry:  ${NPM_CONFIG_REGISTRY:-https://registry.npmjs.org/}"
echo "Go Proxy:      ${GOPROXY:-https://proxy.golang.org,direct}"
echo "=========================================="

# Retrieve registration token via Personal Access Token (PAT) if not directly supplied
if [ -z "${RUNNER_TOKEN}" ]; then
  if [ -z "${ACCESS_TOKEN}" ]; then
    echo "Error: Either RUNNER_TOKEN or ACCESS_TOKEN (Personal Access Token with admin/repo scope) must be provided."
    exit 1
  fi

  echo "Fetching registration token from GitHub API..."
  TOKEN_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "${API_URL}/registration-token")

  REG_TOKEN=$(echo "${TOKEN_RESPONSE}" | jq -r '.token // empty')

  if [ -z "${REG_TOKEN}" ] || [ "${REG_TOKEN}" = "null" ]; then
    echo "Error: Failed to obtain registration token. GitHub response was:"
    echo "${TOKEN_RESPONSE}"
    exit 1
  fi
else
  REG_TOKEN="${RUNNER_TOKEN}"
fi

cd /home/runner/actions-runner

# Configure runner arguments
CONFIG_ARGS=(
  --url "${RUNNER_URL}"
  --token "${REG_TOKEN}"
  --name "${RUNNER_NAME}"
  --work "${RUNNER_WORKDIR}"
  --unattended
  --replace
)

if [ -n "${RUNNER_LABELS}" ]; then
  CONFIG_ARGS+=(--labels "${RUNNER_LABELS}")
fi

if [ -n "${RUNNER_GROUP}" ]; then
  CONFIG_ARGS+=(--runnergroup "${RUNNER_GROUP}")
fi

if [ "${EPHEMERAL}" = "true" ]; then
  CONFIG_ARGS+=(--ephemeral)
fi

if [ "${DISABLE_AUTO_UPDATE}" = "true" ]; then
  CONFIG_ARGS+=(--disableupdate)
fi

echo "Configuring runner..."
./config.sh "${CONFIG_ARGS[@]}"

# Cleanup and unregister on exit
cleanup() {
  echo "Unregistering runner ${RUNNER_NAME}..."
  local REMOVE_TOKEN=""

  if [ -n "${ACCESS_TOKEN}" ]; then
    REMOVE_TOKEN_RESPONSE=$(curl -s -X POST \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "${API_URL}/remove-token" 2>/dev/null || true)
    REMOVE_TOKEN=$(echo "${REMOVE_TOKEN_RESPONSE}" | jq -r '.token // empty')
  fi

  if [ -z "${REMOVE_TOKEN}" ] || [ "${REMOVE_TOKEN}" = "null" ]; then
    REMOVE_TOKEN="${REG_TOKEN}"
  fi

  ./config.sh remove --unattended --token "${REMOVE_TOKEN}" 2>/dev/null || true
}

trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM
trap 'cleanup; exit 0' EXIT

echo "Starting runner ${RUNNER_NAME}..."
./run.sh &
RUN_PID=$!
wait "${RUN_PID}"
