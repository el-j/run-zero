# Host VM bridge (scripts/bridge_supervisor.sh) and OrbStack VMs

##@ Host VM bridge & OrbStack VMs

.PHONY: bridge-start
bridge-start: build-go ## Start the host VM bridge on port 49504 (auto-restarts via launchd)
	@echo "$(CYAN)Starting Host VM Bridge on http://localhost:49504...$(RESET)"
	@./scripts/bridge_supervisor.sh start

.PHONY: bridge-stop
bridge-stop: ## Stop the host VM bridge
	@echo "$(YELLOW)Stopping Host VM Bridge...$(RESET)"
	@./scripts/bridge_supervisor.sh stop
	@echo "$(GREEN)Host VM Bridge stopped.$(RESET)"

.PHONY: bridge-status
bridge-status: ## Check host VM bridge status
	@echo "$(BOLD)$(CYAN)=== Host VM Bridge (port 49504) ===$(RESET)"
	@./scripts/bridge_supervisor.sh status

.PHONY: bridge-logs
bridge-logs: ## Stream live logs from the host VM bridge
	@touch $(BRIDGE_LOG_FILE) && tail -f $(BRIDGE_LOG_FILE)

.PHONY: build-vm-base
build-vm-base: build-go ## Build the golden OrbStack VM base image (slow; rerun after editing docker/provision-toolchain.sh)
	@echo "$(CYAN)Building golden OrbStack VM base image(s)...$(RESET)"
	@./bin/runzero build-vm-base
	@echo "$(GREEN)Golden VM base image(s) ready. Ephemeral VM-routed jobs will now clone instantly.$(RESET)"

.PHONY: vm-list
vm-list: ## List OrbStack Linux VMs
	@orbctl list || true

.PHONY: vm-clean
vm-clean: ## Delete orphaned ephemeral RunZero VMs (keeps golden base images)
	@for vm in $$(orbctl list -q 2>/dev/null | grep '^runzero-vm-' | grep -v '^runzero-vm-base-'); do \
		echo "Deleting $$vm..."; \
		orbctl delete -f $$vm || true; \
	done
	@echo "$(GREEN)VM cleanup complete.$(RESET)"

.PHONY: vm-clean-all
vm-clean-all: ## Delete ALL RunZero VMs including golden base images
	@for vm in $$(orbctl list -q 2>/dev/null | grep '^runzero-vm-'); do \
		echo "Deleting $$vm..."; \
		orbctl delete -f $$vm || true; \
	done
	@echo "$(GREEN)All RunZero VMs deleted.$(RESET)"
