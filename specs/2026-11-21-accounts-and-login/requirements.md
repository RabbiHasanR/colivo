# Phase 1 — Accounts and Log-in: Requirements

## Context

Phase 1 is the second phase in the [roadmap](../roadmap.md). Phase 0
delivered the skeleton: the FastAPI backend with the `StandardResponse`
envelope and a health check, the Ember web app with its data layer and
shell, the test harness for both parts, the API contract pipeline and CI.
There are no tables yet.

This phase creates the first ones. After it, an owner can sign up, which
creates a **home**; the owner and managers add **members** by phone or
email; anyone added logs in with a one-time code. It serves the
[mission](../mission.md)'s first two promises ("an owner signs up, which
creates their home, and adds members by phone or email"; "anyone logs in
with a phone or email and a one-time code") and is the base for every later
phase: each later query is scoped to the home and each write checks the role
set here.

It also settles the **Auth tokens** [deferred decision](../tech-stack.md#deferred-decisions):
an httpOnly cookie session, stored in Redis.

Design references (layout by eye, behaviour from
`colivo-design/requirements.md`):

- `colivo-design/web/WebAuth.html`: log in or create a home.
- `colivo-design/web/WebAuthErrors.html`: wrong code, expired code, locked,
  resent.
- `colivo-design/mobile/Login.html`: the first log-in check ("You were added
  to Our Flat") and "Not added yet" (the web uses the same wording, FR-97).
- `colivo-design/web/WebHomeEmpty.html`: the new home with its setup
  checklist and empty states; `colivo-design/mobile/EmptyStates.html` for
  the empty-state pattern.
- `colivo-design/web/WebMembers.html`: Members & roles (current and past,
  add a member, roles, deactivate).

## Scope

**In scope**

- Owner sign-up: name, phone or email, a 6-digit code, home name, optional
  area, first month and "I live here too"; creates the home, its Home ID and
  the owner's membership (FR-83, FR-88).
- One-time codes by SMS or email: 5-minute life, lock after 5 wrong codes
  for 15 minutes, a new code once a minute and 5 an hour (FR-94).
- Log-in with a phone or email and a code; "Not added yet" for anyone with
  no active membership (FR-84, FR-87); log-out.
- Session in an httpOnly cookie, kept in Redis, membership checked on every
  request.
- The new-home page: setup checklist for the owner and managers, empty
  states for everyone (FR-95).
- Members & roles: add a member by phone or email with an SMS or email
  notice (FR-79), change a member's name and join date, the first log-in
  check (FR-86).
- Roles: the owner gives and removes the Manager role (FR-62–FR-64).
- Deactivate and reactivate a member with a date (FR-80, FR-92).
- History of every change to a member in `change_log` (FR-27).
- Every page above is responsive
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).

**Out of scope**

- **Fund keepers:** moved to Phase 4, where the `fund` table and fund cash
  arrive. A fund keeper can do nothing until funds hold cash, and `fund` and
  `fund_keeper` are better designed with the ledger. The roadmap is updated
  in Verify.
- **Profile photo, ID documents and every file upload:** Phase 2, with the
  `attachment` table and S3 presigned uploads
  ([data-model.md → Files](../data-model.md#files-s3-and-presigned-urls-agreed-21-nov-2026)).
  Members are added without an ID document for now (FR-60).
- Rooms, so the first log-in check shows no room (Phase 2).
- Home rules, deposits and notice (Phases 2 and 7); the `notice_served`
  membership status (Phase 7).
- The `month` table and the "Month starts on 1st / 5th / 10th" choice in
  `colivo-design/mobile/SignUp.html`; months start on the 1st.
- Editing your own phone or email, Home settings, the profile page beyond
  log-out.
- Transferring ownership (FR-63's hand-over; out of v1 scope in the
  roadmap).
- A real SMS or email provider (still a Deferred decision); Phase 1 uses a
  development notifier.
- Bearer tokens for the mobile app (Phase 10 sends the same session token in
  a header).
- KPI cards on the new-home page (they come with their phases).

## Features

### Owner sign-up

Who: anyone who is not active in a home.

- Sign-up is for the person who runs the home (FR-83). They enter their
  name and phone or email, ask for a code, enter it with the home name,
  optional area, first month and "I live here too and pay my share".
- The home and the owner's membership are created in one transaction, and
  the owner is logged in.
- The first month is the current month or the next one (the two choices on
  `WebAuth.html`), in the home's time zone (Asia/Dhaka).
- "I live here too" gives the owner a membership period from the first
  month, so they are charged like any member from then on; without it the
  owner runs the home and has no period (never charged).
- Each home gets a short Home ID: two letters from the home name and four
  random digits, unique (FR-88). Shown on the new-home page, for support;
  nobody types it.
- A phone or email that is active in another home can't sign up: "If your
  number is already in a home, log in instead" (FR-85). A person who is no
  longer active anywhere can.

### One-time codes

Who: anyone, before logging in.

- A code is 6 digits, sent by SMS to a phone or by email to an email
  address, and works for 5 minutes (FR-94).
- A phone is accepted in local (`01712 345678`) or international form and
  stored in E.164 (`+8801712345678`); an email is stored in lower case.
- Asking for a code always answers the same way, whether or not the phone
  or email belongs to anyone, so nobody can find out who uses Colivo.
- A wrong code says how many tries are left; after 5 wrong codes the phone
  or email is locked for 15 minutes ("Too many wrong codes … try again in
  14:52").
- A new code can be sent once a minute, up to 5 an hour; the new code
  replaces the old one ("New code sent … The old one no longer works").
- A code is used once.

### Log-in and session

Who: anyone with an active membership.

- A person logs in with the phone or email the owner or a manager added
  them with, and a code; no home code is needed (FR-84). In the MVP a person
  has at most one active membership, so the log-in goes straight to it.
- No active membership (never added, or deactivated): "Not added yet",
  with two choices: ask the home's owner or manager, or create a new home
  (FR-87).
- The session is a random token in an httpOnly, `SameSite=Lax` cookie
  (`Secure` outside development). Only its SHA-256 hash is stored, in Redis,
  for 30 days from the last use.
- Every request reads the membership from PostgreSQL, so a deactivated
  member is logged out at once (FR-80).
- Log-out ends the session at once.

### New home

Who: everyone logged in; the checklist is for the owner and managers.

- The home page greets the person and shows the home name.
- The owner and managers see the setup checklist (FR-95): "Home created"
  (done), "Add members" (done once anyone besides the owner is active), and
  rooms and rent, home rules and bills (not done; their pages come in
  Phase 2).
- Members don't get the checklist.
- Lists with nothing in them show a short reason and, where it helps, the
  one action that fills them (`EmptyStates.html`): "Today's meals: only you
  so far", "All caught up".

### Members

Who: the owner and managers. Members can't see the members list in Phase 1.

- Add a member: name, phone or email, join date, and role (FR-79). The
  member gets an SMS or email saying they were added and can log in. The
  owner can add a member as a manager; a manager adds members only (FR-64).
- A phone or email active in another home can't be added (FR-85).
- Someone who is a deactivated member of this home can't be added again;
  they are reactivated instead.
- Names are unique among a home's active members, ignoring letter case
  (FR-04).
- The owner or a manager changes a member's name and join date (FR-86).
- First log-in check (FR-86): a member's first log-in shows the home, their
  role, their join date and who added them; they can fix their name, then go
  to their home. After that they go straight to their home. The room or join
  date can only be changed by the owner or a manager.
- The list shows current (active) and past (deactivated) members on two tabs.
- Every change to a member is kept in `change_log`: who, when, old and new
  values (FR-27).

### Roles

Who: the owner.

- Everyone is a member; the owner makes a member a manager and takes the
  role away (FR-62, FR-63). A home can have any number of managers.
- A manager can't make someone a manager (FR-64).
- The owner's own role can't change; a home always has exactly one owner
  (FR-63).

### Deactivate and reactivate

Who: the owner and managers.

- Deactivating asks for confirmation and the date it starts (FR-92): today
  or earlier, not before the start of the member's current stay. The member
  can't log in from that moment.
- Reactivating asks for the date charges start again: after the date they
  were deactivated. The member can log in again.
- The owner can't be deactivated. A manager can deactivate members, but
  not other managers or the owner.
- Reactivating is refused if the member is active in another home now
  (FR-85), or if another active member has the same name.
- The "can't deactivate someone holding fund cash" rule (FR-80) starts in
  Phase 4, when cash exists.

## API

All responses use the `StandardResponse` envelope
([tech-stack.md → API response format](../tech-stack.md#api-response-format)).
"Logged in" means a valid session cookie with an active membership;
otherwise 401. 404 also covers a member of another home, which is never
shown.

| Method | Path                              | Role           | Request                                                              | Response                                                                                                                                                                                       |
| ------ | --------------------------------- | -------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/v1/auth/codes`              | None           | `{ contact }` (phone or email)                                       | 200 `CodeSentOut` (`channel`, `expires_in_seconds`, `resend_in_seconds`), same for any contact. 422 not a phone or email. 429 resend too soon, hourly limit or locked (`retry_in_seconds`)     |
| POST   | `/api/v1/auth/sign-up`            | None           | `{ contact, code, name, home_name, area?, first_month, lives_here }` | 201 `MeOut` and the session cookie. 400 wrong code (tries left), expired code, or first month not this month or next. 409 active in another home. 422. 429 locked                              |
| POST   | `/api/v1/auth/log-in`             | None           | `{ contact, code }`                                                  | 200 `MeOut` and the session cookie. 400 wrong or expired code. 404 "Not added yet" (no active membership). 422. 429 locked                                                                     |
| POST   | `/api/v1/auth/log-out`            | Logged in      | —                                                                    | 200; session ended and cookie cleared                                                                                                                                                          |
| GET    | `/api/v1/me`                      | Logged in      | —                                                                    | 200 `MeOut`: `person` (`phone`, `email`), `membership` (`id`, `name`, `role`, `status`, `joined_on`, `added_by_name`, `details_checked`), `home` (`id`, `code`, `name`, `area`, `first_month`) |
| PATCH  | `/api/v1/me`                      | Logged in      | `{ name }`                                                           | 200 `MeOut`; also marks the first log-in check done. 409 name taken. 422                                                                                                                       |
| GET    | `/api/v1/home/setup`              | Owner, manager | —                                                                    | 200 `SetupOut`: `steps` (`key`, `done`). 403 member                                                                                                                                            |
| GET    | `/api/v1/members`                 | Owner, manager | `?status=active\|inactive`                                           | 200 `list[MemberOut]` (`id`, `name`, `phone`, `email`, `role`, `status`, `joined_on`, `active_since`, `inactive_since`). 403 member                                                            |
| POST   | `/api/v1/members`                 | Owner, manager | `{ name, contact, joined_on, role }` (`role`: `member` or `manager`) | 201 `MemberOut`; notice sent. 403 manager adding a manager, or a member. 409 active in another home, already in this home, or name taken. 422                                                  |
| PATCH  | `/api/v1/members/{id}`            | Owner, manager | `{ name?, joined_on? }`                                              | 200 `MemberOut`. 400 join date after the end of their first stay. 403. 404. 409 name taken. 422                                                                                                |
| PUT    | `/api/v1/members/{id}/role`       | Owner          | `{ role }` (`member` or `manager`)                                   | 200 `MemberOut`. 400 the owner's own role. 403 not the owner. 404. 422                                                                                                                         |
| POST   | `/api/v1/members/{id}/deactivate` | Owner, manager | `{ on, reason? }`                                                    | 200 `MemberOut`. 400 the owner, a date in the future or before their current stay. 403 manager deactivating a manager. 404. 409 already inactive. 422                                          |
| POST   | `/api/v1/members/{id}/reactivate` | Owner, manager | `{ on }`                                                             | 200 `MemberOut`. 400 date not after the deactivation date. 403. 404. 409 already active, active in another home, or name taken. 422                                                            |

`joined_on` is the start of the member's first period. `MeOut` and
`MemberOut` never include another home's data.

Redis keys (no tables): `otp:<contact>` (code hash, expiry, wrong tries),
`otp:lock:<contact>` (15 minutes), `otp:sent:<contact>` (send times in the
last hour), `session:<sha256(token)>` (`person_id`, 30-day sliding TTL).
Expiry and lock times are checked against the app's clock, not only Redis
TTLs, so tests can move time.

## Data model changes

The first tables. Full columns, indexes and the ER diagram are in
[data-model.md](../data-model.md#tables); this is the delta.

| Table               | Change                                                                                                                     | Group and migration        |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| `person`            | New: `phone`, `email` (log-in identity only)                                                                               | 2 · `<rev>_sign_up.py`     |
| `home`              | New: `code`, `name`, `area`, `first_month`, `time_zone`                                                                    | 2 · `<rev>_sign_up.py`     |
| `membership`        | New: `home_id`, `person_id`, `name`, `role`, `status`                                                                      | 2 · `<rev>_sign_up.py`     |
| `membership_period` | New: `membership_id`, `starts_on`, `ends_on`                                                                               | 2 · `<rev>_sign_up.py`     |
| `membership`        | Add `created_by` (who added them) and `details_checked_at` (first log-in check)                                            | 4 · `<rev>_add_members.py` |
| `change_log`        | New: `changed_by`, `entity`, `entity_id`, `action`, `old_values`, `new_values`, `reason`                                   | 4 · `<rev>_add_members.py` |
| —                   | Shared SQLModel base: UUIDv7 `id`, snake_case `__tablename__`, `created_at` / `updated_at`, the `StrEnum` → `CHECK` helper | 2 (with the first table)   |

Group 3 (log-in) and group 5 (roles, deactivate) have no migration: codes
and sessions live in Redis, and group 5 uses existing columns.

Contested choices, agreed at Gate 0 (21 Nov 2026):

- **The member's name is on `membership`, not `person`.** Each home names
  its own member, and "unique among a home's active members" (FR-04) is a
  database index. On `person`, the rule could only be checked in the
  service. `person` holds only phone and email.
- **Active stretches are `membership_period` rows.** The join date is the
  first period's start; "I live here too" means the owner has a period.
  Statement phases can ask "who lived here in October" without reading
  history. Rejected: date columns on `membership` (overwritten by a second
  deactivation) and status plus `change_log` (as-of queries would parse
  `jsonb`).
- **Sessions in Redis**, not a `session` table: codes and lockouts are
  already there, TTLs are native, and losing Redis only logs people out.
- **`home.first_month` instead of a `month` table now:** `month` arrives
  with meals in Phase 3, seeded from this column.
- **`change_log.changed_by` points to `membership`**, not `person`: every
  change is made inside a home.
- **Who made a record:** `created_by` only where the record needs it
  (`membership` now; `attachment` and `entry` later), no `updated_by`
  anywhere: `change_log` keeps every change, and `updated_by` would keep
  only the last.

## Decisions

| Decision                      | Choice                                                                                                                                     | Why                                                                                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scope                         | Sign-up and log-in, members and roles, new-home checklist; fund keepers moved to Phase 4                                                   | User's choice. A fund keeper has nothing to do until funds hold cash; `fund` is designed with the ledger                                                |
| Groups                        | Groundwork → sign-up and session → log-in → add members → roles and status → verify                                                        | User's choice (thinnest journey first). Each group is demoable                                                                                          |
| Merge bar                     | The usual gate, CI green, and a `/security-review` of the branch                                                                           | User's choice. The first phase with auth, codes, cookies and home scoping                                                                               |
| Auth tokens                   | Opaque random token in an httpOnly, `SameSite=Lax` cookie (`Secure` outside development); SHA-256 hash in Redis, 30 days from the last use | User's choice. Scripts can't read it (XSS), and the server can end it at once. Mobile sends the same token as a bearer header in Phase 10               |
| Data model                    | As in [Data model changes](#data-model-changes)                                                                                            | Agreed at Gate 0                                                                                                                                        |
| Actor column names            | `created_by`, `changed_by` (and the planned `confirmed_by`): foreign keys to `membership` without the `_id` suffix                         | User's choice; matches `confirmed_by` already in the meals decision                                                                                     |
| Profile photo and files       | Phase 2; `membership.photo_id` → `attachment`, uploads through S3 presigned POST                                                           | Agreed at Gate 0. Designed once with all the attachment's users (contacts, lease, receipts)                                                             |
| CSRF                          | `SameSite=Lax` cookie, JSON-only request bodies and the CORS allow-list with credentials                                                   | A cross-site page can't send the cookie on a POST, and a JSON body forces a CORS pre-flight that only `BACKEND_CORS_ORIGINS` passes                     |
| Production hosting            | Web and API on the same site (e.g. `app.` and `api.` of one domain)                                                                        | `SameSite=Lax` cookies need it; recorded for Phase 9                                                                                                    |
| Account enumeration           | Asking for a code answers the same for every contact; "Not added yet" only after a correct code                                            | Follows `Login.html` (the "not added" step comes after the code) and stops anyone from listing who uses Colivo                                          |
| Deactivated person logging in | Same "Not added yet" answer as someone never added                                                                                         | FR-87 offers the same two choices (ask the home, or create a home, FR-85); one answer, one test                                                         |
| Sign-up in one request        | `POST /auth/sign-up` takes the code and the home details together                                                                          | `WebAuth.html` collects everything in one form; no half-made sign-up state to store                                                                     |
| "Not added yet" → create home | The sign-up form opens with the contact filled in; a new code is asked for                                                                 | The log-in code was used; keeping a "verified" marker would add a second kind of state for a rare path                                                  |
| Code numbers                  | 5 minutes, 5 tries, 15-minute lock, 1 a minute, 5 an hour are constants in `accounts/constants.py`, not env vars                           | They are business rules (FR-94), the same for every deployment                                                                                          |
| Time in tests                 | An injectable clock (`app/core/clock.py`); expiry and lock times are compared with it                                                      | Tests can move time without waiting 15 minutes, and without a time-freezing dependency                                                                  |
| Sending SMS and email         | A `Notifier` protocol; Phase 1 has only a development notifier that logs each message and pushes it to a Redis list, `dev:outbox`          | No provider is chosen yet; the end-to-end test reads the code from `dev:outbox`. Backend tests replace the notifier (an external service may be mocked) |
| Phone and email checks        | `phonenumbers` for parsing to E.164 (Bangladesh as the default region); Pydantic `EmailStr` (`email-validator`)                            | Proven libraries; a hand-made phone regex would break for other countries ("worldwide use later")                                                       |
| Home ID                       | Two letters from the home name's first words (padded with `X`), a dash, four random digits; unique; retried on a clash                     | Matches `OF-4827` for "Our Flat" (FR-88)                                                                                                                |
| Who sees the members list     | Owner and managers only in Phase 1                                                                                                         | Members' phones and emails stay with the owner and managers; a members' view of names comes with the meal grid                                          |
| Manager deactivating          | A manager deactivates members, not other managers or the owner                                                                             | A manager can't make managers (FR-64), so removing one is the owner's call too                                                                          |
| Deactivation date             | Today or earlier; log-in stops at once                                                                                                     | Leaving later is notice and final settlement (Phase 7); a future date would need a job to flip the status                                               |
| `change_log` module           | `backend/app/modules/history/` (`models.py`, `service.py` with one `record_change` function)                                               | Every later module writes to it; Phase 8's history screens live there too                                                                               |
| Start page                    | The Phase 0 start page goes; `/` sends you to your home or to log-in. Its acceptance test and the smoke end-to-end test are rewritten      | Phase 0 said Phase 1 replaces it. Changing existing tests is asked for at Gate 2 of group 2                                                             |
| 429 status                    | Added to the status table for "too many tries"                                                                                             | FR-94 limits; the web shows the wait time from `retry_in_seconds`                                                                                       |

## Constraints

- Follow [tech-stack.md → Project conventions](../tech-stack.md#project-conventions):
  `CoreRouter` only, `set_response_message` on every endpoint, business rules
  in `service.py`, roles checked in the router, config only through
  `app.core.config.settings`.
- Fetch current docs with `ctx7` for every library this phase touches
  (FastAPI, Pydantic, SQLModel, SQLAlchemy, Alembic, redis-py,
  `phonenumbers`, `email-validator`, Ember, WarpDrive, Tailwind CSS, MSW,
  Playwright) before coding, at the installed version.
- Every behaviour is built test-first, as in [testing.md](../testing.md).
- The schema follows [data-model.md](../data-model.md); a change to it is
  agreed with the user first.
- Money is `Decimal`, never float, and every money change is one database
  transaction (no money yet; sign-up and every member change are one
  transaction with their `change_log` row).
- Every query is scoped to the current home, and roles are checked in the
  router.
- Nothing is erased: members are deactivated, never deleted, and every
  change keeps history in `change_log`.
- `api/openapi.json` is exported and the web types regenerated
  (`make api-types`) after any endpoint change; the mobile client comes with
  the first `[mobile]` phase.
- Config comes from env vars, with `.env.example` updated and no secrets
  committed.
- Alembic migrations apply cleanly to the Phase 0 database (no revisions).
- Codes and session tokens are never logged or stored in plain text,
  except the development notifier's messages in development.
- Every dependency added is named in [plan.md](plan.md); anything beyond it
  is asked first.
