# Dashboard UI (web/) - Vite + TypeScript

##@ Dashboard UI

.PHONY: web-install
web-install: ## Install web/ dependencies (pnpm)
	@cd web && pnpm install

.PHONY: build-ui
build-ui: build-spec ## Build the production dashboard (regenerates API types first)
	@echo "$(CYAN)Building modular TypeScript dashboard...$(RESET)"
	@cd web && pnpm run build
	@echo "$(GREEN)Dashboard UI build complete.$(RESET)"

.PHONY: dev-ui
dev-ui: ## Run the Vite dev server for the dashboard
	@cd web && pnpm run dev

.PHONY: lint-web
lint-web: ## Lint the dashboard with Oxlint
	@cd web && pnpm run lint

.PHONY: fmt-web
fmt-web: ## Format the dashboard sources with oxfmt
	@cd web && pnpm run fmt

.PHONY: check-web
check-web: lint-web ## Web gate: Oxlint, typecheck and build the production dashboard
	@cd web && pnpm run build

.PHONY: dashboard
dashboard: ## Open the observability dashboard in the browser (http://localhost:49505)
	@echo "$(CYAN)Opening RunZero Observability Dashboard at http://localhost:49505...$(RESET)"
	@open http://localhost:49505 || echo "Navigate to http://localhost:49505 in your browser."

.PHONY: deps-check-web
deps-check-web:
	@echo "$(CYAN)Checking web dashboard dependencies (pnpm outdated)...$(RESET)"
	@(cd web && pnpm outdated || true)

.PHONY: deps-update-web
deps-update-web:
	@echo "$(CYAN)Updating web dashboard dependencies...$(RESET)"
	@(cd web && pnpm update)
