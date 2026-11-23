# Phase 1c — Change a Member's Phone or Email: Tests

Written by `/tdd`, one group at a time, in the format of
[testing.md → `tests.md` format](../testing.md#testsmd-format). Group 1 is
groundwork and has no tests.

## Group 2 — The owner or a manager changes a member's log-in

Backend acceptance: `backend/tests/accounts/test_api.py::test_owner_adds_an_email_to_a_member_with_a_code`
Web acceptance: `web/tests/acceptance/members-test.ts` › owner adds an email to a member with a code

### B1 — A person with both a phone and an email logs in with either one

- [ ] T1.1 integration — `test_person_with_both_logs_in_with_either` _(covered by the backend acceptance test's last step; log-in already looks up each column, so a test of its own would pass at once and couldn't be seen failing, rule 2)_
- [ ] T1.2 web integration — log-in form accepts an email _(Phase 1's log-in tests already cover email log-in)_

### B2 — The owner or a manager adds the missing phone or email, confirmed with a code

- [x] T2.1 unit — `test_adding_an_email_keeps_the_phone` ✅
- [x] T2.2 integration — `POST /members/{id}/contact/code` sends the code to the new email, not to the member's phone ✅
- [x] T2.3 web integration — contact editor: typing a new email and pressing Send code shows the code field; Save sends the email and the code ✅
- [x] T2.4 web integration — contact editor labels the missing one "(optional)" ✅

### B3 — The owner or a manager changes a member's phone or email

- [x] T3.1 unit — `test_changing_the_phone_replaces_the_old_one` ✅ (the old phone finds nobody, the new one finds the member) _(passed on its first run: B2's save already writes into the column of its kind; kept to pin it)_
- [x] T3.2 web acceptance — after a member's phone is changed, the Edit tab stays open showing the new phone ✅

### B4 — The owner or a manager removes one while the other remains

- [x] T4.1 unit — `test_removing_the_email_keeps_only_the_phone` ✅
- [x] T4.2 integration — `DELETE /members/{id}/contact/email` answers 200 with the member ✅
- [x] T4.3 integration — `DELETE /members/{id}/contact/fax` answers 422 ✅ _(passed on its first run: the `ContactKind` path parameter added for T4.2 already refuses it)_
- [x] T4.4 web integration — contact editor shows Remove only while both exist; pressing it removes that one ✅

### B5 — The last way a member logs in can't be removed

- [x] T5.1 unit — `test_the_last_way_to_log_in_cant_be_removed` ✅ (400 "They need a phone or an email to log in.")
- [x] T5.2 unit — `test_removing_one_they_dont_have_is_refused` ✅
- [ ] T5.3 unit — database refuses a person with neither _(already pinned by Phase 1's `test_person_checks_reject_bad_rows`)_
- [ ] T5.4 web integration — the 400 message on Remove _(the editor never offers Remove for the last one, T4.4)_

### B6 — Wrong, expired and too many codes are refused as on log-in

- [x] T6.1 integration — `PUT /members/{id}/contact` with a wrong code answers 400 with tries left and changes nothing ✅ _(passed on its first run: the save checks the code first, with log-in's `use_code`)_
- [ ] T6.2 unit — expiry, the lock after 5, and the send limits _(pinned by Phase 1's `test_codes.py`; the scope doesn't change them, and B14 tests what it adds)_
- [x] T6.3 web integration — contact editor shows why a code was refused, with tries left ✅

### B7 — Someone else's phone or email is refused, only after the right code

- [x] T7.1 integration — `PUT` with the right code for someone else's phone answers 409 and changes nothing ✅
- [x] T7.2 integration — `POST …/contact/code` answers the same for someone else's phone as for a free one ✅ _(passed on its first run: it pins that the code request never checks who has the phone)_
- [x] T7.3 web integration — contact editor shows "Someone else logs in with that phone or email." ✅

### B8 — Changing to what they already have is refused

- [x] T8.1 unit — `test_a_code_for_the_phone_they_already_have_is_refused` ✅ (400, nothing sent)
- [x] T8.2 web integration — contact editor offers Send code only once the value differs from the current one ✅

### B9 — Not for a member who is also in another home

- [x] T9.1 integration — the three endpoints answer 403 "Only they can change their log-in, from My profile." for a member active in another home, and send nothing (parametrised) ✅
- [x] T9.2 unit — `test_a_past_membership_in_another_home_also_blocks_the_change` ✅
- [x] T9.3 unit — `test_your_own_row_is_not_blocked_by_your_other_home` ✅
- [x] T9.4 integration — `GET /members` says `contact_editable` false for a member in another home and true for one only here, with nothing about the other home ✅
- [x] T9.5 web integration — Edit tab shows the phone and email read-only with "Only they can change their log-in, from My profile." when not editable ✅

### B10 — A manager can't change the owner's, a member can't change anyone's

- [x] T10.1 integration — the three endpoints answer 403 for a manager on the owner and for a member (parametrised) ✅
- [ ] T10.2 web integration — Edit hidden for the owner's row from a manager _(Phase 1's `member-list-test.gts` pins `canEditDetails`)_

### B11 — Another home's member can't be changed and isn't revealed

- [x] T11.1 integration — the three endpoints answer 404 for another home's member and for an unknown id (parametrised) ✅ _(passed on its first run: `member_to_change` starts with Phase 1's `get_member`; kept to pin the new endpoints' home scoping)_

### B12 — A past member's log-in can't be changed

- [x] T12.1 unit — `test_a_past_members_log_in_cant_be_changed` ✅ (400 "Reactivate them first.")
- [x] T12.2 web integration — a past member's Edit tab shows the phone and email read-only with "Reactivate them to change their log-in." ✅ _(passed on its first run, because the note went in with T9.5; seen failing with the other note)_

### B13 — A phone or email in the wrong form is refused (422)

- [x] T13.1 integration — `POST …/contact/code` and `PUT …/contact` answer 422 for "not a phone" (parametrised; DELETE's 422 is T4.3) ✅ _(passed on its first run: both bodies use Phase 1's `ContactIn`; kept as each endpoint's one 422)_
- [x] T13.2 web integration — contact editor shows the field error on 422 ✅

### B14 — Change codes and log-in codes can't stand in for each other

- [x] T14.1 unit — `test_a_change_code_cannot_log_in` ✅
- [x] T14.2 unit — `test_a_log_in_code_cannot_confirm_a_change` ✅
- [x] T14.3 unit — `test_log_in_and_change_codes_share_the_send_limit` (a change code within a minute of a log-in code to the same phone is "too soon") ✅ _(passed on its first run: T14.1's scoped keys leave `sent_key` shared and give each scope its own lock; kept to pin the agreed rule)_
- [x] T14.4 unit — `test_wrong_change_codes_do_not_lock_log_in` ✅ _(passed on its first run: T14.1's scoped keys leave `sent_key` shared and give each scope its own lock; kept to pin the agreed rule)_

### B15 — A change or removal ends the member's sessions; adding one doesn't

- [x] T15.1 unit — `test_ending_a_persons_sessions_ends_every_one` (`test_sessions.py`) ✅
- [x] T15.2 unit — `test_ending_a_persons_sessions_can_keep_one` ✅
- [x] T15.3 integration — after the owner changes a member's phone, the member's open session answers 401 ✅
- [x] T15.4 integration — after the owner adds an email, the member's open session still works ✅ _(passed on its first run, because T15.3's code already had the `if replaced` guard; seen failing with the guard removed)_
- [x] T15.5 unit — `test_removing_a_contact_ends_the_members_sessions` ✅
- [x] T15.6 integration — the owner changing their own phone on Members stays logged in ✅ _(passed on its first run, because the router already passed the cookie as `keep_token`; seen failing with `keep_token=None`)_

### B16 — The person is told on their old and new phone or email

- [x] T16.1 unit — `test_partly_hidden_shows_only_the_end_of_a_phone_or_the_start_of_an_email` (`test_contact.py`, parametrised) ✅
- [x] T16.2 unit — `test_a_change_tells_the_existing_contacts_and_the_new_one` ✅ (a person with both changes the phone: the old phone and the email get the partly hidden new phone; the new phone gets "You can now log in")
- [x] T16.3 unit — `test_a_removal_tells_the_removed_contact` ✅
- [ ] T16.4 unit — nothing is sent when a change is refused _(the notices go out after the commit, so a refused code never reaches them; T6.1 shows nothing changed)_

### B17 — Every addition, change and removal is kept in the home's history

- [x] T17.1 unit — `test_a_change_is_kept_with_who_and_the_old_and_new_value` ✅
- [x] T17.2 unit — `test_a_removal_is_kept_in_the_history` ✅ _(passed on its first run, because the removal's history row went in with T17.1; seen failing without it)_

### B18 — Two changes to the same new phone or email at once: one wins

- [x] T18.1 unit — `test_a_phone_taken_while_saving_answers_409` ✅ (a `before_flush` hook on the test session commits a rival person with that phone from a second connection; the test deletes the rival afterwards)

### B19 — The members list shows the phone with the email under it _(dropped)_

- [ ] T19.1 web integration — a member with both shows the phone, then the email under it _(B19 dropped on 23 Nov 2026: the members list shows no phone or email in `WebMembers.html`; they are on the Edit tab)_

## Group 3 — My profile

Backend acceptance: `backend/tests/accounts/test_api.py::test_person_changes_their_own_phone_with_a_code`
Web acceptance: `web/tests/acceptance/profile-test.ts` › person changes their own phone on My profile

### B20 — Anyone opens My profile and sees their name, role, "member since", phone and email

- [x] T20.1 integration — `GET /me` answers the person's phone and email ✅
- [x] T20.2 web unit — `formatMonth('2026-11-21')` is "November 2026" ✅
- [x] T20.3 web integration — app shell: the name card links to My profile ✅
- [x] T20.4 web integration — profile page shows the name, "Owner · member since November 2026", the phone and the email ✅
- [x] T20.5 web integration — profile page shows just "Owner" for an owner who doesn't live in the home (no join date) ✅ _(passed on its first run, because the subtitle went in with T20.4; seen failing when "member since" is always added)_

### B21 — On My profile a person fixes their own name, for this home only

- [ ] T21.1 integration — `PATCH /me` changes the name in this home only _(Phase 1's `test_member_fixes_their_name_and_checks_their_details` and 1b's per-home tests already pin it)_
- [x] T21.2 web integration — profile page: Save sends the new name and shows it ✅

### B22 — A person adds, changes or removes their own phone or email, with a code

- [x] T22.1 integration — `POST /me/contact/code` sends the code to the new email, not to the phone ✅
- [x] T22.2 integration — `PUT /me/contact` with the code answers 200 with the person's phone and new email ✅
- [x] T22.3 integration — `DELETE /me/contact/email` answers 200 with only the phone ✅
- [x] T22.4 integration — refusals speak to the person: "That's already your phone or email.", "You need a phone or an email to log in.", "You have no email to remove." (parametrised) ✅
- [x] T22.5 integration — 422 for "hello" on the code and the save, and for `DELETE /me/contact/fax` (parametrised) ✅ _(passed on its first run: Pydantic, the `ContactKind` path parameter and `CurrentPersonDep` already refuse it; kept as each endpoint's check)_
- [x] T22.6 integration — the three endpoints answer 401 without a log-in (parametrised) ✅ _(passed on its first run: Pydantic, the `ContactKind` path parameter and `CurrentPersonDep` already refuse it; kept as each endpoint's check)_
- [ ] T22.7 integration — wrong code, someone else's phone, limits, scoped codes _(same service code as group 2's T6.1, T7.1–T7.2, T14.1–T14.4; rule 7)_
- [ ] T22.8 web integration — the editor's code, refusal and Remove states _(the same `ContactEditor`, tested in group 2; rule 7)_

### B23 — A person in several homes changes their own log-in without choosing a home

- [x] T23.1 integration — a person in two homes changes their phone with no `X-Colivo-Home` header and gets 200, not "Choose a home" ✅ _(passed on its first run, because the route already uses `CurrentPersonDep`; seen failing (409) with `CurrentMemberDep`)_
- [x] T23.2 unit — `test_your_own_change_is_kept_in_each_home_under_your_membership_there` ✅ _(passed on its first run, because group 2's `record_log_in_change` writes one row per home; seen failing when it records only one)_

### B24 — After changing or removing your own, other sessions end and this browser stays

- [x] T24.1 integration — logged in on two browsers, a person changes their phone in one: that one still works, the other answers 401 ✅ _(passed on its first run, because the `/me` routes already pass the cookie as `keep_token`; seen failing (401, 401) with `keep_token=None`)_
- [x] T24.2 integration — removing your own email keeps this browser logged in ✅ _(passed on its first run, because the `/me` routes already pass the cookie as `keep_token`; seen failing (401, 401) with `keep_token=None`)_
- [ ] T24.3 web — anything on the web _(nothing changes on screen; the web acceptance test shows the page still works after the change)_

## Fixes from the manual check (23 Nov 2026)

Bugs found by hand, each reproduced by a failing test first; the tests stay
as regression tests ([testing.md → Workflow](../testing.md#workflow)).

- [x] F1 web integration — contact editor keeps the field focused while you type ✅ (`{{#each}}` had no key, so every keystroke rebuilt the row)
