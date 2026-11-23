# Phase 2 — Home Setup: Plan

Branch: `phase-2-home-setup`, from `main` after Phase 1c's merge, pushed
early with a draft pull request.

Each group is built with `/tdd` as in
[testing.md → Build time](../testing.md#build-time-tdd-one-planmd-group-per-run):
Gate 2 on `tests.md`, then backend → contract → web, one test at a time.
Group 1 is groundwork (no **Behaviours:** line): no tests, one commit, then
stop for review.

Per-behaviour gate: `make test-fast`, `make lint` and `make format-check`
green, then a conventional commit (e.g. `feat(homes): add a room with rent
and beds`, `feat(web): show what each person pays on Rooms`) with no
Co-Authored-By or AI attribution lines.

## 1. Groundwork

Docs, settings, local storage and empty modules. Commit:
`chore: add phase 2 groundwork`.

- Fetch current docs with `ctx7`, at the installed versions: SQLAlchemy and
  SQLModel (partial unique indexes on expressions, `Numeric(12, 2)`),
  Pydantic (`Decimal` fields with `ge=0`, `max_digits`), Alembic (recreating
  a CHECK, inserting rows in a migration), `phonenumbers` (national format),
  Ember (nested routes under `authenticated`), WarpDrive (request builders
  for `PATCH` and `DELETE`), MSW. Groups 4–5 look up boto3 (presigned POST
  conditions, presigned GET, `head_object`, SSE-KMS), MinIO (built-in KMS
  key, private bucket) and Playwright (`setInputFiles`) before their
  backend half.
- **Ask first**, then add: `boto3` (with `boto3-stubs[s3]` as a dev
  dependency for pyright) via `uv add`; rebuild the backend container.
- `compose.yaml`: a `minio` service (pinned image, healthcheck, a
  `minio-data` volume, a built-in KMS key from `.env`) and a one-shot
  `minio-init` that creates the private bucket; the backend depends on it.
  CI gets the same service for the backend job.
- `backend/app/core/config.py` and `.env.example`: `S3_ENDPOINT_URL`,
  `S3_PUBLIC_ENDPOINT_URL` (the URL a browser reaches), `S3_BUCKET`,
  `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_REGION`, `S3_KMS_KEY_ID`,
  `MINIO_KMS_SECRET_KEY` (Compose only). No secret committed. Also
  `web/config/environment.js` or the CSP, if it needs the storage origin.
- Modules: `backend/app/modules/{contacts,bills,files}/` with empty
  `models.py`, `schemas.py`, `service.py`, `router.py`, registered in
  `backend/app/api/api_v1.py`; `backend/app/modules/files/storage.py` with
  the S3 client factory (no behaviour yet).
- `specs/tech-stack.md` Project conventions: add `contacts`, `bills` and
  `files` to the module list.
- Check: `make test-fast`, `make lint`, `make format-check` still green;
  `docker compose up -d --wait` brings MinIO up healthy.

## 2. Rooms and home rules (slice 1)

- **Behaviours:** B1–B16 (B16's "Add bills" step is finished in group 4).
- **Acceptance:**
  - Backend: `backend/tests/homes/test_api.py::test_owner_adds_a_room_and_puts_a_member_in_it`.
  - Web: `web/tests/acceptance/rooms-test.ts` › owner adds a room and sees
    what each person pays.
- **Tables:** `room`, `room_rent`, `room_assignment`, `home_rules_version`;
  `change_log` entity values `room`, `room_assignment`,
  `home_rules_version`, as in [data-model.md](../data-model.md#room-phase-2-planned);
  migration `backend/alembic/versions/<rev>_rooms_and_rules.py`.

### Backend

- `backend/app/modules/homes/models.py`: `Room`, `RoomRent`,
  `RoomAssignment`, `HomeRulesVersion`; `RentSplit` and `RentGapPolicy`
  `StrEnum`s; model imports in `backend/alembic/env.py`; the group's
  migration. `backend/app/modules/history/models.py`: the new
  `ChangeEntity` values.
- `backend/app/modules/homes/service.py`:
  - rooms: `add_room`, `update_room` (rent corrects the current
    `room_rent` row; beds not below the people), `remove_room` (archive;
    400 with people), `list_rooms` with `each_pays` as `Decimal`
    (rent ÷ people, unrounded, shown to 2 decimals);
  - assignments: `assign_room(member, room, on)` (one open stay, beds cap,
    row lock on the room so two assignments can't both fill the last bed);
    deactivation in `accounts/service.py` ends the stay on the same date;
  - rules: `get_rules`, `save_rules` (a version from today in the home's
    time zone, or today's updated);
  - `get_setup`: `rooms` and `rules` steps from the data;
  - `record_change` in the same transaction for every change.
  - Constants: `ROOM_NAME_TAKEN`, `ROOM_FULL`, `ROOM_HAS_PEOPLE`,
    `BEDS_BELOW_PEOPLE`.
- `backend/app/modules/homes/schemas.py`: `RoomIn`, `RoomPatch`, `RoomOut`,
  `RoomAssignIn`, `HomeRulesIn`, `HomeRulesOut`.
  `backend/app/modules/accounts/schemas.py`: `MemberIn` gains `room_id`;
  `MemberOut` and `MeOut.membership` gain `room`.
- `backend/app/modules/homes/router.py`: `/rooms`, `/rooms/{id}`,
  `/home/rules`; `backend/app/modules/accounts/router.py`:
  `PUT /members/{id}/room`. Owner-only `PUT /home/rules` on `OwnerDep`.
- Tests: `backend/tests/homes/{test_service,test_api}.py`,
  `backend/tests/accounts/{test_service,test_api}.py` (room on add, deactivate);
  `backend/tests/conftest.py` gains a home with two rooms.

### Contract

- `make api-export` → `api/openapi.json`; `make api-types`. Commit
  `chore(api): add rooms and home rules`.

### Web

- `web/app/data/builders/{rooms,home-rules}.ts`; `web/app/services/{rooms,home-settings}.ts`.
- Routes and templates under `authenticated/settings/`: `web/app/router.ts`
  (`settings` with `index`, `rooms`), `web/app/routes/authenticated/settings.ts`
  (owner and managers only; members go home),
  `web/app/templates/authenticated/settings/{index,rooms}.gts`.
- `web/app/components/settings/`: `settings-page.gts` (the hub with
  Sections, as in [Screens](requirements.md#screens)),
  `home-rules-form.gts` (segmented choices; read-only for a manager),
  `rooms-page.gts`, `room-form.gts` (with Remove room and its dialog).
- `web/app/components/members/`: Room select on `add-member-form.gts`, Room
  with a move date on `edit-member-form.gts`, Room column on
  `member-list.gts`; `profile/profile-page.gts` subtitle gains the room;
  `auth/first-log-in-check.gts` shows the room.
- `web/app/components/home/setup-checklist.gts`: steps link to their pages;
  `layout/app-shell.gts`: Home settings link for the owner and managers.
- `web/app/utils/money.ts` if not there yet: `formatTaka` (৳, Bangladeshi
  grouping, 2 decimals).
- Tests: `web/tests/unit/utils/money-test.ts`,
  `web/tests/integration/components/settings/{home-rules-form,rooms-page,room-form}-test.gts`,
  `web/tests/integration/components/members/*`, `web/tests/acceptance/rooms-test.ts`,
  `web/tests/acceptance/home-rules-test.ts`; MSW handlers and factories in
  `web/tests/helpers/` typed from the generated API types.

## 3. Home & landlord, and contacts (slice 2)

- **Behaviours:** B17–B29.
- **Acceptance:**
  - Backend: `backend/tests/contacts/test_api.py::test_manager_adds_a_cook_and_a_member_sees_only_name_and_phone`.
  - Web: `web/tests/acceptance/contacts-test.ts` › manager adds a cook and a
    member sees only the name and phone.
- **Tables:** `home` (`address`, `lease_started_on`), `home_rent`,
  `contact`, `contact_method`; `change_log` entity values `home`,
  `contact`; migration `backend/alembic/versions/<rev>_contacts.py`.

### Backend

- `backend/app/modules/homes/models.py`: `Home` columns, `HomeRent`.
  `backend/app/modules/contacts/models.py`: `Contact`, `ContactMethod`,
  `ContactKind`, `MethodKind`; imports in `backend/alembic/env.py`; the
  group's migration.
- `backend/app/modules/homes/service.py`: `get_home_details`,
  `update_home_details` (rent corrects the current `home_rent` row),
  `rent_gap` (rooms' total − landlord rent, from current rows), used by
  `list_rooms` too.
- `backend/app/modules/contacts/service.py`: `add_contact` (not the
  landlord), `update_contact` (methods replace the list; history keeps the
  old list), `end_contact`, `set_landlord`, `list_contacts(viewer, status)`
  (the member view drops the landlord, emails, account ID, note); phone and
  email checks reused from `accounts/contact.py` (moved to
  `backend/app/utils/contact.py` on green if both modules need it).
- `backend/app/modules/contacts/schemas.py`: `ContactIn`, `ContactPatch`,
  `ContactMethodIn`, `ContactOut`, `ContactPublicOut`, `ContactEndIn`,
  `LandlordIn`. `homes/schemas.py`: `HomeDetailsOut`, `HomeDetailsPatch`.
- Routers: `contacts/router.py` (`/contacts…`), `homes/router.py`
  (`/home`, `/home/landlord`).
- Tests: `backend/tests/contacts/{test_service,test_api}.py`,
  `backend/tests/homes/{test_service,test_api}.py`.

### Contract

- `make api-export`, `make api-types`. Commit
  `chore(api): add home details and contacts`.

### Web

- `web/app/data/builders/{home,contacts}.ts`; `web/app/services/contacts.ts`.
- Routes: `settings/home`, `contacts` (every member;
  `web/app/routes/authenticated/contacts.ts`), templates to match.
- `web/app/components/settings/home-page.gts` (the home card and the
  landlord card; read-only for a manager),
  `web/app/components/contacts/{contacts-page,contact-form,contact-methods-editor,end-contact-dialog}.gts`
  (`contact-methods-editor` is shared by the landlord card and Contacts),
  `rooms-page.gts` gains the total line; `layout/app-shell.gts` gains the
  Contacts card.
- Tests: `web/tests/integration/components/contacts/*`,
  `web/tests/integration/components/settings/home-page-test.gts`,
  `web/tests/acceptance/{contacts,home-landlord}-test.ts`.

## 4. Bill categories (slice 3)

- **Behaviours:** B30–B36, and B16's "Add bills" step.
- **Acceptance:**
  - Backend: `backend/tests/bills/test_api.py::test_manager_adds_a_bill_with_an_estimate_paid_to_the_cook`.
  - Web: `web/tests/acceptance/bills-test.ts` › manager adds a bill with an
    estimate paid to the cook.
- **Tables:** `bill_category` (with Household and Landlord rent inserted
  for every existing home); `change_log` entity value `bill_category`;
  migration `backend/alembic/versions/<rev>_bill_categories.py`.

### Backend

- `backend/app/modules/bills/models.py`: `BillCategory`, `BillClass`;
  import in `backend/alembic/env.py`; the migration (table, then the two
  rows per home).
- `backend/app/modules/bills/service.py`: `add_starting_bills(home)`
  (called by sign-up in `accounts/service.py`), `add_bill`, `update_bill`,
  `remove_bill` (400 for the starting two), `list_bills` (split from the
  class, Paid to with "left"); Paid to checked against current contacts of
  the home; `homes/service.py` `get_setup` "bills" step.
- `backend/app/modules/bills/schemas.py`: `BillCategoryIn`,
  `BillCategoryPatch`, `BillCategoryOut`.
- `backend/app/modules/bills/router.py`: `/bill-categories…`.
- Tests: `backend/tests/bills/{test_service,test_api}.py`; the migration's
  data step in `backend/tests/bills/test_migration.py` (Phase 1c home → two
  bills).

### Contract

- `make api-export`, `make api-types`. Commit `chore(api): add bill categories`.

### Web

- `web/app/data/builders/bills.ts`; `web/app/services/bills.ts`.
- Route `settings/bills`; `web/app/components/bills/{bills-page,bill-form}.gts`
  (Remove bill with its dialog; none for the starting two); the hub's
  Sections row "7 bills".
- Tests: `web/tests/integration/components/bills/*`,
  `web/tests/acceptance/bills-test.ts`.

## 5. Files, ID documents and photos (slice 4)

- **Behaviours:** B37–B48.
- **Acceptance:**
  - Backend: `backend/tests/accounts/test_api.py::test_manager_adds_an_id_document_and_only_staff_and_the_member_can_view_it`.
  - Web: `web/tests/acceptance/id-document-test.ts` › manager adds a
    member's ID document and the list shows it.
- **Tables:** `attachment`, `id_document`, `contact_document`, `home_photo`;
  `photo_id` on `membership`, `contact` and `room`; migration
  `backend/alembic/versions/<rev>_files.py`.

### Backend

- `backend/app/modules/files/models.py`: `Attachment`,
  `AttachmentPurpose`, `AttachmentStatus`, `HomePhoto`;
  `contacts/models.py`: `ContactDocument`, `Contact.photo_id`;
  `accounts/models.py`: `IdDocument`, `IdDocType`, `Membership.photo_id`;
  `homes/models.py`: `Room.photo_id`; imports in `backend/alembic/env.py`;
  the migration.
- `backend/app/modules/files/storage.py`: `presigned_upload(key, type,
  size, encrypted)` (a POST policy with `content-length-range`, the exact
  content type, and SSE-KMS for sensitive purposes), `presigned_view(key)`
  (about 5 minutes), `object_info(key)`. Tests run against the real MinIO
  from Compose; it is ours, like PostgreSQL.
- `backend/app/modules/files/service.py`: `start_upload(viewer, purpose,
  …)` (role and the purpose's types and sizes), `finish_upload` (checks the
  object), `view_link(viewer, attachment)` (each purpose's visibility
  rule), `ready_attachment(home, id, purpose)` used by every record that
  takes a file, `clean_up_pending(now)`.
- `backend/app/modules/files/cli.py`: `uv run python -m
  app.modules.files.cli clean-up` for B48.
- `accounts/service.py`: `set_id_document` (replaces the current one),
  `get_id_document`, `set_photo`; `contacts/service.py`: `set_contact_photo`,
  `add_contact_document`, `remove_contact_document`; `homes/service.py`:
  `add_home_photo`, `remove_home_photo`, `set_room_photo`; each with
  `record_change`.
- Schemas and routers as in [requirements.md → API](requirements.md#group-5--files-id-documents-and-photos).
- Tests: `backend/tests/files/{test_service,test_api,test_storage}.py`,
  plus the record tests in `backend/tests/{accounts,contacts,homes}/`.

### Contract

- `make api-export`, `make api-types`. Commit
  `chore(api): add files, ID documents and photos`.

### Web

- `web/app/data/builders/files.ts` (start, finish, link) and
  `web/app/services/uploads.ts` (start → POST the file to the presigned URL
  with `fetch` and `FormData` → finish), the one place outside `data/` that
  talks to storage; listed as a known exception if `eslint-plugin-boundaries`
  needs it.
- `web/app/components/ui/file-picker.gts` (button, type and size check
  before upload, progress, error) and `web/app/components/ui/photo.gts`
  (an image from a short-lived link, initials while loading); `avatar.gts`
  shows the photo when there is one.
- `web/app/components/members/id-document-fields.gts` on Add a member and
  the Edit tab; the ID column on `member-list.gts`; photo on the Edit tab,
  `profile/profile-page.gts` (photo and "ID document · NID · uploaded ✓"
  with View), `auth/first-log-in-check.gts` ("Add a photo (optional)").
- Contacts and Home & landlord: photo and document buttons; Rooms: room
  photo; Home & landlord: home photos.
- Tests: `web/tests/integration/components/ui/file-picker-test.gts`,
  `web/tests/integration/components/members/id-document-fields-test.gts`,
  the touched pages' integration tests, `web/tests/acceptance/id-document-test.ts`.
  MSW handles the storage POST as well as the API.

### End-to-end

- `web/e2e/home-setup.spec.ts`, beside `accounts.spec.ts`,
  `several-homes.spec.ts` and `change-contact.spec.ts` (all must keep
  passing): against `docker compose up` (MinIO included) with no mocks, an
  owner signs up, sets the landlord rent, adds Room A and Room B, adds a
  member to Room B with an ID front and back uploaded from a fixture image,
  saves the home rules, adds a cook and a Cook bill paid to her; the
  checklist shows every step done; the member logs in and sees their room,
  their ID document and the cook's phone, and not the landlord.

## 6. Verify and document

- Run [validation.md](validation.md) in full, including `/security-review`
  of the branch. Findings the user accepts as fixes become behaviours under
  **Security review follow-ups**, built test-first.
- `specs/data-model.md`: this phase's tables from _planned_ to _built_,
  matching the migrations; a Change log row.
- `specs/tech-stack.md`: **Decided in Phase 2** (rent rows by month,
  Each pays by people, rules versions, the edit rights, file storage as
  built, the upload purposes and limits, MinIO locally); file storage
  marked built; **Known limitations**: no map picker, rent edits correct in
  place until Phase 6, the clean-up command isn't scheduled, no landlord
  replacement.
- `specs/roadmap.md`: mark Phase 2 `✅ Complete`; move starting balances and
  custom deals into Phase 6's list.
- `colivo-design/requirements.md`: a Phase 2 change line on FR-57 (address
  text until a later phase) and FR-60 (back image optional for a passport).
- `README.md`: MinIO in the local setup and its console.
- `CHANGELOG.md`: run `/changelog` before merging.
