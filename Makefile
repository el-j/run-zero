# ==============================================================================
# Local GitHub Actions Runner & Autoscaler - Makefile (OrbStack / Docker)
# Multi-Architecture Support: Apple Silicon (ARM64) & Intel/AMD (AMD64 / x86_64)
# Persistent Package Caching + Proxy Registries (Verdaccio, Athens, Docker Mirror)
# ==============================================================================

.DEFAULT_GOAL := help

CACHE_DIR := $(HOME)/.local-github-runner/cache
AUTOSCALER_PID_FILE := .autoscaler.pid
AUTOSCALER_LOG_FILE := .autoscaler.log

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
env: ## Run interactive .env configuration wizard
	@bash scripts/setup_env.sh

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

.PHONY: website-dev
website-dev: ## Run Astro static website in local dev mode
	@echo "$(CYAN)Starting Astro website development server...$(RESET)"
	@cd website && npm run dev

.PHONY: website-build
website-build: ## Build Astro static website and synchronize to docs/
	@echo "$(CYAN)Building Astro static documentation website...$(RESET)"
	@cd website && npm run build && rm -rf ../docs/* && cp -r dist/* ../docs/ && touch ../docs/.nojekyll
	@echo "$(GREEN)Astro website built and synced to docs/ successfully!$(RESET)"

.PHONY: verdaccio-ui
verdaccio-ui: ## Open Verdaccio Web UI in default browser (http://localhost:49501)
	@echo "$(CYAN)Opening Verdaccio Web UI at http://localhost:49501...$(RESET)"
	@open http://localhost:49501 || echo "Navigate to http://localhost:49501 in your browser."

.PHONY: build-arm64
build-arm64: ## Build native ARM64 runner image (Apple Silicon M-series)
	@echo "$(CYAN)Building native ARM64 runner image...$(RESET)"
	docker build --platform linux/arm64 -f docker/Dockerfile -t local-github-runner:arm64 -t local-github-runner:latest ./docker
	@echo "$(GREEN)ARM64 runner built successfully!$(RESET)"

.PHONY: build-amd64
build-amd64: ## Build AMD64 / x86_64 runner image (via OrbStack Rosetta)
	@echo "$(CYAN)Building AMD64 / x86_64 runner image...$(RESET)"
	docker build --platform linux/amd64 -f docker/Dockerfile -t local-github-runner:amd64 ./docker
	@echo "$(GREEN)AMD64 runner built successfully!$(RESET)"

.PHONY: build-autoscaler
build-autoscaler: ## Build the Autoscaler daemon image
	@echo "$(CYAN)Building Autoscaler daemon image...$(RESET)"
	docker build -f docker/Dockerfile.autoscaler -t local-runner-autoscaler:latest .
	@echo "$(GREEN)Autoscaler built successfully!$(RESET)"

.PHONY: build build-all
build: build-arm64 build-amd64 build-autoscaler ## Build all images (ARM64 + AMD64 + Autoscaler)
build-all: build

.PHONY: start up run
start: check-env init-cache ## Start Autoscaler (native host process) + Proxy services (Verdaccio, Athens, Docker mirror)
	@echo "$(CYAN)Starting caching proxy registries (Verdaccio, Athens, Docker mirror)...$(RESET)"
	@docker compose up -d
	@if [ -f $(AUTOSCALER_PID_FILE) ] && kill -0 "$$(cat $(AUTOSCALER_PID_FILE))" 2>/dev/null; then \
		echo "$(YELLOW)Autoscaler already running (PID $$(cat $(AUTOSCALER_PID_FILE))).$(RESET)"; \
	else \
		echo "$(CYAN)Starting Autoscaler as a native host process...$(RESET)"; \
		set -a; . ./.env; set +a; \
		PYTHONPATH=src nohup python3 -u src/autoscaler.py > $(AUTOSCALER_LOG_FILE) 2>&1 & \
		echo $$! > $(AUTOSCALER_PID_FILE); \
	fi
	@echo "$(GREEN)Autoscaler and Proxy registries are running in background!$(RESET)"
	@echo "  • Verdaccio Web UI: $(BOLD)http://localhost:49501$(RESET) (Run $(BOLD)make verdaccio-ui$(RESET))"
	@echo "  • Athens Go Proxy:  $(BOLD)http://localhost:49500$(RESET)"
	@echo "  • Docker Mirror:    $(BOLD)http://localhost:49502$(RESET)"
	@echo "Use $(BOLD)make logs$(RESET) to stream logs or $(BOLD)make status$(RESET) to see active runners."

up: start
run: start

.PHONY: stop down
stop: ## Stop Autoscaler, Proxies, and remove active runner containers
	@echo "$(YELLOW)Stopping Autoscaler and unregistering active runners...$(RESET)"
	@if [ -f $(AUTOSCALER_PID_FILE) ]; then \
		pid=$$(cat $(AUTOSCALER_PID_FILE)); \
		if kill -0 "$$pid" 2>/dev/null; then kill "$$pid"; fi; \
		rm -f $(AUTOSCALER_PID_FILE); \
	fi
	docker compose down
	@echo "$(GREEN)Autoscaler and proxies stopped.$(RESET)"

down: stop

.PHONY: restart
restart: stop start ## Restart Autoscaler and Proxies

.PHONY: logs
logs: ## Stream live logs from the Autoscaler (native host process)
	@touch $(AUTOSCALER_LOG_FILE) && tail -f $(AUTOSCALER_LOG_FILE)

.PHONY: logs-all
logs-all: ## Stream live logs from the Proxy services (Verdaccio + Athens + Docker mirror) -- see `make logs` for the Autoscaler
	@docker compose logs -f

.PHONY: status ps
status: ## Show running Autoscaler, Proxies, and active dynamic runners (containers + VMs)
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Autoscaler (native host process) ===$(RESET)"
	@if [ -f $(AUTOSCALER_PID_FILE) ] && kill -0 "$$(cat $(AUTOSCALER_PID_FILE))" 2>/dev/null; then \
		echo "Running (PID $$(cat $(AUTOSCALER_PID_FILE)))"; \
	else \
		echo "Not running -- run $(BOLD)make start$(RESET)"; \
	fi
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Proxy Services ===$(RESET)"
	@docker compose ps
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Active Ephemeral Runner Containers ===$(RESET)"
	@docker ps --filter "label=managed-by=local-autoscaler" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Labels}}"
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Active Ephemeral Runner VMs ===$(RESET)"
	@orbctl list 2>/dev/null | grep -i runzero-vm || echo "  (none)"
	@echo ""

.PHONY: start-container stop-container
start-container: check-env init-cache ## [Opt-in] Run Autoscaler fully containerized -- Docker driver only, VM drivers cannot work in this mode
	@echo "$(YELLOW)Starting fully containerized Autoscaler. VM drivers (orbstack-vm/wsl2/multipass) shell out$(RESET)"
	@echo "$(YELLOW)to host-native tools that cannot exist inside this container, so only the Docker driver$(RESET)"
	@echo "$(YELLOW)will ever be available in this mode. Use 'make start' instead for full VM support.$(RESET)"
	docker compose --profile container-autoscaler up -d
	@echo "$(GREEN)Containerized Autoscaler and Proxy registries are running!$(RESET)"

stop-container: ## [Opt-in] Stop the fully containerized Autoscaler mode
	docker compose --profile container-autoscaler down

.PHONY: clean
clean: ## Force clean stopped containers and temporary runner volumes
	@echo "$(YELLOW)Cleaning up stopped runner containers and volumes...$(RESET)"
	docker compose down -v
	@docker rm -f $$(docker ps -a -q --filter "label=managed-by=local-autoscaler") 2>/dev/null || true
	@echo "$(GREEN)Cleaned up successfully.$(RESET)"

.PHONY: vm-list
vm-list: ## List active OrbStack Linux runner VMs
	@echo "$(CYAN)Listing active RunZero OrbStack VMs...$(RESET)"
	@orbctl list || true

.PHONY: vm-clean
vm-clean: ## Clean up any orphaned ephemeral RunZero VMs (does NOT touch the golden base image -- see vm-rebuild-base)
	@echo "$(YELLOW)Cleaning up any orphaned RunZero VMs...$(RESET)"
	@for vm in $$(orbctl list -q 2>/dev/null | grep '^runzero-vm-' | grep -v '^runzero-vm-base-'); do \
		echo "Deleting $$vm..."; \
		orbctl delete -f $$vm || true; \
	done
	@echo "$(GREEN)VM cleanup complete.$(RESET)"

.PHONY: build-vm-base
build-vm-base: ## Build the golden OrbStack VM base image (Docker/Node/nvm/.NET/Chrome/Playwright pre-installed) so ephemeral job VMs clone instantly instead of re-provisioning from scratch every run. Takes several minutes; run it once, and again whenever you change docker/provision-toolchain.sh.
	@echo "$(CYAN)Building golden OrbStack VM base image(s) -- this takes several minutes...$(RESET)"
	@for a in $$(if [ "$(RUNNER_ARCH)" = "both" ] || [ -z "$(RUNNER_ARCH)" ]; then echo "arm64 amd64"; else echo "$(RUNNER_ARCH)"; fi); do \
		python3 -c "import sys; sys.path.insert(0, 'src'); from drivers.orbstack_vm_driver import OrbStackVMDriver; sys.exit(0 if OrbStackVMDriver().build_base_image('$$a') else 1)" || exit 1; \
	done
	@echo "$(GREEN)Golden VM base image(s) ready. Ephemeral VM-routed jobs will now clone instantly.$(RESET)"

.PHONY: vm-rebuild-base
vm-rebuild-base: build-vm-base ## Alias for build-vm-base -- use after changing docker/provision-toolchain.sh to refresh the golden image

.PHONY: test-suite
test-suite: ## Run test suite with pytest, mypy type checking, and flake8 linter
	@echo "$(CYAN)Running Flake8, Mypy, and Pytest coverage suite...$(RESET)"
	@docker run --rm -v "$$(pwd):/app" -w /app python:3.11-slim bash -c "\
		pip install --quiet pytest pytest-cov mypy flake8 && \
		flake8 src/ tests/ --max-line-length=160 --extend-ignore=E501,W503,E402 && \
		MYPYPATH=src mypy src/drivers/ src/autoscaler.py --ignore-missing-imports && \
		PYTHONPATH=src pytest --cov=src --cov-report=term-missing tests/"
	@echo "$(GREEN)All tests passed with 0 warnings!$(RESET)"

.PHONY: mutation-test
mutation-test: ## Run mutation testing suite (mutmut)
	@echo "$(CYAN)Running Mutmut Mutation Testing Suite...$(RESET)"
	@docker run --rm -v "$$(pwd):/app" -w /app python:3.11-slim bash -c "\
		pip install --quiet pytest mutmut && \
		PYTHONPATH=src mutmut run || true && \
		mutmut results"

.PHONY: test
test: ## Run local unit tests directly
	@python3 -m unittest discover -s tests -p "test_*.py" -v

.PHONY: run-dev
run-dev: check-env init-cache ## Run local autoscaler in foreground for interactive debugging (native, full VM support)
	@echo "$(CYAN)Starting caching proxy registries (Verdaccio, Athens, Docker mirror)...$(RESET)"
	docker compose up -d
	@echo "$(CYAN)Running Autoscaler in interactive foreground mode (native host process)...$(RESET)"
	@set -a; . ./.env; set +a; PYTHONPATH=src python3 -u src/autoscaler.py



