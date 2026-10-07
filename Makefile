# ==============================================================================
# RunZero - root Makefile
#
# This file only wires things together. Each sub-package owns its own targets:
#
#   mk/common.mk   shared variables, colours, `make help`
#   mk/go.mk       Go engine           (cmd/, pkg/)
#   mk/spec.mk     TypeSpec API schema (spec/)
#   mk/web.mk      Dashboard UI        (web/)
#   mk/website.mk  Astro docs website  (website/ -> docs/)
#   mk/shell.mk    Shell scripts, .env wizard, git hooks
#   mk/cache.mk    Host cache dir + proxy cache volumes (disk usage, cleaning)
#   mk/stack.mk    Docker Compose stack (start/stop/logs/status/images)
#   mk/vm.mk       Host VM bridge + OrbStack VMs
# ==============================================================================

.DEFAULT_GOAL := help

include mk/common.mk
include mk/go.mk
include mk/spec.mk
include mk/web.mk
include mk/website.mk
include mk/shell.mk
include mk/cache.mk
include mk/stack.mk
include mk/vm.mk

##@ Workspace (all packages)

.PHONY: install
install: init-cache spec-install web-install website-install build-spec build-ui build-go install-hooks ## Bootstrap local development environment (deps, build, git hooks)
	@echo "$(GREEN)Install bootstrap complete. Next: run 'make env' (first time), then 'make start'.$(RESET)"

.PHONY: check
check: check-go check-spec check-web check-shell ## Run every quality gate (the same set CI enforces)
	@echo "$(GREEN)All quality gates passed.$(RESET)"

.PHONY: lint
lint: lint-go lint-web website-lint check-shell ## Lint every package (go vet, oxlint x2, shellcheck)

.PHONY: fmt
fmt: fmt-go fmt-web fmt-website ## Auto-format Go, dashboard (oxfmt) and website sources

.PHONY: fmt-check
fmt-check: fmt-check-go fmt-check-website ## Check formatting for Go and website sources

.PHONY: deps-check
deps-check: deps-check-go deps-check-web deps-check-website ## Report outdated dependencies in every package

.PHONY: deps-update
deps-update: deps-update-go deps-update-web deps-update-website ## Apply dependency updates in every package

.PHONY: pre-commit
pre-commit: ## Run the pre-commit quality guard manually
	@bash scripts/pre-commit.sh

.PHONY: pre-push
pre-push: ## Run the pre-push quality guard manually
	@bash scripts/pre-push.sh
