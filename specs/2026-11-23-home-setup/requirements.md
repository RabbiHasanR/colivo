# Phase 2 — Home Setup: Requirements

## Context

Phase 2 follows Phases 1, 1b and 1c in the [roadmap](../roadmap.md). Those
delivered sign-up, log-in with a one-time code, members and roles, a person
in several homes, and changing a phone or email. A new home shows a setup
checklist (FR-95) whose "Add rooms and rent", "Set home rules" and "Add
bills" steps can't be done yet.

After this phase the owner can describe the home the app will calculate
for: its **rooms** and who lives in each, the **home rules**, the home and
its **landlord**, the people and companies it deals with (**contacts**), its
**bills** and their optional estimates, and the files that go with them:
**ID documents**, **profile photos**, contact documents and home and room
photos. It serves the [mission](../mission.md)'s "the owner sets up rooms,
rent, home rules and bills" and "the owner or a manager keeps the home's
contacts", and keeps every home's data separate (NFR-03). Nothing here moves
money; later phases read these tables (meals in Phase 3, statements and rent
changes in Phase 6, deposits and notice in Phase 7).

Moved out of this phase at the spec (23 Nov 2026): **starting balances**
and **custom deals**. Both need `month`, `fund`, `entry` and `bill`
(Phases 4–6); starting balances are the same carry-forward records month
close writes (FR-24), and a custom deal's preview is the BR-4 split. Both go
to Phase 6.

Design references:

- `colivo-design/web/WebSettings.html`: Home settings, the hub, with the
  Home rules card and the Sections list.
- `colivo-design/web/WebSetHome.html`: Home & landlord.
- `colivo-design/web/WebSetRooms.html`: Rooms.
- `colivo-design/web/WebSetContacts.html`: Contacts.
- `colivo-design/web/WebSetBills.html`: Bills & categories.
- `colivo-design/web/WebMembers.html`: Members & roles (Room and ID
  columns, Add a member with room and ID document).
- `colivo-design/web/WebProfile.html`: My profile (photo, room, ID
  document).
- `colivo-design/web/WebHomeEmpty.html`: the setup checklist and the app
  shell (sidebar Contacts card).

Technical rules: [tech-stack.md](../tech-stack.md); schema:
[data-model.md](../data-model.md).

## Scope

**In scope**

- **Rooms:** add, edit and remove rooms with rent and beds; put a member in
  a room and move them; "Each pays" per room
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- **Home rules:** deposit months, notice months, the default way to share a
  rent change and who covers a rent gap, each save kept with the date it
  applies from
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- **Home & landlord:** home name, address, landlord rent, lease start, and
  the landlord with phones and emails; the room total against the landlord's
  rent
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- **Contacts:** add, edit and mark as left; any number of phones and emails;
  Past contacts; members see names and phones only
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- **Bills & categories:** a new home's Household and Landlord rent bills;
  add, edit and remove bills with a group, an optional estimate every month
  and an optional Paid to contact
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- **Files:** private uploads (presigned POST, presigned GET); ID documents;
  profile photos; contact photos and documents (the lease among them); home
  and room photos
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- The setup checklist's rooms, rules and bills steps become doable.
- `/security-review` of the branch.

**Out of scope**

- Starting balances (`WebSetStart.html`) and custom deals
  (`WebSetDeals.html`): Phase 6 (above).
- Meal sessions (the Home settings card): Phase 3.
- Fund keepers and Funds and keepers settings: Phase 4.
- One month's estimate (on Utilities), dated rent changes with a preview
  ("Change rent"), rent overrides: Phase 6.
- Deposit needed on Add a member, the landlord deposit, vacant seats ("Room B
  (after Maruf)"), the deposit and notice snapshot per member: Phase 7.
- Bill payments, so payment counts on Contacts: Phase 5.
- A Google Maps location picker (FR-57): address text only; revisit in
  Phase 9.
- Replacing the landlord (a new lease): the one landlord is edited in place.
- A scheduled clean-up of unfinished uploads: the command exists, scheduling
  waits for the background jobs decision (Phase 9).
- A real SMS or email provider; the mobile app.

## Features

### Rooms

Who: the owner and managers. Members see only their own room.

- A room has a name (unique in the home, ignoring case), a rent (৳ 0 or
  more) and beds (at least 1) (FR-02).
- **Each pays** = room rent ÷ the people in the room now (FR-03, BR-3). A
  room with nobody in it pays nothing, and its rent shows as a shortfall
  against the landlord's rent.
- Beds are the most people a room holds: putting a member in a full room is
  refused, and beds can't be lowered below the people already in it.
- A member is in at most one room at a time. They are put in one when added
  (Add a member's **Room**), or from the Edit tab, which also moves them
  (from a date). Deactivating a member takes them out of their room from
  the same date; reactivating puts them in no room until one is chosen.
- Editing a room's rent corrects its current rent (no month has been closed
  yet); the old value is kept in history. Dated rent changes come in
  Phase 6.
- Removing a room archives it; it is kept on record. A room with people in
  it can't be removed.

### Home rules

Who: the owner changes them; managers see them.

- Deposit months (0–12), notice months (0–12; a minimum, FR-34), the default
  way to share a landlord's rent change (same amount each, or same percent,
  BR-19) and who covers a gap (others equally, by rent share, home fund, ask
  members, BR-20) (FR-28, FR-55).
- A new home has no rules until the owner first saves them; the checklist's
  "Set home rules" is done from then on. Each save keeps the earlier rules
  with the date they applied from (US-R1); two saves on one day keep one
  version. "Current members keep the rules from when they joined" (BR-11):
  Phase 7 reads the version in force on each member's join date.

### Home & landlord

Who: the owner changes it; managers see it. Members never see the
landlord's details (FR-112).

- Home name, address (text, no map) and lease start; the landlord's monthly
  rent, corrected in place like room rent until Phase 6.
- The landlord is the home's one active landlord contact (FR-109): name,
  phones and emails (one primary of each), photo and documents (lease
  agreement, NID) from group 5.
- Rooms and Home & landlord show the room total against the landlord's rent:
  "৳1,200 short of landlord", "৳300 over landlord" or "Matches the
  landlord's rent" (US-C5).

### Contacts

Who: the owner and managers add, edit and end contacts and see everything;
every member sees names and phones of active contacts other than the
landlord (FR-112).

- Kind (cook, internet, electricity, gas, caretaker, other; the landlord is
  on Home & landlord), name, start date, any number of phones and emails
  with an optional label and one primary of each, an optional account or
  customer ID, a note (FR-109). Photo and documents from group 5.
- Phones are checked and stored like log-in phones (E.164, Bangladesh by
  default), emails in lower case.
- **Mark as left** with an end date (not before the start): the contact
  moves to Past contacts with all their details; contacts are never deleted
  (FR-110). A replacement is a new contact.
- Account IDs, notes, emails and documents are for the owner and managers
  only (FR-112).

### Bills & categories

Who: the owner and managers.

- A new home starts with **Household** (Other, FR-05) and **Landlord rent**
  (Rent, paid to the landlord once there is one); existing homes get both
  too. Neither can be removed.
- A bill has a name (unique in the home, ignoring case), a group (prepaid,
  postpaid, rent, other), an optional **estimate every month** (৳ 0 or more;
  none means "Actual only", FR-100), and an optional **Paid to** contact
  (FR-111). Split is shown from the group: By room for rent, Equal otherwise.
- Paid to must be an active contact of the home when it is chosen. A contact
  later marked as left stays on their bills, shown "(left)", until changed.
- Every change, estimates included, is kept in history (FR-100).
- Removing a bill archives it.

### Files, ID documents and photos

Who: as each record's own rules; below.

- Every file is an `attachment`: the client asks the API for an upload, sends
  the file straight to the private bucket (presigned POST), then tells the
  API it is done; a record accepts only a finished upload of the same home
  ([data-model.md → Files](../data-model.md#files-s3-and-presigned-urls-agreed-21-nov-2026)).
  Images (JPEG, PNG, WebP) up to 5 MB; contact documents may also be PDF, up
  to 10 MB. Viewing gives a link valid for about 5 minutes, only to someone
  allowed to see the file.
- **ID document** (FR-60, FR-61): type (NID, passport, driving licence,
  birth certificate, student ID), number, front image and back image
  (optional for a passport). Added by the owner or a manager on Add a
  member (optional) or from the Edit tab; the members list shows the type
  with ✓, or "ID missing". Replacing one keeps the old in history. Only the
  owner and managers see ID images, kept after the member leaves; a member
  sees only their own, on My profile. Stored encrypted.
- **Profile photo** (FR-59, FR-86): the member sets their own at the first
  log-in check or on My profile; the owner or a manager can set it from the
  Edit tab. Shown instead of initials. Per home, like the name.
- **Contact photo and documents** (FR-109, FR-112): on Contacts and on Home &
  landlord (the lease agreement is a landlord document). Documents are for
  the owner and managers only and stored encrypted.
- **Home photos** (several) and **one room photo** (FR-58): the owner adds
  home photos; the owner or a manager adds a room photo.
- Removing a document or photo takes it off its record and keeps it in
  history; the file itself is kept.
- Uploads left unfinished for 24 hours are removed by a clean-up command.

## Screens

Every screen follows its design. Differences agreed with the user on
23 Nov 2026 (Phase 2 spec). Throughout, parts from later phases are hidden,
not shown greyed out, and the brand is "Colivo".

| Screen                   | Design file                                      | Differences                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------ | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Home settings (hub)      | `web/WebSettings.html`                           | No Meal sessions card (Phase 3). Sections lists only Home & landlord, Rooms, Members & roles, Home rules, Bills & categories and Contacts (Custom deals and Starting balances: Phase 6; Grocery fund: Phase 4). Managers see the Home rules card read-only, without Save rules. Members don't get Home settings.                                                                                                                                |
| Settings · Home & landlord | `web/WebSetHome.html`                          | Address is a text field; no "Pick on Google Maps". No "Deposit with landlord" line (Phase 7) and no "Change rent" button (Phase 6). The room total line ("৳1,200 short of landlord") is shown under Monthly rent. Home photos and the landlord's photo and documents arrive with group 5. Managers see it read-only.                                                                                                                          |
| Settings · Rooms         | `web/WebSetRooms.html`                           | The edit note reads "Each person pays ৳3,887.50. A rent change here corrects this room's rent; dated rent changes come later." instead of "creates a rent change from next month" (Phase 6). The edit form has a **Remove room** link with a confirm dialog (not in the design). The "short of landlord" line shows once the landlord's rent is set (group 3). Room photo with group 5.                                                         |
| Settings · Bills & categories | `web/WebSetBills.html`                      | The intro has no "Change one month's estimate on Utilities." (Phase 6). Split is shown, not chosen. Each bill opens an edit form like Add a bill, with a **Remove bill** link and confirm dialog (not in the design); Household and Landlord rent have none. A Paid to contact who has left shows "(left)".                                                                                                                                      |
| Settings · Contacts      | `web/WebSetContacts.html`                        | No payment counts in "Bills paid to them" (Phase 5): it lists the bill names. Photo and Document buttons arrive with group 5. Members get the same page read-only: Current contacts other than the landlord, with name, kind and phones only; no Past list, no buttons.                                                                                                                                                                      |
| Members & roles          | `web/WebMembers.html`                            | Room column and Add a member's Room select as designed, without "(after Maruf)" (Phase 7). No "Deposit needed" line (Phase 7). The ID fields on Add a member are optional (FR-60 as clarified 22 Nov 2026): "+ ID front and back (optional)". The Edit tab gains Room (with a move date) and, in group 5, ID document and photo. Fund keeper stays Phase 4. Phase 1, 1b and 1c differences still apply.                                    |
| My profile               | `web/WebProfile.html`                            | The photo replaces the initials once set; the subtitle gains the room ("Owner · Manager · Room A · member since September 2026"); "ID document · NID · uploaded ✓" with View, or "ID missing" with "Ask the owner or a manager to add it". Still no Preferences card (Phase 1c). Phase 1c's other differences still apply.                                                                                                                      |
| First log-in check       | `mobile/Login.html` (web layout, as in Phase 1)  | Shows the room (group 2) and gains "Add a photo (optional)" (FR-86, group 5). Otherwise as built in Phase 1.                                                                                                                                                                                                                                                                                                                                                                   |
| App shell and new home   | `web/WebHomeEmpty.html`                          | The sidebar gains **Home settings** (owner and managers) and the **Contacts** card ("Cook Rahima · Internet SpeedNet · 1 past"; members see it without the past count). The checklist's rooms, rules and bills steps link to their pages and tick when done. Phase 1, 1b and 1c differences still apply.                                                                                                                                    |

## API

All responses use the `StandardResponse` envelope
([tech-stack.md → API response format](../tech-stack.md#api-response-format)).
Every endpoint acts in the `X-Colivo-Home` home (Phase 1b). Another home's
record is 404 and never revealed; a role that may not act is 403; invalid
input is 422.

### Group 2 — Rooms and home rules

| Method | Path                         | Role           | Request                         | Response                                                                                                                                              |
| ------ | ---------------------------- | -------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/v1/rooms`              | Owner, manager | —                               | 200 `list[RoomOut]` (`id`, `name`, `rent`, `beds`, `people` [`membership_id`, `name`], `each_pays`). **New**                                         |
| POST   | `/api/v1/rooms`              | Owner, manager | `RoomIn` (`name`, `rent`, `beds`) | 201 `RoomOut`. 409 name taken. 403, 422. **New**                                                                                                    |
| PATCH  | `/api/v1/rooms/{id}`         | Owner, manager | `RoomPatch`                     | 200 `RoomOut`. 400 beds below the people in it. 409 name taken. 403, 404, 422. **New**                                                               |
| DELETE | `/api/v1/rooms/{id}`         | Owner, manager | —                               | 200 `RoomOut`; archives it. 400 people still in it. 403, 404. **New**                                                                                |
| PUT    | `/api/v1/members/{id}/room`  | Owner, manager | `{ room_id \| null, on }`       | 200 `MemberOut`; ends the open stay and starts the new one from `on`. 400 room full, past member, `on` before the current stay. 403, 404, 422. **New** |
| POST   | `/api/v1/members`            | Owner, manager | gains optional `room_id`        | 201 `MemberOut`. 400 room full. 404 another home's room. **Changed**                                                                                  |
| GET    | `/api/v1/members`            | Owner, manager | —                               | `MemberOut` gains `room` (`id`, `name`) or null. **Changed**                                                                                          |
| GET    | `/api/v1/me`                 | Logged in      | header                          | `MeOut.membership` gains `room`. **Changed**                                                                                                         |
| GET    | `/api/v1/home/rules`         | Owner, manager | —                               | 200 `HomeRulesOut` or `null` when never saved. **New**                                                                                                |
| PUT    | `/api/v1/home/rules`         | Owner          | `HomeRulesIn`                   | 200 `HomeRulesOut`; a new version from today, or today's updated. 403, 422. **New**                                                                   |
| GET    | `/api/v1/home/setup`         | Owner, manager | —                               | `rooms`, `rules` and `bills` steps now computed. **Changed**                                                                                          |

### Group 3 — Home & landlord, and contacts

| Method | Path                          | Role                             | Request                                   | Response                                                                                                                                                                   |
| ------ | ----------------------------- | -------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/v1/home`                | Owner, manager                   | —                                         | 200 `HomeDetailsOut` (`name`, `code`, `area`, `address`, `lease_started_on`, `rent`, `rooms_total`, `rent_gap`, `landlord`). **New**                                       |
| PATCH  | `/api/v1/home`                | Owner                            | `HomeDetailsPatch`                        | 200 `HomeDetailsOut`. 403, 422. **New**                                                                                                                                    |
| PUT    | `/api/v1/home/landlord`       | Owner                            | `LandlordIn` (`name`, `started_on`, `methods`) | 200 `ContactOut`; creates the landlord or updates them. 403, 422. **New**                                                                                           |
| GET    | `/api/v1/contacts`            | Logged in                        | `?status=current\|past`                   | 200 `list[ContactOut]` for the owner and managers; members get `list[ContactPublicOut]` (`name`, `kind`, phones), current only, no landlord; `past` for a member is 403. **New** |
| POST   | `/api/v1/contacts`            | Owner, manager                   | `ContactIn`                               | 201 `ContactOut`. 400 kind landlord ("Add the landlord on Home & landlord."). 403, 422. **New**                                                                           |
| PATCH  | `/api/v1/contacts/{id}`       | Owner, manager; landlord: owner  | `ContactPatch` (methods replace the list) | 200 `ContactOut`. 400 a contact who has left. 403, 404, 422. **New**                                                                                                      |
| POST   | `/api/v1/contacts/{id}/end`   | Owner, manager                   | `{ ended_on }`                            | 200 `ContactOut`. 400 already left, the landlord, a date before the start. 403, 404, 422. **New**                                                                         |
| GET    | `/api/v1/rooms`               | Owner, manager                   | —                                         | Gains the home totals (`rooms_total`, `rent_gap`) beside the list. **Changed**                                                                                             |

`methods` is a list of `{ kind, value, label, is_primary }`; with no primary
of a kind, the first of that kind is primary. Two primaries of a kind is 422.

### Group 4 — Bill categories

| Method | Path                               | Role           | Request                                                         | Response                                                                                                        |
| ------ | ---------------------------------- | -------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/v1/bill-categories`          | Owner, manager | —                                                               | 200 `list[BillCategoryOut]` (`id`, `name`, `bill_class`, `split`, `default_estimate`, `paid_to`, `removable`). **New** |
| POST   | `/api/v1/bill-categories`          | Owner, manager | `BillCategoryIn` (`name`, `bill_class`, `default_estimate`, `paid_to_contact_id`) | 201. 400 Paid to has left. 404 another home's contact. 409 name taken. 403, 422. **New**                       |
| PATCH  | `/api/v1/bill-categories/{id}`     | Owner, manager | `BillCategoryPatch`                                             | 200. 400, 404, 409, 403, 422 as above. **New**                                                                  |
| DELETE | `/api/v1/bill-categories/{id}`     | Owner, manager | —                                                               | 200; archives it. 400 Household or Landlord rent. 403, 404. **New**                                             |

### Group 5 — Files, ID documents and photos

| Method | Path                                             | Role                                         | Request                                                    | Response                                                                                                                              |
| ------ | ------------------------------------------------ | -------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/v1/attachments`                            | Per purpose (below)                          | `{ purpose, content_type, size_bytes, filename }`          | 201 `UploadOut` (`id`, `url`, `fields`: the presigned POST). 400 type or size not allowed for the purpose. 403, 422. **New**           |
| POST   | `/api/v1/attachments/{id}/finish`                | Who started it                               | —                                                          | 200 `AttachmentOut`; status `ready`. 400 not uploaded, or size or type differ. 403, 404. **New**                                      |
| GET    | `/api/v1/attachments/{id}/link`                  | Whoever may see it                           | —                                                          | 200 `{ url, expires_at }` (presigned GET, about 5 minutes). 403, 404. **New**                                                         |
| PUT    | `/api/v1/members/{id}/id-document`               | Owner, manager                               | `{ doc_type, number, front_id, back_id }`                  | 200 `IdDocumentOut`; the current one becomes replaced. 400 attachment not ready, wrong purpose, back missing (not a passport). 403, 404, 422. **New** |
| GET    | `/api/v1/members/{id}/id-document`               | Owner, manager                               | —                                                          | 200 `IdDocumentOut` or `null`; past members too. **New**                                                                              |
| GET    | `/api/v1/me/id-document`                         | Logged in                                    | header                                                     | 200 your own `IdDocumentOut` or `null`. **New**                                                                                       |
| PUT    | `/api/v1/members/{id}/photo`, `/api/v1/me/photo` | Owner, manager; yourself                     | `{ attachment_id \| null }`                                | 200 `MemberOut` / `MeOut`. 400, 403, 404, 422. **New**                                                                                |
| PUT    | `/api/v1/contacts/{id}/photo`                    | Owner, manager; landlord: owner              | `{ attachment_id \| null }`                                | 200 `ContactOut`. **New**                                                                                                             |
| POST   | `/api/v1/contacts/{id}/documents`                | Owner, manager; landlord: owner              | `{ attachment_id }`                                        | 201 `ContactOut`. **New**                                                                                                             |
| DELETE | `/api/v1/contacts/{id}/documents/{attachment_id}` | Owner, manager; landlord: owner             | —                                                          | 200 `ContactOut`; the link gets `removed_at`. **New**                                                                                 |
| POST   | `/api/v1/home/photos`                            | Owner                                        | `{ attachment_id }`                                        | 201 `HomeDetailsOut`. **New**                                                                                                         |
| DELETE | `/api/v1/home/photos/{attachment_id}`            | Owner                                        | —                                                          | 200 `HomeDetailsOut`. **New**                                                                                                         |
| PUT    | `/api/v1/rooms/{id}/photo`                       | Owner, manager                               | `{ attachment_id \| null }`                                | 200 `RoomOut`. **New**                                                                                                                |
| GET    | `/api/v1/members`, `/api/v1/me`, `/api/v1/contacts`, `/api/v1/home`, `/api/v1/rooms` | as before | — | Gain `photo_id`; `MemberOut` gains `id_document` (`doc_type`, or null); contacts and home gain their documents (owner, managers). **Changed** |

Who may start an upload, by purpose: `profile_photo` anyone (for
themselves) and the owner or a manager; `id_document`, `contact_photo`,
`contact_document` and `room_photo` the owner or a manager; `home_photo`
the owner. Who may see one: profile, room and home photos any member of the
home; contact photos any member (non-landlord) or the owner and managers;
ID documents the owner, managers and the member themselves; contact
documents the owner and managers.

## Data model changes

The full schema and ER diagram are in [data-model.md](../data-model.md);
this is the delta agreed at Gate 0 on 23 Nov 2026.

| Table                | Change                                                                                                                                       | Group and migration              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `room`               | New: name, beds, `archived_at`; `photo_id` in group 5                                                                                        | 2 · `<rev>_rooms_and_rules.py`   |
| `room_rent`          | New: a room's rent from a month (`starts_on` on the 1st)                                                                                     | 2                                |
| `room_assignment`    | New: who lives in which room, from and to a date                                                                                             | 2                                |
| `home_rules_version` | New: deposit and notice months, rent split, rent gap policy, from a date                                                                      | 2                                |
| `change_log`         | Entity CHECK gains `room`, `room_assignment`, `home_rules_version` (group 2), `home`, `contact` (group 3), `bill_category` (group 4)          | 2, 3, 4                          |
| `home`               | Adds `address`, `lease_started_on`                                                                                                           | 3 · `<rev>_contacts.py`          |
| `home_rent`          | New: the landlord's monthly rent from a month                                                                                                | 3                                |
| `contact`            | New, with the one-active-landlord rule; `photo_id` in group 5                                                                                | 3                                |
| `contact_method`     | New: a contact's phones and emails, one primary of each kind                                                                                 | 3                                |
| `bill_category`      | New; Household and Landlord rent added to every existing home                                                                                | 4 · `<rev>_bill_categories.py`   |
| `attachment`         | New                                                                                                                                          | 5 · `<rev>_files.py`             |
| `id_document`        | New: one current per member                                                                                                                  | 5                                |
| `contact_document`, `home_photo` | New link tables with `removed_at`                                                                                                | 5                                |
| `membership`, `contact`, `room` | Add `photo_id` FK `attachment`                                                                                                     | 5                                |

Phase 1c's data stays valid: existing homes get the two starting bills and
nothing else; members start in no room and "ID missing". Each downgrade
drops what its group added and restores the previous entity CHECK.

Contested choices, agreed at Gate 0 (23 Nov 2026):

- **Rent rows from a month** (`room_rent`, `home_rent`), not a rent column:
  October's statement always uses October's rent (FR-51), and Phase 6's rent
  revisions only add a link column. Rejected: `room.rent` moved to rows
  later (a data migration and a late start to the history).
- **The landlord's rent in its own `home_rent`**, the same shape as
  `room_rent`, so a home-wide revision writes both the same way. Rejected:
  a column on `home_rules_version` (a rent change would make a rules
  version).
- **Each pays divides by the people in the room**, as BR-3, US-A1 and the
  edge case "rent per person recalculates from the new occupant count" say;
  beds are only a cap, and an empty room is a shortfall. Rejected: dividing
  by beds.
- **A rent edit corrects the current rent** while no month is closed, kept
  in `change_log`. Nothing has been billed, and dated changes with a preview
  are Phase 6. Rejected: a new row from next month on every edit (a setup
  typo would apply to this month).
- **No rules row until the first save**, then a version per date. The
  checklist can tell whether rules were chosen. Rejected: defaults at
  sign-up.
- **Who edits what:** the owner alone changes Home & landlord and Home rules
  ("Change home settings and rules"); the owner or a manager rooms and
  room assignments, contacts, and bills with their estimates (FR-02, FR-05,
  FR-100, FR-109). Rejected: the owner or a manager for everything.
- **No deposit and notice snapshot yet:** Phase 7 reads the
  `home_rules_version` in force on each join date, and adds a column only
  for re-applying rules to a member. Rejected: copying the months onto
  `membership` now.

## Decisions

| Decision                         | Choice                                                                                                                                                | Why                                                                                                    |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Scope                            | Rooms, rent and rules; Home & landlord and contacts; bill categories; files, ID documents and photos                                                 | User's choice (23 Nov 2026)                                                                            |
| Starting balances, custom deals  | Moved to Phase 6                                                                                                                                      | User's choice; they need `month`, `fund`, `entry` and `bill`, and are the records month close writes  |
| Groups                           | Groundwork → rooms and home rules → Home & landlord and contacts → bill categories → files → verify                                                   | User's choice: feature order, files last; each slice demoable early                                    |
| Merge bar                        | The usual gate, CI green, and `/security-review` of the branch                                                                                        | User's choice; ID and landlord documents behind presigned links are the main risk                      |
| Branch                           | `phase-2-home-setup` from `main` after Phase 1c was merged                                                                                            | User merged Phase 1c first                                                                             |
| Location                         | Address text only, no Google Maps picker                                                                                                              | User's choice; no API key, billing or third-party script now                                           |
| Removing rooms and bills         | A Remove link in the edit form, with a confirm dialog; archives                                                                                       | User's choice; an extra control agreed against the design                                              |
| Later-phase parts on screens     | Hidden, each listed in Screens with its phase                                                                                                         | User's choice                                                                                          |
| Data model                       | The seven contested choices above                                                                                                                     | Agreed at Gate 0                                                                                       |
| History entities                 | `change_log` gains `home`, `room`, `room_assignment`, `home_rules_version`, `contact`, `bill_category`; rent edits under `room` and `home`; a contact's methods, photo and documents under `contact` | Settled at Gate 0                                                               |
| Removing a contact's phone       | Its `contact_method` row is deleted; the old value is in `change_log`                                                                                 | Settled at Gate 0; the same as removing a person's phone in Phase 1c                                   |
| Deactivating a member            | Ends their room stay on the same date; reactivating starts in no room                                                                                | Settled at Gate 0; nobody inactive counts as an occupant                                               |
| Starting bills                   | Household (Other) and Landlord rent (Rent) on every home; neither removable                                                                           | Settled at Gate 0; FR-05, and rent needs a category                                                    |
| Split                            | From the group, not stored: rent By room, others Equal                                                                                                | Settled at Gate 0; other split methods are after the MVP                                               |
| The landlord                     | One landlord contact, edited on Home & landlord, never "Mark as left" here                                                                            | Settled at Gate 0; a new lease is out of scope                                                         |
| Paid to a contact who left       | Kept on the bill, shown "(left)", until changed; choosing one requires an active contact                                                              | Settled at Gate 0; the "cook leaves mid-month" edge case                                               |
| Files                            | Images (JPEG, PNG, WebP) up to 5 MB; PDF up to 10 MB for contact documents; ID and contact documents with SSE-KMS (MinIO's built-in key locally)     | Settled at Gate 0                                                                                      |
| Unfinished uploads               | A clean-up command now; scheduled with the background jobs decision (Phase 9)                                                                         | Settled at Gate 0; keeps that Deferred decision open                                                   |
| ID documents                     | Added by the owner or a manager; back image optional for a passport; the member views their own                                                       | Settled at Gate 0; FR-60, FR-61, roadmap                                                               |
| Contact phones                   | E.164 with `phonenumbers` (Bangladesh by default), shown in national form                                                                             | Settled at the spec; the same rules as log-in phones                                                   |
| Members on Contacts              | The same page, read-only, names, kinds and phones of current non-landlord contacts                                                                    | Settled at the spec; FR-112 and the design's own note                                                  |
| Modules                          | `homes` (rooms, rules, Home & landlord), new `contacts`, `bills` and `files` modules; ID documents and photos in `accounts`                          | Settled at the spec; follows the module list in tech-stack.md                                          |
| New dependency                   | An S3 client (`boto3`) and a MinIO service in `compose.yaml`, asked for at group 1                                                                   | Files are stored in a private S3 bucket (decided Phase 1)                                              |

## Constraints

- Follow [tech-stack.md → Project conventions](../tech-stack.md#project-conventions):
  `CoreRouter` only, `set_response_message` on every endpoint, business
  rules in `service.py`, roles checked in the router, config only through
  `app.core.config.settings`.
- Fetch current docs with `ctx7` for every library this phase touches, at the
  installed version, before coding: FastAPI, Pydantic (decimal fields),
  SQLModel and SQLAlchemy (partial unique indexes, `numeric`), Alembic
  (adding values to a CHECK, data migrations that insert rows), boto3
  (`generate_presigned_post` with conditions, `generate_presigned_url`,
  `head_object`, SSE-KMS), MinIO (built-in KMS key, bucket policy),
  `phonenumbers`, Ember (nested routes under `authenticated`), WarpDrive
  (request builders), MSW, Playwright (file uploads).
- Every behaviour is built test-first, as in [testing.md](../testing.md).
- The schema follows [data-model.md](../data-model.md); a change to it is
  agreed with the user first.
- Money is `Decimal`, never float (rent and estimates are `numeric(12,2)`),
  and every change is one database transaction with its `change_log` rows.
- Every query is scoped to the current home, and roles are checked in the
  router; a file is reachable only through its home's records.
- Nothing is erased: rooms and bills are archived, contacts end, ID
  documents are replaced, documents and photos are unlinked, and every
  change is in `change_log`.
- `api/openapi.json` is exported and the web types regenerated
  (`make api-types`) after any endpoint change; the mobile client comes with
  the first `[mobile]` phase.
- Config comes from env vars, with `.env.example` updated (the S3 endpoint,
  bucket, keys and KMS key) and no secrets committed.
- Alembic migrations apply cleanly to Phase 1c's database.
- No dependency beyond the S3 client is expected; anything else is asked
  first.
