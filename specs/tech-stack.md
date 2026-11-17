# Colivo — Tech Stack

> Decided: **FastAPI** + **PostgreSQL** REST API, **Ember.js** web,
> **Flutter** mobile. Items marked _(to confirm)_ are recommendations that
> fit those choices and still need approval.

## Principles

- **One repo, three apps** — backend, web and mobile change together, so one
  pull request carries a whole feature (Rabbi's requirement: one part at a
  time, spec-driven).
- **API contract first** — FastAPI publishes an OpenAPI file; the Ember and
  Flutter clients are built against it, so they can't drift from the API.
- **Money is exact** — amounts are `Decimal` / `numeric(12,2)`, never floats;
  every calculation has a test against the October 2026 spreadsheet.
- **Nothing is erased** — edits and deletes keep history (soft delete).
- **Popular, well-supported, reliable tools** the builder already knows well:
  FastAPI, PostgreSQL and Ember.js (Rabbi's requirement).
- **Mobile-first UI** that also works well on a desktop browser.

## Recommended framework: FastAPI

We commit to **FastAPI** for a REST API under `/api/v1/`, running on
**Python 3.12** with **PostgreSQL 16**. The web app is **Ember.js**; the
mobile app is **Flutter**.

Why FastAPI:

- **Builder's own stack** — already used in production (Rabbi's choice).
- **OpenAPI out of the box** — every endpoint and Pydantic schema lands in the
  contract that the Ember and Flutter clients use.
- **Typed requests and responses** — Pydantic v2 validates every input, which
  matters for money and role checks.
- **Fast enough, simple first** — endpoints are sync and use SQLModel
  sessions, which FastAPI runs in its threadpool; slow work (OTP,
  notifications) goes to background jobs, and an endpoint can be made async
  later if it needs to be.

Why Ember.js for the web:

- **Builder's own experience** (Rabbi's choice); strong conventions keep
  routes, components and services in predictable places, which suits
  spec-driven, one-phase-at-a-time work.

Why Flutter for mobile:

- **One codebase** for Android and iOS (Rabbi's choice); Android ships first.

## Stack summary

| Layer             | Choice                                                                                                               |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| Language          | Python 3.12 (backend), TypeScript (web), Dart (mobile)                                                               |
| Framework         | FastAPI (backend), Ember.js Octane (web), Flutter (mobile)                                                           |
| UI (web)          | Ember `.gts` components + Tailwind CSS v4; `ember-scaffold` layout                                                   |
| UI (mobile)       | Flutter Material 3 widgets                                                                                           |
| Backend           | REST API under `/api/v1/`, JSON, OpenAPI from FastAPI                                                                |
| Validation        | Pydantic v2                                                                                                          |
| Data access       | SQLModel (on SQLAlchemy 2.0) + Alembic; `fastapi-orm-scaffold` layout                                                |
| Database          | PostgreSQL 16                                                                                                        |
| Background jobs   | Celery + Redis for OTP, notifications, month close _(to confirm)_                                                    |
| File storage      | Private S3 bucket; MinIO locally _(to confirm)_                                                                      |
| Auth              | Phone/email one-time code; JWT access + refresh _(to confirm)_                                                       |
| Web data layer    | WarpDrive (EmberData) request builders + handlers; types generated from `api/openapi.json` with `openapi-typescript` |
| Mobile data layer | Dart client from OpenAPI _(to confirm)_                                                                              |
| Python tooling    | uv (`pyproject.toml` + `uv.lock`), Ruff (lint + format), pyright (types)                                             |
| Web tooling       | pnpm, Vite; ESLint (+ `eslint-plugin-boundaries`), ember-template-lint, Prettier (+ Tailwind plugin), Glint (types)  |
| Mobile lint       | `flutter analyze`, `dart format`                                                                                     |
| Tests             | pytest + `TestClient` (backend); QUnit + MSW (web); Playwright (end-to-end); `flutter test`                          |
| CI                | GitHub Actions with path filters _(to confirm)_                                                                      |
| Local run         | Docker Compose                                                                                                       |

## Decided in Phase 0

_Filled in as Phase 0 is planned and built. Record each decision as:_
**<Topic>:** <decision> — <why>.

- **Backend layout:** follow the `fastapi-orm-scaffold` structure
  (`app/core/`, `app/api/api_v1.py`, `app/modules/<module>/`, `alembic/`) —
  the builder's own proven template, so every module looks the same.
- **ORM:** SQLModel + Alembic — one class serves as table and schema base,
  built on SQLAlchemy 2.0, and it is what the scaffold uses.
- **Packages:** uv with `pyproject.toml` and `uv.lock` instead of the
  scaffold's `pip` + `requirements.txt` — faster installs and a lockfile.
- **API response envelope:** keep the scaffold's `StandardResponse` and
  publish it in OpenAPI — see [API response format](#api-response-format).
- **Sync endpoints:** sync SQLModel sessions, as in the scaffold — simpler
  to write and test; slow work goes to background jobs.
- **Type checker:** pyright instead of mypy — faster, and better inference
  for Pydantic v2 and SQLModel.
- **Testing process:** outside-in TDD as described in [testing.md](testing.md);
  real PostgreSQL with per-test rollback, not SQLite, because exact money
  depends on `numeric` behaviour.
- **Phase 0 scope:** backend, web skeleton and infra — the web is scaffolded
  in Phase 0 so Phase 1 starts on behaviours with a proven red/green setup.
  The mobile structure is still deferred.
- **Web layout:** follow the `ember-scaffold` skill (official blueprint,
  TypeScript, `.gts`, Glint, Vite) — the builder's own template, the web
  counterpart of `fastapi-orm-scaffold`.
- **Web packages:** pnpm — the blueprint default; faster, strict installs.
- **Web data layer:** WarpDrive Model classes + `store.request` with request
  builders and handlers, no adapters or serializers (the legacy path). Only
  `web/app/data/` talks HTTP; only `data/handlers/api-envelope.ts` knows the
  `StandardResponse` envelope and only `data/handlers/errors.ts` knows the
  error body.
- **Web errors:** keep the scaffold's string `errors` list
  (`"body.name: Field required"`); `errors.ts` parses `<loc>: <msg>` into
  field errors and maps 400 → business rule, 409 → conflict. One file knows
  the format, and the backend stays on its scaffold.
- **Web CSS:** Tailwind CSS v4 through its Vite plugin; tokens from
  `colivo-design/README.md` in `@theme` in `web/app/styles/app.css`; utility
  classes live in `components/ui/`.
- **Web tests:** QUnit + MSW (only the HTTP boundary is mocked, typed from
  the generated API types) and Playwright for end-to-end — see
  [testing.md → Web](testing.md#web).
- **Build order:** one `plan.md` group at a time — the group's backend with
  full TDD, then its API contract, then its web with full TDD — not the whole
  backend of a phase first. API mistakes show up while the code is fresh, and
  every group is demoable.

## Project conventions

Every phase follows this layout. Update this section when a convention changes.
_This table is a proposal to approve._

| Directory                                   | Holds                                                                                                                                                                                    |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend/app/main.py`                       | FastAPI app, middleware, exception handlers; `api_router` mounted at `/api/v1`                                                                                                           |
| `backend/app/api/api_v1.py`                 | Registers every module router; `deps.py` (auth dependencies) joins it when auth arrives                                                                                                  |
| `backend/app/core/`                         | `config.py` (settings from env vars), `database.py` (engine, `get_session`), `router.py` (`CoreRouter`), `schemas.py` (`StandardResponse`), `exceptions.py` (error handlers), `utils.py` |
| `backend/app/modules/<module>/`             | `models.py`, `schemas.py`, `service.py`, `router.py` per module: `accounts`, `homes`, `meals`, `groceries`, `payments`, `bills`, `statements`, `deposits`, `inbox`, `messaging`          |
| `backend/app/utils/`                        | Shared helpers used by several modules                                                                                                                                                   |
| `backend/alembic/`, `backend/alembic.ini`   | Alembic migrations (`alembic/versions/`) and config                                                                                                                                      |
| `backend/tests/<module>/`                   | That module's tests                                                                                                                                                                      |
| `backend/pyproject.toml`, `backend/uv.lock` | Python dependencies (uv)                                                                                                                                                                 |
| `web/app/data/`                             | The whole web data layer: `config.ts`, `handlers/` (errors, auth, envelope), `builders/<resource>.ts`, `lifetimes.ts`, `types/api.generated.ts` (never edited by hand)                   |
| `web/app/models/`                           | WarpDrive Model classes, one per resource                                                                                                                                                |
| `web/app/services/`                         | Store, session, current home                                                                                                                                                             |
| `web/app/routes/`, `web/app/templates/`     | Thin: load data, guard access, compose components; everything behind login under `authenticated/`                                                                                        |
| `web/app/components/ui/`                    | Domain-free design system (button, field, card, modal); the only place with Tailwind class lists                                                                                         |
| `web/app/components/layout/`                | Page shell, sidebar, navbar                                                                                                                                                              |
| `web/app/components/<feature>/`             | One folder per feature (`meals`, `groceries`, `payments`, …)                                                                                                                             |
| `web/app/utils/`                            | Pure functions, no Ember imports (money formatting, dates)                                                                                                                               |
| `web/app/styles/app.css`                    | Tailwind import and `@theme` tokens from `colivo-design/README.md`                                                                                                                       |
| `web/tests/`                                | `unit/`, `integration/components/`, `acceptance/` (MSW), `helpers/` (`msw.ts`, `login.ts`, factories)                                                                                    |
| `web/e2e/`                                  | Playwright end-to-end journeys against the real backend                                                                                                                                  |
| `mobile/lib/features/<feature>/`            | Flutter screens, state and widgets per feature                                                                                                                                           |
| `mobile/lib/core/`                          | API client, auth, theme                                                                                                                                                                  |
| `mobile/test/`                              | Flutter tests                                                                                                                                                                            |
| `api/openapi.json`                          | Exported API contract — never edited by hand                                                                                                                                             |
| `infra/`                                    | Docker Compose, Dockerfiles, deploy scripts                                                                                                                                              |
| `colivo-design/`                            | Screen designs and `requirements.md`                                                                                                                                                     |
| `specs/`                                    | Mission, roadmap, tech stack and one folder per phase                                                                                                                                    |

Rules:

- A new endpoint goes in its module's `router.py`, with request and response
  models in `schemas.py` and tests in `backend/tests/<module>/`; a new module
  is registered in `app/api/api_v1.py`.
- Routers use `CoreRouter`, never plain `APIRouter`. Each endpoint calls
  `set_response_message(request, ...)`, sets the status code on the injected
  `Response`, and declares its response model as the return type.
- Business rules live in `service.py`; routers only parse input, check the
  role and call the service. Services raise `StarletteHTTPException` and
  commit explicitly.
- Only `models.py`, `service.py` and `app/core/database.py` touch SQLModel;
  the session comes from `Depends(get_session)`, and every money change runs
  inside one database transaction.
- New models are imported in `alembic/env.py` so autogenerate sees them.
- Money columns are `Decimal` with `sa_type=Numeric(12, 2)`, never `float`;
  timestamps are timezone-aware (never `datetime.utcnow`).
- Config is read only through `app.core.config.settings`, never `os.environ`.
- Every query is scoped to the current **home**; a member never sees another
  home's data.
- After changing an endpoint, export `api/openapi.json` and regenerate the web
  types (`make api-types`) and the mobile client; CI fails if the contract is
  out of date.
- Ember pages and Flutter screens call the API only through their data layer
  (`web/app/data/` via `store.request`, `mobile/lib/core/`).
- Web dependencies point one way: routes → components → services → data →
  utils, enforced by `eslint-plugin-boundaries`. `components/ui/` never
  imports a feature folder. The full rules are in the `ember-scaffold` skill.
- Web: no hex colours or one-off sizes in components (tokens only); tests
  select elements by `data-test-*`, never by CSS class.
- Names: Python `snake_case`; Ember files `kebab-case`, classes
  `PascalCase`; Dart files `snake_case`, classes `PascalCase`; URLs and JSON
  fields `snake_case`.
- Words follow the design: home, owner, fund keeper, grocery fund, home fund,
  cost per meal, deposit, credit.
- Config comes from environment variables (`.env`, with `.env.example`
  committed); never hardcode secrets.

## API response format

Every response, success or error, uses the scaffold's `StandardResponse`
envelope:

```json
{ "success": true, "message": "Home created", "data": { "id": "…" } }
{ "success": false, "message": "Validation Error", "errors": ["body.name: Field required"] }
```

- `CoreRouter` wraps each endpoint's return value in the envelope, and the
  handlers in `app/core/exceptions.py` give errors the same shape.
- `CoreRouter` also declares `StandardResponse[<model>]` as the response model,
  so `api/openapi.json` and the generated clients see the real wrapped shape.
- `message` is set with `set_response_message`; error details go in `errors`
  as a list of strings; empty fields are left out.

| Code | When                                    |
| ---- | --------------------------------------- |
| 200  | GET, update or delete succeeded         |
| 201  | Create succeeded                        |
| 400  | Request breaks a business rule          |
| 401  | Not logged in                           |
| 403  | Logged in, but the role may not do this |
| 404  | Not found, or belongs to another home   |
| 409  | Duplicate or conflicting change         |
| 422  | Input fails validation                  |
| 500  | Unexpected error                        |

## Validation

pytest, Ember QUnit and Flutter tests are how we validate every change. Work
isn't done until they pass.

- `make test` runs every suite once. Use it before committing and in CI.
  Per part: `cd backend && uv run pytest`, `cd web && pnpm test`,
  `cd mobile && flutter test`.
- Watch mode: `uv run ptw` (backend), `pnpm start` then `/tests` (web).
- Every behaviour is built test-first. The process, test levels, settings
  and rules are in [testing.md](testing.md); the `/tdd` skill runs it.
- Fast loop: `make test-fast` (unit + integration, no `slow` tests).
- Each phase's behaviours are listed in its `validation.md` and written as
  tests in the relevant `tests/` folders.
- Run `make lint` and `make format-check` alongside the tests: `uv run ruff
check`, `uv run ruff format --check` and `uv run alembic check` (backend); `pnpm lint` (ESLint, ember-template-lint, Glint) and Prettier
  (web); `flutter analyze` and `dart format --set-exit-if-changed` (mobile).
- CI (`.github/workflows/`) runs the same checks on every push and pull
  request, only for the parts that changed; a PR merges only when CI is green.

## Responsive design

Every page's UI must be responsive. This section is the single standard that
all feature specs reference.

- **Mobile-first:** build for a 360px phone first; `colivo-design/mobile/`
  shows the phone layout.
- **Breakpoints:** 640px (large phone), 768px (tablet), 1024px (sidebar
  appears), 1280px (wide desktop); `colivo-design/web/` shows the desktop layout.
- **Supported widths:** 320px to wide desktop, no horizontal page scroll.
- **Fluid layout:** flex and grid with wrapping; side menus stack on top on
  small screens; wide tables scroll inside their own box.
- **Touch:** tap targets at least 44×44px; nothing depends on hover alone.
- **Viewport:** never disable zoom.
- **Verification:** every phase with UI is checked at 320px, 768px, and 1280px.
  The Flutter app is checked on a small phone (360×640) and a large phone.

## Known limitations

_None yet. Add each one as it's discovered: **<Area>:** <limitation>._

## Deferred decisions

- **Mobile project structure** (scaffold, layout and tooling for
  `mobile/`) — decide before the first phase tagged `[mobile]`.
- **Background jobs:** Celery + Redis recommended; FastAPI background tasks or
  ARQ are lighter alternatives.
- **Auth tokens:** JWT access + refresh for both clients, or httpOnly session
  cookies for web plus tokens for mobile — decide in Phase 1. The scaffold
  keeps a bearer token in `localStorage`, which an XSS bug can steal; only
  `web/app/data/handlers/auth.ts` and `web/app/services/session.ts` change.
- **Flutter state management** (Riverpod, Bloc, or other) — decide before
  Phase 10.
- **SMS provider** for one-time codes in Bangladesh, and the email provider.
- **File storage:** AWS S3 or another S3-compatible store.
- **CI platform:** GitHub Actions or Jenkins.
- **Deployment target:** AWS (EC2 + RDS + S3) or another host — decide by
  Phase 9.
- **Error tracking and monitoring** — decide by Phase 9.
