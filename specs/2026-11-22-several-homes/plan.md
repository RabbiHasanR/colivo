# Phase 1b — A Person in Several Homes: Plan

Branch: `phase-1b-several-homes`, pushed early with a draft pull request.

Each group is built with `/tdd` as in
[testing.md → Build time](../testing.md#build-time-tdd-one-planmd-group-per-run):
Gate 2 on `tests.md`, then backend → contract → web, one test at a time.
Group 1 is groundwork (no **Behaviours:** line): no tests, one commit, then
stop for review.

Per-behaviour gate: `make test-fast`, `make lint` and `make format-check`
green, then a conventional commit (e.g. `feat(accounts): add a member who is
active in another home`, `feat(web): choose a home after log-in`) with no
Co-Authored-By or AI attribution lines.

Phase 1 tests that pin "one active home per person" (FR-85) are changed in
group 2, never deleted or skipped; each change is listed at group 2's
Gate 2 and approved first ([requirements.md → Decisions](requirements.md#decisions)).

## 1. Groundwork

Docs only. Commit: `chore: add phase 1b groundwork`.

- Fetch current docs with `ctx7`, at the installed versions: FastAPI
  (`Header` dependencies with an alias, `CORSMiddleware` `allow_headers`
  and pre-flight), Alembic (`op.drop_index` / `op.create_index` with
  `postgresql_where`), Ember (router service, `beforeModel` guards,
  `router.refresh`), WarpDrive (request handlers adding headers), MSW
  (reading request headers in a handler), Playwright (several pages in one
  browser context, `sessionStorage` per page).
- No new dependency, setting or env var. The header name is a constant,
  `HOME_HEADER = "X-Colivo-Home"`, in `backend/app/modules/accounts/constants.py`
  and `web/app/data/config.ts`.
- Adding `X-Colivo-Home` to CORS `allow_headers` is behaviour (B19), so it
  is built test-first in group 3, not here.
- Check: `make test-fast`, `make lint`, `make format-check` still green.

## 2. Several active homes (slice 1)

- **Behaviours:** B1–B6.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_member_of_another_home_is_added_to_this_home`.
  - Web: `web/tests/acceptance/members-test.ts` › adding someone already in
    this home shows "Already a member of this home".
- **Tables:** `membership`: drop `uq_membership_active_person_id`, add
  `ix_membership_active_person_id`, as in
  [data-model.md](../data-model.md#membership-phase-1-built); migration
  `backend/alembic/versions/<rev>_several_homes.py`.

Until group 3, a person active in several homes logs in to the home they
joined first (`active_membership` orders by `created_at`). This is a
stopgap on the phase branch only, never merged alone; group 3's tests
replace it.

### Backend

- `backend/app/modules/accounts/models.py`: the index change on
  `Membership.__table_args__`; the group's migration.
- `backend/app/modules/accounts/service.py`:
  - `add_member`: refuse an active member of this home (409 "Already a
    member of this home."); keep the past-member 409; no check on other
    homes. The notice names this home.
  - `sign_up`: drop the "already in a home" refusal.
  - `reactivate`: drop the "active in another home" refusal; the name check
    stays.
  - `active_membership` → ordered, the group 2 stopgap above.
  - Constants: `ALREADY_IN_A_HOME` goes; `ALREADY_IN_THIS_HOME` comes.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`; the FR-85
  tests (`test_member_active_in_another_home_cannot_be_added`,
  `test_reactivating_someone_active_in_another_home_is_refused`, the
  sign-up refusal) changed as agreed at Gate 2.

### Contract

- `make api-export` → `api/openapi.json`; `make api-types` (the 409
  descriptions change). Commit `chore(api): update contract for several
homes`.

### Web

- `web/app/components/members/add-member-form.gts`: shows the new 409
  message (it shows the API's message, so likely only its test changes).
- `web/app/components/auth/log-in-page.gts`: the sign-up note's new words
  ([requirements.md → Screens](requirements.md#screens)).
- Tests: `web/tests/integration/components/members/{add-member-form,reactivate-dialog}-test.gts`,
  `web/tests/integration/components/auth/sign-up-form-test.gts` (their
  "already in a home" cases changed as agreed at Gate 2),
  `web/tests/acceptance/members-test.ts`.

## 3. Choose and switch homes (slice 2)

- **Behaviours:** B7–B19.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_person_in_two_homes_chooses_one_after_log_in`.
  - Web: `web/tests/acceptance/choose-home-test.ts` › person in two homes
    chooses one after log-in, then switches.
- **Tables:** none; no migration (the current home travels in a header).

### Backend

- `backend/app/modules/accounts/schemas.py`: `HomeChoiceOut` (`id`,
  `name`, `area`, `role`), `LogInOut` (`homes`, `me`); `MeOut` gains
  `homes`.
- `backend/app/modules/accounts/service.py`: `active_homes(person)` (one
  query for the picker, `MeOut.homes` and the header check);
  `membership_for(person, home_id)` (the active membership, else
  `not_in_home`); `log_in` returns `LogInOut`; `get_me` fills `homes`. The
  group 2 stopgap goes.
- `backend/app/api/deps.py`: `current_person` (cookie → session → person
  with an active home, else 401) and `current_membership` (person +
  `X-Colivo-Home`: one home without it, 409 `choose_home` with several, 403
  `not_in_home`, 422 for a malformed id). `require_role` keeps reading the
  chosen membership's role.
- `backend/app/modules/accounts/router.py`: `POST /auth/log-in` → `LogInOut`;
  `GET /me/homes` on `current_person`.
- `backend/app/main.py`: `X-Colivo-Home` in `CORS_HEADERS`.
- Tests: `backend/tests/accounts/{test_service,test_api}.py`,
  `backend/tests/core/test_cors.py` (pre-flight allows the header, other
  origins still refused); `backend/tests/conftest.py` gains a
  `person_in_two_homes` fixture and a client helper that sends the header.

### Contract

- `make api-export`, `make api-types`. Commit `chore(api): update contract
for choosing a home`.

### Web

- `web/app/services/current-home.ts`: the tab's home id (`sessionStorage`),
  the last home chosen (`localStorage`), every storage access in
  `try/catch`; `choose(id)`, `forget()` (on log-out), `homes` from
  `GET /me` or `GET /me/homes`.
- `web/app/data/handlers/auth.ts`: `createAuthHandler(getHomeId)` adds
  `X-Colivo-Home` when a home is chosen; `web/app/services/store.ts` passes
  the getter.
- `web/app/data/handlers/errors.ts` and `web/app/utils/api-error.ts`: the
  409 `choose_home` and 403 `not_in_home` reasons as their own error kinds,
  so `error-watch.ts` tells "removed from this home" apart from "your role
  changed" (`session.recheckRole`).
- `web/app/data/builders/{auth,me}.ts`: `LogInOut`; `getMyHomes()`.
- `web/app/services/session.ts`: log-in with one home chooses it; with
  several, goes to `choose-home`; `logOut()` also calls
  `currentHome.forget()`; `not_in_home` → notice, then the other home or
  the picker.
- Routes and templates: `web/app/routes/choose-home.ts` and
  `web/app/templates/choose-home.gts` (outside `authenticated`, which would
  loop: its guard reads `GET /me/homes`, 401 → log-in);
  `web/app/routes/authenticated.ts` sends a tab with no chosen home, or a
  409 `choose_home`, to `choose-home`.
- Components: `web/app/components/homes/{home-picker,home-switcher}.gts`;
  `web/app/components/layout/app-shell.gts` shows the switcher (sidebar and
  phone top bar) for a person in several homes. `web/app/components/ui/menu.gts`
  only if a second menu appears; otherwise the switcher keeps its own.
- Tests: `web/tests/unit/services/current-home-test.ts` (tab, last home,
  refused storage), `web/tests/unit/data/handlers-test.ts` (the header, the
  two reasons), `web/tests/integration/components/homes/…`,
  `web/tests/integration/components/layout/app-shell-test.gts`,
  `web/tests/acceptance/{choose-home,log-in,access}-test.ts`;
  `web/tests/helpers/login.ts` gains a person in two homes.

### End-to-end

- `web/e2e/several-homes.spec.ts`, beside Phase 1's `accounts.spec.ts`
  (which must keep passing): against `docker compose up` with no mocks, two
  owners sign up (codes from `dev:outbox`), the second adds the first to
  their home; the first logs in, sees "Choose a home", opens one, then in a
  second page of the same browser context switches to the other home; the
  first page reloads and still shows its own home. The second owner then
  deactivates the first in their home, and the first page's next request
  shows "You're no longer a member of …" and opens the remaining home.

## 4. Verify and document

- Run [validation.md](validation.md) in full, including `/security-review`
  of the branch and Phase 1's deferred 22 Nov web changes (the restyle,
  log-in tabs, the add-or-edit card, the 403 role re-check in
  `error-watch.ts` / `session.recheckRole`). Findings the user accepts as
  fixes become behaviours under **Security review follow-ups**, built
  test-first.
- `specs/data-model.md`: mark `membership`'s index change _built_ and match
  it to the migration; move the Phase 1b open question's answer into the
  change log; update the [Person and membership](../data-model.md#person-and-membership-agreed-19-nov-2026)
  note.
- `specs/tech-stack.md`: add **Decided in Phase 1b** (the `X-Colivo-Home`
  header, `current_person` / `current_membership`, `choose_home` and
  `not_in_home`, per-tab home in `sessionStorage`); add `X-Colivo-Home` to
  **Sessions** and the CORS note; remove **One active home per person** and
  **Account check through "add member"** from **Known limitations**, and add
  any new ones; add `current_person` to `deps.py` in **Project
  conventions**.
- `colivo-design/requirements.md`: a Phase 1b change line on FR-83 (a
  person can own several homes) and the Scope's "one home per account".
- `specs/roadmap.md`: mark Phase 1b `✅ Complete`.
- `README.md`: trying two homes locally (two phones, add one to the other's
  home).
- `CHANGELOG.md`: run `/changelog` before merging.
