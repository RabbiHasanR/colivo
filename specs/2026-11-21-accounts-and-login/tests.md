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
- [ ] T17.2 unit — "Add members" is done once another member is active _(group 4: needs members)_
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
- [x] T9.4 web integration — log-in form: an expired code shows "This code expired. Codes work for 5 minutes." and "Send a new code" asks for one

### B10 — Wrong codes: tries left, then a 15-minute lock

- [x] T10.1 unit — `test_wrong_code_says_how_many_tries_are_left` ✅: the first wrong code → 400 `wrong`, 4 tries left
- [x] T10.2 unit — `test_fifth_wrong_code_locks_the_contact_for_15_minutes` ✅: → 429 `locked`, 900 s to wait; even the right code is refused then
- [x] T10.3 unit — `test_lock_ends_after_15_minutes` ✅: 15 minutes later a new code is sent and works _(passes once the lock is clock-based; seen failing against a lock that only checks the key exists)_
- [x] T10.4 unit — `test_locked_contact_cannot_get_a_new_code` ✅: `issue_code` → 429 `locked`
- [x] T10.5 integration — `test_log_in_with_a_wrong_code_answers_400_with_tries_left` ✅: the envelope carries `data: {reason: "wrong", tries_left: 4}` _(built by T10.1 and T9.3; seen failing with the tries left removed)_
- [x] T10.6 web unit — `formatCountdown` gives `14:52`, `0:45`, `0:00`
- [x] T10.7 web integration — log-in form: a wrong code shows "That code isn't right. 3 tries left."
- [x] T10.8 web integration — log-in form: locked shows "Too many wrong codes", "try again in 14:52" and "Use a different phone or email", which goes back to the phone-or-email step

### B11 — A new code once a minute, 5 an hour, replacing the old one

- [x] T11.1 unit — `test_new_code_waits_a_minute_after_the_last` ✅: at once → 429 `too_soon`, 60 s; a minute later → sent
- [x] T11.2 unit — `test_only_5_codes_an_hour` ✅: the 6th within the hour → 429 `hourly_limit`, wait until the oldest is an hour old; then sent
- [x] T11.3 unit — `test_new_code_replaces_the_old_one` ✅: the old code → 400 `expired`; the new one works
- [x] T11.4 integration — `test_codes_say_when_the_next_one_can_be_sent` ✅: the first answer has `resend_in_seconds: 60`; asking again at once → 429 with `retry_in_seconds: 60`
- [x] T11.5 web unit — the error handler maps 429 to `too-many` and keeps its `data` (`handlers-test.ts`, a new test)
- [x] T11.6 web integration — log-in form: the code step shows "Resend in 1:00" and no Resend button; when it reaches 0:00, "Resend" sends a new code and says "New code sent to …. The old one no longer works."

### B12 — A person with an active membership logs in

- [x] T12.1 unit — `test_log_in_returns_the_active_membership` ✅
- [ ] T12.2 integration — `POST /api/v1/auth/log-in` answers 200 with `MeOut` and sets the cookie _(skipped: the backend acceptance test logs in, then calls `GET /me` with that cookie)_
- [x] T12.3 integration — `test_log_in_answers_422_for_something_that_is_not_a_phone_or_email` ✅
- [x] T12.4 web integration — log-in form: Send code shows "Sent to …"; Log in sends the contact and code and tells the page the person is logged in

### B13 — No active membership → "Not added yet"

- [x] T13.1 unit — `test_log_in_with_no_active_membership_is_not_added_yet` ✅ (parametrised): never added; deactivated → 404, after the right code
- [x] T13.2 web integration — log-in page: a 404 shows "No home uses 01712 345678 yet", "ask its owner or manager", "Create my own home" (fills the sign-up form's phone or email) and "Try another phone or email" (back to the first step)
