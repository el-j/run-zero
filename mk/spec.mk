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

SPEC_GENERATED := web/src/types/api.ts

.PHONY: check-spec
check-spec: ## TypeSpec gate: compile API spec, regenerate TypeScript types, fail if the committed types were stale
	@cd spec && pnpm run all
	@git diff --quiet -- $(SPEC_GENERATED) || (echo "Generated API types were stale and have been regenerated; commit:"; git diff --stat -- $(SPEC_GENERATED); exit 1)
