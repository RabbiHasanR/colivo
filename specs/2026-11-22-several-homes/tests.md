# Phase 1b — A Person in Several Homes: Tests

## Group 2 — Several active homes

Backend acceptance: `backend/tests/accounts/test_api.py::test_member_of_another_home_is_added_to_this_home`
Web acceptance: `web/tests/acceptance/members-test.ts` › adding someone already in this home shows "Already a member of this home"

Phase 1 tests changed because FR-85 was replaced (approved at Gate 2,
23 Nov 2026): T1.1, T2.2, T3.1, T3.2, T3.3, T4.1 and T4.2 change an existing
test, and T1.2 replaces one (deleted).

### B1 — Someone active in another home can be added

- [x] T1.1 unit — `test_member_active_in_another_home_is_added` ✅ _(changed from Phase 1's `test_member_active_in_another_home_cannot_be_added`: FR-85 replaced)_: Maruf, active in Old Flat, is added to Our Flat; he has 2 active memberships and gets the notice naming Our Flat
- [x] T1.2 unit (database rule) — `test_database_allows_one_person_active_in_two_homes` ✅ _(replaces Phase 1's `test_models.py::test_person_cannot_have_two_active_memberships`, deleted with the user's OK on 23 Nov 2026: it pinned the dropped index and was missed at Gate 2)_: two active memberships of one person in different homes, saved past the service, are accepted
- [ ] T1.3 web — _(skipped: the web sends the same request and shows the same success as any add, already covered by `members-test.ts` › owner adds a member)_

### B2 — An active member of this home can't be added again

- [x] T2.1 unit — `test_active_member_of_this_home_cannot_be_added_again` ✅: 409 "Already a member of this home."; no second membership, no notice
- [x] T2.2 web integration — `add-member-form-test.gts` › shows why the API refused the member ✅ _(changed; no web code changes: the form already shows the API's message: its GIVEN and refusal text become "Already a member of this home."; the behaviour it checks, showing the API's 409, is the same)_
- [ ] T2.3 integration — _(skipped: the router only passes the service's 409 on; T2.1 covers the rule, and the 409 envelope is pinned by Phase 1's tests)_

### B3 — Someone active in another home can sign up

- [x] T3.1 unit — `test_person_active_in_another_home_can_sign_up` ✅ _(changed from `test_sign_up_refused_when_already_active_in_a_home`)_: the owner of Our Flat signs up "Second Home"; 2 homes, both owned by the same person; Our Flat's membership is unchanged
- [x] T3.2 unit — `test_email_in_any_letter_case_is_the_same_person` ✅ _(changed: it proved "same person" through the old 409; now the second sign-up, in another letter case, creates its home under the same single person, `rabbi@example.com`)_
- [x] T3.3 web integration — `sign-up-form-test.gts` › shows the API's refusal above the button ✅ _(changed, not deleted as first agreed: on 23 Nov 2026 the user chose to keep the form's error display covered, since sign-up still answers 400 and 429. The old "already in a home" 409 case became a 400 first-month refusal; no web code changes)_

### B4 — A past member who joined another home can be reactivated

- [x] T4.1 unit — `test_member_who_joined_another_home_can_be_reactivated` ✅ _(changed from `test_reactivating_someone_active_in_another_home_is_refused`)_: Maruf left Our Flat and is active in Old Fort; Our Flat reactivates him; both memberships are active
- [x] T4.2 web integration — `reactivate-dialog-test.gts` › shows the API's 409 message ✅ _(changed; no web code changes: its GIVEN becomes "another active member has Karim's name", with the name-taken message, the 409 reactivate still gives)_

### B5 — Each home sees only its own membership of a person

- [x] T5.1 integration — `test_person_in_two_homes_shows_each_homes_details_only` ✅ _(passed on its first run: Phase 1's home scoping already delivers it; seen failing by removing `list_members`'s home filter)_: Maruf is "Maruf Ahmed", manager, in Old Fort; Our Flat adds him as "Maruf", member; Our Flat's `GET /members` shows "Maruf", role member, Our Flat's join date, and no "Maruf Ahmed", "manager" or "Old Fort"

### B6 — Changing a person in one home leaves their other homes alone

- [x] T6.1 unit — `test_changing_a_person_in_one_home_leaves_the_other_home_unchanged` ✅ _(passed on its first run: every Phase 1 change targets one membership row; seen failing by making `deactivate` touch the person's other memberships)_, parametrised over rename and deactivate: Maruf is in Our Flat and Old Fort; Our Flat renames or deactivates him; his Old Fort membership keeps its name, its active status and its open stay
- [ ] T6.2 reactivate case — _(skipped: reactivate finds the member with the same home-scoped `get_member` as rename and deactivate, so a third case tests no new code)_

## Group 3 — Choose and switch homes

Backend acceptance: `backend/tests/accounts/test_api.py::test_person_in_two_homes_chooses_one_after_log_in`
Web acceptance: `web/tests/acceptance/choose-home-test.ts` › person in two homes chooses one after log-in, then switches

Existing tests and helpers changed (approved at Gate 2, 23 Nov 2026):
`test_log_in_returns_the_active_membership` (becomes T7.1); `log-in-test.ts`
› owner logs back in (T7.2); the `POST /auth/log-in` mocks in
`log-in-page-test.gts` and `log-in-form-test.gts`; `web/tests/helpers/accounts.ts`
(`me()` gains `homes`, new `logInBody()` and `myHomes()`).

### B7 — One home: log-in goes straight there

- [x] T7.1 unit — `test_log_in_with_one_home_returns_it` ✅ _(changed from `test_log_in_returns_the_active_membership`: `log_in` now returns `LogInOut`)_: `me` is Our Flat, `homes` has one row
- [x] T7.2 web acceptance — `log-in-test.ts` › owner logs back in with a one-time code ✅ _(changed: the log-in mock answers `LogInOut`; also checks the next `GET /me` sends `X-Colivo-Home` for Our Flat)_

### B8 — Several homes: log-in shows "Choose a home"

- [x] T8.1 unit — `test_log_in_with_several_homes_lists_them_without_me` ✅ _(passed on its first run: B7's `log_in` already handled several homes; seen failing by filling `me` for any number of homes)_: homes by name, each with area and role; `me` is null
- [x] T8.2 integration — `test_my_homes_lists_active_homes_without_a_header` ✅: `GET /me/homes` needs no header and leaves out a home where they're inactive
- [x] T8.3 web integration — `homes/home-picker-test.gts` › lists each home's name, area and role, and chooses the tapped one ✅
- [ ] T8.4 web acceptance — _(skipped: the group's web acceptance test is this journey)_

### B9 — First log-in check per home

- [x] T9.1 integration — `test_me_shows_the_chosen_homes_first_log_in_check` ✅: checked in Our Flat, not yet in Old Fort; `GET /me` answers for the home the header names
- [ ] T9.2 web — _(skipped: the guard already sends an unchecked membership to the check, from `me`; covered by Phase 1's `first-log-in-test.ts`)_

### B10 — Switch homes from the shell

- [x] T10.1 integration — `test_me_lists_the_persons_homes_for_the_switcher` ✅: `MeOut.homes` has both homes
- [x] T10.2 web integration — `homes/home-switcher-test.gts` › lists the other homes and switches to the chosen one ✅
- [x] T10.3 web integration — `layout/app-shell-test.gts` › shows the switcher only for a person in several homes (one vs two homes) ✅
- [ ] T10.4 keyboard (arrows, Escape, focus return) — _(skipped: manual check 5, as Phase 1 did for the dialog)_

### B11 — Each tab keeps its own home

- [x] T11.1 web unit — `services/current-home-test.ts` › a tab starts from its own home, else the last home chosen ✅
- [x] T11.2 web unit — `services/current-home-test.ts` › choosing a home keeps it for this tab and as the last home ✅
- [x] T11.3 web unit — `services/current-home-test.ts` › refused storage (private window) never throws; the home is kept for the page ✅ _(passed on its first run: storage was already read and written in `try`; seen failing without the `catch`)_
- [x] T11.4 web unit — `data/handlers-test.ts` › the auth handler sends `X-Colivo-Home` when a home is chosen, and none otherwise ✅

### B12 — Log-out logs out every tab and forgets the home

- [x] T12.1 integration — `test_log_out_works_without_choosing_a_home` ✅: two homes, no header → 200, session ended
- [x] T12.2 web unit — `services/current-home-test.ts` › forget clears this tab's home and the last home ✅
- [x] T12.3 web acceptance — `log-out-test.ts` › after log-out, a log-in with several homes shows "Choose a home", not the old home ✅

### B13 — No home named with several homes: refused, nothing changes

- [x] T13.1 unit — `test_no_home_named_with_one_home_uses_it` ✅ _(passed on its first run: Phase 1 already used the only home; seen failing by refusing every request that names no home)_
- [x] T13.2 unit — `test_no_home_named_with_several_homes_is_refused` ✅: 409, reason `choose_home`
- [x] T13.3 integration — `test_adding_a_member_without_naming_a_home_changes_nothing` ✅ _(passed on its first run, after T13.2 brought the rule; seen failing with the rule removed)_: owner of two homes, `POST /members` without the header → 409, no member added
- [x] T13.4 web acceptance — `choose-home-test.ts` › a tab with no home chosen, for a person in several homes, opens "Choose a home" ✅

### B14 — Naming a home you're not in: 403, nothing about that home

- [x] T14.1 unit — `test_naming_a_home_the_person_is_not_active_in_is_refused` ✅, parametrised: inactive there, another person's home, an id that doesn't exist → 403, reason `not_in_home`, the same message
- [x] T14.2 integration — `test_not_in_home_answer_is_the_same_for_any_home` ✅ _(passed on its first run, after T14.1; seen failing by answering an existing home differently)_: the bodies for another person's home and an unknown id are identical, and neither names Old Fort

### B15 — Removed from the open home: "Choose a home" with a notice

- [x] T15.1 web acceptance — `choose-home-test.ts` › removed from the open home goes to "Choose a home" with "You're no longer a member of Green House"
- [x] T15.2 web unit — `utils/api-error-test.ts` › `refusalReason` reads `choose_home` and `not_in_home`, and null for anything else ✅

### B16 — Removed from the last home: logged out at once

- [x] T16.1 integration — `test_my_homes_answers_401_with_no_active_home` ✅ _(passed on its first run: `current_person` got the check in B8; seen failing without it)_: session alive, no active home → 401
- [ ] T16.2 web — _(skipped: 401 → log-in is Phase 1's `session-end` handling, already tested)_

### B17 — The role follows the chosen home

- [x] T17.1 integration — `test_role_follows_the_chosen_home` ✅ _(passed on its first run: `require_role` reads the chosen membership since B9; seen failing by taking the person's highest role)_: owner of Our Flat and member of Old Fort; `GET /members` → 200 in Our Flat, 403 (role, no reason) in Old Fort
- [ ] T17.2 web — _(skipped: the nav reads the role from the chosen home's `me`; covered by Phase 1's `members-test.ts` › a member has no Members link)_

### B18 — A malformed home id: 422

- [x] T18.1 integration — `test_home_header_that_is_not_an_id_answers_422` ✅ _(passed on its first run: FastAPI checks the `uuid.UUID` header type; seen failing with the header read as text, which reached the database)_

### B19 — The browser may send the home header, only from the web app

- [x] T19.1 integration — `tests/core/test_api.py::test_preflight_allows_the_home_header` ✅ _(in `test_api.py`, beside Phase 1's CORS tests, not a new `test_cors.py`)_, parametrised: the web app's origin → allowed; another origin → refused
