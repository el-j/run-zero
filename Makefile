# ==============================================================================
# Local GitHub Actions Runner & Autoscaler - Makefile (OrbStack / Docker)
# Multi-Architecture Support: Apple Silicon (ARM64) & Intel/AMD (AMD64 / x86_64)
# Persistent Package Caching + Proxy Registries (Verdaccio, Athens, Docker Mirror)
# ==============================================================================

.DEFAULT_GOAL := help

CACHE_DIR := $(HOME)/.local-github-runner/cache

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
	@echo "$(YELLOW)Multi-architecture CI execution with Verdaccio, Athens & Persistent Caching$(RESET)"
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

.PHONY: init-cache
init-cache: ## Initialize host cache directories
	@mkdir -p $(CACHE_DIR)/toolcache \
	          $(CACHE_DIR)/npm \
	          $(CACHE_DIR)/yarn \
	          $(CACHE_DIR)/pnpm \
	          $(CACHE_DIR)/pip \
	          $(CACHE_DIR)/uv \
	          $(CACHE_DIR)/go-mod \
	          $(CACHE_DIR)/go-build \
	          $(CACHE_DIR)/cargo-registry

.PHONY: cache-size
cache-size: ## Show disk usage of local runner caches and proxies
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Local Runner Cache Disk Usage ($(CACHE_DIR)) ===$(RESET)"
	@if [ -d "$(CACHE_DIR)" ]; then \
		du -sh $(CACHE_DIR)/* 2>/dev/null || echo "Cache directory is currently empty."; \
		echo ""; \
		echo "$(BOLD)Total Cache Size:$(RESET) $$(du -sh $(CACHE_DIR) 2>/dev/null | cut -f1)"; \
	else \
		echo "Cache directory does not exist yet. It will be created when runners run."; \
	fi
	@echo ""

.PHONY: clean-cache
clean-cache: ## Clear the persistent package and tool cache to reclaim disk space
	@echo "$(YELLOW)Clearing local runner caches at $(CACHE_DIR)...$(RESET)"
	@rm -rf $(CACHE_DIR)
	@echo "$(GREEN)Runner cache cleared successfully.$(RESET)"

.PHONY: docs
docs: ## Open documentation landing page in default browser
	@echo "$(CYAN)Opening documentation landing page...$(RESET)"
	@open docs/index.html || echo "Open docs/index.html in your browser."

.PHONY: verdaccio-ui
verdaccio-ui: ## Open Verdaccio Web UI in default browser (http://localhost:4873)
	@echo "$(CYAN)Opening Verdaccio Web UI at http://localhost:4873...$(RESET)"
	@open http://localhost:4873 || echo "Navigate to http://localhost:4873 in your browser."

.PHONY: build-arm64
build-arm64: ## Build native ARM64 runner image (Apple Silicon M-series)
	@echo "$(CYAN)Building native ARM64 runner image...$(RESET)"
	docker build --platform linux/arm64 -t local-github-runner:arm64 -t local-github-runner:latest ./docker
	@echo "$(GREEN)ARM64 runner built successfully!$(RESET)"

.PHONY: build-amd64
build-amd64: ## Build AMD64 / x86_64 runner image (via OrbStack Rosetta)
	@echo "$(CYAN)Building AMD64 / x86_64 runner image...$(RESET)"
	docker build --platform linux/amd64 -t local-github-runner:amd64 ./docker
	@echo "$(GREEN)AMD64 runner built successfully!$(RESET)"

.PHONY: build-autoscaler
build-autoscaler: ## Build the Autoscaler daemon image
	@echo "$(CYAN)Building Autoscaler daemon image...$(RESET)"
	docker build -f docker/Dockerfile.autoscaler -t local-runner-autoscaler:latest ./docker
	@echo "$(GREEN)Autoscaler built successfully!$(RESET)"

.PHONY: build build-all
build: build-arm64 build-amd64 build-autoscaler ## Build all images (ARM64 + AMD64 + Autoscaler)
build-all: build

.PHONY: start up
start: check-env init-cache ## Start Autoscaler and Proxy services (Verdaccio, Athens, Docker mirror)
	@echo "$(CYAN)Starting Local GitHub Runner Autoscaler & Proxy stack (OrbStack)...$(RESET)"
	docker compose up -d
	@echo "$(GREEN)Autoscaler and Proxy registries are running in background!$(RESET)"
	@echo "  • Verdaccio Web UI: $(BOLD)http://localhost:4873$(RESET) (Run $(BOLD)make verdaccio-ui$(RESET))"
	@echo "  • Athens Go Proxy:  $(BOLD)http://localhost:3000$(RESET)"
	@echo "  • Docker Mirror:    $(BOLD)http://localhost:5001$(RESET)"
	@echo "Use $(BOLD)make logs$(RESET) to stream logs or $(BOLD)make status$(RESET) to see active runners."

up: start

.PHONY: stop down
stop: ## Stop Autoscaler, Proxies, and remove active runner containers
	@echo "$(YELLOW)Stopping Autoscaler and unregistering active runners...$(RESET)"
	docker compose down
	@echo "$(GREEN)Autoscaler and proxies stopped.$(RESET)"

down: stop

.PHONY: restart
restart: stop start ## Restart Autoscaler and Proxies

.PHONY: logs
logs: ## Stream live logs from the Autoscaler
	@docker compose logs -f autoscaler

.PHONY: logs-all
logs-all: ## Stream live logs from all services (Autoscaler + Verdaccio + Athens)
	@docker compose logs -f

.PHONY: status ps
status: ## Show running Autoscaler, Proxies, and active dynamic runner containers
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Runner & Proxy Services ===$(RESET)"
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
test: check-env init-cache ## Run local autoscaler in foreground for quick debugging
	@echo "$(CYAN)Running Autoscaler in interactive foreground mode...$(RESET)"
	docker compose up
