# Changelog

All notable changes to Colivo, grouped by date (newest first).

## 2026-11-20

- In the API, answered unknown paths with a 404 and unexpected errors with a generic 500, both in the standard envelope, and never with internal details.
- In the API contract, described every response inside the standard envelope, so the web's generated types match what the API sends.
- Allowed only the web app's address to call the API from a browser (CORS).
- Added a healthcheck to the backend container.
- On the web, added the data layer: it reads the data out of the API envelope, turns API errors into plain errors by kind, and sends the session token as a bearer token.
- On the web, added the Colivo app shell, with a menu button below 1024px, and a start page that shows whether the server is connected.
- Added an end-to-end test that opens the web app against the real backend.
- Added CI on GitHub Actions: one workflow that checks only the parts a change touches, everything on `main`, with a single required `CI OK` check; branches are checked through their pull request.
- Built slim backend images in stages: a dev image with auto-reload and a non-root production image, down from 439 MB to 213 MB.
- Moved the backend to Python 3.14, so UUIDv7 keys come from the standard library.
- Made the backend and web tests fail on deprecation warnings.
- Applied a baseline documentation check: end-to-end runs in CI always start a fresh web server, and the API envelope's OpenAPI wiring is documented.
- On the web, adopted `@action` for component event handlers as the project convention.
- Required the owner's review on every change (`CODEOWNERS`).
- In the specs, recorded Phase 0's decisions and known limitations, and in the design named Ember as the web front end.
- Completed Phase 0 — Project skeleton.
- Added the project README.

## 2026-11-19

- Added meal sessions and meal confirmation to the design, data model, scope, roadmap, and mobile and web screens.
- Added home contacts to the design, data model, and mobile and web screens.
- Added a fund kind to the data model.
- Added the `/changelog` skill and a rule to run it before every merge.
- Added the `/tdd` skill for building each roadmap phase test-first, one plan group at a time.
- In the specs, agreed the domain sketch for every phase and the schema conventions: UUIDv7 keys, text and `CHECK` value sets, singular table names, effective-dated rows and one change log.
- Added the Phase 0 (project skeleton) spec: requirements, plan and validation.
- Added the monorepo groundwork: Docker Compose with PostgreSQL 16 and Redis 7, a separate test database, the root Makefile and `.env.example`.
- Scaffolded the FastAPI backend with uv and Alembic, with tests that rebuild the test database and roll back every test.
- Scaffolded the Ember web app with TypeScript, WarpDrive, Tailwind CSS v4, MSW and Playwright.
- In the API, added a health check that reports the database and Redis, answers 503 when either is down, and gives up on an unreachable one after 2 seconds.

## 2026-11-17

- Adopted an outside-in TDD workflow in `specs/testing.md`, with review gates for behaviours and test cases.
- Adopted the ember-scaffold web layout, split the test settings into backend and web, and set the per-group build order: backend, contract, web.
- Added a data-model gate to `/feature-spec` and the living schema in `specs/data-model.md`.
- Added returns, exchanges and member corrections, with refunds counted only after the member confirms receipt, to the design, scope, roadmap, and mobile and web screens.
- Decided ledger money storage: balances are computed from entries, confirmed entries are never edited, and corrections are new linked entries.
- Tracked fund cash per holder, with several managers and fund keepers, cash handovers, and receiver confirmation of every payment, in the design, data model, scope, roadmap, and mobile and web screens.

## 2026-11-16

- Added the `/feature-spec` skill for writing roadmap phase specs.
- Adopted the fastapi-orm-scaffold backend layout (SQLModel, Alembic, uv) with the `StandardResponse` API format, and narrowed Phase 0 to backend and infra.

## 2026-11-14

- Added carry-forward, estimated bills and split funding rules to the requirements, and extended prior-month import to fund cash and unpaid bills.
- Added estimates, carry-forward and split funding to the design screens, and aligned the grocery fund display and October status.
- Added estimates, carry-forward and split funding to the specs.
- Pointed the tech-stack design paths to `colivo-design`.

## 2026-11-13

- Added the Colivo design reference.
- Added the specs scaffold: mission, roadmap and tech stack.
- Renamed the requirements title to Colivo.
