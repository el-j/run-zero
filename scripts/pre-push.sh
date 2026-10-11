#!/usr/bin/env bash
# ==============================================================================
# RunZero Pre-Push Quality Guard
#
# Verifies outgoing branch changes against quality gates before sending them to
# remote repositories, eliminating broken CI runs and conserving cloud runner
# minutes.
#
# Can be bypassed when needed with:
#   git push --no-verify
#   or RUNZERO_SKIP_PRE_PUSH=1 git push
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

if [ "${RUNZERO_SKIP_PRE_PUSH:-0}" = "1" ]; then
  echo -e "${YELLOW}⚡ [RunZero Pre-Push] Bypassing pre-push checks (RUNZERO_SKIP_PRE_PUSH=1).${RESET}"
  exit 0
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

ensure_node_env() {
  local current_major=0
  if command -v node >/dev/null 2>&1; then
    current_major=$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
  fi

  if [ "$current_major" -ge 22 ]; then
    return 0
  fi

  local nvm_sh=""
  if [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
    nvm_sh="${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  elif [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then
    nvm_sh="/opt/homebrew/opt/nvm/nvm.sh"
  fi

  if [ -n "$nvm_sh" ]; then
    # shellcheck source=/dev/null
    . "$nvm_sh"
    if command -v nvm >/dev/null 2>&1; then
      if [ -f "$PROJECT_ROOT/.nvmrc" ]; then
        nvm use --silent "$PROJECT_ROOT/.nvmrc" >/dev/null 2>&1 || nvm use --silent 22 >/dev/null 2>&1 || true
      else
        nvm use --silent 22 >/dev/null 2>&1 || true
      fi
    fi
  fi

  if command -v node >/dev/null 2>&1; then
    current_major=$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
    if [ "$current_major" -ge 22 ]; then
      return 0
    fi
  fi

  if [ -d "$HOME/.nvm/versions/node" ]; then
    local candidate
    while IFS= read -r candidate; do
      if [ -x "$candidate/bin/node" ]; then
        local cand_major
        cand_major=$("$candidate/bin/node" -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
        if [ "$cand_major" -ge 22 ]; then
          export PATH="$candidate/bin:$PATH"
          return 0
        fi
      fi
    done < <(find "$HOME/.nvm/versions/node" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -V -r)
  fi

  current_major=$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
  if [ "$current_major" -lt 22 ]; then
    echo -e "${RED}✗ Error: Node.js >= 22 is required (active: $(node -v 2>/dev/null || echo 'none')).${RESET}"
    echo -e "${YELLOW}Please activate Node.js 22+ (e.g. 'nvm use 22' or 'nvm use') before pushing.${RESET}"
    exit 1
  fi
}

echo -e "\n${BOLD}${CYAN}🚀 [RunZero Pre-Push Guard] Validating outgoing branch before push...${RESET}"

# 1. Quality Gates (make check / Go, TypeSpec, Web, Shell)
ensure_node_env
echo -e "${CYAN}==> Verifying code quality gates (make check)...${RESET}"
if ! make check; then
  echo -e "\n${BOLD}${RED}✗ [RunZero Pre-Push Guard] Quality checks failed! Push rejected.${RESET}"
  echo -e "${YELLOW}Fix the issues above or use 'git push --no-verify' to force push.${RESET}\n"
  exit 1
fi

echo -e "\n${BOLD}${GREEN}✅ [RunZero Pre-Push Guard] Ready to push! Outgoing commits are clean.${RESET}\n"
exit 0
