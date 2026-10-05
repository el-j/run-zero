#!/usr/bin/env bash
# ==============================================================================
# RunZero Pre-Commit Quality Guard & Auto-Fixer
#
# 1. Auto-fixes (ruff lint --fix + ruff format) staged Python files and re-stages
#    ONLY those files -- and only when they have no additional unstaged edits, so
#    re-staging can never sweep unrelated work-in-progress into the commit.
# 2. Runs the fast quality gates against what is staged: ruff, flake8, mypy,
#    interrogate, shellcheck / bash -n, pytest (no coverage gate -- CI enforces it),
#    and the website's oxlint + prettier.
#
# Tooling comes from $RUNZERO_PY, else .venv-dev/bin/python (`make dev-setup`),
# else python3. Missing tooling is a hard failure, never a silent skip.
# Must stay compatible with macOS's stock bash 3.2 (no mapfile, guarded arrays).
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

if [ -n "${RUNZERO_PY:-}" ]; then
  PY="$RUNZERO_PY"
elif [ -x .venv-dev/bin/python ]; then
  PY=".venv-dev/bin/python"
else
  PY="python3"
fi

echo -e "${BOLD}${CYAN}🔍 [RunZero Pre-Commit Guard] Running quality checks & auto-fixes...${RESET}"

if ! "$PY" -m ruff --version >/dev/null 2>&1 || ! "$PY" -m flake8 --version >/dev/null 2>&1; then
  echo -e "${RED}✗ Dev tooling not found for '$PY'. Run: make dev-setup (or set RUNZERO_PY).${RESET}"
  exit 1
fi

STAGED_PY=()
FULLY_STAGED_PY=()
PARTIAL_PY=()
STAGED_SH=()
STAGED_CORE=0
STAGED_WEB=()
while IFS= read -r f; do
  [ -f "$f" ] || continue
  case "$f" in
    website/*) STAGED_WEB+=("$f") ;;
  esac
  case "$f" in
    src/*.py | tests/*.py) STAGED_CORE=1 ;;
  esac
  case "$f" in
    *.py)
      STAGED_PY+=("$f")
      if git diff --quiet -- "$f"; then
        FULLY_STAGED_PY+=("$f")
      else
        PARTIAL_PY+=("$f")
      fi
      ;;
    *.sh) STAGED_SH+=("$f") ;;
  esac
done < <(git diff --cached --name-only --diff-filter=ACM)

# ------------------------------------------------------------------------------
# 1. Auto-fix fully staged Python files and re-stage exactly those files
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 1/5 Auto-fixing staged Python files (ruff)...${RESET}"
if [ ${#FULLY_STAGED_PY[@]} -gt 0 ]; then
  "$PY" -m ruff check --fix --quiet -- "${FULLY_STAGED_PY[@]}" || true
  "$PY" -m ruff format --quiet -- "${FULLY_STAGED_PY[@]}"
  git add -- "${FULLY_STAGED_PY[@]}"
  echo -e "  ${GREEN}✓ Auto-fixed and re-staged ${#FULLY_STAGED_PY[@]} file(s).${RESET}"
else
  echo -e "  ${YELLOW}No fully staged Python files to auto-fix.${RESET}"
fi
if [ ${#PARTIAL_PY[@]} -gt 0 ]; then
  echo -e "  ${YELLOW}Not auto-fixed (also has unstaged edits): ${PARTIAL_PY[*]}${RESET}"
fi

# ------------------------------------------------------------------------------
# 2. Python lint, format and type gates
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 2/5 Linting staged Python (ruff, flake8)...${RESET}"
if [ ${#STAGED_PY[@]} -gt 0 ]; then
  # Fully staged files: working tree == index, so check them on disk.
  if [ ${#FULLY_STAGED_PY[@]} -gt 0 ]; then
    "$PY" -m ruff check -- "${FULLY_STAGED_PY[@]}"
    "$PY" -m ruff format --check -- "${FULLY_STAGED_PY[@]}"
    "$PY" -m flake8 -- "${FULLY_STAGED_PY[@]}"
  fi
  # Partially staged files: check the staged blob (what will be committed), not the
  # working tree, so unstaged work-in-progress neither fails nor passes the commit.
  if [ ${#PARTIAL_PY[@]} -gt 0 ]; then
    for f in "${PARTIAL_PY[@]}"; do
      git show ":$f" | "$PY" -m ruff check --stdin-filename "$f" -
      git show ":$f" | "$PY" -m ruff format --check --stdin-filename "$f" - >/dev/null
      git show ":$f" | "$PY" -m flake8 --stdin-display-name "$f" -
    done
  fi
  echo -e "  ${GREEN}✓ ruff + flake8 clean.${RESET}"
else
  echo -e "  ${YELLOW}No staged Python files.${RESET}"
fi

if [ "$STAGED_CORE" -eq 1 ]; then
  echo -e "${CYAN}==> 3/5 Type checking and docstring coverage (mypy, interrogate)...${RESET}"
  "$PY" -m mypy src tests
  "$PY" -m interrogate src
else
  echo -e "${CYAN}==> 3/5 ${YELLOW}No staged src/ or tests/ Python files — skipping mypy & interrogate.${RESET}"
fi

# ------------------------------------------------------------------------------
# 4. Shell scripts
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 4/5 Validating staged shell scripts...${RESET}"
if [ ${#STAGED_SH[@]} -gt 0 ]; then
  for sh_file in "${STAGED_SH[@]}"; do
    bash -n "$sh_file"
  done
  if command -v shellcheck >/dev/null 2>&1; then
    shellcheck -x "${STAGED_SH[@]}"
  else
    echo -e "  ${RED}✗ shellcheck not installed (brew install shellcheck / apt-get install shellcheck).${RESET}"
    exit 1
  fi
  echo -e "  ${GREEN}✓ Shell scripts valid.${RESET}"
else
  echo -e "  ${YELLOW}No staged shell scripts.${RESET}"
fi

# ------------------------------------------------------------------------------
# 5. Tests (coverage gate is enforced by `make check` / CI, not here, for speed)
# ------------------------------------------------------------------------------
if [ "$STAGED_CORE" -eq 1 ] && [ "${RUNZERO_PRECOMMIT_SKIP_TESTS:-0}" != "1" ]; then
  echo -e "${CYAN}==> 5/5 Running test suite...${RESET}"
  "$PY" -m pytest -q -x --no-cov
  echo -e "  ${GREEN}✓ Tests passed.${RESET}"
elif [ "$STAGED_CORE" -eq 1 ]; then
  echo -e "${CYAN}==> 5/5 ${YELLOW}Skipping tests (RUNZERO_PRECOMMIT_SKIP_TESTS=1).${RESET}"
else
  echo -e "${CYAN}==> 5/5 ${YELLOW}Skipping tests (no staged src/ or tests/ Python files).${RESET}"
fi

# ------------------------------------------------------------------------------
# Website lint & format check (only when website files are staged)
# ------------------------------------------------------------------------------
if [ ${#STAGED_WEB[@]} -gt 0 ] && command -v npm >/dev/null 2>&1; then
  echo -e "${CYAN}==> Website: oxlint + prettier...${RESET}"
  WEB_REL=()
  for f in "${STAGED_WEB[@]}"; do
    case "$f" in
      *.astro | *.js | *.mjs | *.ts | *.css | *.json | *.md) WEB_REL+=("${f#website/}") ;;
    esac
  done
  (cd website && { npm ls oxlint >/dev/null 2>&1 || npm install >/dev/null 2>&1; } && npm run lint)
  if [ ${#WEB_REL[@]} -gt 0 ]; then
    (cd website && npm exec prettier -- --check "${WEB_REL[@]}") || {
      echo -e "  ${RED}✗ Prettier: formatting issues found. Run: make pre-stage && git add -u${RESET}"
      exit 1
    }
  fi
  echo -e "  ${GREEN}✓ Website checks passed.${RESET}"
fi

echo -e "\n${BOLD}${GREEN}✅ [RunZero Pre-Commit Guard] All quality checks passed.${RESET}\n"
