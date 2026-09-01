# ==============================================================================
# Local GitHub Actions Runner & Autoscaler - Makefile (OrbStack / Docker)
# Multi-Architecture Support: Apple Silicon (ARM64) & Intel/AMD (AMD64 / x86_64)
# Persistent Package Caching + Proxy Registries (Verdaccio, Athens, Docker Mirror, devpi, kellnr)
# ==============================================================================

.DEFAULT_GOAL := help

CACHE_DIR := $(HOME)/.local-github-runner/cache
WEBSITE_DIR := website
AUTOSCALER_PID_FILE := .autoscaler.pid
AUTOSCALER_LOG_FILE := .autoscaler.log
BRIDGE_PID_FILE := .bridge.pid
BRIDGE_LOG_FILE := .bridge.log

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
cache-size: ## Show disk usage of the host package/tool cache only (subset of `make info`)
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
clean-cache: ## Clear the persistent package/tool cache dir ($(CACHE_DIR)) only -- see `make clean-caches` to also clear proxy volumes and images
	@echo "$(YELLOW)Clearing local runner caches at $(CACHE_DIR)...$(RESET)"
	@chmod -R u+w $(CACHE_DIR) 2>/dev/null || true
	@rm -rf $(CACHE_DIR) 2>/dev/null || docker run --rm -v "$(CACHE_DIR):/cache" alpine sh -c "rm -rf /cache/* /cache/.*" 2>/dev/null || true
	@rm -rf $(CACHE_DIR) 2>/dev/null || true
	@echo "$(GREEN)Runner cache cleared successfully.$(RESET)"

# ==============================================================================
# Disk Usage & Cache Management
# ==============================================================================
# Named docker volumes are found by their Compose *logical* name (the
# com.docker.compose.volume label), not a hardcoded "<project>_<name>" string --
# the project-name prefix Compose derives depends on the checkout directory's
# name, which isn't fixed.
define find_volume
$$(docker volume ls --filter "label=com.docker.compose.volume=$(1)" -q | head -1)
endef

.PHONY: info
info: ## Show total disk usage of everything run-zero manages: host cache dir, proxy volumes, runner images, and OrbStack VMs
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Host Package/Tool Cache ($(CACHE_DIR)) ===$(RESET)"
	@if [ -d "$(CACHE_DIR)" ]; then \
		du -sh $(CACHE_DIR)/* 2>/dev/null | sort -k2 || echo "  (empty)"; \
		echo "  $(BOLD)Subtotal:$(RESET) $$(du -sh $(CACHE_DIR) 2>/dev/null | cut -f1)"; \
	else \
		echo "  (not created yet)"; \
	fi
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Proxy Cache Volumes (Verdaccio/Athens/Docker Mirror/apt-cacher-ng/devpi/kellnr) ===$(RESET)"
	@for v in verdaccio-storage athens-storage docker-mirror-storage apt-cacher-storage devpi-storage kellnr-storage; do \
		vol=$(call find_volume,$$v); \
		if [ -n "$$vol" ]; then \
			size=$$(docker run --rm -v "$$vol":/data:ro alpine du -sh /data 2>/dev/null | cut -f1); \
			echo "  $$v: $${size:-unknown}"; \
		else \
			echo "  $$v: (not created yet)"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Runner Images ===$(RESET)"
	@docker images --filter "reference=local-github-runner*" --filter "reference=local-runner-autoscaler*" \
		--format "  {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  (none built yet)"
	@echo ""
	@echo "$(BOLD)$(CYAN)=== OrbStack VMs (golden base image + any still-active ephemeral runners) ===$(RESET)"
	@orbctl list 2>/dev/null | grep -i runzero-vm || echo "  (none)"
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Ephemeral Runner Containers ===$(RESET)"
	@docker ps -a --filter "label=managed-by=local-autoscaler" --format "  {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (none)"
	@echo ""

.PHONY: clean-caches
clean-caches: clean-cache clean-verdaccio clean-athens clean-docker-mirror clean-apt-cacher clean-devpi clean-kellnr ## Clear EVERY cache run-zero manages: host cache dir + all proxy volumes (does NOT touch runner images or the VM base image -- see clean-images/vm-clean)
	@echo "$(GREEN)All run-zero caches cleared.$(RESET)"

.PHONY: clean-npm clean-yarn clean-pnpm clean-pip clean-uv clean-go-mod clean-go-build clean-cargo-registry clean-toolcache
clean-npm: ## Clear only the cached npm packages
	@rm -rf $(CACHE_DIR)/npm && echo "$(GREEN)npm cache cleared.$(RESET)"
clean-yarn: ## Clear only the cached yarn packages
	@rm -rf $(CACHE_DIR)/yarn && echo "$(GREEN)yarn cache cleared.$(RESET)"
clean-pnpm: ## Clear only the cached pnpm store
	@rm -rf $(CACHE_DIR)/pnpm && echo "$(GREEN)pnpm cache cleared.$(RESET)"
clean-pip: ## Clear only the cached pip packages
	@rm -rf $(CACHE_DIR)/pip && echo "$(GREEN)pip cache cleared.$(RESET)"
clean-uv: ## Clear only the cached uv packages
	@rm -rf $(CACHE_DIR)/uv && echo "$(GREEN)uv cache cleared.$(RESET)"
clean-go-mod: ## Clear only the cached Go module downloads
	@chmod -R u+w $(CACHE_DIR)/go-mod 2>/dev/null || true
	@rm -rf $(CACHE_DIR)/go-mod 2>/dev/null || docker run --rm -v "$(CACHE_DIR)/go-mod:/cache" alpine sh -c "rm -rf /cache/* /cache/.*" 2>/dev/null || true
	@rm -rf $(CACHE_DIR)/go-mod 2>/dev/null || true
	@echo "$(GREEN)Go module cache cleared.$(RESET)"
clean-go-build: ## Clear only the cached Go build cache
	@rm -rf $(CACHE_DIR)/go-build && echo "$(GREEN)Go build cache cleared.$(RESET)"
clean-cargo-registry: ## Clear only the cached Cargo registry
	@rm -rf $(CACHE_DIR)/cargo-registry && echo "$(GREEN)Cargo registry cache cleared.$(RESET)"
clean-toolcache: ## Clear only the cached hosted tool versions (Node/Go/etc SDK installs, per-arch)
	@chmod -R u+w $(CACHE_DIR)/toolcache 2>/dev/null || true
	@rm -rf $(CACHE_DIR)/toolcache 2>/dev/null || true
	@echo "$(GREEN)Tool cache cleared.$(RESET)"

.PHONY: clean-verdaccio clean-athens clean-docker-mirror clean-apt-cacher
clean-verdaccio: ## Wipe the Verdaccio (npm proxy) cache volume
	@docker compose stop verdaccio >/dev/null 2>&1 || true
	@docker compose rm -f verdaccio >/dev/null 2>&1 || true
	@vol=$(call find_volume,verdaccio-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)Verdaccio cache cleared.$(RESET) Run 'make start' to recreate it."
clean-athens: ## Wipe the Athens (Go module proxy) cache volume
	@docker compose stop athens >/dev/null 2>&1 || true
	@docker compose rm -f athens >/dev/null 2>&1 || true
	@vol=$(call find_volume,athens-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)Athens cache cleared.$(RESET) Run 'make start' to recreate it."
clean-docker-mirror: ## Wipe the Docker Hub pull-through mirror cache volume
	@docker compose stop docker-mirror >/dev/null 2>&1 || true
	@docker compose rm -f docker-mirror >/dev/null 2>&1 || true
	@vol=$(call find_volume,docker-mirror-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)Docker mirror cache cleared.$(RESET) Run 'make start' to recreate it."
clean-apt-cacher: ## Wipe the apt-cacher-ng (.deb package proxy) cache volume
	@docker compose stop apt-cacher >/dev/null 2>&1 || true
	@docker compose rm -f apt-cacher >/dev/null 2>&1 || true
	@vol=$(call find_volume,apt-cacher-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)apt-cacher-ng cache cleared.$(RESET) Run 'make start' to recreate it."

.PHONY: clean-devpi clean-kellnr
clean-devpi: ## Wipe the devpi (pip/uv PyPI proxy) cache volume
	@docker compose stop devpi >/dev/null 2>&1 || true
	@docker compose rm -f devpi >/dev/null 2>&1 || true
	@vol=$(call find_volume,devpi-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)devpi cache cleared.$(RESET) Run 'make start' to recreate it."
clean-kellnr: ## Wipe the kellnr (Cargo/crates.io proxy) cache volume
	@docker compose stop kellnr >/dev/null 2>&1 || true
	@docker compose rm -f kellnr >/dev/null 2>&1 || true
	@vol=$(call find_volume,kellnr-storage); [ -n "$$vol" ] && docker volume rm "$$vol" >/dev/null 2>&1 || true
	@echo "$(GREEN)kellnr cache cleared.$(RESET) Run 'make start' to recreate it."

.PHONY: clean-images
clean-images: ## Remove the built runner/autoscaler images (local-github-runner:*, local-runner-autoscaler:*) -- forces a full rebuild next time
	@docker rmi -f local-github-runner:arm64 local-github-runner:amd64 local-github-runner:latest local-runner-autoscaler:latest 2>/dev/null || true
	@echo "$(GREEN)Runner images removed.$(RESET) Run 'make build' to rebuild."

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

.PHONY: dashboard
dashboard: ## Open RunZero Real-Time Observability Web Dashboard in browser (http://localhost:49505)
	@echo "$(CYAN)Opening RunZero Observability Dashboard at http://localhost:49505...$(RESET)"
	@open http://localhost:49505 || echo "Navigate to http://localhost:49505 in your browser."

.PHONY: bridge-start bridge-stop bridge-status bridge-logs
bridge-start: ## Start Host VM Bridge server on host (port 49504)
	@if [ -f $(BRIDGE_PID_FILE) ] && kill -0 "$$(cat $(BRIDGE_PID_FILE))" 2>/dev/null; then \
		echo "$(YELLOW)Host VM Bridge already running (PID $$(cat $(BRIDGE_PID_FILE))).$(RESET)"; \
	else \
		echo "$(CYAN)Starting Host VM Bridge on http://localhost:49504...$(RESET)"; \
		set -a; [ -f .env ] && . ./.env; set +a; \
		PYTHONPATH=src nohup python3 -u src/vm_bridge.py > $(BRIDGE_LOG_FILE) 2>&1 & \
		echo $$! > $(BRIDGE_PID_FILE); \
		echo "$(GREEN)Host VM Bridge running in background (PID $$(cat $(BRIDGE_PID_FILE))).$(RESET)"; \
	fi

bridge-stop: ## Stop Host VM Bridge server
	@echo "$(YELLOW)Stopping Host VM Bridge...$(RESET)"
	@if [ -f $(BRIDGE_PID_FILE) ]; then \
		pid=$$(cat $(BRIDGE_PID_FILE)); \
		if kill -0 "$$pid" 2>/dev/null; then kill "$$pid"; fi; \
		rm -f $(BRIDGE_PID_FILE); \
	fi
	@echo "$(GREEN)Host VM Bridge stopped.$(RESET)"

bridge-status: ## Check Host VM Bridge status
	@echo "$(BOLD)$(CYAN)=== Host VM Bridge (port 49504) ===$(RESET)"
	@if [ -f $(BRIDGE_PID_FILE) ] && kill -0 "$$(cat $(BRIDGE_PID_FILE))" 2>/dev/null; then \
		echo "Running (PID $$(cat $(BRIDGE_PID_FILE)))"; \
	else \
		echo "Not running"; \
	fi

bridge-logs: ## Stream live logs from the Host VM Bridge
	@touch $(BRIDGE_LOG_FILE) && tail -f $(BRIDGE_LOG_FILE)

.PHONY: start up run
start: check-env init-cache bridge-start ## Start containerized Autoscaler + Host VM Bridge + Proxy services + Web Dashboard
	@echo "$(CYAN)Starting RunZero containerized stack (Autoscaler, Dashboard, Proxy registries)...$(RESET)"
	@docker compose up -d
	@echo "$(GREEN)RunZero Fleet & Observability Stack is running!$(RESET)"
	@echo "  • 📊 Web Dashboard:  $(BOLD)http://localhost:49505$(RESET) (Run $(BOLD)make dashboard$(RESET))"
	@echo "  • 🌉 Host VM Bridge: $(BOLD)http://localhost:49504$(RESET)"
	@echo "  • 📦 Verdaccio UI:   $(BOLD)http://localhost:49501$(RESET) (Run $(BOLD)make verdaccio-ui$(RESET))"
	@echo "  • 🐧 APT Cacher:     $(BOLD)http://localhost:49503/acng-report.html$(RESET) (Run $(BOLD)make apt-cacher-ui$(RESET))"
	@echo "  • 🐹 Athens Go:      $(BOLD)http://localhost:49500$(RESET)"
	@echo "  • 🐳 Docker Mirror:  $(BOLD)http://localhost:49502$(RESET)"
	@echo "  • 🐍 devpi (pip/uv): $(BOLD)http://localhost:49507/root/pypi/+simple/$(RESET)"
	@echo "  • 🦀 kellnr (Cargo): $(BOLD)http://localhost:49506$(RESET)"
	@echo "Use $(BOLD)make logs$(RESET) to stream logs or $(BOLD)make status$(RESET) to see active runners."

up: start
run: start

.PHONY: stop down
stop: bridge-stop ## Stop Autoscaler, Host VM Bridge, Proxies, and remove active runner containers
	@echo "$(YELLOW)Stopping Autoscaler and unregistering active runners...$(RESET)"
	@if [ -f $(AUTOSCALER_PID_FILE) ]; then \
		pid=$$(cat $(AUTOSCALER_PID_FILE)); \
		if kill -0 "$$pid" 2>/dev/null; then kill "$$pid"; fi; \
		rm -f $(AUTOSCALER_PID_FILE); \
	fi
	docker compose down
	@echo "$(GREEN)Autoscaler, VM bridge, and proxies stopped.$(RESET)"

down: stop

.PHONY: restart
restart: stop start ## Restart Autoscaler and Proxies

.PHONY: logs
logs: ## Stream live logs from the Autoscaler container
	@docker compose logs -f autoscaler 2>/dev/null || (touch $(AUTOSCALER_LOG_FILE) && tail -f $(AUTOSCALER_LOG_FILE))

.PHONY: logs-all
logs-all: ## Stream live logs from all services (Autoscaler + Proxies)
	@docker compose logs -f

.PHONY: status ps
status: bridge-status ## Show running Autoscaler, VM Bridge, Proxies, and active dynamic runners (containers + VMs)
	@echo ""
	@echo "$(BOLD)$(CYAN)=== RunZero Container Stack (Autoscaler & Proxies) ===$(RESET)"
	@docker compose ps
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Active Ephemeral Runner Containers ===$(RESET)"
	@docker ps --filter "label=managed-by=local-autoscaler" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Labels}}"
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Active Ephemeral Runner VMs ===$(RESET)"
	@orbctl list 2>/dev/null | grep -i runzero-vm || echo "  (none)"
	@echo ""

.PHONY: start-host stop-host
start-host: check-env init-cache bridge-start ## Start Autoscaler natively on host Python (without containerizing autoscaler)
	@echo "$(CYAN)Starting caching proxy registries (Verdaccio, Athens, Docker mirror, apt-cacher, devpi, kellnr)...$(RESET)"
	@docker compose up -d verdaccio athens docker-mirror apt-cacher devpi kellnr
	@if [ -f $(AUTOSCALER_PID_FILE) ] && kill -0 "$$(cat $(AUTOSCALER_PID_FILE))" 2>/dev/null; then \
		echo "$(YELLOW)Autoscaler already running on host (PID $$(cat $(AUTOSCALER_PID_FILE))).$(RESET)"; \
	else \
		echo "$(CYAN)Starting Autoscaler with Web Dashboard on host...$(RESET)"; \
		set -a; . ./.env; set +a; \
		PYTHONPATH=src nohup python3 -u src/autoscaler.py > $(AUTOSCALER_LOG_FILE) 2>&1 & \
		echo $$! > $(AUTOSCALER_PID_FILE); \
	fi
	@echo "$(GREEN)Host Autoscaler & Stack is running!$(RESET)"

stop-host: stop ## Stop host Autoscaler and stack

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

.PHONY: vm-clean-all
vm-clean-all: ## Delete ALL RunZero OrbStack VMs including golden base images
	@echo "$(YELLOW)Deleting all RunZero VMs including base master templates...$(RESET)"
	@for vm in $$(orbctl list -q 2>/dev/null | grep '^runzero-vm-'); do \
		echo "Deleting $$vm..."; \
		orbctl delete -f $$vm || true; \
	done
	@echo "$(GREEN)All RunZero VMs deleted.$(RESET)"

.PHONY: clean-all reset-all
clean-all: stop clean vm-clean-all clean-caches clean-images ## Complete nuclear reset: stop autoscaler, wipe all caches, delete all VMs, and remove images for fresh out-of-the-box test
	@echo "$(GREEN)RunZero completely reset to fresh out-of-the-box state.$(RESET)"

reset-all: clean-all

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
		apt-get update -qq && apt-get install -y -qq --no-install-recommends make > /dev/null && \
		pip install --quiet pytest pytest-cov mypy flake8 && \
		flake8 src/ tests/ --max-line-length=160 --extend-ignore=E501,W503,E402 && \
		MYPYPATH=src mypy src/ --ignore-missing-imports && \
		PYTHONPATH=src pytest --cov=src --cov-report=term-missing tests/"
	@echo "$(GREEN)All tests passed with 0 warnings!$(RESET)"

.PHONY: mutation-test
mutation-test: ## Run mutation testing suite (mutmut) -- fails the build on surviving mutants
	@echo "$(CYAN)Running Mutmut Mutation Testing Suite...$(RESET)"
	@docker run --rm -v "$$(pwd):/app" -w /app python:3.11-slim bash -c "\
		apt-get update -qq && apt-get install -y -qq --no-install-recommends make > /dev/null && \
		pip install --quiet pytest pytest-cov mutmut && \
		PYTHONPATH=src mutmut run; \
		status=\$$?; \
		mutmut results; \
		exit \$$status"

.PHONY: test
test: ## Run local unit tests directly
	@PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py" -v

.PHONY: install-hooks
install-hooks: ## Install RunZero pre-commit quality guard into .git/hooks/pre-commit
	@echo "$(CYAN)Installing RunZero pre-commit hook...$(RESET)"
	@mkdir -p .git/hooks
	@cp scripts/pre-commit.sh .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)Pre-commit hook installed successfully! Every git commit will now be guarded.$(RESET)"

.PHONY: pre-commit
pre-commit: ## Run the RunZero pre-commit quality guard manually
	@bash scripts/pre-commit.sh

.PHONY: lint
lint: ## Run Flake8 linter and Mypy static type checker
	@echo "$(CYAN)Running Flake8 linter...$(RESET)"
	@flake8 src/ tests/ --max-line-length=160 --extend-ignore=E501,W503,E402 || echo "Install flake8 for full linting."
	@echo "$(CYAN)Running Mypy type checker...$(RESET)"
	@MYPYPATH=src mypy src/ --ignore-missing-imports || echo "Install mypy for full typechecking."

.PHONY: deps-check
deps-check: ## Check dependency update opportunities (Python env + website Node packages)
	@echo "$(CYAN)Checking Python environment dependency updates...$(RESET)"
	@if command -v python3 >/dev/null 2>&1; then \
		python3 -m pip list --outdated --format=columns 2>/dev/null || echo "Unable to query Python package updates in current environment."; \
	else \
		echo "python3 not found; skipping Python dependency check."; \
	fi
	@echo "$(CYAN)Checking website Node package updates (npm outdated + ncu)...$(RESET)"
	@if command -v npm >/dev/null 2>&1; then \
		(cd $(WEBSITE_DIR) && npm outdated || true); \
		if command -v ncu >/dev/null 2>&1; then \
			(cd $(WEBSITE_DIR) && ncu); \
		else \
			(cd $(WEBSITE_DIR) && npx -y npm-check-updates); \
		fi; \
	else \
		echo "npm not found; skipping Node dependency check."; \
	fi

.PHONY: deps-update
deps-update: ## Apply dependency updates where possible (website package.json via ncu)
	@echo "$(CYAN)Updating website Node dependencies...$(RESET)"
	@if command -v npm >/dev/null 2>&1; then \
		if command -v ncu >/dev/null 2>&1; then \
			(cd $(WEBSITE_DIR) && ncu -u); \
		else \
			(cd $(WEBSITE_DIR) && npx -y npm-check-updates -u); \
		fi; \
		(cd $(WEBSITE_DIR) && npm install); \
	else \
		echo "npm not found; cannot update website dependencies automatically."; \
	fi
	@echo "$(YELLOW)Python dependency updates are environment-specific; use your venv manager (pip/uv/poetry) to apply upgrades intentionally.$(RESET)"

.PHONY: fmt-check
fmt-check: ## Check formatting for Python and website sources
	@echo "$(CYAN)Checking Python formatting...$(RESET)"
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format --check --line-length=160 src/ tests/; \
	elif command -v black >/dev/null 2>&1; then \
		black --check --line-length=160 src/ tests/; \
	else \
		echo "Install ruff or black for Python format checks."; \
	fi
	@echo "$(CYAN)Checking website formatting with Prettier...$(RESET)"
	@if command -v npm >/dev/null 2>&1; then \
		(cd $(WEBSITE_DIR) && { npm ls prettier-plugin-astro >/dev/null 2>&1 || npm install; } && \
			npm exec prettier -- --plugin=prettier-plugin-astro --check "src/**/*.{astro,js,ts,css,md,json}" "public/**/*.{css,md,json}"); \
	else \
		echo "npm not found; skipping website format checks."; \
	fi

.PHONY: fmt
fmt: ## Auto-format Python and website sources
	@echo "$(CYAN)Formatting Python sources...$(RESET)"
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format --line-length=160 src/ tests/; \
	elif command -v black >/dev/null 2>&1; then \
		black --line-length=160 src/ tests/; \
	else \
		echo "Install ruff or black for Python auto-formatting."; \
	fi
	@echo "$(CYAN)Formatting website sources with Prettier...$(RESET)"
	@if command -v npm >/dev/null 2>&1; then \
		(cd $(WEBSITE_DIR) && { npm ls prettier-plugin-astro >/dev/null 2>&1 || npm install; } && \
			npm exec prettier -- --plugin=prettier-plugin-astro --write "src/**/*.{astro,js,ts,css,md,json}" "public/**/*.{css,md,json}"); \
	else \
		echo "npm not found; skipping website auto-formatting."; \
	fi

.PHONY: nice
nice: deps-check lint fmt-check ## Safe quality pass: check dependency updates + lint + format verification
	@echo "$(GREEN)Nice pass complete.$(RESET)"

.PHONY: very-nice
very-nice: deps-update lint-fix fmt lint fmt-check ## Aggressive quality pass: update deps, auto-fix formatting, then re-verify
	@echo "$(GREEN)Very nice pass complete.$(RESET)"

.PHONY: lint-fix
lint-fix: ## Auto-fix Python formatting and strip trailing whitespace
	@echo "$(CYAN)Auto-fixing formatting and stripping trailing whitespace...$(RESET)"
	@find src tests -name "*.py" -exec sed -i '' -E 's/[[:space:]]+$$//' {} + 2>/dev/null || true
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check --fix --line-length=160 src/ tests/; \
		ruff format --line-length=160 src/ tests/; \
	elif command -v autopep8 >/dev/null 2>&1; then \
		autopep8 --in-place --recursive --aggressive --max-line-length=160 src/ tests/; \
	fi
	@echo "$(GREEN)Auto-fixes applied successfully.$(RESET)"

.PHONY: run-dev
run-dev: check-env init-cache ## Run local autoscaler in foreground for interactive debugging (native, full VM support)
	@echo "$(CYAN)Starting caching proxy registries (Verdaccio, Athens, Docker mirror)...$(RESET)"
	docker compose up -d
	@echo "$(CYAN)Running Autoscaler in interactive foreground mode (native host process)...$(RESET)"
	@set -a; . ./.env; set +a; PYTHONPATH=src python3 -u src/autoscaler.py



