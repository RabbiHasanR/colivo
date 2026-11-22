# Phase 1b — A Person in Several Homes: Tests

## Group 2 — Several active homes

Backend acceptance: `backend/tests/accounts/test_api.py::test_member_of_another_home_is_added_to_this_home`
Web acceptance: `web/tests/acceptance/members-test.ts` › adding someone already in this home shows "Already a member of this home"

Phase 1 tests changed because FR-85 was replaced (approved at Gate 2,
23 Nov 2026): T1.1, T2.2, T3.1, T3.2, T4.1 and T4.2 change an existing
test; T3.3 deletes one, and T1.2 replaces one (deleted).

### B1 — Someone active in another home can be added

- [x] T1.1 unit — `test_member_active_in_another_home_is_added` ✅ _(changed from Phase 1's `test_member_active_in_another_home_cannot_be_added`: FR-85 replaced)_: Maruf, active in Old Flat, is added to Our Flat; he has 2 active memberships and gets the notice naming Our Flat
- [x] T1.2 unit (database rule) — `test_database_allows_one_person_active_in_two_homes` ✅ _(replaces Phase 1's `test_models.py::test_person_cannot_have_two_active_memberships`, deleted with the user's OK on 23 Nov 2026: it pinned the dropped index and was missed at Gate 2)_: two active memberships of one person in different homes, saved past the service, are accepted
- [ ] T1.3 web — _(skipped: the web sends the same request and shows the same success as any add, already covered by `members-test.ts` › owner adds a member)_

### B2 — An active member of this home can't be added again

- [x] T2.1 unit — `test_active_member_of_this_home_cannot_be_added_again` ✅: 409 "Already a member of this home."; no second membership, no notice
- [x] T2.2 web integration — `add-member-form-test.gts` › shows why the API refused the member _(changed: its GIVEN and refusal text become "Already a member of this home."; the behaviour it checks, showing the API's 409, is the same)_
- [ ] T2.3 integration — _(skipped: the router only passes the service's 409 on; T2.1 covers the rule, and the 409 envelope is pinned by Phase 1's tests)_

### B3 — Someone active in another home can sign up

- [x] T3.1 unit — `test_person_active_in_another_home_can_sign_up` ✅ _(changed from `test_sign_up_refused_when_already_active_in_a_home`)_: the owner of Our Flat signs up "Second Home"; 2 homes, both owned by the same person; Our Flat's membership is unchanged
- [x] T3.2 unit — `test_email_in_any_letter_case_is_the_same_person` ✅ _(changed: it proved "same person" through the old 409; now the second sign-up, in another letter case, creates its home under the same single person, `rabbi@example.com`)_
- [x] T3.3 web — `sign-up-form-test.gts` › shows the 409 message when the person is already in a home: **deleted** _(the API no longer answers 409 to sign-up; the form's error display stays covered by its 422 and refused-contact tests)_

### B4 — A past member who joined another home can be reactivated

- [x] T4.1 unit — `test_member_who_joined_another_home_can_be_reactivated` _(changed from `test_reactivating_someone_active_in_another_home_is_refused`)_: Maruf left Our Flat and is active in Old Fort; Our Flat reactivates him; both memberships are active
- [x] T4.2 web integration — `reactivate-dialog-test.gts` › shows the API's 409 message _(changed: its GIVEN becomes "another active member has Karim's name", with the name-taken message, the 409 reactivate still gives)_

### B5 — Each home sees only its own membership of a person

- [x] T5.1 integration — `test_person_in_two_homes_shows_each_homes_details_only`: Maruf is "Maruf Ahmed", manager, in Old Fort; Our Flat adds him as "Maruf", member; Our Flat's `GET /members` shows "Maruf", role member, Our Flat's join date, and no "Maruf Ahmed", "manager" or "Old Fort"

### B6 — Changing a person in one home leaves their other homes alone

- [x] T6.1 unit — `test_changing_a_person_in_one_home_leaves_the_other_home_unchanged`, parametrised over rename and deactivate: Maruf is in Our Flat and Old Fort; Our Flat renames or deactivates him; his Old Fort membership keeps its name, its active status and its open stay
- [ ] T6.2 reactivate case — _(skipped: reactivate finds the member with the same home-scoped `get_member` as rename and deactivate, so a third case tests no new code)_
