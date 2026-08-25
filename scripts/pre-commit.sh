#!/usr/bin/env bash
# ==============================================================================
# RunZero Pre-Commit Quality Guard & Auto-Fixer
# Validates code style, static types, shell syntax, and runs unit tests.
# Automatically fixes formatting and re-stages updated files.
# ==============================================================================

set -eo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}${CYAN}🔍 [RunZero Pre-Commit Guard] Running quality checks & auto-fixes...${RESET}"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"

AUTOFIXED=0

# ------------------------------------------------------------------------------
# 1. Auto-Fix Trailing Whitespace & Newlines in Python, Shell, and Astro files
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 1/5 Checking and auto-fixing trailing whitespace & file endings...${RESET}"
while IFS= read -r file; do
  if [ -f "$file" ]; then
    # Strip trailing carriage returns and whitespace
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' -E 's/[[:space:]]+$//' "$file" 2>/dev/null || true
    else
      sed -i -E 's/[[:space:]]+$//' "$file" 2>/dev/null || true
    fi
    # Ensure newline at EOF
    if [ -n "$(tail -c 1 "$file" 2>/dev/null)" ]; then
      echo "" >> "$file"
    fi
  fi
done < <(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|sh|astro|md|yml|yaml|json|css)$' || true)

# ------------------------------------------------------------------------------
# 2. Python Formatting & Auto-Fixes (ruff / autopep8 / black if available)
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 2/5 Running Python auto-fixers (imports, formatting)...${RESET}"
PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.py$' || true)

if [ -n "$PY_FILES" ]; then
  if command -v ruff >/dev/null 2>&1; then
    echo -e "  • Using ${BOLD}ruff${RESET} to auto-fix Python linting & formatting..."
    echo "$PY_FILES" | xargs ruff check --fix --line-length=160 2>/dev/null || true
    echo "$PY_FILES" | xargs ruff format --line-length=160 2>/dev/null || true
  elif command -v autopep8 >/dev/null 2>&1; then
    echo -e "  • Using ${BOLD}autopep8${RESET} to auto-format Python code..."
    echo "$PY_FILES" | xargs autopep8 --in-place --aggressive --max-line-length=160 2>/dev/null || true
  fi

  # Re-stage any auto-fixed files
  echo "$PY_FILES" | xargs git add 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# 3. Flake8 Linting & Mypy Type Checking
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 3/5 Checking Python syntax, linting (Flake8) & types (Mypy)...${RESET}"
if command -v flake8 >/dev/null 2>&1; then
  flake8 src/ tests/ --max-line-length=160 --extend-ignore=E501,W503,E402
  echo -e "  ${GREEN}✓ Flake8: 0 lint errors.${RESET}"
else
  # Fallback: check syntax using python -m py_compile
  find src tests -name "*.py" -exec python3 -m py_compile {} +
  echo -e "  ${GREEN}✓ Python syntax: Valid (flake8 not installed locally).${RESET}"
fi

if command -v mypy >/dev/null 2>&1; then
  MYPYPATH=src mypy src/ --ignore-missing-imports
  echo -e "  ${GREEN}✓ Mypy: 100% Type Safe.${RESET}"
fi

# ------------------------------------------------------------------------------
# 4. Shell Script Syntax Validation
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 4/5 Validating Shell Scripts (bash -n)...${RESET}"
for sh_file in docker/start.sh docker/provision-toolchain.sh scripts/setup_env.sh scripts/pre-commit.sh; do
  if [ -f "$sh_file" ]; then
    bash -n "$sh_file"
    echo -e "  ${GREEN}✓ $sh_file: Syntax valid.${RESET}"
  fi
done

# ------------------------------------------------------------------------------
# 5. Fast Local Unit Tests
# ------------------------------------------------------------------------------
echo -e "${CYAN}==> 5/5 Running unit test suite...${RESET}"
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py" > /dev/null
echo -e "  ${GREEN}✓ Unit Tests: All tests passed successfully!${RESET}"

echo -e "\n${BOLD}${GREEN}✅ [RunZero Pre-Commit Guard] All quality checks passed. Proceeding with commit!${RESET}\n"
exit 0
