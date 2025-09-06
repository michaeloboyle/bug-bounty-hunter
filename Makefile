SHELL := /bin/bash
REPO := bugbounty-ops
BUNDLE_DIR := dist_bundle

.PHONY: help setup build-ui api workers dev stop clean bundle

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies
	@echo "Installing Python dependencies..."
	@pip install -r requirements.txt || echo "⚠️  Python deps failed - install manually"
	@if [ -d ui ]; then echo "Installing UI dependencies..." && cd ui && npm ci || echo "⚠️  UI deps failed"; fi

build-ui: ## Build React UI with Material-UI
	@if [ -d ui ]; then cd ui && npm run build || echo "⚠️  UI build failed"; else echo "⚠️  UI directory not found"; fi

mcp-test: ## Test MCP server connection
	@echo "Testing MCP server..."
	@python engine/mcp_server.py --test || echo "⚠️  MCP server test failed"

api: ## Run API only
	docker compose up --build api

workers: ## Run workers only
	docker compose up --build workers

mcp: ## Run MCP server only
	docker compose up --build mcp

dev: ## Full stack (API, workers, UI, Postgres, Redis, MinIO)
	docker compose up --build

stop: ## Stop stack
	docker compose down

test: ## Run test suite with coverage
	docker compose --profile testing up --build test

test-watch: ## Run tests in watch mode
	docker compose --profile testing run --rm test pytest -f

test-unit: ## Run only unit tests
	docker compose --profile testing run --rm test pytest tests/ -m "unit or not integration"

test-integration: ## Run only integration tests  
	docker compose --profile testing run --rm test pytest tests/ -m integration

test-coverage: ## Generate coverage report
	docker compose --profile testing run --rm test pytest --cov-report=html:test-results/coverage

test-local: ## Run tests locally (requires deps)
	pytest -v --cov=engine --cov-report=term-missing

clean: stop ## Clean artifacts
	rm -rf $(BUNDLE_DIR) $(REPO)_bundle.zip || true

bundle: build-ui ## Create Claude Flow hand-off ZIP
	@mkdir -p $(BUNDLE_DIR)
	@test -d flow || (echo "Missing ./flow"; exit 1)
	@cp -R flow $(BUNDLE_DIR)/
	@test -d profiles || (echo "Missing ./profiles"; exit 1)
	@cp -R profiles $(BUNDLE_DIR)/
	@if [ -d ui/dist ]; then mkdir -p $(BUNDLE_DIR)/ui && cp -R ui/dist $(BUNDLE_DIR)/ui/; fi
	@cd $(BUNDLE_DIR) && zip -rq ../$(REPO)_bundle.zip .
	@echo "Created $(REPO)_bundle.zip"
