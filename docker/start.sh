#!/bin/bash
set -e

# Ensure Docker socket permissions if mounted
if [ -S /var/run/docker.sock ]; then
  sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

# Ensure toolcache permissions if mounted. Never recurse into a host-backed cache
# mount: its contents already appear runner-owned (OrbStack/virtiofs maps ownership to
# the accessing user), and walking ~100k cached files costs seconds per job (#67).
if [ -d /opt/hostedtoolcache ]; then
  sudo chown runner:runner /opt/hostedtoolcache 2>/dev/null || true
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
    /home/runner/.cache/ms-playwright
  )
fi

# Ensure /home/runner and all tool/language directories (Go, Cargo, NVM, Pip) are owned and writable
sudo mkdir -p /home/runner/go/bin /home/runner/go/pkg /home/runner/.cache /home/runner/.local/bin /opt/hostedtoolcache
# `find -xdev` fixes the image's own files but never descends into bind-mounted caches.
sudo find /home/runner -xdev -exec chown runner:runner {} + 2>/dev/null || true
sudo find /home/runner/go /home/runner/.cache -xdev -exec chmod 777 {} + 2>/dev/null || true
sudo chown runner:runner /opt/hostedtoolcache 2>/dev/null || true
sudo chmod 777 /opt/hostedtoolcache 2>/dev/null || true

for cache_dir in "${CACHE_DIRS[@]}"; do
  if [ -d "${cache_dir}" ]; then
    path="/home/runner"
    rel="${cache_dir#/home/runner/}"
    IFS='/' read -ra parts <<< "${rel}"
    for part in "${parts[@]}"; do
      path="${path}/${part}"
      sudo chown runner:runner "${path}" 2>/dev/null || true
    done
  fi
done

# Final, verified pass on the plain (never bind-mounted) tool directories that
# job steps write into directly, e.g. `actions/setup-go`'s own `mkdir
# $GOPATH/bin`. The `find -xdev` pass above already covers these in the
# common case, but its failures are swallowed by `|| true`, so a real
# ownership failure would otherwise go unnoticed until a much later,
# harder-to-diagnose step. Re-
# assert ownership on exactly the paths that must be writable, verify it
# actually took as the runner user, and fall back to a permissive chmod
# (bypassing ownership entirely) rather than leave a job to fail on it.
for must_own in /home/runner/go /home/runner/go/bin /home/runner/.local/bin; do
  sudo mkdir -p "${must_own}"
  sudo chown runner:runner "${must_own}" 2>/dev/null || true
  if ! sudo -u runner test -w "${must_own}"; then
    echo "⚠️  ${must_own} not writable by 'runner' after chown -- forcing chmod 777"
    sudo chmod 777 "${must_own}"
  fi
done

# Detect architecture for automatic labels
ARCH=$(uname -m)
case "${ARCH}" in
  "aarch64"|"arm64") ARCH_LABEL="arm64" ;;
  "x86_64"|"amd64") ARCH_LABEL="x64,amd64" ;;
  *) ARCH_LABEL="${ARCH}" ;;
esac

# Proxy Registry auto-detection (Verdaccio/Athens/devpi). Try explicit env vars first,
# then discover across common runtime topologies:
# 1) --network host via published localhost ports
# 2) Compose bridge networking via service DNS names
# 3) OrbStack host DNS alias
# pnpm 11 reads only pnpm_config_*, pnpm <=10 and npm only npm_config_*, Yarn berry only
# YARN_NPM_REGISTRY_SERVER -- set every spelling (keep in sync with drivers/runner_env.py).
use_npm_registry() {
  export NPM_CONFIG_REGISTRY="$1" npm_config_registry="$1" pnpm_config_registry="$1"
  export YARN_REGISTRY="$1" YARN_NPM_REGISTRY_SERVER="$1"
  npm config set registry "$1" --global 2>/dev/null || true
  echo "⚡ Verdaccio NPM proxy $2: $1"
}
if [ -n "${NPM_CONFIG_REGISTRY:-}" ]; then
  use_npm_registry "${NPM_CONFIG_REGISTRY}" "configured from env"
elif curl -s --connect-timeout 1 http://localhost:49501/ >/dev/null 2>&1; then
  use_npm_registry "http://localhost:49501/" connected
elif curl -s --connect-timeout 1 http://verdaccio:4873/ >/dev/null 2>&1; then
  use_npm_registry "http://verdaccio:4873/" connected
elif curl -s --connect-timeout 1 http://host.orb.internal:49501/ >/dev/null 2>&1; then
  use_npm_registry "http://host.orb.internal:49501/" connected
fi

if [ -n "${GOPROXY:-}" ]; then
  echo "⚡ Athens Go proxy configured from env: ${GOPROXY}"
elif curl -s --connect-timeout 1 http://localhost:49500/ >/dev/null 2>&1; then
  export GOPROXY="http://localhost:49500,https://proxy.golang.org,direct"
  echo "⚡ Athens Go proxy connected: http://localhost:49500"
elif curl -s --connect-timeout 1 http://athens:3000/ >/dev/null 2>&1; then
  export GOPROXY="http://athens:3000,https://proxy.golang.org,direct"
  echo "⚡ Athens Go proxy connected: http://athens:3000"
elif curl -s --connect-timeout 1 http://host.orb.internal:49500/ >/dev/null 2>&1; then
  export GOPROXY="http://host.orb.internal:49500,https://proxy.golang.org,direct"
  echo "⚡ Athens Go proxy connected: http://host.orb.internal:49500"
fi

# devpi's default "root/pypi" index is a real pull-through PyPI mirror; both pip and uv
# honor PIP_INDEX_URL, uv additionally reads UV_INDEX_URL.
if [ -n "${PIP_INDEX_URL:-}" ]; then
  export UV_INDEX_URL="${UV_INDEX_URL:-${PIP_INDEX_URL}}"
  pip config set global.index-url "${PIP_INDEX_URL}" 2>/dev/null || true
  echo "⚡ devpi PyPI proxy configured from env: ${PIP_INDEX_URL}"
elif curl -s --connect-timeout 1 http://localhost:49507/root/pypi/+simple/ >/dev/null 2>&1; then
  export PIP_INDEX_URL="http://localhost:49507/root/pypi/+simple/"
  export UV_INDEX_URL="${PIP_INDEX_URL}"
  pip config set global.index-url "${PIP_INDEX_URL}" 2>/dev/null || true
  echo "⚡ devpi PyPI proxy connected: ${PIP_INDEX_URL}"
elif curl -s --connect-timeout 1 http://devpi:3141/root/pypi/+simple/ >/dev/null 2>&1; then
  export PIP_INDEX_URL="http://devpi:3141/root/pypi/+simple/"
  export UV_INDEX_URL="${PIP_INDEX_URL}"
  pip config set global.index-url "${PIP_INDEX_URL}" 2>/dev/null || true
  export PIP_TRUSTED_HOST="${PIP_TRUSTED_HOST:-devpi}"
  echo "⚡ devpi PyPI proxy connected: ${PIP_INDEX_URL}"
elif curl -s --connect-timeout 1 http://host.orb.internal:49507/root/pypi/+simple/ >/dev/null 2>&1; then
  export PIP_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"
  export UV_INDEX_URL="${PIP_INDEX_URL}"
  pip config set global.index-url "${PIP_INDEX_URL}" 2>/dev/null || true
  export PIP_TRUSTED_HOST="${PIP_TRUSTED_HOST:-host.orb.internal}"
  echo "⚡ devpi PyPI proxy connected: ${PIP_INDEX_URL}"
fi

# kellnr's crates.io proxy is a real sparse-index mirror. Unlike pip/Go, Cargo has no
# single "index URL" env var for this -- verified live (2026-08-26) that cargo silently
# ignores CARGO_SOURCE_<name>_* env vars for a dynamic/custom [source.*] table (a real
# cargo limitation: env-var config only reaches keys cargo statically knows about, not
# free-form registry-map tables). Only a real ~/.cargo/config.toml source-replacement
# block works, confirmed by tracing cargo's own network layer: with the env vars alone it
# fetched straight from https://index.crates.io/config.json; with this file in place it
# fetched kellnr's config.json instead, and the resulting .crate landed in kellnr's own
# on-disk cache.
#
# Uses host.orb.internal, not localhost -- kellnr bakes its own configured
# KELLNR_ORIGIN__HOSTNAME (see docker-compose.yml) into the "dl" (download) URL every
# client gets back from config.json, regardless of which URL that client used to reach
# it. Confirmed live (2026-08-26) this is a real trap, not a style choice: pointing the
# registry at "localhost:49506" let the index metadata fetch succeed (reachable from a
# --network host container) but then broke the actual .crate download, because kellnr's
# advertised dl URL was itself "localhost:49506" -- unreachable from a context where
# "localhost" doesn't mean the Mac host (an OrbStack VM, or a Mode 2 bridge-network
# container). host.orb.internal is OrbStack's universal DNS name for the Mac host and
# resolves correctly from every context this stack runs runners in -- verified live from
# a real OrbStack VM, a --network host container, and a plain bridge-network container.
KELLNR_REGISTRY_URL=""
if curl -fsS --connect-timeout 1 http://host.orb.internal:49506/api/v1/cratesio/config.json >/dev/null 2>&1; then
  KELLNR_REGISTRY_URL="sparse+http://host.orb.internal:49506/api/v1/cratesio/"
elif curl -fsS --connect-timeout 1 http://kellnr:8000/api/v1/cratesio/config.json >/dev/null 2>&1; then
  KELLNR_REGISTRY_URL="sparse+http://kellnr:8000/api/v1/cratesio/"
elif curl -fsS --connect-timeout 1 http://localhost:49506/api/v1/cratesio/config.json >/dev/null 2>&1; then
  KELLNR_REGISTRY_URL="sparse+http://localhost:49506/api/v1/cratesio/"
fi

if [ -n "${KELLNR_REGISTRY_URL}" ]; then
  mkdir -p "${HOME}/.cargo"
  cat > "${HOME}/.cargo/config.toml" <<'CARGOCFG'
[source.crates-io]
replace-with = "kellnr-proxy"

[source.kellnr-proxy]
registry = "__RUNZERO_KELLNR_REGISTRY__"
CARGOCFG
  sed -i "s|__RUNZERO_KELLNR_REGISTRY__|${KELLNR_REGISTRY_URL}|g" "${HOME}/.cargo/config.toml"
  echo "⚡ kellnr Cargo/crates.io proxy connected: ${KELLNR_REGISTRY_URL}"
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
elif curl -fsS --connect-timeout 1 http://apt-cacher:3142/acng-report.html >/dev/null 2>&1; then
  echo 'Acquire::http::Proxy "http://apt-cacher:3142";' | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
  echo "⚡ apt-cacher-ng proxy connected: http://apt-cacher:3142"
elif curl -fsS --connect-timeout 1 http://host.orb.internal:49503/acng-report.html >/dev/null 2>&1; then
  echo 'Acquire::http::Proxy "http://host.orb.internal:49503";' | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
  echo "⚡ apt-cacher-ng proxy connected: http://host.orb.internal:49503"
fi

# Fallback/alias for environment variable names
REPO="${REPO:-${REPOSITORY}}"
ORG="${ORG:-${ORGANIZATION}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-${TOKEN:-${PAT_TOKEN:-${GITHUB_TOKEN}}}}"
RUNNER_TOKEN="${RUNNER_TOKEN:-${REGISTRATION_TOKEN}}"
BASE_RUNNER_NAME="${RUNNER_NAME:-}"
RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
RUNNER_GROUP="${RUNNER_GROUP:-}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,local,${ARCH_LABEL}}"
EPHEMERAL="${EPHEMERAL:-false}"
DISABLE_AUTO_UPDATE="${DISABLE_AUTO_UPDATE:-true}"

# Keep an explicit RUNNER_NAME stable so autoscaler -> GitHub runner correlation
# remains exact (required for safe orphan/zombie reconciliation). When absent,
# generate a unique default runner name.
if [ -n "${BASE_RUNNER_NAME}" ]; then
  RUNNER_NAME="${BASE_RUNNER_NAME}"
else
  BASE_RUNNER_NAME="runner-${ARCH_LABEL%%,*}"
  RAND_ID=$(head /dev/urandom | LC_ALL=C tr -dc 'a-z0-9' | head -c 6 || echo "${RANDOM}")
  RUNNER_NAME="${BASE_RUNNER_NAME}-${RAND_ID}"
fi

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
echo "Pip Index:     ${PIP_INDEX_URL:-https://pypi.org/simple/}"
if [ -f "${HOME}/.cargo/config.toml" ] && grep -q "kellnr-proxy" "${HOME}/.cargo/config.toml" 2>/dev/null; then
  CARGO_REGISTRY_URL="${KELLNR_REGISTRY_URL:-$(grep -E '^registry\s*=\s*"' "${HOME}/.cargo/config.toml" 2>/dev/null | head -1 | sed -E 's/^registry\s*=\s*"(.*)"/\1/')}"
  echo "Cargo Source:  kellnr proxy (${CARGO_REGISTRY_URL:-configured})"
else
  echo "Cargo Source:  crates.io (default)"
fi
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

# Keep credentials out of every job step: run.sh and its children inherit only exported
# variables, so drop the export attribute from all credential names. The autoscaler only
# ever passes RUNNER_TOKEN (a registration token); a PAT supplied for standalone use stays
# in this shell solely for cleanup()'s remove-token call. NOTE: the container's initial
# environment remains readable via /proc/1/environ by the same user -- see SECURITY.md.
export -n ACCESS_TOKEN TOKEN PAT_TOKEN GITHUB_TOKEN RUNNER_TOKEN REGISTRATION_TOKEN
unset TOKEN PAT_TOKEN RUNNER_TOKEN REGISTRATION_TOKEN

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
