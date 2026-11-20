# Phase 0 — Project Skeleton: Plan

Branch: `phase-0-project-skeleton`.

Each group is built with `/tdd` as in
[testing.md → Build time](../testing.md#build-time-tdd-one-planmd-group-per-run):
Gate 2 on `tests.md`, then backend → contract → web, one test at a time.
Groups 1, 2, 3 and 5 are scaffolding (no **Behaviours:** line): no tests, one
commit each, then stop for review. Group 4 is the phase's one slice.

Per-behaviour gate: `make test-fast`, `make lint` and `make format-check`
green, then a conventional commit with no Co-Authored-By or AI attribution
lines. The gate starts once group 1 has created the `Makefile`; until a part
exists, its targets are skipped, and each part is checked with its own tools.

## 1. Groundwork

Scaffolding. Commit: `chore: add monorepo groundwork`.

- Fetch current docs with `ctx7` for Docker Compose (healthchecks,
  `depends_on` conditions) and the PostgreSQL 16 image's init scripts.
- Create `backend/`, `web/`, `api/`, `infra/`, `docs/`.
- `compose.yaml` at the root: `postgres:16` and `redis:7` with healthchecks
  and named volumes. The backend service joins in group 2.
- `infra/postgres/init/01-create-test-db.sql`: creates `colivo_test`.
- `.env.example`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`,
  `DATABASE_URL`, `TEST_DATABASE_URL`, `REDIS_URL`, `BACKEND_CORS_ORIGINS`,
  `ENVIRONMENT`, `VITE_API_HOST`; placeholder values only.
- Root `Makefile` with `help` and the targets from
  [testing.md → Commands](../testing.md#commands): `test-fast`, `test`,
  `lint`, `format-check`, `api-export`, `api-types`, and the per-part
  `backend-*` and `web-*` targets they call. A part's targets skip it with a
  message until its folder has its project file.
- `.gitignore`: `.env`, `.venv/`, `node_modules/`, `dist/`, test reports,
  Playwright output, database volumes.

## 2. Backend scaffold

Scaffolding. Commit: `chore(backend): scaffold FastAPI app`.

- Fetch current docs with `ctx7`: FastAPI (app setup, lifespan, exception
  handlers, CORS), pydantic-settings, SQLModel and SQLAlchemy 2.0 (engine,
  session, joining a test session to an outer transaction), Alembic
  (`env.py` with settings), pytest.
- `backend/pyproject.toml` and `backend/uv.lock`, Python 3.14. Dependencies:
  `fastapi`, `uvicorn[standard]`, `sqlmodel`, `alembic`, `psycopg[binary]`,
  `pydantic-settings`, `redis`. Dev: `pytest`, `pytest-cov`,
  `pytest-watcher`, `httpx`, `ruff`, `pyright`. Ruff, pyright and pytest
  settings (markers `slow`, test paths) live in `pyproject.toml`.
- `fastapi-orm-scaffold` layout:
  - `backend/app/main.py`: app, exception handlers, `api_router` at
    `/api/v1`.
  - `backend/app/core/config.py` (`settings`), `database.py` (engine,
    `get_session`), `router.py` (`CoreRouter`), `schemas.py`
    (`StandardResponse`), `exceptions.py`, `utils.py`
    (`set_response_message`).
  - `backend/app/api/api_v1.py`: empty `api_router`.
  - `backend/app/scripts/export_openapi.py`: writes `api/openapi.json`
    (`make api-export`).
- `backend/alembic.ini`, `backend/alembic/env.py` (URL from `settings`,
  `SQLModel.metadata`), `backend/alembic/versions/` empty.
- `backend/tests/conftest.py`: builds the test database with
  `alembic upgrade head` once per session; a `session` fixture in a
  transaction rolled back after each test; a `client` fixture
  (`TestClient` with `get_session` overridden).
- `infra/backend.Dockerfile` (uv, dev server with reload) and the `backend`
  service in `compose.yaml`, depending on healthy `postgres` and `redis`.
- Check: `uv run pytest` runs with no tests and no errors, `make lint`,
  `make format-check`, `uv run alembic check`, `docker compose up` serves
  `/docs`.

## 3. Web scaffold

Scaffolding. Commit: `chore(web): scaffold Ember app`.

Follow the `ember-scaffold` skill, sections 1, 2 and 4, except the starter
files that have tests: they are built test-first in group 4.

- Fetch current docs with `ctx7`: Ember (blueprint flags, test helpers),
  WarpDrive (store setup, import paths), Tailwind CSS v4 (Vite plugin), MSW
  (browser worker), Playwright, openapi-typescript.
- Generate `web/` with the official blueprint (TypeScript, pnpm, Vite,
  `.gts`, Glint). Package name `colivo-web`.
- Dev dependencies: `msw`, `@playwright/test`, `openapi-typescript`,
  `eslint-plugin-boundaries`, `tailwindcss`, `@tailwindcss/vite`,
  `prettier-plugin-tailwindcss`. Dependencies: `@fontsource/inter`,
  `@fontsource/space-grotesk`.
- Folders from the skill: `app/data/{handlers,builders,types}`,
  `app/models`, `app/utils`, `app/components/{ui,layout}`,
  `tests/{helpers,acceptance,integration/components,unit/data}`, `e2e/`.
- `web/app/styles/app.css`: Tailwind import and the Colivo tokens from
  `colivo-design/README.md → Design tokens` in `@theme`; fonts imported.
- ESLint boundaries (routes → components → services → data → utils).
- `web/tests/helpers/msw.ts` (worker started and reset per test, handlers
  typed with `api.generated.ts`), `web/playwright.config.ts`.
- `web/.env.example` pointing at `VITE_API_HOST`, the root `Makefile`'s web
  targets enabled.
- Check: `pnpm test` runs the blueprint's tests, `pnpm lint`, Prettier
  check, `pnpm build`.

## 4. Health check (slice 1)

- **Behaviours:** B1–B12.
- **Acceptance:**
  - Backend: `backend/tests/health/test_api.py::test_health_reports_database_and_redis_ok`.
  - Web: `web/tests/acceptance/start-page-test.ts` › visitor sees the
    server is connected.
- **Tables:** none; no migration.

### Backend

- `backend/app/modules/health/schemas.py`: `ServiceStatus` (`StrEnum`),
  `HealthOut`.
- `backend/app/modules/health/service.py`: one check per dependency with a
  short timeout, and the overall result.
- `backend/app/modules/health/router.py`: `GET /health` on `CoreRouter`,
  200 or 503.
- `backend/app/api/api_v1.py`: register the health router.
- `backend/app/core/exceptions.py`: 404 and 500 in the envelope, no
  internals in a 500.
- `backend/app/main.py`: CORS from `settings.backend_cors_origins`.
- `backend/app/core/router.py`: OpenAPI declares
  `StandardResponse[<model>]`.
- Tests: `backend/tests/health/{test_service,test_api}.py`,
  `backend/tests/core/test_api.py` (404, 500, CORS, OpenAPI shape).

### Contract

- `make api-export` → `api/openapi.json`; `make api-types` →
  `web/app/data/types/api.generated.ts`. Commit
  `chore(api): update contract for health check`.

### Web

- `web/app/data/handlers/{types,api-envelope,errors,auth}.ts`,
  `web/app/data/config.ts`, `web/app/data/lifetimes.ts`: from the
  `ember-scaffold` starter files, adjusted to the string `errors` list.
- `web/app/services/store.ts` wired with the three handlers;
  `web/app/services/session.ts` with an in-memory token.
- `web/app/data/builders/health.ts`: the health request (no Model; health
  is not a record).
- `web/app/components/ui/button.gts` (menu button),
  `web/app/components/layout/app-shell.gts`,
  `web/app/components/health/server-status.gts`.
- `web/app/templates/application.gts` (the shell), `web/app/routes/index.ts`
  and `web/app/templates/index.gts` (start page).
- Tests: `web/tests/unit/data/{handlers-test,builders-test}.ts`,
  `web/tests/integration/components/{ui/button-test,layout/app-shell-test,health/server-status-test}.gts`,
  `web/tests/acceptance/start-page-test.ts`.

### End-to-end

- `web/e2e/smoke.spec.ts`: against `docker compose up` with no mocks, a
  visitor opens the web app and sees "Server connected".

## 5. CI

Scaffolding. Commit: `ci: add backend and web workflows`, then reworked to
one workflow (`ci: run backend and web checks from one gated workflow`).

- Fetch current docs with `ctx7` or each action's own `action.yml` at the
  pinned commit: GitHub Actions (service containers, `concurrency`),
  `astral-sh/setup-uv`, `pnpm/action-setup`, `dorny/paths-filter`.
- `.github/workflows/ci.yml`, one workflow on every pull request and every
  push to `main` (a branch is checked through its pull request):
  - `changes` (`dorny/paths-filter`, `some-with-excludes`) decides which parts
    changed. Backend: `backend/**`, `api/**`, `infra/backend.Dockerfile`,
    `Makefile`, the workflow. Web: `web/**`, `api/**`, `Makefile`, the
    workflow. Both exclude `**/*.md`. A branch push is compared with its
    merge-base on `main`; a PR with its base.
  - `backend` (if changed): services `postgres:16` (with `colivo_test`) and
    `redis:7`; `uv sync --locked`, `make backend-test-fast`, backend lint and
    format check, `make backend-migrations-check`, `make api-export` with
    `git diff --exit-code api/`, and `docker build --target prod`.
  - `web` (if changed): `pnpm install --frozen-lockfile`, `make api-types`
    with `git diff --exit-code web/app/data/types/`, `make web-test-fast`
    (headless Chrome), web lint and format check, `pnpm build`.
  - `ci-ok`: always runs; fails if any job failed or was cancelled. **The one
    required check** for branch protection, so a skipped part never blocks a
    merge.
  - On a push to `main` every job runs, whatever changed.
- Actions pinned to commit SHAs; `concurrency` cancels superseded runs except
  on `main`; dependency caches for uv and pnpm.
- Check: push the branch (asked first) and see `CI OK` green; see
  [validation.md → Manual checks](validation.md#manual-checks).

## 6. Verify and document

- Run [validation.md](validation.md) in full.
- `specs/data-model.md`: confirm the Phase 0 change-log row (no tables).
- `specs/tech-stack.md`: under **Decided in Phase 0**, record CI (GitHub
  Actions with path filters), the health check shape, psycopg 3,
  root `compose.yaml`, the test database, `make api-export`, the in-memory
  session and self-hosted fonts; update the `infra/` row in **Project
  conventions** and approve that table; mark CI as decided in **Stack
  summary**; remove CI platform from **Deferred decisions**; add **Known
  limitations** (no end-to-end tests in CI).
- `colivo-design/requirements.md → NFR-11`: web front end is Ember, not
  React / Next.js.
- `README.md` at the root: clean-checkout setup, `make` targets, how to run
  each part and the end-to-end test, the OpenAPI export.
- `specs/roadmap.md`: mark Phase 0 `✅ Complete`.
- `CHANGELOG.md`: run `/changelog` before merging.
