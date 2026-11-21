# Colivo — Roadmap

High-level implementation order. Phases are **vertical slices**: each ships one
usable, demoable piece end to end (data → API → UI). Keep every phase small.
Every phase follows the directory and naming rules in
[tech-stack.md → Project conventions](tech-stack.md#project-conventions), and
every phase's UI meets the
[responsive design standard](tech-stack.md#responsive-design).

**Build order:** backend and web are built together, one feature at a time.
The mobile app comes after web v1 works and reuses the same API. Each phase is
tagged with the parts it touches: `[backend]`, `[web]`, `[mobile]`.

Screen designs: `colivo-design/web/` and `colivo-design/mobile/` (index in
`colivo-design/README.md`). Behaviour rules: `colivo-design/requirements.md`.

## Phase 0 — Project skeleton ✅ Complete

`[backend] [web] [infra]`

- Scaffold the monorepo: `backend/`, `web/`, `api/`, `infra/`, `docs/`. The
  backend follows the `fastapi-orm-scaffold` layout with uv, the web follows
  the `ember-scaffold` layout with pnpm (see
  [tech-stack.md → Project conventions](tech-stack.md#project-conventions)).
- Test setup for both parts as in [testing.md](testing.md): pytest with a
  rolled-back test database, QUnit + MSW, Playwright, and the root `Makefile`
  targets (`test-fast`, `test`, `lint`, `format-check`, `api-types`).
- Backend answers `GET /api/v1/health` with the database and Redis status,
  inside the
  [`StandardResponse` envelope](tech-stack.md#api-response-format).
- `api/openapi.json` is exported and the web's API types are generated from it.
- Web: the store is wired with the error, auth and envelope handlers; the
  Colivo design tokens are in `@theme`; the app shell renders.
- `docker compose up` starts PostgreSQL, Redis and the backend.
- Smoke end-to-end test: Playwright opens the web app against the running
  backend.
- CI runs lint, format check and tests for the backend and the web on every
  push.
- The mobile skeleton comes later, once its structure is decided
  ([tech-stack.md → Deferred decisions](tech-stack.md#deferred-decisions)).

## Phase 1 — Accounts and log-in ✅ Complete

`[backend] [web]`

After this phase, an owner can sign up, which creates a **home**, and anyone
added to it can log in.

### Sign-up and log-in

- Model **user**, **home** and **membership** (role per home).
- Sign-up with name and phone or email, a 6-digit code, then home name.
- Log-in with a one-time code; wrong code, expired code, lock after 5 tries.
- "Not added yet" when a phone or email belongs to no home.

### Members and roles

- Owner or manager adds a **member** by phone or email; they get an SMS or
  email.
- Roles: owner, manager, member; owner gives and removes the Manager role.
  Any number of managers. Fund keepers moved to Phase 4, where funds hold
  cash (decided in the Phase 1 spec).
- Deactivate and reactivate a member.
- New home shows the setup checklist and empty states.

## Phase 1b — A person in several homes ⏳ Not started

`[backend] [web]`

After this phase, one person can be an active member of several homes at
once, and chooses which home to use after logging in (decided 21 Nov 2026,
after Phase 1's security review; replaces the MVP's one-active-home rule,
FR-85).

- Adding a phone or email that is already in **this** home is refused (409);
  one active in another home can be added.
- Sign-up and reactivation no longer refuse someone active in another home.
- Log-in with several active homes asks which home; a person in one home
  goes straight there, as now.
- The session knows the current home; switch homes from the shell.
- Data model at the phase's Gate 0: drop "one active membership per person",
  and how a session keeps its current home
  ([data-model.md → Open questions](data-model.md#open-questions)).

## Phase 2 — Home setup ⏳ Not started

`[backend] [web]`

After this phase, the owner can describe the home the app will calculate for.

### Rooms, rent and rules

- Model **room** (rent, beds) and room assignment per member.
- **Home rules**: deposit months, notice period, rent-gap policy.
- Home and landlord details: address, photos, landlord rent, landlord deposit.

### Home contacts

- Model **contact** (landlord, cook, internet, electricity, gas, caretaker,
  other) with any number of phones and emails, optional photo, account ID,
  note and documents
  ([data-model.md → Contacts and files](data-model.md#contacts-and-files-agreed-19-nov-2026)).
- Shared **attachment** model for files (contact documents, lease; receipts
  reuse it later); sensitive files encrypted.
- The landlord is the landlord contact on Home & landlord; one active
  landlord at a time.
- Mark a contact as left (cook or provider changes); past contacts are kept.
- Members see cook and provider names and phones; landlord details and
  documents for the owner and managers only.

### Bills and starting balances

- **Bill** categories: rent, prepaid, postpaid, other; a default
  **Household** category for non-food items (shared like a bill, not by
  meals); custom deals.
- Optional **Paid to** contact per bill category (one per category).
- Optional default **estimate** per bill category, used every month.
- **Starting balances** imported once from the old spreadsheet: member
  balances, home fund and grocery fund cash **per holder**, money with
  shoppers and unpaid bills.

## Phase 3 — Meals and cost per meal ⏳ Not started

`[backend] [web]`

After this phase, every member logs meals and sees today's count.

### Meal grid

- Model **meal session** per home (breakfast, lunch, dinner; on/off, order,
  weight) and **meal entry** (member, date, session, own, guests)
  ([data-model.md → Meals](data-model.md#meals-sessions-guests-and-confirmation-agreed-19-nov-2026)).
- **Home guests** per date and session (owner and managers).
- **Confirm** a session after it is cooked, one or several at once.
- Members change their own meals until the session is confirmed or the day
  ends; owner and manager change anyone's, logged.
- Today's meals and **Cook for** totals (members + guests + home guests) on
  every home page.

### Cost per meal

- Live **cost per meal** = groceries ÷ billable meals (confirmed sessions,
  own + guests × session weight; home guests left out); 0 when there are
  none.

## Phase 4 — Groceries and the grocery fund ⏳ Not started

`[backend] [web]`

After this phase, groceries are recorded with who paid and from where.

### Grocery entries

- Model **grocery entry** with source: own pocket, grocery fund, home fund,
  money given.
- Receipt required; entries count toward the cost per meal.
- Grocery entries are the first **ledger** entries
  ([data-model.md → Decisions](data-model.md#decisions)): once saved they are
  never edited in place, only changed by linked entries.
- **Split funding**: one entry mixes a shared source (grocery fund, home
  fund or money given) with own pocket; the shared part is capped at what is
  available and only the pocket part is credited.

### Grocery fund and give money first

- **Funds** as rows (grocery fund and home fund) and **cash per holder**
  ([data-model.md → Funds and holders](data-model.md#funds-and-holders-agreed-17-nov-2026)).
- **Fund keepers**, chosen per fund (grocery fund, home fund or both); any
  number per fund (moved here from Phase 1).
- **Grocery fund** balance and top-ups; a top-up names the holder who
  received it, and that holder confirms it.
- A holder gives grocery money to a shopper; nobody gives out more than they
  hold; spending is capped at what was given; leftover is handed back.
- **Handover** of cash between holders, confirmed by the receiver.

## Phase 5 — Bills, payments and confirmation ⏳ Not started

`[backend] [web]`

After this phase, every money movement is reported with proof and confirmed.

### I paid and confirmation

- One **I paid** flow for every purpose, receipt required.
- Confirmation rules by role; reject with a reason; fix and resend; withdraw.
- Manager records a payment directly.

### Bills to pay

- **Bills to pay** list; mark paid; a home fund holder pays a bill or gives
  money for it, capped at what they hold and at free-to-spend cash; member
  reports it paid.
- Every payment into the home fund names who received it; that holder
  confirms it.
- Split funding for bills (home fund or given money + own pocket).
- Carried bills shown as "From \<month>"; estimated bills tagged "Estimated".

### Returns and corrections

- **Return / exchange** on a grocery or bill entry: amount returned, an
  optional item taken instead with its receipt, reason and proof; confirmed
  like the original. Money back lowers the pocket part first; any shared part
  that comes back is money with the payer until handed back.
- A member sends a **correction** of their own confirmed entry for
  confirmation; the owner or a manager corrects any entry directly and the
  member is told.
- A **refund** to a member counts only after the member confirms receipt;
  "Not received" sends it back.

## Phase 6 — Statement and month close ⏳ Not started

`[backend] [web]`

After this phase, a month can be closed and balances carry forward.

### Statement

- Utilities split (prepaid, postpaid), rent shares, rent gap handling.
- **Monthly statement** for everyone; **my bill** for each member.

### Month close and corrections

- Pre-close checklist; close the month; credits and dues carry over.
- Close writes carry-forward records: home fund and grocery fund opening cash,
  money with shoppers, unpaid bills. Paying a carried bill lowers cash only
  and is never split among members again.
- A closed month is never reopened; owner or manager corrects an entry (a
  return on a closed month's entry included) and the difference goes into the
  open month.
- The checklist also lists returns and corrections waiting for confirmation,
  refunds waiting for the member, and meal sessions not yet confirmed
  (closing anyway confirms them as logged).
- Cash count and carry-forward **per holder** for each fund; payments and
  handovers still waiting for their receiver are listed.
- Previous month balances (view only).

### Estimated bills

- Change one month's estimate without changing the default.
- Members are charged the estimate until the actual bill is entered; the
  actual replaces it.
- Month closed on an estimate: the difference is added to the open month as
  an adjustment line (reuses the correction logic above).

### Rent changes

- Change rent for the home, a room or a member from a chosen month.

## Phase 7 — Deposits, notice and settlement ⏳ Not started

`[backend] [web]`

After this phase, members can join and leave cleanly.

- Member **deposits** and the deposit ledger.
- **Notice** to leave with the minimum notice period.
- **Final settlement**: deposit applied to the last months, deactivation.
- **Past members** list (owner and managers only).

## Phase 8 — Inbox, messages and history ⏳ Not started

`[backend] [web]`

After this phase, everyone sees what needs them and nothing is lost.

- **Inbox** per role: things to confirm and updates.
- **Messages**: home group chat and one-to-one.
- **History** on every entry; soft delete with a reason, per the deletion
  rules.

## Phase 9 — Web MVP ⏳ Not started

`[backend] [web] [infra]`

Closes the mission's unmet promises and makes the web version shippable.

### Parallel run

- Replay October 2026 and check every balance against the spreadsheet.
- Run one month side by side with the spreadsheet.

### Ship-readiness

- Production deploy, HTTPS, backups, health checks, error tracking.
- Receipt and ID document storage is private.
- README and runbook.

## Phase 10 — Mobile app ⏳ Not started

`[mobile]`

After this phase, members use a phone app on the same API.

### Mobile slices (one spec each)

- Skeleton, log-in and home for each role.
- Meals, groceries and I paid.
- Inbox, messages, my bill and notice.
- Owner and manager tools (confirm, give money, close month).
- Store release (Play Store first).

## Later (out of v1 scope)

Short-notice waiver voting, whole-home
move-out with landlord deposit settlement, PDF/Excel export and WhatsApp
sharing, meal cut-off times and default meal patterns, reminders, grocery
shopping roster, Bangla and other languages, currencies other than ৳ (BDT),
split methods other than meal-based groceries (flatshare, bills-only, paying
guest), payment gateway integration, transferring ownership, notification
settings.

Next version (after the MVP): **custom funds** (repair, festival). Chosen
members pay in, either a set amount split equally or open contributions;
spent like the home fund; kept off the monthly bill; carried over at close.
The agreed shape is in `colivo-design/requirements.md → Phase 4`; the
`fund.kind` column is already planned so nothing blocks it.
