#!/bin/bash
set -e

# Ensure Docker socket permissions if mounted
if [ -S /var/run/docker.sock ]; then
  sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

# Fallback/alias for environment variable names
REPO="${REPO:-${REPOSITORY}}"
ORG="${ORG:-${ORGANIZATION}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-${TOKEN:-${PAT_TOKEN:-${GITHUB_TOKEN}}}}"
RUNNER_TOKEN="${RUNNER_TOKEN:-${REGISTRATION_TOKEN}}"
BASE_RUNNER_NAME="${RUNNER_NAME:-runner}"
RUNNER_WORKDIR="${RUNNER_WORKDIR:-_work}"
RUNNER_GROUP="${RUNNER_GROUP:-}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,local}"
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

echo "Target URL: ${RUNNER_URL}"
echo "Runner Name: ${RUNNER_NAME}"
echo "Runner Labels: ${RUNNER_LABELS}"
echo "Ephemeral: ${EPHEMERAL}"

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

  REG_TOKEN=$(echo "${TOKEN_RESPONSE}" | jq -r .token // empty)

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
    REMOVE_TOKEN=$(echo "${REMOVE_TOKEN_RESPONSE}" | jq -r .token // empty)
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
