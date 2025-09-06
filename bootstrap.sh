# === Bug Bounty Ops: one-shot bootstrap (repo root) ===
set -euo pipefail

mkdir -p flow/prompts flow/policies profiles ui engine/api engine/scanner-farm engine/safe-poc engine/policy engine/dupdb ops/stubs

# ---------- Claude Flow spec ----------
cat > flow/claude_flow.yaml <<'YAML'
version: 1
flows:
  - id: bugbounty-orchestrator
    description: End-to-end automated bounty pipeline with human gate
    entry:
      agent: coordination
      input_schema:
        type: object
        properties:
          program_id: { type: string }
          priority: { type: string, enum: [high_ceiling, fast_pay, mobile, web3] }
    agents:
      - id: coordination
        tools: [queue, scope_policy, rate_governor, dup_db, platform_api]
        next: recon
      - id: recon
        tools: [amass, tech_fingerprint, passive_dns]
        next: analysis
      - id: analysis
        tools: [nuclei_planner, burp_planner, custom_checks]
        next: scanner_farm
      - id: scanner_farm
        tools: [nuclei_run, burp_dast, custom_runners]
        next: exploitation
      - id: exploitation
        tools: [safe_poc, sandbox, evidence_capture]
        next: reporting
      - id: reporting
        tools: [cvss_v4, report_template, submission_adapter]
        human_gate: true
        next: submit
      - id: submit
        tools: [hackerone_api, bugcrowd_api, intigriti_api]
YAML

# ---------- Prompts (stubs) ----------
cat > flow/prompts/coordination.md <<'MD'
You are the Coordination Agent. Objectives:
- Enforce scope and rate policy before any scan.
- Decompose target into assets; create a scan_plan.
- Route work to Recon → Analysis → Scanner → Exploitation → Reporting.
Gate: stop if scope_policy returns ambiguous or disallowed.
MD

cat > flow/prompts/reporting.md <<'MD'
You are the Reporting Agent. Produce a submission-ready report:
- Summary, Impact, Affected assets, Repro steps, Minimal PoC, CVSS v4.
- Include evidence URIs, timestamps, request/response excerpts (sanitized).
- Output JSON: {title, body_md, cvss_v4, attachments[]}
MD

# ---------- Policies ----------
cat > flow/policies/scope-validator.json <<'JSON'
{"rules":[{"name":"automation_ok_if_rps","when":{"program.auto_ok":true},"limits":{"rps":"program.rps"}},{"name":"ban_destructive","deny":["DELETE","/admin","/prod-data"]}]}
JSON

# ---------- Profiles ----------
cat > profiles/nuclei-profile.yaml <<'YAML'
rate-limit: 1
concurrency: 5
retries: 1
bulk-size: 25
header:
  User-Agent: BugBountyOps/1.0
YAML

cat > profiles/burp-settings.json <<'JSON'
{"scanSpeed":"fast","maxConcurrentRequests":5,"inscopeOnly":true,"issueDefinitions":["xss","ssrf","idor","csrf","jwt"]}
JSON

# ---------- API stub ----------
cat > engine/api/main.py <<'PY'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BugBountyOps API")

PROGRAMS = [
    {"id":"h1-google","name":"Google VRP","platform":"H1","payoutMax":1000000,"rps":0.5,"autoOK":True,"triageDays":14,"assetCount":2800,"tags":["web","mobile","cloud"]},
    {"id":"apple-vrp","name":"Apple Security Bounty","platform":"Direct","payoutMax":1000000,"rps":0.2,"autoOK":False,"triageDays":30,"assetCount":120,"tags":["mobile","kernel"]},
    {"id":"msrc","name":"Microsoft (MSRC)","platform":"Direct","payoutMax":40000,"rps":0.5,"autoOK":True,"triageDays":10,"assetCount":900,"tags":["cloud","desktop","ai"]},
    {"id":"github","name":"GitHub","platform":"H1","payoutMax":30000,"rps":1.0,"autoOK":True,"triageDays":7,"assetCount":700,"tags":["dev","api","actions"]},
]
FINDINGS = [
    {"id":"f1","programId":"github","type":"IDOR","severity":7.5,"status":"ready_to_submit","payoutEst":8000},
    {"id":"f2","programId":"h1-google","type":"SSRF","severity":8.8,"status":"needs_human","payoutEst":25000},
    {"id":"f3","programId":"msrc","type":"AuthZ bypass","severity":9.1,"status":"queued","payoutEst":15000},
]

@app.get("/programs")
def programs(): return PROGRAMS

@app.post("/queue")
def queue(program_id: str, priority: str = "fast_pay"):
    return {"queued": True, "program_id": program_id, "priority": priority}

@app.get("/findings")
def findings(status: str | None = None):
    return [f for f in FINDINGS if not status or f["status"]==status]
PY

# ---------- Workers / stubs ----------
cat > ops/stubs/worker_stub.py <<'PY'
import time
print("Workers online. Wire real scanners at engine/scanner-farm/*")
while True: time.sleep(5)
PY

# ---------- docker-compose ----------
cat > ops/docker-compose.yml <<'YML'
version: "3.9"
services:
  api:
    image: python:3.11-slim
    container_name: bbops-api
    working_dir: /app
    command: bash -lc "pip install uvicorn fastapi && uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload"
    volumes:
      - ../engine/api:/app/api:ro
      - ../profiles:/app/profiles:ro
      - ../ui/dist:/app/static:ro
    environment:
      - PORT=8080
      - DB_URL=${DB_URL}
      - REDIS_URL=redis://redis:6379/0
      - ARTIFACT_S3=${ARTIFACT_S3}
      - DEFAULT_RPS=${DEFAULT_RPS:-0.5}
    ports: ["8080:8080"]
    depends_on: [db, redis, minio]

  workers:
    image: python:3.11-slim
    container_name: bbops-workers
    working_dir: /app
    command: bash -lc "pip install requests && python -u worker_stub.py"
    volumes:
      - ../engine/scanner-farm:/app/scanner-farm:ro
      - ../engine/safe-poc:/app/safe-poc:ro
      - ../engine/policy:/app/policy:ro
      - ../engine/dupdb:/app/dupdb:ro
      - ../profiles:/app/profiles:ro
      - ./stubs/worker_stub.py:/app/worker_stub.py:ro
    environment:
      - REDIS_URL=redis://redis:6379/0
      - ARTIFACT_S3=${ARTIFACT_S3}
      - DEFAULT_RPS=${DEFAULT_RPS:-0.5}
    depends_on: [redis, minio]

  ui:
    image: nginx:1.27-alpine
    container_name: bbops-ui
    ports: ["4173:80"]
    volumes:
      - ../ui/dist:/usr/share/nginx/html:ro
    depends_on: [api]

  db:
    image: postgres:16-alpine
    container_name: bbops-db
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=bbops
    ports: ["5432:5432"]
    volumes: [dbdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    container_name: bbops-redis
    ports: ["6379:6379"]

  minio:
    image: quay.io/minio/minio:RELEASE.2025-02-28T09-55-16Z
    container_name: bbops-minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minio
      - MINIO_ROOT_PASSWORD=minio123
    ports: ["9000:9000", "9001:9001"]
    volumes: [miniodata:/data]
volumes: { dbdata: {}, miniodata: {} }
YML

# ---------- Makefile ----------
cat > Makefile <<'MAKE'
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
MAKE

# ---------- env example ----------
cat > .env.example <<'ENV'
H1_TOKEN=
BUGCROWD_TOKEN=
INTIGRITI_TOKEN=
DB_URL=postgresql://postgres:postgres@db:5432/bbops
ARTIFACT_S3=http://minio:9000/bbops
DEFAULT_RPS=0.5
ENV

# Done
echo "Bootstrap complete.
Next:
  1) cp .env.example .env
  2) make dev        # http://localhost:4173 UI, http://localhost:8080 API
  3) make bundle     # creates bugbounty-ops_bundle.zip for Claude Flow upload
"