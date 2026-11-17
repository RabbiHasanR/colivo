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
statement, credit, deposit, inbox item, message.

The main question to settle here is how money is stored (see
[Open questions](#open-questions)).

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
- No hard deletes of user data; history follows the rule chosen in
  [Open questions](#open-questions).
- A rule a user could notice (unique, check, foreign key) is enforced in the
  database **and** listed as a behaviour in the phase's `validation.md`.
- One Alembic migration per `plan.md` group, edited on the phase branch until
  the group is done; a migration merged to `main` is never edited.

## Open questions

To settle in the domain sketch, or in the first phase that needs them:

| Question                           | Options                                                                                               |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Money storage                      | Ledger of entries with balances computed from them, or stored balances updated on each change         |
| History (soft delete)              | Audit table per entity, versioned rows (`valid_from` / `valid_to`), or `deleted_at` plus an event log |
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

| Phase | Change |
| ----- | ------ |
| —     | —      |
