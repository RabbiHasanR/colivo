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
- **Fast and async** — handles the inbox, OTP and notification flows without
  blocking.

Why Ember.js for the web:

- **Builder's own experience** (Rabbi's choice); strong conventions keep
  routes, components and services in predictable places, which suits
  spec-driven, one-phase-at-a-time work.

Why Flutter for mobile:

- **One codebase** for Android and iOS (Rabbi's choice); Android ships first.

## Stack summary

| Layer           | Choice                                                         |
| --------------- | -------------------------------------------------------------- |
| Language        | Python 3.12 (backend), TypeScript (web), Dart (mobile)         |
| Framework       | FastAPI (backend), Ember.js Octane (web), Flutter (mobile)     |
| UI (web)        | Ember components + Tailwind CSS _(to confirm)_                 |
| UI (mobile)     | Flutter Material 3 widgets                                     |
| Backend         | REST API under `/api/v1/`, JSON, OpenAPI from FastAPI          |
| Validation      | Pydantic v2                                                    |
| Data access     | SQLAlchemy 2.0 ORM + Alembic migrations _(to confirm)_         |
| Database        | PostgreSQL 16                                                  |
| Background jobs | Celery + Redis for OTP, notifications, month close _(to confirm)_ |
| File storage    | Private S3 bucket; MinIO locally _(to confirm)_                |
| Auth            | Phone/email one-time code; JWT access + refresh _(to confirm)_ |
| Web data layer  | Typed client from OpenAPI in an Ember service _(to confirm)_   |
| Mobile data layer | Dart client from OpenAPI _(to confirm)_                      |
| Python tooling  | uv (packages), Ruff (lint + format), mypy _(to confirm)_       |
| Web lint/format | ESLint, ember-template-lint, Prettier, Glint (types)           |
| Mobile lint     | `flutter analyze`, `dart format`                               |
| Tests           | pytest + httpx (backend); Ember QUnit (web); `flutter test`    |
| CI              | GitHub Actions with path filters _(to confirm)_                |
| Local run       | Docker Compose                                                 |

## Decided in Phase 0

_Filled in as Phase 0 is built. Record each decision as:_

- **<Topic>:** <decision> — <why>.

## Project conventions

Every phase follows this layout. Update this section when a convention changes.
_This table is a proposal to approve._

| Directory                           | Holds                                              |
| ----------------------------------- | -------------------------------------------------- |
| `backend/app/main.py`               | FastAPI app, routers mounted under `/api/v1`       |
| `backend/app/core/`                 | Settings (env vars), security, auth dependencies   |
| `backend/app/db/`                   | Engine, session, base model                        |
| `backend/app/domains/<domain>/`     | `models.py`, `schemas.py`, `service.py`, `router.py` per domain: `accounts`, `homes`, `meals`, `groceries`, `payments`, `bills`, `statements`, `deposits`, `inbox`, `messaging` |
| `backend/migrations/`               | Alembic migrations                                 |
| `backend/tests/<domain>/`           | That domain's tests                                |
| `web/app/routes/`, `web/app/templates/` | Ember routes and their templates               |
| `web/app/components/`               | Reusable Ember components                          |
| `web/app/services/`                 | API client, session, current home                  |
| `web/tests/`                        | Unit, integration and acceptance tests             |
| `mobile/lib/features/<feature>/`    | Flutter screens, state and widgets per feature     |
| `mobile/lib/core/`                  | API client, auth, theme                            |
| `mobile/test/`                      | Flutter tests                                      |
| `api/openapi.json`                  | Exported API contract — never edited by hand       |
| `infra/`                            | Docker Compose, Dockerfiles, deploy scripts        |
| `docs/design/`                      | Screen designs and `requirements.md`               |
| `specs/`                            | Mission, roadmap, tech stack and one folder per phase |

Rules:

- A new endpoint goes in its domain's `router.py`, with request and response
  models in `schemas.py` and tests in `backend/tests/<domain>/`.
- Business rules live in `service.py`; routers only parse input, check the
  role and call the service.
- Only `models.py`, `service.py` and `backend/app/db/` touch SQLAlchemy;
  every money change runs inside one database transaction.
- Every query is scoped to the current **home**; a member never sees another
  home's data.
- After changing an endpoint, export `api/openapi.json` and regenerate the web
  and mobile clients; CI fails if the contract is out of date.
- Ember pages and Flutter screens call the API only through their client
  (`web/app/services/`, `mobile/lib/core/`).
- Names: Python `snake_case`; Ember files `kebab-case`, classes
  `PascalCase`; Dart files `snake_case`, classes `PascalCase`; URLs and JSON
  fields `snake_case`.
- Words follow the design: home, owner, fund keeper, grocery fund, home fund,
  cost per meal, deposit, credit.
- Config comes from environment variables (`.env`, with `.env.example`
  committed); never hardcode secrets.

## Validation

pytest, Ember QUnit and Flutter tests are how we validate every change. Work
isn't done until they pass.

- `make test` runs every suite once. Use it before committing and in CI.
  Per part: `cd backend && uv run pytest`, `cd web && npm test`,
  `cd mobile && flutter test`.
- Watch mode: `uv run ptw` (backend), `npm start` then `/tests` (web).
- Each phase's acceptance criteria are written as tests in the relevant
  `tests/` folders.
- Run `make lint` and `make format-check` alongside the tests: Ruff and
  `alembic check` (backend); ESLint, ember-template-lint, Glint and Prettier
  (web); `flutter analyze` and `dart format --set-exit-if-changed` (mobile).
- CI (`.github/workflows/`) runs the same checks on every push and pull
  request, only for the parts that changed; a PR merges only when CI is green.

## Responsive design

Every page's UI must be responsive. This section is the single standard that
all feature specs reference.

- **Mobile-first:** build for a 360px phone first; `docs/design/mobile/`
  shows the phone layout.
- **Breakpoints:** 640px (large phone), 768px (tablet), 1024px (sidebar
  appears), 1280px (wide desktop); `docs/design/web/` shows the desktop layout.
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

- **ORM:** SQLAlchemy 2.0 + Alembic recommended; SQLModel is the alternative.
- **Background jobs:** Celery + Redis recommended; FastAPI background tasks or
  ARQ are lighter alternatives.
- **Auth tokens:** JWT access + refresh for both clients, or session cookies
  for web plus tokens for mobile.
- **Web data layer:** generated OpenAPI client in an Ember service, or
  ember-data with a REST adapter.
- **Web CSS:** Tailwind CSS or plain CSS with design tokens.
- **Flutter state management** (Riverpod, Bloc, or other) — decide before
  Phase 10.
- **SMS provider** for one-time codes in Bangladesh, and the email provider.
- **File storage:** AWS S3 or another S3-compatible store.
- **CI platform:** GitHub Actions or Jenkins.
- **Deployment target:** AWS (EC2 + RDS + S3) or another host — decide by
  Phase 9.
- **Error tracking and monitoring** — decide by Phase 9.