# Phase 1c — Change a Member's Phone or Email: Plan

Branch: `phase-1c-change-contact`, pushed early with a draft pull request.

Each group is built with `/tdd` as in
[testing.md → Build time](../testing.md#build-time-tdd-one-planmd-group-per-run):
Gate 2 on `tests.md`, then backend → contract → web, one test at a time.
Group 1 is groundwork (no **Behaviours:** line): no tests, one commit, then
stop for review.

Per-behaviour gate: `make test-fast`, `make lint` and `make format-check`
green, then a conventional commit (e.g. `feat(accounts): change a member's
phone with a code`, `feat(web): add an email on the Edit tab`) with no
Co-Authored-By or AI attribution lines.

## 1. Groundwork

Docs and constants only. Commit: `chore: add phase 1c groundwork`.

- Fetch current docs with `ctx7`, at the installed versions: FastAPI (enum
  path parameters, `DELETE` routes with a response body), redis-py (sets:
  `SADD`, `SMEMBERS`, `EXPIRE`, pipelines), Alembic (`op.drop_index` of a
  partial index, `op.create_index`), Ember (a route under `authenticated`,
  `LinkTo`), WarpDrive (request builders for `PUT` and `DELETE`), MSW
  (handlers with path parameters), Playwright (two browser contexts, reading
  `dev:outbox`).
- No new dependency, setting or env var.
- Constants: in `backend/app/modules/accounts/constants.py`, the Redis key
  prefixes `CHANGE_CODE_PREFIX = "otp:change"` and
  `PERSON_SESSIONS_PREFIX = "person_sessions"`.
- Check: `make test-fast`, `make lint`, `make format-check` still green.

## 2. The owner or a manager changes a member's log-in (slice 1)

- **Behaviours:** B1–B19.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_owner_adds_an_email_to_a_member_with_a_code`.
  - Web: `web/tests/acceptance/members-test.ts` › owner adds an email to a
    member with a code.
- **Tables:** `membership`: add `ix_membership_person_id`, drop
  `ix_membership_active_person_id`, as in
  [data-model.md](../data-model.md#membership-phase-1-built); migration
  `backend/alembic/versions/<rev>_change_contact.py`. Redis keys
  `otp:change:…` and `person_sessions:…` (no migration).

### Backend

- `backend/app/modules/accounts/models.py`: the index change on
  `Membership.__table_args__`; the group's migration.
- `backend/app/modules/accounts/codes.py`: codes, wrong counts and locks
  keyed by a scope (log-in, or a change for one person), so a change code
  can't log in (B14); the send limit stays per contact for both. A refactor
  on green where it only moves keys; the new scope is test-first.
- `backend/app/modules/accounts/sessions.py`: `create_session` and
  `save_session` keep the session in `person_sessions:{person_id}` (same
  30 days); `end_sessions(person_id, keep=None)` ends all of a person's
  sessions, or all but one.
- `backend/app/modules/accounts/service.py`:
  - `check_contact_editable(editor, member)`: 403 for a member also in
    another home, active or past (`ix_membership_person_id`), and for a
    manager editing the owner; 400 for a past member. Editing your own row
    skips the other-home check.
  - `request_contact_code(person, contact)`: 400 for the value they already
    have; sends a change code to the new contact; the same answer whether or
    not someone else has it.
  - `set_contact(person, contact, code)`: checks the code, then 409 if
    someone else has it (also the unique violation under a race, B18); sets
    `phone` or `email`; one `change_log` row per home the person is in, in
    one transaction; after the commit, ends sessions if it replaced a value,
    and sends the notices (B16).
  - `remove_contact(person, channel)`: 400 for the last one or one they
    don't have; the same history, sessions and notice.
  - `member_out`: `contact_editable` for the viewer.
  - Constants: `ONLY_THEY_CAN`, `REACTIVATE_FIRST`, `SAME_CONTACT`,
    `CONTACT_TAKEN`, `LAST_CONTACT`; the notice texts, with the masking in
    `backend/app/modules/accounts/contact.py` (`partly_hidden(contact)`).
- `backend/app/modules/accounts/schemas.py`: `ContactChangeIn` (`contact`,
  `code`), `ContactKind` (`phone`, `email`) for the path; `MemberOut` gains
  `contact_editable`; `MePersonOut` gains `email`.
- `backend/app/modules/accounts/router.py`: `POST /members/{id}/contact/code`,
  `PUT /members/{id}/contact`, `DELETE /members/{id}/contact/{channel}` on
  `OwnerOrManagerDep`, with the code errors (`CODE_ERRORS`) declared.
- Tests: `backend/tests/accounts/{test_service,test_api,test_codes,test_sessions,test_contact}.py`;
  `backend/tests/conftest.py` gains a member with both a phone and an email.

### Contract

- `make api-export` → `api/openapi.json`; `make api-types`. Commit
  `chore(api): add changing a member's log-in`.

### Web

- `web/app/data/builders/members.ts`: `requestMemberContactCode`,
  `setMemberContact`, `removeMemberContact`; `web/app/services/members.ts`
  wraps them.
- `web/app/components/contact/contact-editor.gts`: Phone and Email fields
  showing the current values ("(optional)" on the missing one), Send code →
  code field → Save, Remove while both exist, read-only with a note when
  `@editable` is false; given `@sendCode`, `@save` and `@remove` by its page.
  Reuses `components/auth/code-field.gts` and `components/auth/code-errors.gts`.
- `web/app/components/members/edit-member-form.gts` (or the Edit tab in
  `members-page.gts`): the contact editor under Name and Joined on, from the
  member's `contact_editable`, with "Only they can change their log-in, from
  My profile." when false.
- `web/app/components/members/member-list.gts`: phone with the email under
  it when both exist (B19).
- Tests: `web/tests/integration/components/contact/contact-editor-test.gts`,
  `web/tests/integration/components/members/{edit-member-form,member-list}-test.gts`,
  `web/tests/acceptance/members-test.ts`; MSW handlers and factories in
  `web/tests/helpers/` typed from the generated API types.

## 3. My profile (slice 2)

- **Behaviours:** B20–B24.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_person_changes_their_own_phone_with_a_code`.
  - Web: `web/tests/acceptance/profile-test.ts` › person changes their own
    phone on My profile.
- **Tables:** none; no migration.

### Backend

- `backend/app/modules/accounts/router.py`: `POST /me/contact/code`,
  `PUT /me/contact`, `DELETE /me/contact/{channel}` on `CurrentPersonDep`
  (no home), reusing group 2's service functions; a change or removal ends
  the person's sessions except the one in this request's cookie (B24).
- `backend/app/modules/accounts/service.py`: `get_me` fills
  `person.email`; the per-home history rows for a person in several homes
  (B23) if group 2's tests didn't already require them.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`, with the
  `person_in_two_homes` fixture from Phase 1b.

### Contract

- `make api-export`, `make api-types`. Commit `chore(api): add changing
your own log-in`.

### Web

- `web/app/data/builders/me.ts`: `requestMyContactCode`, `setMyContact`,
  `removeMyContact`; `web/app/services/profile.ts` wraps them and refreshes
  `session.me` after a change.
- Route and template: `web/app/router.ts` (`profile` under
  `authenticated`), `web/app/routes/authenticated/profile.ts`,
  `web/app/templates/authenticated/profile.gts`.
- `web/app/components/profile/profile-page.gts`: the "My details" card from
  `WebProfile.html` (initials, name, role and "member since", Name with its
  Save through `PATCH /me`, then the contact editor), as in
  [requirements.md → Screens](requirements.md#screens).
- `web/app/components/layout/app-shell.gts`: the name card (sidebar and phone
  top bar) links to My profile.
- Tests: `web/tests/integration/components/profile/profile-page-test.gts`,
  `web/tests/integration/components/layout/app-shell-test.gts`,
  `web/tests/acceptance/profile-test.ts`.

### End-to-end

- `web/e2e/change-contact.spec.ts`, beside `accounts.spec.ts` and
  `several-homes.spec.ts` (both must keep passing): against
  `docker compose up` with no mocks, an owner signs up with a phone and adds
  a member by phone; on the member's Edit tab the owner adds an email with
  the code from `dev:outbox`; the member logs in with the email, opens My
  profile and changes the phone with a code; logging in with the old phone
  then gets "Not added yet", and the owner's members list shows the new
  phone and the email.

## 4. Verify and document

- Run [validation.md](validation.md) in full, including `/security-review`
  of the branch. Findings the user accepts as fixes become behaviours under
  **Security review follow-ups**, built test-first.
- `specs/data-model.md`: mark the `membership` index change _built_ and
  match it to the migration; mark the Redis keys built in
  [Log-in contacts](../data-model.md#log-in-contacts-agreed-23-nov-2026).
- `specs/tech-stack.md`: add **Decided in Phase 1c** (a phone and an email
  per person, code-confirmed changes, the other-home rule, ending sessions
  through `person_sessions`, scoped code keys); add to **Known limitations**:
  an owner or manager can add a phone or email they control to a member who
  is in no other home and so log in as them (the member is told), and the
  read-only Edit tab tells the owner a member is in some other home.
- `colivo-design/requirements.md`: Phase 1c change lines on FR-84 (log in
  with a phone or an email, either one) and FR-86 (the owner or a manager
  changes a member's phone or email; a member changes their own on My
  profile).
- `specs/roadmap.md`: mark Phase 1c `✅ Complete`.
- `README.md`: trying it locally (codes from `dev:outbox`).
- `CHANGELOG.md`: run `/changelog` before merging.
