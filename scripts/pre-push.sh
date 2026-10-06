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

echo -e "\n${BOLD}${CYAN}🚀 [RunZero Pre-Push Guard] Validating outgoing branch before push...${RESET}"

# 1. Quality Gates (make check / Go, TypeSpec, Web, Shell)
echo -e "${CYAN}==> Verifying code quality gates (make check)...${RESET}"
if ! make check; then
  echo -e "\n${BOLD}${RED}✗ [RunZero Pre-Push Guard] Quality checks failed! Push rejected.${RESET}"
  echo -e "${YELLOW}Fix the issues above or use 'git push --no-verify' to force push.${RESET}\n"
  exit 1
fi

echo -e "\n${BOLD}${GREEN}✅ [RunZero Pre-Push Guard] Ready to push! Outgoing commits are clean.${RESET}\n"
exit 0
