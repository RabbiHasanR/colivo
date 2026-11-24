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
**Python 3.14** with **PostgreSQL 16**. The web app is **Ember.js**; the
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

| Layer             | Choice                                                                                                                  |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Language          | Python 3.14 (backend), TypeScript (web), Dart (mobile)                                                                  |
| Framework         | FastAPI (backend), Ember.js Octane (web), Flutter (mobile)                                                              |
| UI (web)          | Ember `.gts` components + Tailwind CSS v4; `ember-scaffold` layout                                                      |
| UI (mobile)       | Flutter Material 3 widgets                                                                                              |
| Backend           | REST API under `/api/v1/`, JSON, OpenAPI from FastAPI                                                                   |
| Validation        | Pydantic v2                                                                                                             |
| Data access       | SQLModel (on SQLAlchemy 2.0) + Alembic; `fastapi-orm-scaffold` layout                                                   |
| Database          | PostgreSQL 16                                                                                                           |
| Background jobs   | Celery + Redis for OTP, notifications, month close _(to confirm)_                                                       |
| File storage      | Private S3 bucket, uploads by presigned POST and reads by presigned GET; MinIO locally, Chainguard's image (decided Phase 1, built Phase 2) |
| Auth              | Phone/email one-time code; server session: random token in an httpOnly cookie, its hash in Redis (decided Phase 1)      |
| Web data layer    | WarpDrive (EmberData) request builders + handlers; types generated from `api/openapi.json` with `openapi-typescript`    |
| Mobile data layer | Dart client from OpenAPI _(to confirm)_                                                                                 |
| Python tooling    | uv (`pyproject.toml` + `uv.lock`), Ruff (lint + format), pyright (types)                                                |
| Web tooling       | pnpm, Vite; ESLint (+ `eslint-plugin-boundaries`), ember-template-lint, Prettier (+ Tailwind plugin), Glint (types)     |
| Mobile lint       | `flutter analyze`, `dart format`                                                                                        |
| Tests             | pytest + `TestClient` (backend); QUnit + MSW (web); Playwright (end-to-end); `flutter test`                             |
| CI                | GitHub Actions: one `ci.yml`, change detection, a `CI OK` gate                                                          |
| Local run         | Docker Compose                                                                                                          |

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
- **Data model:** designed with the user before each phase's spec is
  written (`/feature-spec` Gate 0) and recorded in the living
  [data-model.md](data-model.md); a one-time domain sketch for all phases is
  agreed before Phase 1 — data is far costlier to change than code, and
  Colivo's money lives in the database.
- **Python 3.14** instead of 3.12 — 3.12 only gets security fixes now; 3.14
  is mature (3.14.10), fully supported, faster, and every backend dependency
  installs from a ready-made wheel. It also has `uuid.uuid7()` in the standard
  library, so UUIDv7 keys need no extra package. 3.15 was checked and rejected
  for now: `pyyaml` (through `uvicorn[standard]`) had no 3.15 wheel yet;
  revisit in Phase 9. Set in `backend/.python-version`, `pyproject.toml`
  (`requires-python`, Ruff, pyright) and `infra/backend.Dockerfile`.
- **Migrations:** one Alembic migration per `plan.md` group, edited on the
  phase branch until the group is done — a clean history of one migration
  per slice instead of one per behaviour.
- **CI:** GitHub Actions, one `.github/workflows/ci.yml`. A `changes` job
  (`dorny/paths-filter`) runs the Backend and Web jobs only when their
  inputs change (their folder, `api/`, the `Makefile`, the workflow; never
  `*.md`); `main` runs everything. An always-running **`CI OK`** job is the
  one required check, so a skipped part never blocks a merge. Branches are
  checked through their pull request, `main` on push. Actions are pinned to
  commit SHAs — a moved tag can't change what runs.
- **Branches:** one `phase-<N>-<slug>` branch per phase, pushed early with a
  draft pull request; merged with a merge commit (keeps the per-behaviour
  test-first history). `main` is protected by the `protect-main` ruleset;
  `.github/CODEOWNERS` makes the owner's review required.
- **Health check:** `GET /api/v1/health` reports `database` and `redis` as
  `ok`/`down`: 200 when both are ok, 503 (same data) when either is down.
  Every PostgreSQL and Redis connection gives up after
  `CONNECT_TIMEOUT_SECONDS` (2 s), so health answers fast when one is down.
- **Envelope in OpenAPI:** `StandardResponse[T]` is generic and `CoreRouter`
  declares it for each route's success status; `success` follows the status
  code (`< 400`). Errors use the same envelope; a 500 never carries internals.
- **Database driver:** psycopg 3 (`psycopg[binary]`).
- **Local stack:** `compose.yaml` at the repo root (PostgreSQL 16, Redis 7,
  the backend); the web dev server runs on the host. Tests use a separate
  `colivo_test` database (`infra/postgres/init/01-create-test-db.sql`
  locally, a `psql` step in CI), rebuilt with `alembic upgrade head` on every
  run.
- **Backend images:** one multi-stage `infra/backend.Dockerfile` with a `dev`
  target (Compose, auto-reload) and a `prod` target (runtime dependencies
  only, non-root, precompiled). 439 MB → 213 MB, no loss of speed.
- **Contract:** `make api-export` writes `api/openapi.json`; `make api-types`
  regenerates the web types from it. CI fails if either is out of date.
- **Deprecations fail the tests:** pytest turns `DeprecationWarning` into an
  error, and Ember's deprecation workflow throws (`throwOnUnhandled`), so an
  outdated pattern shows up the day a dependency is upgraded.
- **Web data layer details:** MSW v3 (`onUnhandledFrame`); the handlers use
  small local types and join WarpDrive's once in `services/store.ts`;
  `errors.ts` treats WarpDrive's non-HTTP statuses (0 network, 20 aborted)
  as "no response". The Phase 0 session has no token (`readToken()` → null).
- **Fonts:** Inter and Space Grotesk self-hosted (`@fontsource`), no
  third-party requests.
- **Docs per group:** each `/tdd` group looks up current docs (`find-docs` /
  `ctx7`) for every library and language version it uses for the first time,
  at the installed version; the installed package wins when they disagree.

## Decided in Phase 1

- **Sessions:** a random token (`secrets.token_urlsafe(32)`) in an httpOnly,
  `SameSite=Lax` cookie, `Secure` outside development; Redis keeps only its
  SHA-256 hash and the person, 30 days from the last use. Every request reads
  the active membership from PostgreSQL, so deactivation logs out at once.
  Chosen over JWTs (no instant revocation) and a `localStorage` token (XSS).
  Mobile will send the same token as a bearer header (Phase 10).
- **CSRF:** `SameSite=Lax`, JSON-only bodies and the CORS allow-list with
  credentials (explicit methods and headers, never `*`).
- **One-time codes:** 6 digits from `secrets`, stored hashed with their end
  time; 5 minutes, 5 wrong tries then a 15-minute lock (an atomic `INCR`),
  one a minute and 5 an hour (a Redis sorted set), a replaced code answers
  "expired". Times are checked against an injectable clock
  (`app/core/clock.py`), so tests move time.
- **Account enumeration:** asking for a code answers the same for anyone;
  "Not added yet" and "already in a home" only after the right code.
- **Notifier:** `app/core/notifier.py`, a `Notifier` protocol. Only the
  development `LogNotifier` exists (log line plus the Redis list
  `dev:outbox`, read by the end-to-end test); production refuses to start
  with it (B40).
- **Errors with data:** `AppError` puts a `data` model in the error envelope
  (a refused code's reason, tries left, seconds to wait); 429 is "too many
  tries".
- **Contacts:** phones in E.164 with `phonenumbers` (Bangladesh by
  default), emails checked with `email-validator` and stored lower case.
- **History:** `app/modules/history/` and one `record_change` call, in the
  same transaction as the change.
- **Roles in code:** `require_role(...)`, `OwnerDep` and `OwnerOrManagerDep`
  in `app/api/deps.py` decide who may call an endpoint; rules that depend on
  the target (a manager and another manager, the owner's row) are in the
  service.
- **Web data:** no WarpDrive models yet; every request is plain data with
  `SkipCache`, lists are read again after a change. `ApiError` lives in
  `utils/` so components can check it; services re-export API types for
  components; a `session-end` request handler sends a page whose session
  ended to log-in.
- **Dates on the web:** `formatDate` uses fixed month names (newer Chrome
  writes "Sept" in `en-GB`); the home's "today" comes from its time zone.
- **Dialogs:** the native `<dialog>` with `showModal()` (focus trap,
  Escape, focus return) through an `ember-modifier` function modifier.

## Decided in Phase 1b

- **Several homes per person:** a person can be an active member of any
  number of homes; each home has its own membership (name, role, status,
  stays, first log-in check). Sign-up, adding a member and reactivating no
  longer refuse someone active elsewhere; adding an active member of the
  same home is a 409.
- **Current home per request:** the client names the home in the
  `X-Colivo-Home` header (a home id); the session stays "who you are"
  (`person_id` in Redis). Chosen over the home in the session (one home for
  every tab sharing the cookie, so a form could save into the wrong home)
  and `/homes/{id}/…` paths (rewrites every endpoint). The mobile app will
  send the same header.
- **Dependencies:** `current_person` (cookie → session → a person with at
  least one active home, else 401) for endpoints that need no home
  (`/auth/log-out`, `/me/homes`); `current_membership` (person + header) for
  everything else, so `require_role` reads the role in the chosen home.
- **Header rules:** no header with one active home uses it; with several,
  409 `choose_home`; a home the person isn't active in, or one that doesn't
  exist, the same 403 `not_in_home`; a malformed id, 422. The refusal's
  shape, `HomeRefusalOut`, is declared once in OpenAPI, on `GET /me`.
- **Log-in answer:** `LogInOut` (`homes`, and `me` only for one home);
  `MeOut.homes` feeds the home switcher.
- **Per-tab home on the web:** `services/current-home.ts` keeps the tab's
  home in `sessionStorage` and the last home chosen in `localStorage` (where
  a new tab starts), every access in `try/catch`; the auth handler sends it
  through a getter, so `data/` never imports a service. Log-out forgets
  both. After being removed from the open home, the tab always goes to
  "Choose a home" with a notice.
- **CORS:** `X-Colivo-Home` is in the explicit `allow_headers` list.

## Decided in Phase 1c

- **A phone and an email per person:** either one logs in. The existing
  `person` CHECK (`phone IS NOT NULL OR email IS NOT NULL`) keeps the last
  one; a removal it refuses (two at once) answers the same 400 as the early
  check.
- **Every added or changed phone or email is proven with a code** sent to
  the new one, by the owner or a manager (`/members/{id}/contact…`) or by
  the person on My profile (`/me/contact…`). "Someone else logs in with
  that" is answered only after the right code, so the code request answers
  the same either way; the unique index catches two saves at once (409).
- **The other-home rule:** the owner or a manager can't change the log-in of
  a member who is in another home, active or past (403); only the person
  can, from My profile. Checked again on save and on remove, not only when
  the code is sent. Served by `ix_membership_person_id`.
- **Scoped code keys:** change codes live under
  `otp:change:{person_id}:{contact}` with their own wrong count and lock, so
  a change code can't log in and a log-in code can't confirm a change. The
  once-a-minute, 5-an-hour send limit (`otp:sent:{contact}`) is shared.
- **Ending sessions:** each session is listed in
  `person_sessions:{person_id}`. A change or removal ends all the person's
  sessions (owner or manager) or all but this browser's (My profile);
  adding one ends none. A session refresh writes only while the session
  still exists (`SET … XX`), so a request in flight can't bring an ended
  session back (B25, security review).
- **Notices:** an addition or change is sent to the existing phone or email
  (the new one partly hidden) and to the new one; a removal to the one
  removed. Every change is a `change_log` row in each of the person's homes.

## Project conventions

Every phase follows this layout. Update this section when a convention changes.

| Directory                                   | Holds                                                                                                                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `backend/app/main.py`                       | FastAPI app, middleware, exception handlers; `api_router` mounted at `/api/v1`                                                                                                             |
| `backend/app/api/api_v1.py`                 | Registers every module router; `deps.py` holds the log-in and role dependencies (`current_person`, `current_membership`, `require_role`, `OwnerDep`, `OwnerOrManagerDep`)                  |
| `backend/app/core/`                         | `config.py` (settings from env vars), `database.py` (engine, `get_session`), `router.py` (`CoreRouter`), `schemas.py` (`StandardResponse`), `exceptions.py` (error handlers), `utils.py`   |
| `backend/app/modules/<module>/`             | `models.py`, `schemas.py`, `service.py`, `router.py` per module: `accounts`, `homes`, `history`, `contacts`, `files`, `meals`, `groceries`, `payments`, `bills`, `statements`, `deposits`, `inbox`, `messaging` |
| `backend/app/utils/`                        | Shared helpers used by several modules                                                                                                                                                     |
| `backend/alembic/`, `backend/alembic.ini`   | Alembic migrations (`alembic/versions/`) and config                                                                                                                                        |
| `backend/tests/<module>/`                   | That module's tests                                                                                                                                                                        |
| `backend/pyproject.toml`, `backend/uv.lock` | Python dependencies (uv)                                                                                                                                                                   |
| `web/app/data/`                             | The whole web data layer: `config.ts`, `handlers/` (errors, auth, envelope), `builders/<resource>.ts`, `lifetimes.ts`, `types/api.generated.ts` (never edited by hand)                     |
| `web/app/models/`                           | WarpDrive Model classes, one per resource                                                                                                                                                  |
| `web/app/services/`                         | Store, session, current home                                                                                                                                                               |
| `web/app/routes/`, `web/app/templates/`     | Thin: load data, guard access, compose components; everything behind login under `authenticated/`                                                                                          |
| `web/app/components/ui/`                    | Domain-free design system (button, field, card, modal); the only place with Tailwind class lists                                                                                           |
| `web/app/components/layout/`                | Page shell, sidebar, navbar                                                                                                                                                                |
| `web/app/components/<feature>/`             | One folder per feature (`meals`, `groceries`, `payments`, …)                                                                                                                               |
| `web/app/utils/`                            | Pure functions, no Ember imports (money formatting, dates)                                                                                                                                 |
| `web/app/styles/app.css`                    | Tailwind import and `@theme` tokens from `colivo-design/README.md`                                                                                                                         |
| `web/tests/`                                | `unit/`, `integration/components/`, `acceptance/` (MSW), `helpers/` (`msw.ts`, `login.ts`, factories)                                                                                      |
| `web/e2e/`                                  | Playwright end-to-end journeys against the real backend                                                                                                                                    |
| `mobile/lib/features/<feature>/`            | Flutter screens, state and widgets per feature                                                                                                                                             |
| `mobile/lib/core/`                          | API client, auth, theme                                                                                                                                                                    |
| `mobile/test/`                              | Flutter tests                                                                                                                                                                              |
| `api/openapi.json`                          | Exported API contract — never edited by hand                                                                                                                                               |
| `infra/`                                    | Dockerfiles (`backend.Dockerfile`: `dev` and `prod` targets), the Postgres init script, deploy scripts; `compose.yaml` is at the repo root                                                 |
| `colivo-design/`                            | Screen designs and `requirements.md`                                                                                                                                                       |
| `specs/`                                    | Mission, roadmap, tech stack, testing, data model (`data-model.md`, the living schema) and one folder per phase                                                                            |

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
- Tables, columns and constraints follow [data-model.md](data-model.md);
  a schema change not agreed there is agreed with the user first. One
  migration per `plan.md` group; a migration merged to `main` is never edited.
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
- Web: event handlers on classes are `@action` methods (from `@ember/object`),
  as in the Ember guides; not arrow-function fields.
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

| Code | When                                         |
| ---- | -------------------------------------------- |
| 200  | GET, update or delete succeeded              |
| 201  | Create succeeded                             |
| 400  | Request breaks a business rule               |
| 401  | Not logged in                                |
| 403  | Logged in, but the role may not do this      |
| 404  | Not found, or belongs to another home        |
| 409  | Duplicate or conflicting change              |
| 422  | Input fails validation                       |
| 429  | Too many tries; `data` says how long to wait |
| 500  | Unexpected error                             |

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
- Run `make lint` and `make format-check` alongside the tests: Ruff and
  pyright (backend); ESLint, ember-template-lint, Stylelint, Glint and the
  Playwright files' type check (web); Ruff format and Prettier;
  `make backend-migrations-check` runs `alembic check`. Mobile adds
  `flutter analyze` and `dart format --set-exit-if-changed`.
- CI (`.github/workflows/ci.yml`) runs the same `make` targets, only for the
  parts that changed (everything on `main`); a pull request merges only when
  the `CI OK` check is green.

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

Add each one as it's discovered: **<Area>:** <limitation>.

- **End-to-end tests in CI:** not run there; they need the whole stack.
  `make test` runs them locally. Add to CI with the deploy work (Phase 9).
- **Base image:** `python:3.14-slim` carries Debian packages with known
  vulnerabilities. Rebuild on the latest base and scan images in CI
  (Phase 9).
- **Dev container:** has no test tools (`--no-dev`); run tests on the host
  (`make test-fast`), not with `docker compose exec backend pytest`.
- **Redis timeout:** the 2 s `socket_timeout` applies to every command; a
  future blocking command (e.g. a job queue) needs its own client.
- **OpenAPI wrapping:** `CoreRouter` relies on FastAPI merging a route's
  `responses` with its return model's schema; test T6.1 pins it.
- **Playwright on Fedora:** uses Playwright's fallback Ubuntu build of
  Chromium (Fedora isn't officially supported); fine for local runs.
- **Shell styling:** the app shell's Tailwind classes live in
  `components/layout/`, not only `components/ui/`.
- **No real SMS or email provider:** only the development notifier, so
  production can't start yet (B40); a provider is chosen by Phase 9.
- **Sessions in Redis:** flushing Redis logs everyone out (no data is lost).
- **Same site in production:** `SameSite=Lax` cookies need the web app and
  the API on one site (e.g. `app.` and `api.` of one domain), Phase 9.
- **No ID documents yet:** members are added without one until Phase 2's
  `attachment` (FR-60).
- **Anyone can be added to a home:** an owner or manager can add any phone
  or email; the person then sees that home in their list and gets an SMS.
  Nothing about them is revealed (security review, 23 Nov 2026).
- **Picker after every log-in:** a person in several homes always chooses
  after logging in; the last home is only where a new tab starts.
- **An owner or manager can take over a member in no other home:** they
  can add a phone or email they control (with its code) and log in as that
  member. The member is told on their existing phone or email. Members in
  another home are protected by the other-home rule (Phase 1c).
- **The read-only Edit tab hints at another home:** it tells the owner or a
  manager that a member is in some other home, though never which one
  (Phase 1c).
- **Sessions from before Phase 1c:** sessions are listed in
  `person_sessions` only when created or used, so one left unused across
  the Phase 1c deploy wouldn't be ended by a log-in change. Nothing is
  deployed yet (B40), so no action; a deploy that keeps old sessions would
  need a one-off backfill (security review, 23 Nov 2026).
- **Not test-driven, checked by hand:** countdowns ticking, layout at each
  width, focus after "Create my own home", the dialog's keyboard behaviour.

## Deferred decisions

- **Mobile project structure** (scaffold, layout and tooling for
  `mobile/`) — decide before the first phase tagged `[mobile]`.
- **Background jobs:** Celery + Redis recommended; FastAPI background tasks or
  ARQ are lighter alternatives.
- **Flutter state management** (Riverpod, Bloc, or other) — decide before
  Phase 10.
- **SMS provider** for one-time codes in Bangladesh, and the email provider.
- **Deployment target:** AWS (EC2 + RDS + S3) or another host — decide by
  Phase 9.
- **Error tracking and monitoring** — decide by Phase 9.
