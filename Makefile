# ==============================================================================
# Local GitHub Actions Runner & Autoscaler - Makefile (OrbStack / Docker)
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
	@echo "$(BOLD)$(CYAN)Local GitHub Actions Runner & Autoscaler$(RESET)"
	@echo "$(YELLOW)Fast, containerized CI execution powered by OrbStack & Docker$(RESET)"
	@echo ""
	@echo "$(BOLD)Usage:$(RESET) make $(GREEN)<target>$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
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

.PHONY: build
build: ## Build both Runner and Autoscaler Docker images
	@echo "$(CYAN)Building Runner and Autoscaler images...$(RESET)"
	docker compose build
	@echo "$(GREEN)Images built successfully!$(RESET)"

.PHONY: start up
start: check-env ## Start the Runner Autoscaler in background
	@echo "$(CYAN)Starting Local GitHub Runner Autoscaler (OrbStack)...$(RESET)"
	docker compose up -d --build
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
	docker compose up --build
