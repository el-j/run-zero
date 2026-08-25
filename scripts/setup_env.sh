#!/usr/bin/env bash
# ==============================================================================
# RunZero — Interactive Configuration Wizard
# Generates .env with customized credentials, drivers, and architecture settings.
# ==============================================================================

set -e

# Terminal Colors
CYAN="\033[36m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
BOLD="\033[1m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}${CYAN}╔═══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║             ⚡ RunZero — Setup & Config Wizard ⚡             ║${RESET}"
echo -e "${BOLD}${CYAN}║    Zero Cloud Minutes. Zero K8s Bloat. Zero Idle Waste.       ║${RESET}"
echo -e "${BOLD}${CYAN}╚═══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Non-interactive fallback (for CI/automated scripts)
if [ ! -t 0 ] || [ "$CI" = "true" ] || [ "$NON_INTERACTIVE" = "true" ]; then
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Non-interactive terminal detected. Creating default .env from .env.example...${RESET}"
        cp .env.example .env
        echo -e "${GREEN}Created .env file.${RESET}"
    else
        echo -e "${YELLOW}.env file already exists. Skipping wizard.${RESET}"
    fi
    exit 0
fi

# If .env exists, ask to overwrite or keep
if [ -f .env ]; then
    echo -e "${YELLOW}An existing .env file was found.${RESET}"
    read -r -p "Do you want to reconfigure and overwrite it? [y/N]: " OVERWRITE_ENV
    if [[ ! "$OVERWRITE_ENV" =~ ^[yY](es)?$ ]]; then
        echo -e "${GREEN}Keeping existing .env file.${RESET}"
        exit 0
    fi
    echo ""
fi

# 1. GitHub Personal Access Token
echo -e "${BOLD}1. GitHub Personal Access Token (PAT)${RESET}"
echo -e "   Create one at: ${CYAN}https://github.com/settings/tokens${RESET} (Classic PAT with ${BOLD}repo${RESET} scope)"
read -r -p "   🔑 Enter your GitHub ACCESS_TOKEN: " ACCESS_TOKEN
while [ -z "$ACCESS_TOKEN" ]; do
    echo -e "   ${RED}ACCESS_TOKEN is required.${RESET}"
    read -r -p "   🔑 Enter your GitHub ACCESS_TOKEN: " ACCESS_TOKEN
done
echo ""

# 2. GitHub Username (Owner)
echo -e "${BOLD}2. GitHub Account Owner / Username${RESET}"
echo -e "   RunZero will automatically monitor active repositories under this account."
read -r -p "   👤 Enter your GitHub username: " GITHUB_OWNER
while [ -z "$GITHUB_OWNER" ]; do
    echo -e "   ${RED}GitHub username is required for auto-discovery.${RESET}"
    read -r -p "   👤 Enter your GitHub username: " GITHUB_OWNER
done
echo ""

# 3. Organization (Optional)
echo -e "${BOLD}3. GitHub Organization (Optional)${RESET}"
echo -e "   Leave empty if configuring runners for your personal account."
read -r -p "   🏢 GitHub Organization (optional, press Enter to skip): " GITHUB_ORG
echo ""

# 4. Runner Execution Backend
echo -e "${BOLD}4. Execution Engine Backend${RESET}"
echo -e "   [1] ${BOLD}auto${RESET}         - Hybrid Auto-Routing (Docker containers for builds + Linux VMs for browser/systemd)"
echo -e "   [2] ${BOLD}docker${RESET}       - Ephemeral Docker containers only (~0.3s boot, ~20MB RAM)"
echo -e "   [3] ${BOLD}orbstack-vm${RESET}  - Dedicated OrbStack Linux VMs (Full systemd, unconfined Chrome sandbox)"
echo -e "   [4] ${BOLD}wsl2${RESET}         - Native Windows WSL2 Linux VMs"
echo -e "   [5] ${BOLD}multipass${RESET}    - Canonical Multipass cross-platform Ubuntu VMs"
read -r -p "   Select backend [1-5, default: 1 (auto)]: " BACKEND_CHOICE

case "$BACKEND_CHOICE" in
    2) RUNNER_BACKEND="docker" ;;
    3) RUNNER_BACKEND="orbstack-vm" ;;
    4) RUNNER_BACKEND="wsl2" ;;
    5) RUNNER_BACKEND="multipass" ;;
    *) RUNNER_BACKEND="auto" ;;
esac
echo -e "   Selected: ${GREEN}${RUNNER_BACKEND}${RESET}"
echo ""

# 5. Architecture
echo -e "${BOLD}5. Runner Architectures${RESET}"
echo -e "   [1] ${BOLD}both${RESET}   - Multi-arch (Native ARM64 + Rosetta x86_64 AMD64)"
echo -e "   [2] ${BOLD}arm64${RESET}  - Native Apple Silicon / ARM64 only"
echo -e "   [3] ${BOLD}amd64${RESET}  - Intel/AMD x86_64 only"
read -r -p "   Select architecture [1-3, default: 1 (both)]: " ARCH_CHOICE

case "$ARCH_CHOICE" in
    2) RUNNER_ARCH="arm64" ;;
    3) RUNNER_ARCH="amd64" ;;
    *) RUNNER_ARCH="both" ;;
esac
echo -e "   Selected: ${GREEN}${RUNNER_ARCH}${RESET}"
echo ""

# 6. Max Concurrency
echo -e "${BOLD}6. Concurrency Limit${RESET}"
read -r -p "   ⚡ Max concurrent runner instances [default: 4]: " MAX_RUNNERS_INPUT
MAX_RUNNERS="${MAX_RUNNERS_INPUT:-4}"
echo -e "   Max runners set to: ${GREEN}${MAX_RUNNERS}${RESET}"
echo ""

# 7. Package Proxy Caching
echo -e "${BOLD}7. Package Proxy Registries${RESET}"
echo -e "   Starts local Verdaccio (npm) on :49501 and Athens (Go) on :49500 to accelerate CI builds."
read -r -p "   Enable package caching proxies? [Y/n, default: Y]: " PROXIES_INPUT
if [[ "$PROXIES_INPUT" =~ ^[nN](o)?$ ]]; then
    PROXIES_ENABLED="false"
else
    PROXIES_ENABLED="true"
fi
echo -e "   Proxies: ${GREEN}${PROXIES_ENABLED}${RESET}"
echo ""

# Generate .env file
cat <<EOF > .env
# ==============================================================================
# RunZero Environment Configuration
# Generated by make env wizard on $(date)
# ==============================================================================

# GitHub Authentication
ACCESS_TOKEN=${ACCESS_TOKEN}

# Target Configuration
OWNER=${GITHUB_OWNER}
AUTO_DISCOVER_REPOS=true
ACTIVE_REPO_DAYS=60
ORG=${GITHUB_ORG}

# Execution Engine & Hybrid Routing
RUNNER_BACKEND=${RUNNER_BACKEND}
AUTO_ROUTE_VM=true
RUNNER_ARCH=${RUNNER_ARCH}

# Fleet Capacity
MIN_RUNNERS=0
MAX_RUNNERS=${MAX_RUNNERS}
POLL_INTERVAL=5
DISCOVERY_INTERVAL=900

# Package Registries & Tool Caching
PROXIES_ENABLED=${PROXIES_ENABLED}
CACHE_ENABLED=true
HOST_CACHE_DIR=~/.local-github-runner/cache

# Networking
DOCKER_NETWORK=host
DOCKER_SOCK=/var/run/docker.sock
EOF

chmod 600 .env

echo -e "${BOLD}${GREEN}✔ .env successfully generated!${RESET}"
echo ""
echo -e "${CYAN}Configuration Summary:${RESET}"
echo -e "  • Owner:        ${BOLD}${GITHUB_OWNER}${RESET}"
echo -e "  • Engine:       ${BOLD}${RUNNER_BACKEND}${RESET}"
echo -e "  • Arch:         ${BOLD}${RUNNER_ARCH}${RESET}"
echo -e "  • Concurrency:  ${BOLD}${MAX_RUNNERS} runners${RESET}"
echo -e "  • Proxies:      ${BOLD}${PROXIES_ENABLED}${RESET}"
echo ""
echo -e "You can now run ${BOLD}${GREEN}make start${RESET} to launch your runner fleet!"
echo ""
