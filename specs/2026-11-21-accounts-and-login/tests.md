# Phase 1 — Accounts and Log-in: Tests

## Group 2 — Sign-up and session

Backend acceptance: `backend/tests/accounts/test_api.py::test_owner_signs_up_and_home_is_created`
Web acceptance: `web/tests/acceptance/sign-up-test.ts` › owner creates a home and lands on the new-home page

Removed with approval (design sketch, choice 9): the Phase 0 start-page
acceptance test and the server-status unit and integration tests (the start
page is gone); the bearer-token case of `handlers-test.ts` becomes T15.3;
`web/e2e/smoke.spec.ts` now checks that the log-in page opens.

### Phase 0 fixes

- [x] T0.1 integration — `test_invalid_input_answers_422_in_the_envelope` ✅: `success: false`, `message: "Validation Error"`, `errors: ["body.<field>: <msg>"]` (`backend/tests/core/test_api.py`)
- [x] T0.2 unit — `test_every_check_matches_its_enum` ✅: each `CHECK (col IN …)` in the test database equals its `StrEnum` (`backend/tests/core/test_models.py`)

### B1 — Owner signs up and the home is created

- [x] T1.1 unit — `test_sign_up_creates_the_home_and_its_owner` ✅: home name, area, first month; an active `owner` membership with the given name
- [x] T1.2 integration — `POST /api/v1/auth/sign-up` ✅ answers 201 with `MeOut` and sets the session cookie
- [x] T1.3 integration — `POST /api/v1/auth/sign-up` ✅ answers 422 for a missing, blank or over-80-character name or home name
- [x] T1.4 unit (database rule) — `test_home_and_member_checks_reject_bad_rows` ✅: blank or 81-character home or member name, 81-character area, first month not on the 1st; a badly formed Home ID is added with `home.code` in B4
- [x] T1.5 web integration — `sends a code, then creates the home with every field` ✅: sign-up form: "Send code and create home" asks for a code, then shows the code step ("Sent to …"), then sends every field with the code
- [x] T1.6 web integration — `shows 422 messages under their fields` ✅: sign-up form shows 422 messages under their fields

### B2 — "I live here too" decides whether the owner pays

- [x] T2.1 unit — `test_owner_stay_follows_i_live_here_too` ✅ (parametrised): ticked → one stay from the first month; not ticked → no stay
- [ ] T2.2 web integration — the checkbox is sent as `lives_here` _(skipped: covered by T1.5, which checks every field sent)_

### B3 — The first month is this month or next

- [x] T3.1 unit — `test_first_month_must_be_this_month_or_next` ✅ (parametrised, clock at 30 Nov 2026 19:00 UTC = 1 Dec 01:00 in Dhaka): December and January accepted; November and February answer 400
- [ ] T3.2 integration — the same 400 over HTTP _(skipped: the service raises the 400; T3.1 checks it, one behaviour, one test)_
- [x] T3.3 web unit — `first-month choices are this month and next in the home time zone` ✅: `firstMonthChoices` gives this month and next as `{ value, label }` in Asia/Dhaka, across the month boundary

### B4 — Each home gets a unique Home ID

- [x] T4.1 unit — `test_home_code_takes_two_letters_from_the_name` ✅ (parametrised): "Our Flat" → `OF-`, "Sunrise" → `SU-`, "A" → `AX-`, a Bangla name → `XX-`
- [x] T4.2 unit — `test_home_code_is_drawn_again_when_taken` ✅
- [x] T4.3 unit (database rule) — `test_two_homes_cannot_share_a_code` ✅
- [x] T4.4 web integration — `greets the person and shows the home name and its Home ID` ✅: the welcome block shows the home name and its Home ID

### B5 — Active in another home → "log in instead"

- [x] T5.1 unit — `test_sign_up_refused_when_already_active_in_a_home` ✅: 409, nothing created
- [x] T5.2 unit — `test_person_no_longer_active_anywhere_can_sign_up` ✅: the same person is reused
- [x] T5.3 unit (database rule) — `test_person_cannot_have_two_active_memberships` ✅
- [x] T5.4 web integration — `shows the 409 message when the person is already in a home` ✅: sign-up form shows the 409 message

### B6 — A code is sent, with the same answer for anyone

- [x] T6.1 unit — `test_code_goes_by_sms_to_a_phone_and_by_email_to_an_email` ✅ (parametrised): six digits, through the notifier
- [x] T6.2 integration — `test_codes_answer_the_same_for_anyone` ✅: `POST /api/v1/auth/codes` gives the same answer for a contact nobody uses and for an owner's
- [x] T6.3 integration — `test_codes_answer_422_for_something_that_is_not_a_phone_or_email` ✅: `POST /api/v1/auth/codes` answers 422 for something that isn't a phone or email
- [x] T6.4 web integration — `shows a refused contact under its field, until it is fixed` ✅: a refused code request shows its 422 under "Phone or email"; fixing it and sending again clears it and opens the code step _(added while building: the code step had no error handling)_

### B7 — One phone in any form is one person; emails ignore case

- [x] T7.1 unit — `test_contact_is_normalised` ✅ (parametrised): `01712 345678`, `+880 1712-345678` → `+8801712345678`; `Rabbi@Example.COM` → `rabbi@example.com`
- [x] T7.2 unit — `test_contact_that_is_not_a_phone_or_email_is_rejected` ✅ (parametrised): `hello`, `123`, `a@`, empty
- [x] T7.3 unit (database rule) — `test_two_people_cannot_share_a_phone_or_email` ✅ (parametrised)
- [x] T7.4 unit (database rule) — `test_person_checks_reject_bad_rows` ✅ (parametrised): no phone and no email, a phone not in E.164, an upper-case email
- [x] T7.5 unit — `test_email_in_any_letter_case_is_the_same_person` ✅: signing up by email keeps it as the person's email; the same email in other letters finds that person (409) _(added while building: nothing else checked that an email sign-up stores and finds `email`)_

### B8 — A code is used once

- [x] T8.1 unit — `test_code_works_only_once` ✅: a second use answers 400
- [x] T8.2 unit — `test_sign_up_refused_with_a_wrong_code` ✅: 400, nothing created

### B14 — A log-in lasts 30 days from the last use; log-out ends it

- [x] T14.1 unit — `test_session_ends_30_days_after_its_last_use` ✅: used on day 29 → still valid on day 58; unused for 31 days → gone
- [x] T14.2 integration — `test_log_out_ends_the_session_and_clears_the_cookie` ✅: `POST /api/v1/auth/log-out` ends the session (then `GET /me` is 401) and clears the cookie
- [x] T14.3 integration — `test_me_sends_the_cookie_again_for_30_days` ✅: `GET /api/v1/me` sends the cookie again with a 30-day `Max-Age`
- [x] T14.4 web acceptance — `owner logs out from the shell and is back on log-in` ✅: owner logs out from the shell and is back on log-in (`web/tests/acceptance/log-out-test.ts`)

### B15 — The cookie is out of page scripts' reach, and only the web app may send it

- [x] T15.1 integration — `test_session_cookie_is_httponly_lax_and_secure_when_set` ✅ (parametrised on `SESSION_COOKIE_SECURE`)
- [x] T15.2 integration — `test_only_the_web_origin_may_send_credentials` ✅: a pre-flight from the web origin gets 200, its origin and `Access-Control-Allow-Credentials: true`; another origin gets 400 and no allowed origin, so the browser never sends the request
- [x] T15.3 web unit — `auth handler sends cookies and no Authorization header` ✅: the auth handler sends every request with `credentials: 'include'` and no `Authorization` header

### B16 — Everything else needs a log-in

- [x] T16.1 integration — `test_endpoints_need_a_log_in` ✅ (parametrised over `GET /me`, `POST /auth/log-out`, `GET /home/setup`): no cookie, or an unknown token → 401
- [x] T16.2 web acceptance — `a visitor who is not logged in is sent to log-in` ✅: a visitor who isn't logged in opening `/` is sent to `/log-in` (`web/tests/acceptance/access-test.ts`)
- [x] T16.3 web acceptance — `someone logged in who opens log-in is sent home` ✅: someone logged in opening `/log-in` is sent home (same file)

### B17 — The owner and managers see the setup checklist

- [x] T17.1 unit — `test_new_home_checklist_has_only_home_created_done` ✅
- [ ] T17.2 unit — "Add members" is done once another member is active _(moved to group 4, where members can be added)_
- [ ] T17.3 integration — `GET /api/v1/home/setup` answers 200 for the owner _(skipped: the backend acceptance test calls it)_
- [x] T17.4 web integration — `shows each step done or not, and how many are done` ✅: the checklist shows each step done or not, and "1 of 5 done"

### B18 — Members don't get the checklist

- [x] T18.1 integration — `test_setup_answers_403_for_a_member` ✅: `GET /api/v1/home/setup` answers 403 for a member
- [x] T18.2 web acceptance — `a member's home page has no checklist and never asks for it` ✅: a member's home page has no checklist and never asks for it (`access-test.ts`) _(the route's guard was written with B16, before this test; seen failing by removing the guard)_

### B19 — Empty lists explain themselves

- [x] T19.1 web integration — `says what will appear, and offers its one action only when given` ✅: the empty state shows its reason and, when given, its one action
- [ ] T19.2 web acceptance — the new home shows the "Today's meals" and "All caught up" empty states _(skipped: the web acceptance test checks them)_

## Group 3 — Log-in

Backend acceptance: `backend/tests/accounts/test_api.py::test_owner_logs_back_in_with_one_time_code`
Web acceptance: `web/tests/acceptance/log-in-test.ts` › owner logs back in with a one-time code

### B9 — A code works for 5 minutes

- [x] T9.1 unit — `test_code_expires_after_5_minutes` ✅ (parametrised): used at 4:59 → works; at 5:00 → 400 `expired`
- [x] T9.2 unit — `test_code_nobody_asked_for_answers_expired` ✅: no code was sent → 400 `expired`
- [x] T9.3 integration — `test_log_in_with_an_expired_code_answers_400_with_the_reason` ✅: the error envelope carries `data: {reason: "expired"}`
- [x] T9.4 web integration — `an expired code says so and offers a new one` ✅: log-in form: an expired code shows "This code expired. Codes work for 5 minutes." and "Send a new code" asks for one

### B10 — Wrong codes: tries left, then a 15-minute lock

- [x] T10.1 unit — `test_wrong_code_says_how_many_tries_are_left` ✅: the first wrong code → 400 `wrong`, 4 tries left
- [x] T10.2 unit — `test_fifth_wrong_code_locks_the_contact_for_15_minutes` ✅: → 429 `locked`, 900 s to wait; even the right code is refused then
- [x] T10.3 unit — `test_lock_ends_after_15_minutes` ✅: 15 minutes later a new code is sent and works _(passes once the lock is clock-based; seen failing against a lock that only checks the key exists)_
- [x] T10.4 unit — `test_locked_contact_cannot_get_a_new_code` ✅: `issue_code` → 429 `locked`
- [x] T10.5 integration — `test_log_in_with_a_wrong_code_answers_400_with_tries_left` ✅: the envelope carries `data: {reason: "wrong", tries_left: 4}` _(built by T10.1 and T9.3; seen failing with the tries left removed)_
- [x] T10.6 web unit — `formats seconds left as minutes and seconds` ✅: `formatCountdown` gives `14:52`, `0:45`, `0:00`
- [x] T10.7 web integration — `a wrong code says how many tries are left` ✅: log-in form: a wrong code shows "That code isn't right. 3 tries left."
- [x] T10.8 web integration — `a locked phone shows the wait and offers another phone or email` ✅: log-in form: locked shows "Too many wrong codes", "try again in 14:52" and "Use a different phone or email", which goes back to the phone-or-email step

### B11 — A new code once a minute, 5 an hour, replacing the old one

- [x] T11.1 unit — `test_new_code_waits_a_minute_after_the_last` ✅: at once → 429 `too_soon`, 60 s; a minute later → sent
- [x] T11.2 unit — `test_only_5_codes_an_hour` ✅: the 6th within the hour → 429 `hourly_limit`, wait until the oldest is an hour old; then sent
- [x] T11.3 unit — `test_new_code_replaces_the_old_one` ✅: the old code → 400 `expired`; the new one works
- [x] T11.4 integration — `test_codes_say_when_the_next_one_can_be_sent` ✅: the first answer has `resend_in_seconds: 60`; asking again at once → 429 with `retry_in_seconds: 60`
- [x] T11.5 web unit — `error handler maps 429 to too-many and keeps its data` ✅: the error handler maps 429 to `too-many` and keeps its `data` (`handlers-test.ts`, a new test)
- [x] T11.6 web integration — `shows when a new code can be sent, then resends it` ✅: log-in form: the code step shows "Didn't get it? Resend in 1:00" and no Resend button; when it reaches 0:00, "Resend" sends a new code and says "New code sent to …. The old one no longer works."

### B12 — A person with an active membership logs in

- [x] T12.1 unit — `test_log_in_returns_the_active_membership` ✅
- [ ] T12.2 integration — `POST /api/v1/auth/log-in` answers 200 with `MeOut` and sets the cookie _(skipped: the backend acceptance test logs in, then calls `GET /me` with that cookie)_
- [x] T12.3 integration — `test_log_in_answers_422_for_something_that_is_not_a_phone_or_email` ✅
- [x] T12.4 web integration — `sends a code, then logs in with it` ✅: log-in form: Send code shows "Sent to …"; Log in sends the contact and code and tells the page the person is logged in

### B13 — No active membership → "Not added yet"

- [x] T13.1 unit — `test_log_in_with_no_active_membership_is_not_added_yet` ✅ (parametrised): never added; deactivated → 404, after the right code
- [x] T13.2 web integration — `not added yet: ask the home, or create a home, or try another` ✅: log-in page: a 404 shows "No home uses 01712 345678 yet", "ask its owner or manager", "Create my own home" (fills the sign-up form's phone or email) and "Try another phone or email" (back to the first step)

## Group 4 — Add members

Backend acceptance: `backend/tests/accounts/test_api.py::test_owner_adds_member_who_then_logs_in`
Web acceptance: `web/tests/acceptance/members-test.ts` › owner adds a member

### B17 — The setup checklist's "Add members" step

- [x] T17.2 unit — `test_members_step_is_done_once_another_member_is_active` ✅ _(moved here from group 2)_

### B20 — The owner or a manager adds a member, who gets a notice

- [x] T20.1 unit — `test_owner_adds_a_member_who_gets_a_notice` ✅: an active member, added by the owner, staying from the join date; one SMS to their phone naming the home
- [ ] T20.2 integration — `POST /api/v1/members` answers 201 with `MemberOut` _(skipped: the backend acceptance test adds a member through it)_
- [x] T20.3 integration — `test_add_member_answers_422_for_a_bad_name_or_contact` ✅ (parametrised)
- [x] T20.4 web integration — `sends the new member, then tells the page` ✅: add-member form: sends the name, phone or email, join date and role, then tells the page
- [x] T20.5 web integration — `shows each member's name, role, status and join date` ✅: member list: shows each member's name, role, status and join date

### B21 — Only the owner can add a manager

- [x] T21.1 integration — `test_only_the_owner_can_add_a_manager` ✅ (parametrised): the owner → 201; a manager → 403, nothing added
- [x] T21.2 web integration — `offers the Manager role to the owner only` ✅: add-member form: the "Manager" choice is there for the owner, not for a manager

### B22 — Members can't see or change the members list

- [x] T22.1 integration — `test_members_answer_403_for_a_member` ✅ (parametrised over `GET` and `POST /api/v1/members`)
- [x] T22.2 web acceptance — `a member has no Members link, and opening Members sends them home` ✅: a member has no Members link and opening `/members` sends them home (`members-test.ts`)

### B23 — Active in another home can't be added

- [x] T23.1 unit — `test_member_active_in_another_home_cannot_be_added` ✅: 409; no membership, no notice
- [x] T23.2 web integration — `shows why the API refused the member` ✅: add-member form shows the 409 message

### B24 — A deactivated member of this home is reactivated, not added again

- [x] T24.1 unit — `test_deactivated_member_of_this_home_is_not_added_again` ✅: 409 that says to reactivate them
- [x] T24.2 unit (database rule) — `test_person_has_one_membership_per_home` ✅
- [ ] T24.3 web integration — the form shows that 409 _(skipped: the same message path as T23.2)_

### B25 — Active members' names are unique, ignoring letter case

- [x] T25.1 unit — `test_two_active_members_cannot_share_a_name` ✅ (parametrised): "Maruf" and "maruf" → 409
- [x] T25.2 unit — `test_a_deactivated_members_name_can_be_used_again` ✅ _(passes once only active members are checked; seen failing against a check of every member)_
- [x] T25.3 unit (database rule) — `test_database_refuses_two_active_members_with_one_name` ✅

### B26 — The owner or a manager changes a member's name or join date

- [x] T26.1 unit — `test_owner_changes_a_members_name_and_join_date` ✅: the name changes and the first stay starts on the new date
- [x] T26.2 unit — `test_join_date_cannot_be_after_the_end_of_the_first_stay` ✅: 400; also 400 for an owner with no stay (design choice 4)
- [x] T26.3 unit — `test_new_name_cannot_be_one_already_taken` ✅: 409
- [x] T26.4 integration — `test_change_member_answers_422_for_a_blank_name` ✅
- [x] T26.5 web integration — `sends a member's new name and join date, then tells the page` ✅: edit-member form: sends the new name and join date, then tells the page

### B27 — The first log-in check

- [x] T27.1 unit — `test_me_says_who_added_the_member_and_whether_they_checked` ✅: a new member → added by "Rabbi Hasan", not checked; the owner who signed up → checked
- [x] T27.2 unit — `test_member_fixes_their_name_and_checks_their_details` ✅
- [x] T27.3 integration — `test_change_me_answers_422_for_a_blank_name` ✅
- [x] T27.4 web integration — `shows where they were added, then sends their name` ✅: first log-in check: shows the home, role, join date and who added them; "Go to my home" sends the name
- [x] T27.5 web acceptance — `a member checks their details once, then goes straight home` ✅: a member who hasn't checked their details sees the check first, then their home; the next time, straight home (`first-log-in-test.ts`)

### B28 — Another home's member, or an unknown id, gives 404

- [x] T28.1 integration — `test_changing_another_homes_member_answers_404` ✅ (parametrised): another home's member, an id that doesn't exist; nothing of the other home in the body
- [x] T28.2 integration — `test_members_list_shows_only_this_homes_members` ✅ _(passes once the list filters by home; seen failing without the filter)_

### B29 — Invalid names and contacts are refused with a clear message

- [ ] T29.1 backend — _(covered: T20.3, T26.4 and T27.3 are the 422 tests of the three endpoints)_
- [x] T29.2 web integration — `shows 422 messages under their fields` ✅: add-member form shows 422 messages under their fields

### B30 — Every change to a member is kept in the history

- [x] T30.1 unit — `test_record_change_keeps_who_when_and_old_and_new_values` ✅ (`backend/tests/history/test_service.py`)
- [x] T30.2 unit — `test_adding_and_changing_members_is_recorded` ✅ (parametrised): added (create, new values); name or join date changed (update, old and new values); own name fixed (update, by the member)

## Group 5 — Roles, deactivate and reactivate

Backend acceptance: `backend/tests/accounts/test_api.py::test_owner_deactivates_member_who_can_no_longer_log_in`
Web acceptance: `web/tests/acceptance/member-status-test.ts` › manager deactivates and reactivates a member
End-to-end: `web/e2e/accounts.spec.ts` › the owner signs up, adds a member who logs in, then deactivates them (replaces `smoke.spec.ts`)

### B28 — The new endpoints never reach another home's member

- [x] T28.3 integration — `test_status_and_role_changes_answer_404_for_another_homes_member` ✅ (parametrised over role, deactivate, reactivate) _(`get_member` already scoped them; seen failing without its home check)_

### B31 — The owner gives and takes away the Manager role

- [x] T31.1 unit — `test_owner_makes_a_member_a_manager_and_back` ✅ (parametrised): member → manager, manager → member; recorded in the history
- [x] T31.2 integration — `test_only_the_owner_changes_roles` ✅ (parametrised): a manager, a member → 403
- [x] T31.3 integration — `test_change_role_answers_422_for_a_role_that_cannot_be_given` ✅ (`owner`, an unknown role) _(the schema came with T31.1; seen failing with `RoleIn` widened to every role)_
- [x] T31.4 web integration — role editor: the owner sees "Make manager" for a member and "Remove manager" for a manager, and it sends the new role; a manager sees neither

### B32 — The owner's role can't change; a home has one owner

- [x] T32.1 unit — `test_owners_own_role_cannot_change` ✅: 400
- [x] T32.2 unit (database rule) — `test_home_has_at_most_one_owner` ✅
- [x] T32.3 web integration — member list: the owner's row has no role button

### B33 — Deactivating, from a date, logs the member out at once

- [x] T33.1 unit — `test_deactivating_closes_the_stay_on_the_chosen_date` ✅: inactive; the open stay ends that day; recorded in the history
- [x] T33.2 unit — `test_deactivation_date_must_be_today_or_earlier_and_in_the_stay` ✅ (parametrised): tomorrow, before the stay began → 400
- [x] T33.3 unit — `test_inactive_member_cannot_be_deactivated_again` ✅: 409
- [x] T33.4 integration — `test_deactivated_member_is_logged_out_at_once` ✅: the member's session answers 401 on its next request
- [x] T33.5 unit (database rule) — `test_stay_cannot_end_before_it_starts` ✅
- [x] T33.6 integration — `test_deactivate_answers_422_without_a_date` ✅ _(the schema came with T33.1; seen failing with a default date)_
- [x] T33.7 web integration — `starts at today; Confirm deactivates, Cancel sends nothing` ✅: deactivate dialog: starts at today; Confirm sends the date and tells the page; Cancel sends nothing
- [x] T33.8 web acceptance — `a page whose session ended goes to log-in` ✅: a page that gets a 401 (the session ended) goes to log-in (`member-status-test.ts`)

### B34 — The owner can't be deactivated; a manager can't deactivate a manager

- [x] T34.1 unit — `test_owner_cannot_be_deactivated` ✅: 400
- [x] T34.2 unit — `test_manager_cannot_deactivate_another_manager` ✅: 403
- [x] T34.3 unit (database rule) — `test_owner_is_always_active` ✅
- [x] T34.4 web integration — `offers Deactivate only for members the viewer may deactivate` ✅: member list: no Deactivate on the owner's row; a manager sees none on a manager's row

### B35 — Reactivating, from the date charges start again

- [x] T35.1 unit — `test_reactivating_opens_a_new_stay_from_the_chosen_date` ✅: active; the old stay kept and a new one opened; recorded in the history
- [x] T35.2 unit — `test_reactivation_date_must_be_after_the_deactivation` ✅: the same day → 400
- [x] T35.3 unit — `test_active_member_cannot_be_reactivated` ✅: 409
- [x] T35.4 unit (database rule) — `test_member_has_one_open_stay` ✅
- [x] T35.5 integration — `test_reactivate_answers_422_without_a_date` ✅
- [x] T35.6 web integration — `sends the date charges start again, then tells the page` ✅: reactivate dialog: Confirm sends the date charges start again and tells the page

### B36 — Reactivating is refused while active elsewhere or the name is taken

- [x] T36.1 unit — `test_reactivating_someone_active_in_another_home_is_refused` ✅: 409
- [x] T36.2 unit — `test_reactivating_into_a_taken_name_is_refused` ✅: 409
- [x] T36.3 web integration — reactivate dialog shows the API's 409 message

### B37 — Current and past members on separate tabs

- [x] T37.1 integration — `test_members_list_includes_deactivated_members_with_their_status` ✅ _(the list already had everyone; seen failing with the list limited to active members)_
- [x] T37.2 web integration — `current members with Deactivate, past members with Reactivate` ✅: member tabs: Current lists the active members with Deactivate; Past lists the deactivated ones with Reactivate
