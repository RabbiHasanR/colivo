# Changelog

All notable changes to Colivo, grouped by date (newest first).

## 2026-11-21

- In the specs, added the Phase 1 spec (accounts and log-in) and its data model: people, homes, memberships with their stays, and a change log.
- In the API, answered invalid input with a 422 in the standard envelope, naming each field.
- Added owner sign-up: it creates the home with a unique Home ID and makes the person signing up its owner, paying from the first month (this month or next, in the home's time zone) when they live there too; someone already in a home is told to log in instead.
- Added one-time codes by SMS or email, with the same answer for any phone or email; a phone in any form, or an email in any letter case, is one person.
- Added log-in sessions: a random token in an httpOnly cookie that other sites can't send, kept hashed in Redis for 30 days from its last use; everything but sign-up, codes and the health check needs a log-in, and log-out ends the session at once.
- Added the new-home setup checklist for the owner and managers, and empty lists that explain what will appear.
- On the web, added sign-up and the new home: the sign-up form and its errors, a greeting with the Home ID, the checklist, and log-out in the shell; log-in replaced the start page, and the web sends the session cookie instead of a bearer token.
- Added log-in with a one-time code, "Not added yet" for anyone active in no home, and code limits: a code works once for 5 minutes, five wrong codes lock the phone or email for 15 minutes, and a new code can be sent once a minute and five times an hour.
- On the web, added the log-in form with its code messages (tries left, expired, locked with a countdown, resend) and "Not added yet", which offers to create a home.
- Added a history of who changed what, kept for every change to a member.
- Added members: the owner or a manager adds a member by phone or email, who gets a notice; only the owner adds managers; names are unique among a home's active members; someone active in another home can't be added, and a past member is reactivated instead.
- Added changing a member's name and join date, and a first log-in check that shows a member where they were added and lets them fix their name.
- Fixed home scoping: another home's members are never found or changed.
- On the web, added the Members page for the owner and managers: the member list, adding and editing members, and the first log-in check.
- In CI, migrated the database before checking for missing migrations.
- Added roles and member status: the owner gives and takes away the Manager role (the owner's own role never changes; a home has one owner), and the owner or a manager deactivates a member from a date, logging them out at once, and reactivates them from the date charges start again.
- On the web, added current and past member tabs, the deactivate and reactivate dialogs, the owner's role editor, and sending a page whose session ended to log-in.
- Added an end-to-end test of the whole journey in two browsers: sign-up, adding a member who logs in, then deactivating them.
- After a security review, made reactivating a manager and changing the owner's details the owner's call only, and made production refuse to start with the development notifier, which logs one-time codes.
- In the specs, recorded Phase 1 as built (data model, tech stack, README), moved fund keepers to Phase 4, and planned Phase 1b, a person in several homes.
- Completed Phase 1 — Accounts and log-in.

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
