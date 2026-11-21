# Phase 1 — Accounts and Log-in: Plan

Branch: `phase-1-accounts-and-login`, pushed early with a draft pull request.

Each group is built with `/tdd` as in
[testing.md → Build time](../testing.md#build-time-tdd-one-planmd-group-per-run):
Gate 2 on `tests.md`, then backend → contract → web, one test at a time.
Group 1 is groundwork (no **Behaviours:** line): no tests, one commit, then
stop for review.

Per-behaviour gate: `make test-fast`, `make lint` and `make format-check`
green, then a conventional commit (e.g. `feat(accounts): lock log-in after 5
wrong codes`, `feat(web): show locked log-in message`) with no
Co-Authored-By or AI attribution lines.

## 1. Groundwork

Configuration and docs only. Commit: `chore: add phase 1 groundwork`.

- Fetch current docs with `ctx7`, at the installed versions: FastAPI
  (cookies on `Response`, `Request.cookies`, dependencies with `Security`,
  CORS with credentials), Pydantic v2 (`EmailStr`, `field_validator`),
  SQLModel and SQLAlchemy 2.0 (partial unique indexes with
  `postgresql_where`, functional indexes on `lower(name)`, `CheckConstraint`,
  `jsonb`), Alembic (autogenerate of partial and functional indexes),
  redis-py (pipelines, `SET` with `EX`/`NX`, sorted sets), `phonenumbers`
  (parse, E.164 format), Ember (router service, `beforeModel` guards),
  WarpDrive (`credentials` on requests), MSW (cookies, `HttpResponse`
  headers), Playwright (reading a value from a shell command).
- Ask before adding, then add backend dependencies: `phonenumbers`,
  `email-validator`. No new web dependency.
- `backend/app/core/config.py` and `.env.example`:
  `SESSION_COOKIE_SECURE` (false in development), `NOTIFIER` (`log` only for
  now). Cookie name and the FR-94 numbers are constants, not settings.
- `backend/app/core/clock.py`: `now()` behind a FastAPI dependency, so tests
  move time.
- `backend/app/main.py`: CORS `allow_credentials=True` (the allow-list is
  already explicit).
- `backend/app/modules/{accounts,homes,history}/__init__.py`, and empty
  routers for `accounts` and `homes` registered in
  `backend/app/api/api_v1.py`.
- Check: `make test-fast`, `make lint`, `make format-check` still green.

## 2. Sign-up and session (slice 1)

- **Behaviours:** B1–B8, B14–B19. B17's "Add members done" case is tested in
  group 4, once members can be added.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_owner_signs_up_and_home_is_created`.
  - Web: `web/tests/acceptance/sign-up-test.ts` › owner creates a home and
    lands on the new-home page.
- **Tables:** `person`, `home`, `membership` (without `created_by` and
  `details_checked_at`), `membership_period`, as in
  [data-model.md](../data-model.md#tables); migration
  `backend/alembic/versions/<rev>_sign_up.py`.

### Backend

- `backend/app/core/models.py`: the shared base (UUIDv7 `id` from
  `uuid.uuid7()`, snake_case `__tablename__`, `created_at` / `updated_at` set
  by the database) and the `StrEnum` → `CHECK` helper; a test compares each
  check with its enum.
- `backend/app/core/notifier.py`: the `Notifier` protocol and the
  development notifier (log line plus the `dev:outbox` Redis list);
  `get_notifier` dependency, replaced by a fake in tests.
- `backend/app/modules/accounts/`:
  - `constants.py`: code length, life, tries, lock, resend limits, session
    life, cookie name.
  - `models.py`: `Person`, `Membership`, `MembershipPeriod`; `Role`,
    `MembershipStatus` enums.
  - `schemas.py`: `ContactIn` (phone or email, normalised), `CodeRequestIn`,
    `CodeSentOut`, `SignUpIn`, `MeOut`.
  - `codes.py`: issue, check and use codes in Redis (hashes, expiry,
    tries, lock, send limits) with the clock.
  - `sessions.py`: create, read (sliding 30 days), end; token hashed with
    SHA-256.
  - `service.py`: `request_code`, `sign_up` (person, home, membership,
    owner's period when `lives_here`, in one transaction), `get_me`.
  - `deps.py` joins `backend/app/api/`: `current_membership` (cookie →
    session → active membership, else 401) and `require_role(...)`.
  - `router.py`: `POST /auth/codes`, `POST /auth/sign-up`,
    `POST /auth/log-out`, `GET /me`; cookie set and cleared here.
- `backend/app/modules/homes/`:
  - `models.py`: `Home`; `service.py`: Home ID generation, `get_setup`
    (checklist steps); `schemas.py`: `SetupOut`; `router.py`:
    `GET /home/setup`.
- `backend/alembic/env.py`: import the new models; the group's migration.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`,
  `backend/tests/homes/{test_service,test_api}.py`,
  `backend/tests/core/test_models.py` (enum ↔ check);
  `backend/tests/conftest.py` gains Redis clean-up per test, the fake
  notifier, a movable clock and an `owner` fixture that signs up.

### Contract

- `make api-export` → `api/openapi.json`; `make api-types`. Commit
  `chore(api): update contract for sign-up and session`.

### Web

- `web/app/data/handlers/auth.ts`: send cookies (`credentials: 'include'`)
  instead of a bearer token; on 401 tell the session service.
- `web/app/services/session.ts`: the current person, membership and home
  from `GET /me`; `load()`, `logOut()`, `isOwnerOrManager`.
- `web/app/data/builders/{auth,me,home}.ts`.
- `web/app/utils/{contact,months}.ts`: what a typed contact looks like
  (phone or email), the first-month choices and their labels.
- Routes and templates: `web/app/routes/{index,log-in}.ts`,
  `web/app/templates/log-in.gts` (the "Create your home" side of
  `WebAuth.html` in this group), `web/app/routes/authenticated.ts` (guard:
  load the session, else go to `log-in`),
  `web/app/routes/authenticated/index.ts` and
  `web/app/templates/authenticated/index.gts` (new home). The Phase 0 start
  page, `components/health/server-status.gts`'s route use, and their
  acceptance test are replaced; asked at Gate 2.
- Components: `web/app/components/auth/{sign-up-form,code-field}.gts`,
  `web/app/components/home/{welcome,setup-checklist,empty-state}.gts`;
  `web/app/components/layout/app-shell.gts` gains the signed-in person, their
  roles and Log out; `web/app/components/ui/{field,text-input,checkbox}.gts`
  (fields repeat on every form from here on).
- Tests: `web/tests/unit/data/builders-test.ts`,
  `web/tests/unit/utils/{contact,months}-test.ts`,
  `web/tests/integration/components/{auth,home,ui}/…`,
  `web/tests/acceptance/sign-up-test.ts`; `web/tests/helpers/login.ts`
  (an MSW session for acceptance tests).

## 3. Log-in (slice 2)

- **Behaviours:** B9–B13.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_owner_logs_back_in_with_one_time_code`.
  - Web: `web/tests/acceptance/log-in-test.ts` › owner logs back in with a
    one-time code.
- **Tables:** none; no migration (codes and sessions are in Redis).

### Backend

- `backend/app/modules/accounts/codes.py`: expiry, wrong tries left, lock
  and send limits as errors with `retry_in_seconds`.
- `backend/app/modules/accounts/service.py`: `log_in` (active membership
  or "Not added yet").
- `backend/app/modules/accounts/router.py`: `POST /auth/log-in`; 429
  handling.
- `backend/app/core/exceptions.py`: the 429 envelope carries
  `retry_in_seconds` in `data` if the scaffold's error shape needs it.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`.

### Contract

- `make api-export`, `make api-types`. Commit
  `chore(api): update contract for log-in`.

### Web

- `web/app/data/handlers/errors.ts`: 429 as a "too many tries" error with
  its wait time; 404 from log-in as "Not added yet".
- `web/app/utils/countdown.ts`: seconds → `14:52`.
- `web/app/templates/log-in.gts`: the "Log in" side and its tabs on narrow
  screens.
- Components: `web/app/components/auth/{log-in-form,code-errors,not-added}.gts`
  (wrong code with tries left, expired, locked with countdown, resend
  countdown, `WebAuthErrors.html`).
- Tests: `web/tests/unit/utils/countdown-test.ts`,
  `web/tests/unit/data/handlers-test.ts` (429),
  `web/tests/integration/components/auth/…`,
  `web/tests/acceptance/log-in-test.ts`.

## 4. Add members (slice 3)

- **Behaviours:** B20–B30, and B17's "Add members done" case.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_owner_adds_member_who_then_logs_in`.
  - Web: `web/tests/acceptance/members-test.ts` › owner adds a member.
- **Tables:** `membership` gains `created_by` and `details_checked_at`;
  new `change_log`; migration `backend/alembic/versions/<rev>_add_members.py`.

### Backend

- `backend/app/modules/history/`: `models.py` (`ChangeLog`,
  `ChangeEntity`, `ChangeAction`), `service.py` (`record_change`, called in
  the same transaction as the change).
- `backend/app/modules/accounts/schemas.py`: `MemberIn`, `MemberUpdateIn`,
  `MemberOut`, `MeUpdateIn`.
- `backend/app/modules/accounts/service.py`: `add_member` (find or create
  the person, FR-85 check, period from `joined_on`, notice through the
  notifier), `list_members`, `update_member`, `update_me` (name, details
  checked).
- `backend/app/modules/accounts/router.py`: `GET /members`,
  `POST /members`, `PATCH /members/{id}`, `PATCH /me`.
- `backend/app/modules/homes/service.py`: "Add members" done when another
  member is active.
- `backend/alembic/env.py`: import `ChangeLog`; the group's migration.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`,
  `backend/tests/history/test_service.py`.

### Contract

- `make api-export`, `make api-types`. Commit
  `chore(api): update contract for members`.

### Web

- `web/app/models/member.ts`, `web/app/data/builders/members.ts`.
- Routes and templates: `web/app/routes/authenticated/members.ts` (owner
  and managers only, else back home), `web/app/templates/authenticated/members.gts`,
  `web/app/routes/authenticated/welcome.ts` and
  `web/app/templates/authenticated/welcome.gts` (first log-in check; the
  `authenticated` route sends a member there until their details are
  checked).
- Components: `web/app/components/members/{member-list,add-member-form,edit-member-form}.gts`,
  `web/app/components/auth/first-log-in-check.gts`; the shell's nav gains
  Members for the owner and managers.
- Tests: `web/tests/integration/components/members/…`,
  `web/tests/integration/components/auth/first-log-in-check-test.gts`,
  `web/tests/acceptance/{members,first-log-in}-test.ts`.

## 5. Roles, deactivate and reactivate (slice 4)

- **Behaviours:** B31–B37.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_owner_deactivates_member_who_can_no_longer_log_in`.
  - Web: `web/tests/acceptance/member-status-test.ts` › manager deactivates
    and reactivates a member.
- **Tables:** none new; uses `membership.role`, `membership.status`,
  `membership_period` and `change_log`. No migration.

### Backend

- `backend/app/modules/accounts/schemas.py`: `RoleIn`, `DeactivateIn`,
  `ReactivateIn`.
- `backend/app/modules/accounts/service.py`: `change_role`, `deactivate`
  (closes the open period, locks the membership row), `reactivate` (FR-85
  and name checks, new period); each writes `change_log`.
- `backend/app/modules/accounts/router.py`: `PUT /members/{id}/role`,
  `POST /members/{id}/deactivate`, `POST /members/{id}/reactivate`.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`.

### Contract

- `make api-export`, `make api-types`. Commit
  `chore(api): update contract for roles and member status`.

### Web

- `web/app/data/builders/members.ts`: role, deactivate, reactivate.
- Components: `web/app/components/members/{role-editor,deactivate-dialog,reactivate-dialog,member-tabs}.gts`;
  `web/app/components/ui/dialog.gts` (the centred confirmation dialog,
  FR-97; three dialogs use it).
- Tests: `web/tests/integration/components/{members,ui}/…`,
  `web/tests/acceptance/member-status-test.ts`.

### End-to-end

- `web/e2e/accounts.spec.ts`, replacing `web/e2e/smoke.spec.ts` (asked at
  Gate 2): against `docker compose up` with no mocks, an owner signs up
  (the code read from `dev:outbox` with
  `docker compose exec -T redis redis-cli`), adds a member, logs out; the
  member logs in and passes the first log-in check; the owner logs in and
  deactivates the member; the member's next log-in gets "Not added yet".

## 6. Verify and document

- Run [validation.md](validation.md) in full, including `/security-review`.
- `specs/data-model.md`: change `person`, `home`, `membership`,
  `membership_period` and `change_log` from _planned_ to _built_ and match
  them to the two migrations; update the change log.
- `specs/tech-stack.md`: add **Decided in Phase 1** (cookie session in
  Redis, CSRF approach, `Notifier` and the development outbox, clock,
  `phonenumbers` and `email-validator`, actor columns, the `history`
  module); mark Auth as decided in **Stack summary**; remove **Auth tokens**
  from **Deferred decisions**; record **File storage** as decided (S3 with
  presigned POST and GET, MinIO locally, built in Phase 2); add 429 to the
  status table; add `history` to the module list and `deps.py` to
  `app/api/` in **Project conventions**; add **Known limitations** (no real
  SMS or email provider yet; sessions are lost if Redis is flushed; web and
  API must share a site in production; members are added without an ID
  document until Phase 2).
- `specs/roadmap.md`: mark Phase 1 `✅ Complete`; move fund keepers to
  Phase 4.
- `README.md`: how to log in locally (the code is in the backend log and
  `dev:outbox`).
- `CHANGELOG.md`: run `/changelog` before merging.
