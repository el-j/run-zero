# ==============================================================================
# Local GitHub Actions Runner & Autoscaler - Makefile (OrbStack / Docker)
# Multi-Architecture Support: Apple Silicon (ARM64) & Intel/AMD (AMD64 / x86_64)
# ==============================================================================

.DEFAULT_GOAL := help

# Colors for terminal styling
CYAN    := \033[36m
GREEN   := \033[32m
YELLOW  := \033[33m
RED     := \033[31m
MAGENTA := \033[35m
RESET   := \033[0m
BOLD    := \033[1m

.PHONY: help
help: ## Display available commands
	@echo ""
	@echo "$(BOLD)$(CYAN)Local GitHub Actions Runner & Autoscaler (OrbStack)$(RESET)"
	@echo "$(YELLOW)Multi-architecture CI execution (ARM64 Native + AMD64 Rosetta Emulation)$(RESET)"
	@echo ""
	@echo "$(BOLD)Usage:$(RESET) make $(GREEN)<target>$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""

.PHONY: env
env: ## Create .env from template if missing
	@if [ ! -f .env ]; then \
		echo "$(CYAN)Creating .env from .env.example...$(RESET)"; \
		cp .env.example .env; \
		echo "$(GREEN)Created .env$(RESET) - Please edit it and set your $(BOLD)ACCESS_TOKEN$(RESET) & $(BOLD)OWNER$(RESET)."; \
	else \
		echo "$(YELLOW).env file already exists.$(RESET)"; \
	fi

.PHONY: check-env
check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file missing.$(RESET)"; \
		echo "Run $(BOLD)make env$(RESET) and set your $(BOLD)ACCESS_TOKEN$(RESET) first."; \
		exit 1; \
	fi

.PHONY: build-arm64
build-arm64: ## Build native ARM64 runner image (Apple Silicon M-series)
	@echo "$(CYAN)Building native ARM64 runner image...$(RESET)"
	docker build --platform linux/arm64 -t local-github-runner:arm64 -t local-github-runner:latest .
	@echo "$(GREEN)ARM64 runner built successfully!$(RESET)"

.PHONY: build-amd64
build-amd64: ## Build AMD64 / x86_64 runner image (via OrbStack Rosetta)
	@echo "$(CYAN)Building AMD64 / x86_64 runner image...$(RESET)"
	docker build --platform linux/amd64 -t local-github-runner:amd64 .
	@echo "$(GREEN)AMD64 runner built successfully!$(RESET)"

.PHONY: build-autoscaler
build-autoscaler: ## Build the Autoscaler daemon image
	@echo "$(CYAN)Building Autoscaler daemon image...$(RESET)"
	docker build -f Dockerfile.autoscaler -t local-runner-autoscaler:latest .
	@echo "$(GREEN)Autoscaler built successfully!$(RESET)"

.PHONY: build build-all
build: build-arm64 build-amd64 build-autoscaler ## Build all images (ARM64 + AMD64 + Autoscaler)
build-all: build

.PHONY: start up
start: check-env ## Start the multi-arch Autoscaler in background
	@echo "$(CYAN)Starting Local GitHub Runner Autoscaler (OrbStack)...$(RESET)"
	docker compose up -d
	@echo "$(GREEN)Autoscaler is running in background!$(RESET)"
	@echo "Use $(BOLD)make logs$(RESET) to stream logs or $(BOLD)make status$(RESET) to see active runners."

up: start

.PHONY: stop down
stop: ## Stop the Autoscaler and remove active runner containers
	@echo "$(YELLOW)Stopping Autoscaler and unregistering active runners...$(RESET)"
	docker compose down
	@echo "$(GREEN)Autoscaler stopped.$(RESET)"

down: stop

.PHONY: restart
restart: stop start ## Restart the Autoscaler

.PHONY: logs
logs: ## Stream live logs from the Autoscaler
	@docker compose logs -f autoscaler

.PHONY: status ps
status: ## Show running Autoscaler and active dynamic runner containers
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Autoscaler Service ===$(RESET)"
	@docker compose ps
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Active Ephemeral Runner Containers ===$(RESET)"
	@docker ps --filter "label=managed-by=local-autoscaler" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Labels}}"
	@echo ""

.PHONY: clean
clean: ## Force clean stopped containers and temporary runner volumes
	@echo "$(YELLOW)Cleaning up stopped runner containers and volumes...$(RESET)"
	docker compose down -v
	@docker rm -f $$(docker ps -a -q --filter "label=managed-by=local-autoscaler") 2>/dev/null || true
	@echo "$(GREEN)Cleaned up successfully.$(RESET)"

.PHONY: test
test: check-env ## Run local autoscaler in foreground for quick debugging
	@echo "$(CYAN)Running Autoscaler in interactive foreground mode...$(RESET)"
	docker compose up
