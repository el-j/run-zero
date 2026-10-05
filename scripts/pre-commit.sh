#!/usr/bin/env bash
# ==============================================================================
# RunZero Pre-Commit Quality Guard & Auto-Fixer
#
# 1. Auto-formats staged Go files (gofmt -s -w) and re-stages them.
# 2. Runs Go gates (go vet ./..., go test -race ./...).
# 3. Runs TypeSpec & Web gates if spec/ or web/ files are staged.
# 4. Validates shell scripts (bash -n, shellcheck).
# 5. Lints and formats website sources with oxlint and prettier.
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

echo -e "${BOLD}${CYAN}🔍 [RunZero Pre-Commit Guard] Running quality checks & auto-fixes...${RESET}"

STAGED_GO=()
FULLY_STAGED_GO=()
STAGED_SPEC=0
STAGED_WEB=0
STAGED_WEBSITE=0
STAGED_SH=()

while IFS= read -r f; do
  [ -f "$f" ] || continue
  case "$f" in
    spec/*) STAGED_SPEC=1 ;;
    web/*) STAGED_WEB=1 ;;
    website/*) STAGED_WEBSITE=1 ;;
  esac
  case "$f" in
    *.go)
      STAGED_GO+=("$f")
      if git diff --quiet -- "$f"; then
        FULLY_STAGED_GO+=("$f")
      fi
      ;;
    *.sh) STAGED_SH+=("$f") ;;
  esac
done < <(git diff --cached --name-only --diff-filter=ACM)

# ------------------------------------------------------------------------------
# 1. Auto-format staged Go files (gofmt)
# ------------------------------------------------------------------------------
if [ ${#FULLY_STAGED_GO[@]} -gt 0 ]; then
  echo -e "${CYAN}==> 1/5 Formatting staged Go files (gofmt)...${RESET}"
  gofmt -s -w "${FULLY_STAGED_GO[@]}"
  git add -- "${FULLY_STAGED_GO[@]}"
  echo -e "  ${GREEN}✓ Formatted and re-staged ${#FULLY_STAGED_GO[@]} Go file(s).${RESET}"
fi

# ------------------------------------------------------------------------------
# 2. Go quality gates (vet + test)
# ------------------------------------------------------------------------------
if [ ${#STAGED_GO[@]} -gt 0 ]; then
  echo -e "${CYAN}==> 2/5 Running Go vet and unit tests...${RESET}"
  go vet ./...
  go test -race ./...
  echo -e "  ${GREEN}✓ Go quality gates passed.${RESET}"
else
  echo -e "${CYAN}==> 2/5 ${YELLOW}No staged Go files — skipping go vet & test.${RESET}"
fi

# ------------------------------------------------------------------------------
# 3. TypeSpec & Web Dashboard gates
# ------------------------------------------------------------------------------
if [ "$STAGED_SPEC" -eq 1 ] || [ "$STAGED_WEB" -eq 1 ]; then
  echo -e "${CYAN}==> 3/5 Compiling TypeSpec schema & building Web Dashboard...${RESET}"
  if [ "$STAGED_SPEC" -eq 1 ]; then
    (cd spec && pnpm run all)
  fi
  if [ "$STAGED_WEB" -eq 1 ]; then
    (cd web && pnpm run build)
  fi
  echo -e "  ${GREEN}✓ TypeSpec & Web build successful.${RESET}"
else
  echo -e "${CYAN}==> 3/5 ${YELLOW}No staged spec or web files — skipping web build.${RESET}"
fi

# ------------------------------------------------------------------------------
# 4. Shell scripts
# ------------------------------------------------------------------------------
if [ ${#STAGED_SH[@]} -gt 0 ]; then
  echo -e "${CYAN}==> 4/5 Validating staged shell scripts...${RESET}"
  for sh_file in "${STAGED_SH[@]}"; do
    bash -n "$sh_file"
  done
  if command -v shellcheck >/dev/null 2>&1; then
    shellcheck -x "${STAGED_SH[@]}"
  else
    echo -e "  ${RED}✗ shellcheck not installed.${RESET}"
    exit 1
  fi
  echo -e "  ${GREEN}✓ Shell scripts valid.${RESET}"
else
  echo -e "${CYAN}==> 4/5 ${YELLOW}No staged shell scripts.${RESET}"
fi

# ------------------------------------------------------------------------------
# 5. Website lint & format check
# ------------------------------------------------------------------------------
if [ "$STAGED_WEBSITE" -eq 1 ] && command -v npm >/dev/null 2>&1; then
  echo -e "${CYAN}==> 5/5 Website: oxlint + prettier...${RESET}"
  (cd website && { npm ls oxlint >/dev/null 2>&1 || npm install >/dev/null 2>&1; } && npm run lint)
  (cd website && npm exec prettier -- --check "src/**/*.{astro,js,ts,css,md,json}" "public/**/*.{css,md,json}")
  echo -e "  ${GREEN}✓ Website checks passed.${RESET}"
fi

echo -e "\n${BOLD}${GREEN}✅ [RunZero Pre-Commit Guard] All quality checks passed.${RESET}\n"
