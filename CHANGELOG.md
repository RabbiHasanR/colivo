# Changelog

All notable changes to Colivo, grouped by date (newest first).

## 2026-11-23

- Allowed a person to be an active member of several homes: an owner or manager can add someone who is active elsewhere, someone already in a home can sign up for another, and a past member who joined another home can be reactivated; adding an active member of the same home again is refused ("Already a member of this home.").
- Each home sees only its own membership of a person (their name, role and dates there), and a change in one home leaves their other homes alone.
- On the web, reworded the sign-up note to say that someone already in a home can create their own.
- In the API, every home-scoped request names its home in an `X-Colivo-Home` header: log-in lists the person's homes and goes straight into the only one; `GET /me/homes` lists them for choosing; a request that names no home for someone in several is refused ("Choose a home") and changes nothing; naming a home they aren't in gives the same 403 whether or not it exists; log-out needs no home; roles are checked in the chosen home; the web app's origin may send the header.
- On the web, a person in several homes picks one on "Choose a home" after log-in and switches from the home name in the sidebar or the phone top bar; each tab keeps its own home and a new tab starts in the last one chosen; log-out forgets it; signing up opens the new home; being removed from the open home shows "Choose a home" with "You're no longer a member of …".
- Added `make web-screens` shots of the "Create a home" tab, "Choose a home" and the home menu, and an end-to-end journey where Rabbi, added to two homes, chooses one, switches in a second tab and is told when one removes him.
- Ran the security review of Phase 1b and of Phase 1's 22 Nov web changes: no findings.
- Completed Phase 1b — A person in several homes.
- In the specs, added the Phase 1c spec (change a member's phone or email): a person can have a phone and an email, every new one is confirmed with a code sent to it, and a change ends their other sessions.
- In the API, the owner or a manager can add, change or remove a member's phone or email: a code goes to the new one and the change is saved once it is typed; the last way to log in can't be removed ("They need a phone or an email to log in."); a phone or email someone else logs in with is refused only after the right code; the one they already have is refused; a wrong code changes nothing.
- In the API, only the person can change a log-in they also use in another home, now or in the past ("Only they can change their log-in, from My profile."); a manager can't change the owner's; another home's member is not found; a past member must be reactivated first.
- In the API, codes for a change are kept apart from log-in codes, so neither works as the other; changing or removing a member's phone or email logs them out everywhere; they are told on their old and new phone or email; every change is kept in the home's history; two saves of the same new phone or email at once give one a "taken" answer.
- On the web, the members' Edit tab adds, changes and removes a phone or email with a code, offers a code only for a new one, explains each refusal, and shows the log-in read-only for a member who is also in another home or has left.
- Added My profile, opened from your name in the sidebar: it shows your name, role, "member since", phone and email; you fix your name for this home, and add, change or remove your own phone or email with a code, without choosing a home; a change applies to every home you are in and keeps this browser logged in while your other sessions end.
- Added an end-to-end journey where the owner adds a member's email and the member changes their own phone on My profile.
- Fixed from the manual check: the phone or email field lost focus while typing; My profile showed an old phone after a change on Members; removing both at the same moment answered 500 instead of 400; a refused name on My profile showed no message. Send code and Remove now sit beside the field.
- Fixed from the Phase 1c security review: a request in flight could bring back a session that a log-in change had just ended.
- Completed Phase 1c — Change a member's phone or email.

## 2026-11-22

- On the web, restyled every Phase 1 screen to match colivo-design: form controls, buttons and cards; the sidebar with icons, the current page in teal and a profile card with initials; the home page with its header, four stat cards (empty until their phases) and the setup checklist with a progress bar; Members & roles with role and status pills; and log-in with its brand panel, card forms and styled code errors.
- On the web, the home page's header names the current month in the home's time zone; "Start ›" on "Add members" and an "Add members" button on the empty meals card open Members for the owner and managers.
- On the web, log-in and sign-up became two tabs; "Send code" sits beside the code box and "Log in" waits until a code is sent; a wrong or expired code marks the box invalid.
- On the web, drew the taka sign with Noto Sans Bengali, which Inter and Space Grotesk lack.
- In the roadmap, planned Phase 1c: changing a member's phone or email.
- On the web, Members has one add-or-edit card: Edit opens an "Edit <name>" tab with Cancel, and you can switch back to adding; editing another member now starts from their own details instead of what was typed for the last one.
- In the requirements, removing the Manager role is blocked while that person holds fund cash or has money waiting for their confirmation (FR-104, built in Phase 4).
- On the web, a manager who lost the role is sent home on their next action, and the Members link disappears.
- In the specs, log-in codes are read from the development outbox in Redis; ID documents and profile photos are planned as Phase 2's last group, the ID optional when adding (FR-60) and the photo settable by the owner or a manager too (FR-86).
- In the project rules, every phase follows colivo-design for web and mobile, with each difference agreed and listed in the phase's Screens table; recorded Phase 1's agreed differences.
- Added `make web-screens`, which saves every page at 390px and 1440px with sample data to compare with the design; it found and fixed the members table widening the page on phones.
- Deferred the security review of the 22 Nov web changes to Phase 1b.
- In the specs, added the Phase 1b spec (a person in several homes): one person can be active in several homes, and each request names its home in a header, so each browser tab keeps its own home.

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
