# Shell scripts, .env wizard and git hooks

SHELL_SCRIPTS := docker/start.sh docker/provision-toolchain.sh scripts/setup_env.sh \
	scripts/pre-commit.sh scripts/pre-push.sh scripts/bridge_supervisor.sh

##@ Scripts, env & git hooks

.PHONY: env
env: ## Run the interactive .env configuration wizard
	@bash scripts/setup_env.sh

.PHONY: check-env
check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file missing.$(RESET)"; \
		echo "Run $(BOLD)make env$(RESET) and set your $(BOLD)ACCESS_TOKEN$(RESET) first."; \
		exit 1; \
	fi

.PHONY: check-shell
check-shell: ## Shell gates: bash -n + shellcheck on every maintained script
	@for f in $(SHELL_SCRIPTS); do bash -n "$$f" || exit 1; done
	shellcheck -x $(SHELL_SCRIPTS)

.PHONY: install-hooks
install-hooks: ## Install the pre-commit and pre-push guards into .git/hooks/
	@echo "$(CYAN)Installing RunZero Git hooks (pre-commit & pre-push)...$(RESET)"
	@mkdir -p .git/hooks
	@printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' '' 'PROJECT_ROOT="$$(git rev-parse --show-toplevel 2>/dev/null || pwd)"' 'exec "$$PROJECT_ROOT/scripts/pre-commit.sh"' > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' '' 'PROJECT_ROOT="$$(git rev-parse --show-toplevel 2>/dev/null || pwd)"' 'exec "$$PROJECT_ROOT/scripts/pre-push.sh"' > .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "$(GREEN)Hooks installed successfully! pre-commit and pre-push guards are active.$(RESET)"
