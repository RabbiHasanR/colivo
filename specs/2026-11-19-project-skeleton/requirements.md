# Phase 0 — Project Skeleton: Requirements

## Context

Phase 0 is the first phase in the [roadmap](../roadmap.md). Nothing is built
yet: the repo holds only specs, the design and the changelog. This phase
creates the monorepo that every later phase builds on: the backend, the web
app, local infrastructure, the test harness for both parts, the API contract
pipeline and CI.

It serves the [mission](../mission.md)'s technical promises rather than a
user-facing one: exact money and tests against the October 2026 spreadsheet
need a real PostgreSQL test database from day one, and "responsive web first"
needs the app shell and design tokens in place before Phase 1's log-in
screens. The stack and its reasons are in [tech-stack.md](../tech-stack.md);
the TDD process is in [testing.md](../testing.md).

Design references:

- `colivo-design/web/WebHomeEmpty.html`: the app shell (sidebar with the
  home name, nav and the signed-in person; content area). Phase 0 builds the
  shell's frame only; its nav items and content arrive with their phases.
- `colivo-design/README.md → Design tokens`: fonts, colours, radius, touch
  targets.

After this phase, `docker compose up` gives a working backend whose health
check reports PostgreSQL and Redis, and the web app opens inside the Colivo
shell and shows whether it can reach the server.

## Scope

**In scope**

- Monorepo: `backend/`, `web/`, `api/`, `infra/`, `docs/`, a root
  `Makefile`, `compose.yaml`, `.env.example`.
- Backend in the `fastapi-orm-scaffold` layout with uv: settings from env
  vars, database engine and session, `CoreRouter`, the `StandardResponse`
  envelope and its error handlers, Alembic set up with no revisions.
- `GET /api/v1/health` reporting the database and Redis, inside the
  envelope.
- CORS for the web app's origin.
- Backend test harness: pytest, a separate test database built with
  `alembic upgrade head` once per session, one rolled-back transaction per
  test, `TestClient`, the `slow` marker.
- API contract: `api/openapi.json` exported from FastAPI, web types
  generated from it (`make api-types`).
- Web in the `ember-scaffold` layout with pnpm: store wired with the error,
  auth and envelope handlers; a health request builder; Tailwind CSS v4 with
  the Colivo tokens in `@theme`; self-hosted Inter and Space Grotesk.
- The responsive app shell and a start page that shows the server status
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- Web test harness: QUnit, MSW, Playwright, and one end-to-end smoke journey
  against the real backend.
- GitHub Actions CI with path filters: backend checks when `backend/` or
  `api/` changes, web checks when `web/` or `api/` changes.

**Out of scope**

- Any table, and the shared SQLModel base (UUIDv7 `id`, snake_case
  `__tablename__`, `created_at` / `updated_at`, the `StrEnum` → `CHECK`
  helper). They arrive with Phase 1's first table, so they are proven on a
  real table.
- Log-in, the login route and session persistence: the auth token storage
  choice is a [Deferred decision](../tech-stack.md#deferred-decisions) for
  Phase 1. Phase 0's session service holds a token in memory only.
- Generic resource builders (`findRecord`, `query`): added with Phase 1's
  first resource.
- Nav items and page content inside the shell: each phase adds its own.
- Background jobs (Celery), file storage (S3 / MinIO), SMS and email
  providers.
- Running end-to-end tests in CI, a production Dockerfile and deploy
  (Phase 9).
- Pre-commit hooks.
- The mobile skeleton (before the first `[mobile]` phase).

## Features

### Health check

`GET /api/v1/health` tells a person, Docker or a load balancer whether the
backend can reach its two dependencies.

- Reports `database` and `redis`, each `ok` or `down`.
- 200 when both are `ok`; 503 when either is `down`, with the same `data`
  so the caller sees which one failed.
- Each check has a short timeout, so health answers quickly when a
  dependency is down.
- Public: no log-in, no role. It reveals nothing beyond `ok` / `down`.
- Serves `colivo-design/requirements.md → NFR-11` (REST API under
  `/api/v1`, FastAPI + PostgreSQL + Redis) and gives Phase 9's health checks
  their endpoint.

### API envelope and errors

Every response, success or error, uses the
[`StandardResponse` envelope](../tech-stack.md#api-response-format).

- An unknown path answers 404 in the envelope.
- An unexpected error answers 500 in the envelope with a generic message:
  no stack trace, SQL or internal names.
- `api/openapi.json` declares each endpoint's wrapped
  `StandardResponse[<model>]` shape, so the generated web types match what
  the API really sends.
- The web app's origin (`BACKEND_CORS_ORIGINS`) may call the API from the
  browser; other origins get no CORS headers.

### Web data layer

Only `web/app/data/` talks HTTP
([tech-stack.md → Decided in Phase 0](../tech-stack.md#decided-in-phase-0)).

- `data/handlers/api-envelope.ts` unwraps `data` from the envelope; nothing
  else knows the envelope.
- `data/handlers/errors.ts` turns error responses into plain errors: 422
  `"<loc>: <msg>"` strings become field errors, 400 a business-rule error,
  409 a conflict, anything else a general error.
- `data/handlers/auth.ts` sends the session's token as a bearer token when
  there is one, and no `Authorization` header when there isn't.

### App shell and start page

Who: anyone opening the web app (no log-in yet).

- Every page renders inside the Colivo shell: the name, the sidebar from
  1024px up, and a menu button below 1024px that opens and closes it
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- The start page calls the health check and shows "Server connected", which
  part is down, or "Can't reach the server". Phase 1 replaces it with the
  log-in page.
- Layout follows `colivo-design/web/WebHomeEmpty.html` by eye; it is
  checked by hand, not test-driven ([testing.md → Web](../testing.md#web)).

### Local run and CI

- `docker compose up` starts PostgreSQL 16, Redis 7 and the backend; the web
  dev server runs on the host with `pnpm start`.
- The test database is created by an init script in `infra/postgres/`.
- CI runs on every pull request and every push to `main`, per part, using
  the same `make` targets as local runs.

## API

| Method | Path                | Role          | Request | Response                                                                                                                                                   |
| ------ | ------------------- | ------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/v1/health`    | None (public) | —       | 200 `StandardResponse[HealthOut]`, `data: { "database": "ok", "redis": "ok" }`. 503 with `success: false` and the same `data` showing which part is `down` |
| any    | `/api/v1/<unknown>` | —             | —       | 404 envelope, `success: false`                                                                                                                             |

`HealthOut`: `database` and `redis`, each a `ServiceStatus` (`StrEnum`:
`ok`, `down`).

## Data model changes

None. Phase 0 creates no table and no migration: Alembic is set up
(`backend/alembic/`, `alembic.ini`, `env.py` reading `settings`) with no
revisions, and the test database is built with `alembic upgrade head` from
the start so Phase 1's first migration runs through the same path. The full
schema is in [data-model.md](../data-model.md).

## Decisions

| Decision                 | Choice                                                                                                       | Why                                                                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Scope                    | Backend + infra core and web skeleton + app shell; shared model base and pre-commit hooks left out           | User's choice. The model base is proven on Phase 1's first real table; `make format-check` and CI already cover formatting                 |
| Groups                   | Groundwork → backend scaffold → web scaffold → health check slice → CI → verify                              | User's choice ("part by part, then one slice"). The web scaffold is its own group so each scaffold commit is reviewed on its own           |
| Merge bar                | The usual gate plus CI green on the pull request                                                             | User's choice. Proves CI works before Phase 1 depends on it                                                                                |
| CI platform              | GitHub Actions, one workflow per part with path filters; `api/` changes trigger both                         | User's choice. Matches the builder's stack and the repo's GitHub remote; resolves the CI platform Deferred decision                        |
| Health module            | `backend/app/modules/health/` (`schemas`, `service`, `router`; no `models`)                                  | Follows the module rules like every later module, instead of a special case in `core/`                                                     |
| Health status codes      | 200 when both `ok`, 503 when either `down`, same `data` in both                                              | Docker and load balancers read the status code; the web reads `data` to say which part failed                                              |
| Health timeouts          | Short connect timeout per check (about 2 s)                                                                  | Health must answer quickly when a dependency is down, and the "down" tests stay inside the 60 s budget                                     |
| Testing "down" states    | Point the check at an unreachable address (a closed port), never a mock                                      | PostgreSQL and Redis are ours; `testing.md` forbids mocking them                                                                           |
| Database driver          | `psycopg[binary]` (psycopg 3)                                                                                | Current driver, supported by SQLAlchemy 2.0; binary wheels need no system libraries                                                        |
| Compose file location    | `compose.yaml` at the repo root; Dockerfiles and the Postgres init script in `infra/`                        | `docker compose up` works from the root, as the roadmap says; tech-stack's `infra/` row is updated to match in Verify                      |
| Test database            | `colivo_test`, created by `infra/postgres/init/01-create-test-db.sql`; `TEST_DATABASE_URL` in `.env.example` | One `docker compose up` gives both databases; tests never touch the dev database                                                           |
| OpenAPI export           | `make api-export` writes `api/openapi.json` from `app.main:app`, run before `make api-types`                 | One command the `/tdd` contract step and CI both use                                                                                       |
| Start page               | Temporary page showing the server status; replaced by log-in in Phase 1                                      | Makes the slice real end to end (backend → contract → store → page) and gives the smoke e2e something true to check                        |
| Session in Phase 0       | `services/session.ts` holds the token in memory only                                                         | Auth token storage is Phase 1's decision; `auth.ts` and its test exist so the store is wired as the roadmap says                           |
| Fonts                    | Self-hosted Inter and Space Grotesk (`@fontsource` packages)                                                 | No third-party request from members' phones, works offline in dev, no Google Fonts privacy question                                        |
| Colour schemes           | Light only                                                                                                   | `colivo-design` defines one scheme; no dark tokens exist                                                                                   |
| End-to-end in CI         | Not in Phase 0; `make test` runs it locally                                                                  | CI would need the full Compose stack and a browser; added when deploy work starts (Phase 9)                                                |
| Python version           | 3.14 instead of the stack's original 3.12                                                                    | 3.12 is security-fixes-only; 3.14 is mature, faster, every dependency has a wheel, and it has `uuid.uuid7()`; 3.15 lacked a `pyyaml` wheel |
| `requirements.md` NFR-11 | Says "React / Next.js"; [tech-stack.md](../tech-stack.md) decided Ember. Fixed to Ember in Verify            | The stack decision is made; the design's requirements file is out of date                                                                  |

## Constraints

- Follow [tech-stack.md → Project conventions](../tech-stack.md#project-conventions):
  `CoreRouter` only, `set_response_message` on every endpoint, business rules
  in `service.py`, config only through `app.core.config.settings`.
- Fetch current docs with `ctx7` for every library this phase touches
  (FastAPI, Pydantic, pydantic-settings, SQLModel, SQLAlchemy, Alembic,
  psycopg, redis-py, pytest, Ember, WarpDrive, Tailwind CSS, MSW, Playwright,
  openapi-typescript, GitHub Actions) before coding.
- Every behaviour is built test-first, as in [testing.md](../testing.md).
  Scaffolding and configuration are not behaviour and have no tests.
- The schema follows [data-model.md](../data-model.md); Phase 0 adds none.
  Any change to it is agreed with the user first.
- Money is `Decimal`, never float, and every money change is one database
  transaction (no money yet; the test harness's rollback-per-test supports
  it).
- Every query is scoped to the current home, and roles are checked in the
  router (no home data yet; health is the only public endpoint).
- Nothing is erased: edits and deletes keep history (no records yet).
- `api/openapi.json` is exported and the web types regenerated
  (`make api-types`) after any endpoint change; the mobile client comes with
  the first `[mobile]` phase.
- Config comes from env vars, with `.env.example` updated and no secrets
  committed.
- Alembic is set up so that later migrations apply cleanly; Phase 0 has no
  previous database to migrate.
- Every dependency added is named in [plan.md](plan.md); anything beyond it
  is asked first.
