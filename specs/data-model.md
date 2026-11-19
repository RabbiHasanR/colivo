# Colivo — Data model

The living schema: what the database holds now and why. Each phase's
`requirements.md → Data model changes` holds only that phase's delta and
links here. Nothing here is decided without the user: `/feature-spec` step 4
(Gate 0) is the discussion, and this file records the result.

Status marks: _(Phase N, planned)_ when agreed in a spec, _(Phase N, built)_
once the phase's migrations are merged.

## Domain sketch

_Pending — agree before the Phase 1 spec._

The main entities and how they relate, for **all** phases, from
`colivo-design/requirements.md`: no columns yet. The goal is that early
tables don't block later money flows. Expected entities: user, home,
membership (role per home), room, room assignment, home rules, bill
category, meal session, meal entry, meal session day, grocery entry,
grocery fund, home fund, payment, bill, statement, credit, deposit, inbox
item, message, contact, contact method, attachment, and the linked entries
that change money later: return, correction and refund. Funds and their
holders are decided below ([Funds and holders](#funds-and-holders-agreed-17-nov-2026)),
and so are meals ([Meals](#meals-sessions-guests-and-confirmation-agreed-19-nov-2026))
and contacts ([Contacts and files](#contacts-and-files-agreed-19-nov-2026)).

Money storage is decided: a ledger (see [Decisions](#decisions)).

## Conventions

Project-wide rules that already apply are in
[tech-stack.md → Project conventions](tech-stack.md#project-conventions):
money is `numeric(12,2)` as `Decimal`, timestamps are timezone-aware, every
query is scoped to the current home, nothing is erased, and every money
change is one transaction.

Database-specific rules:

- Names are `snake_case`. Foreign keys are `<table>_id`.
- Every home-owned table has `home_id NOT NULL` referencing `home`, and an
  index that starts with `home_id`.
- Every table has `created_at` and `updated_at` (`timestamptz`, set by the
  database).
- No hard deletes of user data. Money entries follow the ledger rules in
  [Decisions](#decisions); other records follow the history rule chosen in
  [Open questions](#open-questions).
- A rule a user could notice (unique, check, foreign key) is enforced in the
  database **and** listed as a behaviour in the phase's `validation.md`.
- One Alembic migration per `plan.md` group, edited on the phase branch until
  the group is done; a migration merged to `main` is never edited.

## Decisions

### Money storage: a ledger _(agreed 17 Nov 2026)_

Every money event is an **entry**, and every balance is computed from
entries: member credit and due, home fund cash, grocery fund cash and money
with shoppers. No balance column is the source of truth. A cached total may
be added later for speed (NFR-05), but it is always rebuilt from entries.

Rules (from `colivo-design/requirements.md` FR-17, FR-27, FR-90, FR-96,
FR-102, FR-103, NFR-07):

- **A confirmed entry is never updated or deleted.** A change is a new entry
  linked to the original: a return (FR-102), a correction (FR-103), a delete
  that cancels it in full (FR-96) or a closed-month correction (FR-90). The
  link column's name is settled at Gate 0.
- **Every entry has a status:** waiting, confirmed, rejected or withdrawn.
  Only confirmed entries count (FR-75, FR-91). A refund is confirmed by the
  member who received it (FR-17).
- **Effective amount** = the original plus its confirmed linked entries.
  Totals sum effective amounts, so the original's numbers stay as they were
  entered.
- **Months:** a linked entry counts in its original's month. If that month
  is closed, its statement shows the corrected figures and each member's
  difference is posted to the open month (FR-90).
- **Split funding:** an entry stores its shared part and its pocket part
  separately (FR-98), so a return can lower the pocket part first (FR-102).
- **A return can't exceed what is left of the original.** This compares
  rows, which a `CHECK` constraint can't do, so the service checks it inside
  the transaction after locking the original row (`SELECT … FOR UPDATE`);
  two returns sent at the same time can't both pass.

Why a ledger instead of stored balances:

- **Proof:** the app exists so "who paid what" is never argued about. With
  stored balances, an edit overwrites the old number; with a ledger, every
  step is a row anyone can trace (FR-22).
- **Closed months stay closed:** a correction is a new row, so a closed
  month's entries never change (FR-89, FR-90).
- **One way to check the maths:** recomputing every balance from entries is
  the October 2026 replay test (NFR-02); stored balances would need a second
  check that they still match their entries.

Entry kinds expected so far (columns at each phase's Gate 0): grocery
purchase, grocery fund top-up, bill, payment, refund, money given, money
handed back, handover, return, correction, and adjustment (closed-month
correction, estimate adjustment).

### Funds and holders _(agreed 17 Nov 2026)_

From `colivo-design/requirements.md` FR-62–FR-67, FR-104, FR-105, BR-23.

- **A fund is a row, not a hard-coded name.** A `fund` table per home
  starts with two rows, grocery fund and home fund. Custom funds (Release
  plan) then need no schema change, which keeps early tables from blocking
  later money flows.
- **A fund has a kind** _(added 19 Nov 2026)_: `grocery`, `home` or
  `custom`. Rules hang on the kind, not the name: grocery-fund spending feeds
  the cost per meal (BR-2), the home fund has reserved deposit cash (FR-32),
  and a custom fund has neither. `custom` is reserved; custom-fund screens
  come after the MVP. Their agreed shape (chosen members, a set amount split
  equally or open contributions, kept off the monthly bill) is in
  `colivo-design/requirements.md → Phase 4` and will need a fund-member link
  and a collection record then.
- **Every money entry that moves fund cash names its fund and its holder**
  (the person who received or paid the cash). A handover names two holders.
  Cash per holder (BR-23) and each fund's balance are sums over these
  entries; nothing is stored as a balance.
- **Money with shoppers is a holder balance** limited to one purpose (given
  for groceries or for a bill), so it is computed the same way as any
  holder's cash.
- **Who may hold a fund** comes from roles: the owner and managers hold any
  fund; fund keepers hold the funds they are chosen for. "Fund keeper of
  fund X" is a link between a membership and a fund, so one person can keep
  both funds and a fund can have several keepers.
- **The spending cap is per holder.** A holder's cash can't go below 0, and
  for the home fund free-to-spend (FR-32) can't either. Like the return cap,
  this compares rows, so the service checks it inside the transaction after
  locking the holder's fund rows; two spends at the same moment can't both
  pass.
- **A waiting handover or payment counts for nobody new:** until the
  receiver confirms, the money stays with the giver (and is locked) or, for
  a payment in, is in nobody's cash.

Why per holder instead of one total per fund: with two people holding the
same fund, one total lets a holder give out cash someone else has, and the
month-close cash count has no single person to check it against (G4).

### Meals: sessions, guests and confirmation _(agreed 19 Nov 2026)_

From `colivo-design/requirements.md` FR-08–FR-11, FR-106–FR-108, BR-2,
BR-24.

- **A meal session is a row, not a column.** Each home has its own
  sessions (breakfast, lunch, dinner) with an on/off flag, an order and a
  `weight` (`numeric`, default 1; breakfast can be 0.5). A home that adds
  or drops breakfast changes rows, not the schema, the same reasoning as
  funds.
- **A meal entry is one row per member, date and session** with two
  counts: `own` (0, 0.5 or 1) and `guests` (0 or more, steps of 0.5). Kept
  separate so a guest meal is visible later instead of hidden inside "2.0".
  Unique on (member, date, session).
- **A meal session day is one row per home, date and session.** It holds
  the home-guest count and the confirmation (`confirmed_by`,
  `confirmed_at`, empty until confirmed). One table for both, because both
  belong to the session of a day, not to a member.
- **Only confirmed sessions count.** Billable meals = Σ over confirmed
  sessions of (own + guests) × weight; home guests are never billable, so
  the books still balance (BR-1). Cook for = own + guests + home guests,
  without weights. Both are computed, not stored.
- **The lock is a rule, not a column.** A member can write a meal entry
  only while its session day is unconfirmed and its date is today or later
  (home time zone); the service checks it. Owner and manager edits after
  that go to the change log (FR-27).
- **Weights in closed months don't change:** a weight change applies to
  the open month, so a closed month's statement keeps the weights it was
  closed with (the weight used is recorded with the month at close, decided
  at the meals phase's Gate 0).

### Contacts and files _(agreed 19 Nov 2026)_

From `colivo-design/requirements.md` FR-109–FR-112.

- **One contact table for everyone the home deals with**, with a `kind`
  (landlord, cook, internet, electricity, gas, caretaker, other): name,
  optional photo, optional account / customer ID, note, `started_on` and
  `ended_on`. One table instead of landlord, cook and provider tables, so
  phones, emails and documents are handled once.
- **Phones and emails are rows in a contact method table** (`type` phone
  or email, `value`, `label`, `is_primary`), not JSON lists, so each value
  is validated and searchable, and a contact can have any number.
- **Never deleted:** a contact who leaves gets `ended_on` and shows in
  Past contacts. At most one active landlord per home.
- **Paid to:** a bill category has an optional payee contact (at most
  one). Each bill payment stores the contact it was paid to, so changing
  the cook never rewrites old payments.
- **One attachment table for every file** (contact documents, the lease,
  and later receipts and proof under FR-74), linked to what it belongs to.
  How the link is modelled (one link table per owner type, or an owner
  type + id pair) is settled at the Phase 2 Gate 0. Sensitive files are
  encrypted, as ID documents are (FR-61).
- **Visibility is a service rule:** members get cook and provider names
  and phones only; landlord details, account IDs, notes and documents are
  for the owner and managers (FR-112).

### History of money entries _(agreed 17 Nov 2026)_

Money entries are append-only (above), so their history is the chain of
linked entries plus the change log (FR-27). History for other records
(rooms, members, rules) is still open below.

## Open questions

To settle in the domain sketch, or in the first phase that needs them:

| Question                                                    | Options                                                                                               |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| History of non-money records                                | Audit table per entity, versioned rows (`valid_from` / `valid_to`), or `deleted_at` plus an event log |
| Primary keys                                                | UUID (safe to expose, no guessing) or `bigint` identity (smaller, ordered)                            |
| Fixed value sets (role, bill type, fund kind, contact kind) | PostgreSQL enum, `CHECK` constraint on text, or a lookup table                                        |
| Table names                                                 | Singular (`home`, SQLModel's default) or plural (`homes`)                                             |

## ER diagram

_No tables yet._

```mermaid
erDiagram
```

## Tables

_No tables yet. Each table gets a `### <table>` section with a
`| Column | Type | Null | Default | Constraint | Why |` table, its indexes
and the query each serves, and its status mark._

## Change log

| Phase                | Change                                                                                                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Design (17 Nov 2026) | Money storage decided as a ledger; returns and corrections are linked entries                                        |
| Design (17 Nov 2026) | Funds are rows; fund cash is tracked per holder; fund keeper is chosen per fund                                      |
| Design (19 Nov 2026) | Meal sessions are rows with a weight; own and guest meals stored apart; home guests and confirmation per session day |
| Design (19 Nov 2026) | One contact table with phones and emails as rows; one attachment table; payee per bill category; fund kind added     |
