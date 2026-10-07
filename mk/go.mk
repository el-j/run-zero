# Go engine (cmd/, pkg/)

GO_DIRS := pkg cmd

##@ Go engine

.PHONY: build-go
build-go: ## Compile the engine binary into bin/runzero
	go build -o bin/runzero ./cmd/runzero

.PHONY: build-go-multiarch
build-go-multiarch: ## Compile static binaries for darwin/linux x arm64/amd64 into bin/
	@mkdir -p bin
	CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o bin/runzero-darwin-arm64 ./cmd/runzero
	CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build -ldflags="-s -w" -o bin/runzero-darwin-amd64 ./cmd/runzero
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o bin/runzero-linux-amd64 ./cmd/runzero
	CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o bin/runzero-linux-arm64 ./cmd/runzero
	@echo "$(GREEN)Multi-architecture binaries compiled into bin/$(RESET)"

.PHONY: test
test: ## Run Go unit tests
	go test ./...

.PHONY: check-go
check-go: lint-go ## Go gates: go vet + go test with race detector and coverage
	go test -race -cover ./...

.PHONY: lint-go
lint-go: ## Run go vet
	go vet ./...

.PHONY: fmt-go
fmt-go: ## Format Go sources (gofmt -s)
	@gofmt -s -w $(GO_DIRS)

.PHONY: fmt-check-go
fmt-check-go: ## Check Go formatting
	@test -z "$$(gofmt -l $(GO_DIRS))" || (echo "Unformatted Go files:" && gofmt -l $(GO_DIRS) && exit 1)

.PHONY: doctor
doctor: build-go ## Verify cache wiring and engine diagnostics (no GitHub token needed)
	@./bin/runzero doctor

.PHONY: deps-check-go
deps-check-go:
	@echo "$(CYAN)Checking Go module updates...$(RESET)"
	@go list -u -m all 2>/dev/null || true

.PHONY: deps-update-go
deps-update-go:
	@echo "$(CYAN)Updating Go dependencies...$(RESET)"
	@go get -u ./... && go mod tidy
