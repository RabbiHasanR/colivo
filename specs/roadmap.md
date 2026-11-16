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

## Phase 0 — Project skeleton ⏳ Not started

`[backend] [infra]`

- Scaffold the monorepo: `backend/`, `api/`, `infra/`, `docs/`. The backend
  follows the `fastapi-orm-scaffold` layout with uv (see
  [tech-stack.md → Project conventions](tech-stack.md#project-conventions)).
- Backend answers `GET /api/v1/health` with the database and Redis status,
  inside the
  [`StandardResponse` envelope](tech-stack.md#api-response-format).
- `docker compose up` starts PostgreSQL, Redis and the backend.
- CI runs lint, format check and tests for the backend on every push.
- Web and mobile skeletons come later, once their structure is decided
  ([tech-stack.md → Deferred decisions](tech-stack.md#deferred-decisions)).

## Phase 1 — Accounts and log-in ⏳ Not started

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
- Roles: owner, manager, fund keeper, member; owner gives and removes roles.
- Deactivate and reactivate a member.
- New home shows the setup checklist and empty states.

## Phase 2 — Home setup ⏳ Not started

`[backend] [web]`

After this phase, the owner can describe the home the app will calculate for.

### Rooms, rent and rules

- Model **room** (rent, beds) and room assignment per member.
- **Home rules**: deposit months, notice period, rent-gap policy.
- Home and landlord details: address, photos, landlord rent, landlord deposit.

### Bills and starting balances

- **Bill** categories: rent, prepaid, postpaid, other; custom deals.
- Optional default **estimate** per bill category, used every month.
- **Starting balances** imported once from the old spreadsheet: member
  balances, home fund cash, grocery fund cash, money with shoppers and unpaid
  bills.

## Phase 3 — Meals and cost per meal ⏳ Not started

`[backend] [web]`

After this phase, every member logs meals and sees today's count.

### Meal grid

- Model **meal entry** (member, date, lunch, dinner, guests).
- Members change their own meals; owner and manager change anyone's.
- Today's meals and "cook for" totals on every home page.

### Cost per meal

- Live **cost per meal** = groceries ÷ meals; 0 when there are no meals.

## Phase 4 — Groceries and the grocery fund ⏳ Not started

`[backend] [web]`

After this phase, groceries are recorded with who paid and from where.

### Grocery entries

- Model **grocery entry** with source: own pocket, grocery fund, home fund,
  money given.
- Receipt required; entries count toward the cost per meal.
- **Split funding**: one entry mixes a shared source (grocery fund, home
  fund or money given) with own pocket; the shared part is capped at what is
  available and only the pocket part is credited.

### Grocery fund and give money first

- **Grocery fund** balance, top-ups and fund keeper.
- Fund keeper or manager gives grocery money to a shopper; spending is capped
  at what was given; leftover is returned.

## Phase 5 — Bills, payments and confirmation ⏳ Not started

`[backend] [web]`

After this phase, every money movement is reported with proof and confirmed.

### I paid and confirmation

- One **I paid** flow for every purpose, receipt required.
- Confirmation rules by role; reject with a reason; fix and resend; withdraw.
- Manager records a payment directly.

### Bills to pay

- **Bills to pay** list; mark paid; give home fund money to a member to pay a
  bill; member reports it paid.
- Split funding for bills (home fund or given money + own pocket).
- Carried bills shown as "From \<month>"; estimated bills tagged "Estimated".

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
- A closed month is never reopened; owner or manager corrects an entry and the
  difference goes into the open month.
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

A person in more than one home, short-notice waiver voting, whole-home
move-out with landlord deposit settlement, PDF/Excel export and WhatsApp
sharing, meal cut-off times and default meal patterns, reminders, grocery
shopping roster, Bangla and other languages, currencies other than ৳ (BDT),
split methods other than meal-based groceries (flatshare, bills-only, paying
guest), payment gateway integration, transferring ownership, notification
settings.
