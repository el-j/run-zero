# Docker Compose stack: autoscaler, dashboard, proxy registries, runner images

##@ Docker stack

.PHONY: build
build: ## Build the autoscaler and runner container images (arm64 + amd64)
	@docker compose --profile static build

.PHONY: start
start: check-env init-cache bridge-start ## Start autoscaler + host VM bridge + proxies + dashboard (containerized)
	@echo "$(CYAN)Starting RunZero containerized stack (Autoscaler, Dashboard, Proxy registries)...$(RESET)"
	@docker compose up -d --build
	@echo "$(GREEN)RunZero Fleet & Observability Stack is running!$(RESET)"
	@echo "  • 📊 Web Dashboard:  $(BOLD)http://localhost:49505$(RESET) (Run $(BOLD)make dashboard$(RESET))"
	@echo "  • 🌉 Host VM Bridge: $(BOLD)http://localhost:49504$(RESET)"
	@echo "  • 📦 Verdaccio UI:   $(BOLD)http://localhost:49501$(RESET)"
	@echo "  • 🐧 APT Cacher:     $(BOLD)http://localhost:49503/acng-report.html$(RESET)"
	@echo "  • 🐹 Athens Go:      $(BOLD)http://localhost:49500$(RESET)"
	@echo "  • 🐳 Docker Mirror:  $(BOLD)http://localhost:49502$(RESET)"
	@echo "  • 🐍 devpi (pip/uv): $(BOLD)http://localhost:49507/root/pypi/+simple/$(RESET)"
	@echo "  • 🦀 kellnr (Cargo): $(BOLD)http://localhost:49506$(RESET)"
	@echo "Use $(BOLD)make logs$(RESET) to stream logs or $(BOLD)make status$(RESET) to see active runners."

.PHONY: up
up: start

.PHONY: start-host
start-host: check-env init-cache build-go build-ui bridge-start ## Start the autoscaler natively on the host (proxies stay in Docker)
	@echo "$(CYAN)Starting caching proxy registries...$(RESET)"
	@docker compose up -d verdaccio athens docker-mirror apt-cacher devpi kellnr
	@if [ -f $(AUTOSCALER_PID_FILE) ] && kill -0 "$$(cat $(AUTOSCALER_PID_FILE))" 2>/dev/null; then \
		echo "$(YELLOW)Autoscaler already running on host (PID $$(cat $(AUTOSCALER_PID_FILE))).$(RESET)"; \
	else \
		echo "$(CYAN)Starting RunZero Go Engine with Web Dashboard on host...$(RESET)"; \
		nohup ./bin/runzero -dist=web/dist > $(AUTOSCALER_LOG_FILE) 2>&1 & \
		echo $$! > $(AUTOSCALER_PID_FILE); \
	fi
	@echo "$(GREEN)Host Autoscaler & Stack is running!$(RESET)"

.PHONY: run-dev
run-dev: check-env init-cache build-go build-ui ## Run the engine in the foreground for interactive debugging
	@echo "$(CYAN)Starting caching proxy registries...$(RESET)"
	docker compose up -d verdaccio athens docker-mirror apt-cacher devpi kellnr
	@echo "$(CYAN)Running Go engine in interactive foreground mode...$(RESET)"
	@./bin/runzero -dist=web/dist

.PHONY: stop
stop: bridge-stop ## Stop autoscaler, host VM bridge, proxies and runner containers
	@echo "$(YELLOW)Stopping Autoscaler and unregistering active runners...$(RESET)"
	@if [ -f $(AUTOSCALER_PID_FILE) ]; then \
		pid=$$(cat $(AUTOSCALER_PID_FILE)); \
		if kill -0 "$$pid" 2>/dev/null; then kill "$$pid"; fi; \
		rm -f $(AUTOSCALER_PID_FILE); \
	fi
	docker compose down
	@echo "$(GREEN)Autoscaler, VM bridge, and proxies stopped.$(RESET)"

.PHONY: down
down: stop

.PHONY: restart
restart: stop start ## Restart autoscaler and proxies

.PHONY: logs
logs: ## Stream live logs from the autoscaler
	@docker compose logs -f autoscaler 2>/dev/null || (touch $(AUTOSCALER_LOG_FILE) && tail -f $(AUTOSCALER_LOG_FILE))

.PHONY: logs-all
logs-all: ## Stream live logs from all compose services
	@docker compose logs -f

.PHONY: status
status: bridge-status ## Show autoscaler, bridge, proxies and active runners (containers + VMs)
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

.PHONY: ps
ps: status

.PHONY: clean
clean: ## Remove compose containers/volumes and leftover runner containers
	@echo "$(YELLOW)Cleaning up stopped runner containers and volumes...$(RESET)"
	docker compose down -v
	@docker rm -f $$(docker ps -a -q --filter "label=managed-by=local-autoscaler") 2>/dev/null || true
	@echo "$(GREEN)Cleaned up successfully.$(RESET)"

.PHONY: clean-images
clean-images: ## Remove built runner/autoscaler images (forces a full rebuild)
	@docker rmi -f local-github-runner:arm64 local-github-runner:amd64 local-github-runner:latest local-runner-autoscaler:latest 2>/dev/null || true
	@echo "$(GREEN)Runner images removed.$(RESET) Run 'make build' to rebuild."

.PHONY: clean-all
clean-all: stop clean vm-clean-all clean-caches clean-images ## Nuclear reset: stop everything, wipe caches, VMs and images
	@echo "$(GREEN)RunZero completely reset to fresh out-of-the-box state.$(RESET)"
