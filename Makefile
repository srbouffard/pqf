# PQF — Product Quality Framework
# Usage: make <target>
# All Python targets assume the venv/dev deps are installed: make install
# All UI targets run inside ui/

.DEFAULT_GOAL := help
.PHONY: help install install-ui install-all \
	lint format format-check \
	test test-ui test-all \
	build dev \
	audit audit-python audit-ui \
	score score-docs \
	e2e _require-github-token _require-openrouter-key

PYTHON := python3
PIP    := pip
NPM    := npm
SCORE_DIR := .pqf-score

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  PQF — Product Quality Framework"
	@echo ""
	@echo "  Setup"
	@echo "    make install        Install Python dev dependencies"
	@echo "    make install-ui     Install Node/UI dependencies"
	@echo "    make install-all    Install everything"
	@echo ""
	@echo "  Python"
	@echo "    make lint           Lint Python with ruff"
	@echo "    make format         Auto-format Python with ruff"
	@echo "    make format-check   Check Python formatting without modifying"
	@echo "    make test           Run Python unit tests"
	@echo ""
	@echo "  UI (React/TypeScript)"
	@echo "    make test-ui        Run Vitest unit tests"
	@echo "    make build          Build the React app (ui/dist/)"
	@echo "    make dev            Start Vite dev server"
	@echo "    make e2e            Run Playwright end-to-end tests"
	@echo ""
	@echo "  Combined"
	@echo "    make test-all       Run both Python and UI tests"
	@echo ""
	@echo "  Security"
	@echo "    make audit          Run pip-audit + npm audit"
	@echo "    make audit-python   Run pip-audit only"
	@echo "    make audit-ui       Run npm audit only"
	@echo ""
	@echo "  Scoring (requires GITHUB_TOKEN + OPENROUTER_API_KEY)"
	@echo "    make score PRODUCT=<id>   Score a single product (all dimensions)"
	@echo "    make score-docs PRODUCT=<id>   Run only the documentation scorer"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
install:
	$(PIP) install -e ".[dev]"

install-ui:
	cd ui && $(NPM) install

install-all: install install-ui

# ── Python: lint & format ────────────────────────────────────────────────────
lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

# ── Python: tests ─────────────────────────────────────────────────────────────
test:
	pytest --tb=short

# ── UI: tests, build, dev ─────────────────────────────────────────────────────
test-ui:
	cd ui && $(NPM) test

build:
	cd ui && $(NPM) run build

dev:
	cd ui && $(NPM) run dev

e2e:
	cd ui && $(NPM) run e2e

# ── Combined ──────────────────────────────────────────────────────────────────
test-all: test test-ui

# ── Security audits ───────────────────────────────────────────────────────────
audit-python:
	pip-audit

audit-ui:
	cd ui && $(NPM) audit --audit-level=high

audit: audit-python audit-ui

# ── Scoring ───────────────────────────────────────────────────────────────────
# Usage: make score PRODUCT=matrix
PRODUCT ?= $(error PRODUCT is required. Usage: make score PRODUCT=matrix)

score: _require-github-token _require-openrouter-key
	@echo "Scoring product: $(PRODUCT)"
	@mkdir -p $(SCORE_DIR)/$(PRODUCT)
	$(PYTHON) scorers/test_verification/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/test_verification.json
	$(PYTHON) scorers/documentation/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/documentation.json
	$(PYTHON) scorers/substrate_compat/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/substrate_compat.json
	$(PYTHON) scorers/security_ssdlc/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/security_ssdlc.json
	$(PYTHON) scorers/support_engagement/scorer.py --product-yaml products/$(PRODUCT).yaml \
		> $(SCORE_DIR)/$(PRODUCT)/support_engagement.json
	@echo ""
	@echo "Results in $(SCORE_DIR)/$(PRODUCT)/"
	@for f in $(SCORE_DIR)/$(PRODUCT)/*.json; do echo "  $$f:"; cat $$f | $(PYTHON) -m json.tool --indent 2; echo ""; done

score-docs: _require-github-token _require-openrouter-key
	$(PYTHON) scorers/documentation/scorer.py --product-yaml products/$(PRODUCT).yaml

_require-github-token:
	@test -n "$(GITHUB_TOKEN)" || (echo "Error: GITHUB_TOKEN is not set" && exit 1)

_require-openrouter-key:
	@test -n "$(OPENROUTER_API_KEY)" || (echo "Error: OPENROUTER_API_KEY is not set" && exit 1)
