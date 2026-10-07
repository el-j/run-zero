# Astro documentation website (website/) -> published into docs/

WEBSITE_DIR := website
PRETTIER_GLOBS := "src/**/*.{astro,js,ts,css,md,json}" "public/**/*.{css,md,json}"
# Reinstall (from the lockfile) when the linked binaries are missing.
WEBSITE_ENSURE_DEPS := { [ -x node_modules/.bin/oxlint ] && [ -x node_modules/.bin/prettier ] || npm ci; }

##@ Website & docs

.PHONY: website-install
website-install: ## Install website dependencies (npm)
	@if [ -n "$(HAVE_NPM)" ]; then \
		echo "$(CYAN)Installing website Node dependencies...$(RESET)"; \
		cd $(WEBSITE_DIR) && npm ci; \
	else \
		echo "$(YELLOW)npm not found; skipping website dependency install.$(RESET)"; \
	fi

.PHONY: website-dev
website-dev: ## Run the Astro website in dev mode
	@cd $(WEBSITE_DIR) && npm run dev

.PHONY: website-build
website-build: ## Build the Astro website and sync it into docs/
	@echo "$(CYAN)Building Astro static documentation website...$(RESET)"
	@cd $(WEBSITE_DIR) && npm run build && rm -rf ../docs/* && cp -r dist/* ../docs/ && touch ../docs/.nojekyll
	@echo "$(GREEN)Astro website built and synced to docs/ successfully!$(RESET)"

.PHONY: website-lint
website-lint: ## Run Oxlint on website sources
	@if [ -n "$(HAVE_NPM)" ]; then \
		cd $(WEBSITE_DIR) && $(WEBSITE_ENSURE_DEPS) && npm run lint; \
	else \
		echo "$(YELLOW)npm not found; skipping website lint.$(RESET)"; \
	fi

.PHONY: e2e
e2e: ## Run Playwright end-to-end tests for the website
	@cd $(WEBSITE_DIR) && npx playwright test

.PHONY: docs
docs: ## Open the built documentation (docs/index.html) in the browser
	@open docs/index.html || echo "Open docs/index.html in your browser."

.PHONY: fmt-website
fmt-website:
	@if [ -n "$(HAVE_NPM)" ]; then \
		cd $(WEBSITE_DIR) && $(WEBSITE_ENSURE_DEPS) && npm exec prettier -- --write $(PRETTIER_GLOBS); \
	fi

.PHONY: fmt-check-website
fmt-check-website:
	@if [ -n "$(HAVE_NPM)" ]; then \
		cd $(WEBSITE_DIR) && $(WEBSITE_ENSURE_DEPS) && npm exec prettier -- --check $(PRETTIER_GLOBS); \
	fi

.PHONY: deps-check-website
deps-check-website:
	@echo "$(CYAN)Checking website Node package updates (npm outdated)...$(RESET)"
	@if [ -n "$(HAVE_NPM)" ]; then (cd $(WEBSITE_DIR) && npm outdated || true); fi

.PHONY: deps-update-website
deps-update-website:
	@echo "$(CYAN)Updating website Node dependencies...$(RESET)"
	@if [ -n "$(HAVE_NPM)" ]; then (cd $(WEBSITE_DIR) && npx -y npm-check-updates -u && npm install); fi
