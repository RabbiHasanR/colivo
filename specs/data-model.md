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
category, meal, grocery entry, grocery fund, home fund, payment, bill,
statement, credit, deposit, inbox item, message, and the linked entries
that change money later: return, correction and refund.

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
handed back, return, correction, and adjustment (closed-month correction,
estimate adjustment).

### History of money entries _(agreed 17 Nov 2026)_

Money entries are append-only (above), so their history is the chain of
linked entries plus the change log (FR-27). History for other records
(rooms, members, rules) is still open below.

## Open questions

To settle in the domain sketch, or in the first phase that needs them:

| Question                           | Options                                                                                               |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------- |
| History of non-money records       | Audit table per entity, versioned rows (`valid_from` / `valid_to`), or `deleted_at` plus an event log |
| Primary keys                       | UUID (safe to expose, no guessing) or `bigint` identity (smaller, ordered)                            |
| Fixed value sets (role, bill type) | PostgreSQL enum, `CHECK` constraint on text, or a lookup table                                        |
| Table names                        | Singular (`home`, SQLModel's default) or plural (`homes`)                                             |

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

| Phase                | Change                                                                        |
| -------------------- | ----------------------------------------------------------------------------- |
| Design (17 Nov 2026) | Money storage decided as a ledger; returns and corrections are linked entries |
