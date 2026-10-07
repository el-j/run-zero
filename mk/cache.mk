# Host package/tool cache dir + proxy cache volumes (Verdaccio, Athens,
# Docker mirror, apt-cacher-ng, devpi, kellnr).
#
# Named docker volumes are found by their Compose *logical* name (the
# com.docker.compose.volume label), not a hardcoded "<project>_<name>" string --
# the project-name prefix Compose derives depends on the checkout directory's
# name, which isn't fixed.
define find_volume
$$(docker volume ls --filter "label=com.docker.compose.volume=$(1)" -q | head -1)
endef

# $(1)=compose service, $(2)=volume logical name, $(3)=display name
define clean_proxy
@docker compose stop $(1) >/dev/null 2>&1 || true
@docker compose rm -f $(1) >/dev/null 2>&1 || true
@vol=$(call find_volume,$(2)); [ -z "$$vol" ] || docker volume rm "$$vol" >/dev/null 2>&1 || true
@echo "$(GREEN)$(3) cache cleared.$(RESET) Run 'make start' to recreate it."
endef

# Remove a cache subdirectory; falls back to a container for root-owned files.
# $(1)=subdir under CACHE_DIR, $(2)=display name
define clean_cache_dir
@chmod -R u+w $(CACHE_DIR)/$(1) 2>/dev/null || true
@rm -rf $(CACHE_DIR)/$(1) 2>/dev/null || docker run --rm -v "$(CACHE_DIR)/$(1):/cache" alpine sh -c "rm -rf /cache/* /cache/.*" 2>/dev/null || true
@rm -rf $(CACHE_DIR)/$(1) 2>/dev/null || true
@echo "$(GREEN)$(2) cache cleared.$(RESET)"
endef

PROXY_VOLUMES := verdaccio-storage athens-storage docker-mirror-storage apt-cacher-storage devpi-storage kellnr-storage

##@ Caches & disk usage

.PHONY: init-cache
init-cache: ## Initialize host cache directories
	@mkdir -p $(addprefix $(CACHE_DIR)/,toolcache npm yarn pnpm pip uv go-mod go-build cargo-registry)

.PHONY: info
info: ## Show disk usage of everything run-zero manages (cache dir, volumes, images, VMs)
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Host Package/Tool Cache ($(CACHE_DIR)) ===$(RESET)"
	@if [ -d "$(CACHE_DIR)" ]; then \
		du -sh $(CACHE_DIR)/* 2>/dev/null | sort -k2 || echo "  (empty)"; \
		echo "  $(BOLD)Subtotal:$(RESET) $$(du -sh $(CACHE_DIR) 2>/dev/null | cut -f1)"; \
	else \
		echo "  (not created yet)"; \
	fi
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Proxy Cache Volumes ===$(RESET)"
	@for v in $(PROXY_VOLUMES); do \
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
	@echo "$(BOLD)$(CYAN)=== OrbStack VMs ===$(RESET)"
	@orbctl list 2>/dev/null | grep -i runzero-vm || echo "  (none)"
	@echo ""
	@echo "$(BOLD)$(CYAN)=== Ephemeral Runner Containers ===$(RESET)"
	@docker ps -a --filter "label=managed-by=local-autoscaler" --format "  {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (none)"
	@echo ""

.PHONY: cache-size
cache-size: ## Show disk usage of the host package/tool cache only
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

.PHONY: cache-smoke
cache-smoke: ## Validate proxy caches are reachable from host and runner-network
	@echo "$(BOLD)$(CYAN)=== Cache Proxy Smoke Test ===$(RESET)"
	@echo "$(CYAN)Checking host-published cache endpoints...$(RESET)"
	@fail=0; \
	for e in "Verdaccio|http://localhost:49501/" "Athens|http://localhost:49500/" \
	         "devpi|http://localhost:49507/root/pypi/+simple/" "apt-cacher|http://localhost:49503/acng-report.html" \
	         "kellnr|http://localhost:49506/api/v1/cratesio/config.json" "Docker mirror|http://localhost:49502/v2/"; do \
		name=$${e%%|*}; url=$${e#*|}; \
		if curl -fsS "$$url" >/dev/null; then echo "  ✓ $$name (host): $$url"; else echo "  ✗ $$name host endpoint unavailable"; fail=1; fi; \
	done; [ $$fail -eq 0 ]
	@echo "$(CYAN)Checking cache endpoints from runner-network DNS...$(RESET)"
	@docker network inspect runner-network >/dev/null 2>&1 || (echo "  ✗ Docker network 'runner-network' not found. Run 'make start' first." && exit 1)
	@fail=0; \
	for e in "Verdaccio|http://verdaccio:4873/" "Athens|http://athens:3000/" \
	         "devpi|http://devpi:3141/root/pypi/+simple/" "apt-cacher|http://apt-cacher:3142/acng-report.html" \
	         "kellnr|http://kellnr:8000/api/v1/cratesio/config.json"; do \
		name=$${e%%|*}; url=$${e#*|}; \
		if docker run --rm --network runner-network curlimages/curl:8.10.1 -fsS "$$url" >/dev/null; then echo "  ✓ $$name (runner-network): $$url"; else echo "  ✗ $$name runner-network endpoint unavailable"; fail=1; fi; \
	done; [ $$fail -eq 0 ]
	@echo "$(CYAN)Inspecting host Docker daemon registry mirrors...$(RESET)"
	@mirrors=$$(docker info --format '{{json .RegistryConfig.Mirrors}}' 2>/dev/null || echo '[]'); \
		echo "  Mirrors: $$mirrors"; \
		echo "$$mirrors" | grep -Eq 'localhost:49502|host\.orb\.internal:49502' && \
			echo "  ✓ Host Docker daemon mirror includes run-zero docker-mirror" || \
			echo "  ⚠ Host Docker daemon mirror does not include run-zero docker-mirror (Docker-backend pulls may bypass cache)"
	@echo "$(GREEN)Cache smoke test complete.$(RESET)"

.PHONY: clean-caches
clean-caches: clean-cache clean-verdaccio clean-athens clean-docker-mirror clean-apt-cacher clean-devpi clean-kellnr ## Clear EVERY cache: host cache dir + all proxy volumes (not images/VMs)
	@echo "$(GREEN)All run-zero caches cleared.$(RESET)"

.PHONY: clean-cache
clean-cache: ## Clear the host package/tool cache dir only (see clean-caches for everything)
	@echo "$(YELLOW)Clearing local runner caches at $(CACHE_DIR)...$(RESET)"
	$(call clean_cache_dir,,Runner)

# Individual host cache subdirectories
.PHONY: clean-npm clean-yarn clean-pnpm clean-pip clean-uv clean-go-mod clean-go-build clean-cargo-registry clean-toolcache
clean-npm: ; @rm -rf $(CACHE_DIR)/npm && echo "$(GREEN)npm cache cleared.$(RESET)"
clean-yarn: ; @rm -rf $(CACHE_DIR)/yarn && echo "$(GREEN)yarn cache cleared.$(RESET)"
clean-pnpm: ; @rm -rf $(CACHE_DIR)/pnpm && echo "$(GREEN)pnpm cache cleared.$(RESET)"
clean-pip: ; @rm -rf $(CACHE_DIR)/pip && echo "$(GREEN)pip cache cleared.$(RESET)"
clean-uv: ; @rm -rf $(CACHE_DIR)/uv && echo "$(GREEN)uv cache cleared.$(RESET)"
clean-go-build: ; @rm -rf $(CACHE_DIR)/go-build && echo "$(GREEN)Go build cache cleared.$(RESET)"
clean-cargo-registry: ; @rm -rf $(CACHE_DIR)/cargo-registry && echo "$(GREEN)Cargo registry cache cleared.$(RESET)"
clean-go-mod: ; $(call clean_cache_dir,go-mod,Go module)
clean-toolcache: ; $(call clean_cache_dir,toolcache,Tool)

# Proxy cache volumes
.PHONY: clean-verdaccio clean-athens clean-docker-mirror clean-apt-cacher clean-devpi clean-kellnr
clean-verdaccio: ; $(call clean_proxy,verdaccio,verdaccio-storage,Verdaccio)
clean-athens: ; $(call clean_proxy,athens,athens-storage,Athens)
clean-docker-mirror: ; $(call clean_proxy,docker-mirror,docker-mirror-storage,Docker mirror)
clean-apt-cacher: ; $(call clean_proxy,apt-cacher,apt-cacher-storage,apt-cacher-ng)
clean-devpi: ; $(call clean_proxy,devpi,devpi-storage,devpi)
clean-kellnr: ; $(call clean_proxy,kellnr,kellnr-storage,kellnr)
