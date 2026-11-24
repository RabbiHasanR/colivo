# Phase 2 — Home Setup: Tests

Written by `/tdd`, one group at a time, in the format of
[testing.md → `tests.md` format](../testing.md#testsmd-format). Group 1 is
groundwork and has no tests.

## Group 2 — Rooms and home rules

Backend acceptance: `backend/tests/homes/test_api.py::test_owner_adds_a_room_and_puts_a_member_in_it`
Web acceptance: `web/tests/acceptance/rooms-test.ts` › owner adds a room and sees what each person pays

Agreed at Gate 2: `GET /rooms` returns `RoomsOut` (`rooms`, `people`,
`rent_total`) instead of a list, so the All rooms row is added up in the
backend, not the web.

### B1 — The owner or a manager adds a room; Rooms shows its people, rent and what each pays

- [x] T1.1 unit — `test_each_pays_divides_room_rent_by_the_people_in_it` (৳7,775 ÷ 2 = 3,887.50; ৳6,670 ÷ 3 = 2,223.33; nobody in it → None; parametrised)
- [x] T1.2 unit — `test_rooms_total_counts_people_and_adds_rents` (Room A + Room B → 3 people, ৳14,445; archived rooms left out)
- [x] T1.3 unit — `test_a_new_rooms_rent_starts_this_month_or_the_homes_first_month`
- [x] T1.4 integration — `POST /rooms` returns 201 with the room in the `StandardResponse` shape
- [x] T1.5 web unit — `formatTaka` shows ৳6,670, ৳3,887.50 and ৳1,00,000 (paisa only when there are some; Bangladeshi grouping)
- [x] T1.6 web integration — rooms page lists each room's people, rent and each pays ("—" for an empty room) and the All rooms row from the API's totals
- [x] T1.7 web integration — room form "Add a room" sends name, rent and beds, and the list shows the new room

### B2 — Room names are unique in a home, ignoring case

- [x] T2.1 unit — `test_a_room_name_taken_in_any_case_is_refused` (409 "There's already a room called Room B.")
- [x] T2.2 unit — `test_an_archived_rooms_name_can_be_used_again`
- [x] T2.3 unit — `test_database_refuses_two_active_rooms_with_one_name` (`test_models.py`, past the service)
- [x] T2.4 web integration — room form shows "There's already a room called Room B." on a 409

### B3 — A room needs at least 1 bed and a rent of ৳0 or more

- [x] T3.1 integration — `POST /rooms` with 0 beds, 51 beds, rent −1, rent 1.234 or a blank name returns 422 (parametrised)
- [x] T3.2 unit — `test_database_checks_room_beds_and_rent` (`test_models.py`: beds ≥ 1, `room_rent.amount` ≥ 0, `starts_on` on the 1st)
- [x] T3.3 web integration — room form shows the field's message from a 422

### B4 — The owner or a manager edits a room; a rent edit corrects the current rent and is kept in history

- [x] T4.1 unit — `test_a_rent_edit_corrects_the_current_rent_and_keeps_the_old_in_history` (still one `room_rent` row; `change_log` old 7,775 → new 8,000)
- [x] T4.2 integration — `PATCH /rooms/{id}` returns 200 with the changed room; 422 for a negative rent
- [x] T4.3 web integration — "Edit Room B" shows the room's values and saves the changes

### B5 — An empty room can be removed and stays on record; one with people can't

- [x] T5.1 unit — `test_removing_an_empty_room_archives_it` (leaves the list, row kept, `change_log` delete)
- [x] T5.2 unit — `test_a_room_with_people_in_it_cannot_be_removed` (400 "Move its people to another room first.")
- [x] T5.3 integration — `DELETE /rooms/{id}` returns 200 with the archived room
- [x] T5.4 web integration — Remove room asks to confirm, then the room leaves the list; the 400 message shows in the dialog

### B6 — A member is put in a room when added or from the Edit tab, and moved from a date; the list and My profile show it

- [x] T6.1 unit — `test_adding_a_member_with_a_room_puts_them_in_it_from_their_join_date`
- [x] T6.2 unit — `test_a_move_ends_the_old_room_and_starts_the_new_on_the_move_date` (both stays kept)
- [x] T6.3 unit — `test_no_room_takes_a_member_out_of_their_room`
- [x] T6.4 unit — `test_a_move_is_refused_for_their_own_room_a_future_date_a_date_before_their_stay_or_a_past_member` (400, parametrised)
- [x] T6.5 integration — `PUT /members/{id}/room` returns 200 `MemberOut` with the room; 422 for a missing `on`
- [x] T6.6 integration — `GET /members` and `GET /me` show the member's room (null when none)
- [x] T6.7 web integration — Add a member sends the chosen room; a full room shows "(full)" and can't be chosen
- [x] T6.8 web integration — Edit tab's Room and "Moves on" date send the move
- [x] T6.9 web integration — members list shows each member's room, "—" for none
- [x] T6.10 web integration — My profile's subtitle and the first log-in check show the room

### B7 — A room can't hold more people than its beds, and beds can't go below the people in it

- [x] T7.1 unit — `test_a_full_room_refuses_another_member` (400 "Room B is full: 2 beds.", on a move and on Add a member)
- [x] T7.2 unit — `test_beds_cannot_be_set_below_the_people_in_the_room` (400)
- [x] T7.3 unit — `test_two_members_put_in_the_last_bed_at_once_only_one_gets_it` (two committed connections, cleaned up after; the room row lock)
- [x] T7.4 web integration — Edit tab shows "Room B is full: 2 beds." from a 400

### B8 — A member is in one room at a time; the history keeps both

- [x] T8.1 unit — `test_database_refuses_two_open_room_stays_for_one_member` (`test_models.py`)
- [ ] T8.2 unit — move history keeps both stays _(T6.2 checks both stays; a second test would test it twice, rule 7)_

### B9 — Deactivating takes a member out of their room; reactivating puts them in no room

- [x] T9.1 unit — `test_deactivating_a_member_ends_their_room_stay_on_that_date`
- [x] T9.2 unit — `test_a_reactivated_member_is_in_no_room`
- [ ] T9.3 web integration — Edit tab shows "No room" after reactivation _(the list shows a null room as "—", T6.9)_

### B10 — A member can't change rooms or move anyone, and doesn't see Rooms

- [x] T10.1 integration — a member gets 403 from `GET`/`POST /rooms`, `PATCH`/`DELETE /rooms/{id}` and `PUT /members/{id}/room` (parametrised)
- [x] T10.2 web integration — the sidebar shows Home settings to the owner and managers, not to a member
- [x] T10.3 web acceptance — a member opening `/settings/rooms` is sent home (`access-test.ts`)

### B11 — Another home's room or member can't be seen, changed or used (404)

- [x] T11.1 integration — another home's room: `PATCH`, `DELETE`, and `PUT /members/{id}/room` with it; another home's member: `PUT /members/{id}/room` — all 404 and nothing changes (parametrised)

### B12 — The owner sets the home rules; Home settings shows them

- [x] T12.1 integration — `PUT /home/rules` saves them and `GET /home/rules` returns them, with `starts_on`
- [x] T12.2 unit — `test_a_home_has_no_rules_until_they_are_first_saved` (`GET` → null)
- [x] T12.3 web integration — home rules form shows the saved choices and saves new ones

### B13 — Each save keeps the earlier rules with their date; two saves on one day keep one version

- [x] T13.1 unit — `test_rules_saved_on_a_later_day_keep_the_earlier_version`
- [x] T13.2 unit — `test_two_saves_on_one_day_keep_one_version`
- [x] T13.3 unit — `test_database_refuses_two_rules_versions_from_one_date` (`test_models.py`)

### B14 — Deposit and notice months are whole numbers from 0 to 12

- [x] T14.1 integration — `PUT /home/rules` with 13, −1, 1.5 or an unknown policy returns 422 (parametrised)
- [x] T14.2 unit — `test_database_checks_deposit_and_notice_months` (`test_models.py`: 0–12)
- [ ] T14.3 web integration — form shows a 422 _(the form only offers the design's choices, 0–3 and 0–2, so it can't send a bad value)_

### B15 — Only the owner changes the home rules; a manager sees them read-only

- [x] T15.1 integration — a manager and a member get 403 from `PUT /home/rules`; a member also from `GET`
- [x] T15.2 web integration — a manager sees the rules without Save rules

### B16 — The checklist ticks rooms and rules once done, and each step opens its page (bills: group 4)

- [x] T16.1 unit — `test_setup_ticks_rooms_once_a_room_exists_and_rules_once_saved` (an archived room doesn't count)
- [x] T16.2 web integration — the rooms and rules steps link to Rooms and Home settings
