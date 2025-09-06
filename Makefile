SHELL := /bin/bash
REPO := bugbounty-ops
BUNDLE_DIR := dist_bundle

.PHONY: help setup build-ui api workers dev stop clean bundle

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: ## Install UI deps (optional)
	@if [ -d ui ]; then cd ui && npm ci || true; fi

build-ui: ## Build MUI+D3 app (skip if ui/dist already present)
	@if [ -d ui ]; then cd ui && npm run build || true; fi

api: ## Run API only
	docker compose -f ops/docker-compose.yml up --build api

workers: ## Run workers only
	docker compose -f ops/docker-compose.yml up --build workers

dev: ## Full stack (API, workers, UI, Postgres, Redis, MinIO)
	docker compose -f ops/docker-compose.yml up --build

stop: ## Stop stack
	docker compose -f ops/docker-compose.yml down

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
