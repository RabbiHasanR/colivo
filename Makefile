# Colivo root Makefile: one entry point for every part (specs/testing.md → Commands).
# A part's targets print "skip" until that part is scaffolded.

.DEFAULT_GOAL := help

# Runs $(1) inside a part's folder, or skips when the part has no project file yet.
backend = $(if $(wildcard backend/pyproject.toml),cd backend && $(1),@echo "skip $@: backend/ is not scaffolded yet")
web = $(if $(wildcard web/package.json),cd web && $(1),@echo "skip $@: web/ is not scaffolded yet")

.PHONY: help test-fast test lint format-check api-export api-types \
	backend-test-fast backend-test backend-lint backend-format-check backend-migrations-check \
	web-test-fast web-e2e web-test web-lint web-format-check

help: ## List the targets
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-26s %s\n", $$1, $$2}'

# ── Every part ──────────────────────────────────────────────────────────

test-fast: backend-test-fast web-test-fast ## Fast tests, no end-to-end

test: backend-test web-test ## Every suite, end-to-end included (needs docker compose up)

lint: backend-lint web-lint ## Ruff + pyright; ESLint, template lint, Glint

format-check: backend-format-check web-format-check ## Ruff format; Prettier

# ── API contract ────────────────────────────────────────────────────────

api-export: ## Write api/openapi.json from the FastAPI app
	$(call backend,uv run python -m app.scripts.export_openapi)

api-types: ## Regenerate web/app/data/types/api.generated.ts from api/openapi.json
	$(call web,pnpm exec openapi-typescript ../api/openapi.json -o app/data/types/api.generated.ts)

# ── Backend ─────────────────────────────────────────────────────────────

backend-test-fast: ## Backend unit + integration tests (not slow)
	$(call backend,uv run pytest -m "not slow")

backend-test: ## Every backend test, slow included
	$(call backend,uv run pytest)

backend-lint: ## Ruff check + pyright
	$(call backend,uv run ruff check . && uv run pyright)

backend-format-check: ## Ruff format check
	$(call backend,uv run ruff format --check .)

backend-migrations-check: ## alembic check: no model change without a migration (needs the database)
	$(call backend,uv run alembic check)

# ── Web ─────────────────────────────────────────────────────────────────

web-test-fast: ## Web unit, integration and acceptance tests (mocked network)
	$(call web,pnpm test)

web-e2e: ## Playwright against the real backend (needs docker compose up)
	$(call web,pnpm exec playwright test)

web-test: web-test-fast web-e2e ## Every web test

web-lint: ## ESLint, ember-template-lint, Glint
	$(call web,pnpm lint)

web-format-check: ## Prettier check
	$(call web,pnpm exec prettier --check .)
