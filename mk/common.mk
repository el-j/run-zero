# Shared variables, colours and `make help`.

CACHE_DIR := $(HOME)/.local-github-runner/cache
AUTOSCALER_PID_FILE := .autoscaler.pid
AUTOSCALER_LOG_FILE := .autoscaler.log
BRIDGE_LOG_FILE := .bridge.log

# Baked into the autoscaler image so it can tell when the bridge runs other code (#72).
export RUNZERO_GIT_SHA := $(shell git rev-parse --short=12 HEAD 2>/dev/null)

# Ensure Node >= 22 (from .nvmrc / NVM) is prioritized when active Node is older
NODE_BIN_22 := $(shell if [ "$$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)" -lt 22 ]; then \
	if [ -s "$$HOME/.nvm/nvm.sh" ]; then . "$$HOME/.nvm/nvm.sh" >/dev/null 2>&1; \
	elif [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then . "/opt/homebrew/opt/nvm/nvm.sh" >/dev/null 2>&1; fi; \
	if command -v nvm >/dev/null 2>&1; then \
		nvm_node="$$(nvm which 2>/dev/null | tail -n 1)"; \
		if [ -z "$$nvm_node" ] || [ "$$nvm_node" = "N/A" ]; then \
			nvm_node="$$(nvm which 22 2>/dev/null | tail -n 1)"; \
		fi; \
		if [ -n "$$nvm_node" ] && [ "$$nvm_node" != "N/A" ]; then \
			dirname "$$nvm_node"; \
		fi; \
	fi; \
fi)
ifneq ($(NODE_BIN_22),)
export PATH := $(NODE_BIN_22):$(PATH)
endif

# Colors for terminal styling
CYAN    := \033[36m
GREEN   := \033[32m
YELLOW  := \033[33m
RED     := \033[31m
RESET   := \033[0m
BOLD    := \033[1m

# True when npm is available (website tooling is optional for Go-only work).
HAVE_NPM := $(shell command -v npm >/dev/null 2>&1 && echo 1)

# Targets are documented with `target: deps ## description`; `##@ Title` lines
# start a new section in the help output (file order = include order).
.PHONY: help
help: ## Display available commands
	@printf "\n$(BOLD)$(CYAN)RunZero - Local GitHub Actions Runner & Autoscaler$(RESET)\n"
	@printf "Usage: make $(GREEN)<target>$(RESET)\n"
	@awk -v b="$(BOLD)" -v g="$(GREEN)" -v r="$(RESET)" 'BEGIN { FS = ":.*## " } \
		/^##@/ { printf "\n%s%s%s\n", b, substr($$0, 5), r } \
		/^[a-zA-Z0-9_-]+:.*## / { printf "  %s%-20s%s %s\n", g, $$1, r, $$2 }' $(MAKEFILE_LIST)
	@echo ""
