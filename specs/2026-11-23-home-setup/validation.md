# Phase 2 — Home Setup: Validation

Setup from a clean checkout: `cp .env.example .env`, `docker compose up -d`
(now with MinIO), `cd backend && uv sync && uv run alembic upgrade head`,
`cd web && pnpm install --frozen-lockfile`. `alembic upgrade head` must
apply this phase's migrations cleanly to a Phase 1c database that has homes,
members, a past member and a person in two homes in it.

## Behaviours

**Gate 1** of [testing.md](../testing.md#spec-time-feature-spec). Money
against the October 2026 spreadsheet doesn't apply yet: rent and estimates
are stored, not charged (Phase 6). The one money figure, Each pays, is
checked against the October sheet's rooms (Room A ৳6,670 for one person,
Room B ৳7,775 for two → ৳3,887.50 each). Phase 1, 1b and 1c behaviours
still hold.

### Rooms

- B1 — The owner or a manager adds a room with a name, its rent and its
  beds; Rooms lists each room with the people in it, its rent and what each
  person pays (rent ÷ people in it, ৳7,775 for two → ৳3,887.50). [backend]
  [web]
- B2 — Room names are unique in a home, ignoring case: "There's already a
  room called Room B." [backend] [web]
- B3 — A room needs at least 1 bed and a rent of ৳0 or more; anything else
  is refused with a clear message (422). [backend] [web]
- B4 — The owner or a manager edits a room's name, rent and beds; a rent
  edit corrects the room's current rent, and the old value is kept in
  history. [backend] [web]
- B5 — The owner or a manager removes a room nobody is in; it leaves the
  list and stays on record. A room with people in it can't be removed:
  "Move its people to another room first." [backend] [web]
- B6 — A member is put in a room when they are added, or from the Edit tab,
  which also moves them from a chosen date; the members list and the
  member's own My profile show their room. [backend] [web]
- B7 — A room can't hold more people than its beds ("Room B is full: 2
  beds."), and its beds can't be set below the people already in it.
  [backend] [web]
- B8 — A member is in one room at a time: a move ends the old room from the
  move date, and the history keeps both. [backend]
- B9 — Deactivating a member takes them out of their room from the same
  date; a reactivated member is in no room until one is chosen. [backend]
  [web]
- B10 — A member can't add, change or remove rooms or move anyone (403),
  and doesn't see Rooms. [backend] [web]
- B11 — Another home's room or member can't be seen, changed or used for a
  room, and the answer doesn't reveal they exist (404). [backend]

### Home rules

- B12 — The owner sets the deposit months, the notice months, the default
  way to share a landlord's rent change and who covers a rent gap; Home
  settings shows them. [backend] [web]
- B13 — Each save keeps the earlier rules with the date they applied from;
  two saves on the same day keep one version. [backend]
- B14 — Deposit and notice months are whole numbers from 0 to 12; anything
  else is refused with a clear message (422). [backend] [web]
- B15 — Only the owner changes the home rules: a manager sees them
  read-only, and a manager's or member's change is refused (403). [backend]
  [web]
- B16 — The setup checklist ticks "Add rooms and rent" once the home has a
  room, "Set home rules" once the rules are saved, and "Add bills" once it
  has a bill besides Household and Landlord rent; each step opens its page.
  [backend] [web]

### Home & landlord

- B17 — The owner changes the home's name, address, lease start and the
  landlord's monthly rent; a rent change corrects the current rent and is
  kept in history. [backend] [web]
- B18 — The owner adds the landlord with a name, start date, phones and
  emails, and edits them later on Home & landlord; a home has one active
  landlord. [backend] [web]
- B19 — Rooms and Home & landlord compare the rooms' total rent with the
  landlord's: "৳1,200 short of landlord", "৳300 over landlord" or "Matches
  the landlord's rent". [backend] [web]
- B20 — Only the owner changes Home & landlord: a manager sees it
  read-only, and a manager's or member's change is refused (403). [backend]
  [web]

### Contacts

- B21 — The owner or a manager adds a contact with a kind, name and start
  date, any number of phones and emails each with an optional label, an
  account or customer ID and a note. [backend] [web]
- B22 — A contact has one primary phone and one primary email; the first of
  each is primary unless another is chosen, and two primaries are refused.
  [backend] [web]
- B23 — A contact's phones and emails are checked like log-ins: a phone in
  the wrong form or an email that isn't one is refused with a clear message
  (422). [backend] [web]
- B24 — The owner or a manager edits a contact, and every change is kept in
  history; the landlord is changed only by the owner, on Home & landlord.
  [backend] [web]
- B25 — The owner or a manager marks a contact as left with an end date (not
  before their start): they move to Past contacts with all their details
  and are never deleted. [backend] [web]
- B26 — Every member sees the names, kinds and phones of current contacts
  other than the landlord, and nothing else: no landlord, emails, account
  IDs, notes, documents or past contacts. [backend] [web]
- B27 — A member can't add, change or end a contact (403). [backend] [web]
- B28 — Another home's contact can't be seen or changed, and the answer
  doesn't reveal it exists (404). [backend]
- B29 — The sidebar's Contacts card names the current cook and internet
  provider and how many contacts are past ("Cook Rahima · Internet SpeedNet
  · 1 past"; members don't see the past count). [web]

### Bills & categories

- B30 — Every home has the Household and Landlord rent bills, new homes
  from sign-up and existing homes from this phase; neither can be removed.
  [backend] [web]
- B31 — The owner or a manager adds a bill with a name, a group (prepaid,
  postpaid, rent, other), an optional estimate every month and an optional
  Paid to contact; the list shows the split from the group (By room for
  rent, Equal otherwise), the estimate or "Actual only", and the contact's
  name and primary phone. [backend] [web]
- B32 — Bill names are unique in a home, ignoring case: "There's already a
  bill called Cook." [backend] [web]
- B33 — An estimate is ৳0 or more; a negative one is refused (422), and
  clearing it means "Actual only". [backend] [web]
- B34 — Paid to must be a current contact of this home; a contact marked as
  left stays on their bills, shown "(left)", until the bill is changed.
  [backend] [web]
- B35 — The owner or a manager edits or removes a bill; a removed bill
  leaves the list and stays on record, and every change, estimates
  included, is kept in history with who, when and the old and new value.
  [backend] [web]
- B36 — A member can't see or change bills (403), and another home's bill or
  contact can't be used (404). [backend] [web]

### Files, ID documents and photos

- B37 — An upload is accepted only in the types and sizes its purpose
  allows (images up to 5 MB; PDF up to 10 MB for contact documents), and
  only from someone allowed to make that kind of upload; anything else is
  refused before the file is sent. [backend] [web]
- B38 — A file is never public: it can be viewed only through a link that
  ends after about 5 minutes, given only to someone allowed to see it.
  [backend]
- B39 — A record accepts only a finished upload of the same home and the
  right purpose; an unfinished upload, one whose size or type differs from
  what was asked, or another home's file is refused. [backend]
- B40 — The owner or a manager adds a member's ID document (type, number,
  front and back; the back is optional for a passport) on Add a member or
  from the Edit tab; the members list shows "NID ✓" or "ID missing".
  [backend] [web]
- B41 — Replacing an ID document keeps the old one in history; a member has
  one current ID document. [backend] [web]
- B42 — Only the owner and managers see ID document images, past members'
  included; a member sees only their own, on My profile, and anyone else's
  is refused (403). [backend] [web]
- B43 — ID documents and contact documents are stored encrypted. [backend]
- B44 — A member sets their own profile photo at the first log-in check or
  on My profile, and the owner or a manager can set it from the Edit tab;
  it is shown instead of their initials. [backend] [web]
- B45 — The owner or a manager adds a contact's photo and documents (the
  owner, for the landlord's lease and NID); documents are seen only by the
  owner and managers. [backend] [web]
- B46 — The owner adds home photos on Home & landlord, and the owner or a
  manager adds one photo per room. [backend] [web]
- B47 — Removing a document or photo takes it off its record and keeps it in
  history. [backend] [web]
- B48 — Uploads left unfinished for 24 hours are removed by the clean-up
  command, and finished ones are never touched. [backend]

### Security review follow-ups

Filled in after the `/security-review` in the last group: each finding the
user accepts as a fix becomes a behaviour here, built test-first.

## Automated checks

| Check                     | Command                                                                                                         | Pass criteria                                                                                  |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fast tests                | `make test-fast`                                                                                                | All pass; backend under 60 s, web under 90 s                                                   |
| All tests with end-to-end | `docker compose up -d && make test`                                                                             | All pass, every earlier journey and the home-setup journey included; none skipped              |
| Lint                      | `make lint`                                                                                                     | Ruff, pyright, ESLint, ember-template-lint, Stylelint, Glint clean                             |
| Format                    | `make format-check`                                                                                             | Ruff format and Prettier report no changes                                                     |
| No missing migration      | `make backend-migrations-check`                                                                                 | "No new upgrade operations detected"                                                           |
| Migrations up and down    | `cd backend && uv run alembic downgrade base && uv run alembic upgrade head` on the test database               | Both succeed                                                                                   |
| Phase 1c data migrates    | `alembic downgrade 1c59687c8639`, seed homes with members, a past member and a person in two homes, `alembic upgrade head` | Succeeds; every home has Household and Landlord rent; everyone still logs in          |
| Value sets match enums    | The CHECK-vs-`StrEnum` test for every new value set                                                             | Passes                                                                                         |
| Contract and web types    | `make api-export api-types && git diff --exit-code api/ web/app/data/types/`                                    | No diff                                                                                        |
| Web build                 | `cd web && pnpm build`                                                                                          | Succeeds                                                                                       |
| CI                        | `CI OK` on the pull request                                                                                     | Green                                                                                          |
| Security review           | `/security-review` on the branch                                                                                | No open high or medium finding; each finding fixed (test first) or recorded with the user's OK |

## TDD record

Every group's section in `tests.md` (groups 2–5) is complete: each selected
test is ✅, each unticked test has its reason, and no `xfail` or `test.todo`
mark is left. Any earlier test changed by this phase (for example the setup
checklist's steps, or `MemberOut` gaining `room`) is named in `tests.md`
with what changed and why, and was approved at Gate 2. Group 1 is
groundwork and has no tests.

## Manual checks

1. **End-to-end walkthrough against the design.** Sign up as Rabbi and
   create "Our Flat" (`WebAuth.html`). On Home & landlord
   (`WebSetHome.html`) set the address, landlord rent ৳15,645 and lease
   start, add the landlord Nurul Hossain with two phones (one "bKash") and
   an email, a home photo and the lease PDF. On Rooms (`WebSetRooms.html`)
   add Room A (৳6,670, 1 bed) and Room B (৳7,775, 2 beds); the total line
   says "৳1,200 short of landlord". Add Hijam and Maruf to Room B with an ID
   document each (`WebMembers.html`); Room B shows ৳3,887.50 each. Save the
   home rules (`WebSettings.html`). On Contacts (`WebSetContacts.html`) add
   Rahima (cook) and SpeedNet (internet, customer ID); on Bills & categories
   (`WebSetBills.html`) add Cook (Postpaid, ৳2,500 estimate, paid to Rahima)
   and Internet. The checklist shows 5 of 5 done (`WebHomeEmpty.html`).
   Mark Rahima as left: she is under Past, and Cook shows "Rahima Begum
   (left)".
2. **As a member.** Log in as Maruf: no Home settings in the sidebar; My
   profile shows Room B and "ID document · NID · uploaded ✓" with View;
   Contacts shows SpeedNet's name and phone only, no landlord. Set a profile
   photo; it replaces his initials in the sidebar and on Rabbi's Members
   list.
3. **As a manager.** Make Hijam a manager. Home rules and Home & landlord are
   read-only for him; he can add a room, a contact and a bill, and see
   Maruf's ID images.
4. **Files.** Try a 6 MB photo and a `.exe`: refused before upload. Copy an
   ID image's link, wait 6 minutes, open it: refused. Open the MinIO console:
   the bucket has no public access, keys are under `homes/<home_id>/`, and ID
   documents show server-side encryption.
5. **Widths.** Home settings, Home & landlord, Rooms, Contacts, Bills &
   categories, Members and My profile at **320px, 768px and 1280px**, in the
   light scheme (the design's only one): no horizontal page scroll, wide
   tables scroll in their own box, file buttons and phone rows fit, every
   tap target is at least 44×44px.
6. **Keyboard only.** Add a room, add a contact with two phones and choose
   the primary, add a bill with a Paid to contact, and upload an ID front
   using only the keyboard: visible focus ring, logical order, the confirm
   dialogs trap and return focus, and errors are read out.
7. **Polish and Lighthouse.** Lighthouse (mobile) on Home settings, Contacts
   and Members: no accessibility or best-practice failures, no console
   errors, no third-party requests, and the wording matches
   [Screens](requirements.md#screens).

## Done means

- Every automated check above passes and every manual check is done.
- `specs/data-model.md` (this phase's tables marked _built_ and matching the
  migrations), `specs/tech-stack.md` (**Decided in Phase 2**, file storage
  built, known limitations), `README.md` (MinIO in the local setup),
  `specs/roadmap.md` (Phase 2 complete; starting balances and custom deals
  under Phase 6), `colivo-design/requirements.md` (change lines on FR-57
  and FR-60 where the phase decided them) and `CHANGELOG.md` are updated.
- `api/openapi.json` is current.
- No secrets, `.env`, database files, uploaded files, MinIO data or presigned
  links are committed.
