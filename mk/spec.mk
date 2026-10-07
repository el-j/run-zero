# TypeSpec API schema (spec/) -> generates web/src/types/api.ts

##@ TypeSpec API schema

.PHONY: spec-install
spec-install: ## Install spec/ dependencies (pnpm)
	@cd spec && pnpm install

.PHONY: build-spec
build-spec: ## Compile the TypeSpec schema and generate TypeScript types
	@echo "$(CYAN)Compiling TypeSpec schema and generating TypeScript types...$(RESET)"
	@cd spec && pnpm run all
	@echo "$(GREEN)TypeSpec compilation complete.$(RESET)"

.PHONY: check-spec
check-spec: ## TypeSpec gate: compile API spec and regenerate TypeScript types
	@cd spec && pnpm run all
