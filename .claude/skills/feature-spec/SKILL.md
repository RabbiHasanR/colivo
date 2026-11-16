---
name: feature-spec
description: Start the next Colivo roadmap phase. Find it in specs/roadmap.md, create its branch, ask the user grouped questions, then write specs/YYYY-MM-DD-<feature>/{requirements,plan,validation}.md. Run manually with an optional feature hint.
disable-model-invocation: true
allowed-tools: Bash(git status *), Bash(git branch *), Bash(git switch *), Bash(git log *), Bash(date *), Bash(ls *), Bash(npx prettier *), Read, Glob, Grep, Write, AskUserQuestion
---

Write the feature spec for the next piece of Colivo work. Extra instructions
from the user, if any: $ARGUMENTS

Never write a file before step 4. The user answers the questions first.

## 1. Gather context

Read all of these before deciding anything:

- `specs/roadmap.md`: the phases, their part tags (`[backend]`, `[web]`,
  `[mobile]`, `[infra]`), and which are marked `✅ Complete` (the others say
  `⏳ Not started`).
- `specs/mission.md`: scope, audience, and what success looks like.
- `specs/tech-stack.md`: the stack, **Decided in Phase 0**, **Project
  conventions**, **Validation**, **Responsive design**, **Known limitations**,
  and **Deferred decisions**. Note every item still marked _(to confirm)_.
- `colivo-design/requirements.md`: the behaviour rules for this phase's
  features.
- `colivo-design/README.md`, then the screens for this phase in
  `colivo-design/web/` and `colivo-design/mobile/`.
- Every existing `specs/YYYY-MM-DD-*/` directory. Read the newest one in full;
  it is the template for tone, structure, and level of detail. If there is
  none yet, this skill's step 4 is the template.
- What code exists: `ls backend web mobile api infra` and `git log --oneline -15`.
- `git status` and `git branch -a`.

## 2. Pick the feature and branch

- **Feature:** the first roadmap phase not marked `✅ Complete`. If the user's
  extra instructions name a feature or phase, use that one instead. If every
  phase is complete, compare `mission.md` and `colivo-design/requirements.md`
  with the code and existing specs, list the gaps (unmet mission promises,
  deferred decisions, known limitations), and let the user choose in step 3.
- **Name:** a short kebab-case slug for the feature, e.g. `accounts-and-login`.
- **Directory:** `specs/<today>-<slug>/`, where today comes from `date +%F`.
- **Branch:** `phase-<N>-<slug>`, where N is the roadmap phase number.
  - If the working tree has uncommitted changes, stop and ask the user
    what to do with them.
  - Branch from `main` unless the user says otherwise:
    `git switch -c <branch> main`.
  - If the branch already exists, ask before reusing it.

## 3. Ask the user (required, before writing anything)

Call `AskUserQuestion` once, with one question per file you will write:

1. **requirements.md:** scope. Which items are in this phase? Use
   `multiSelect` and give each option's trade-off in its description.
2. **plan.md:** task ordering and slicing, e.g. backend then web per slice
   in one spec, a sub-branch per slice, or the thinnest end-to-end version
   first.
3. **validation.md:** the merge bar beyond the existing gate, e.g. current
   checks only, plus CI green, or plus new tooling.

Rules for the questions:

- Ground every option in what you read; name real files, routes, tables,
  and `colivo-design` screens.
- Put your recommended option first, with "(Recommended)" in its label.
- Ask a 4th question only for a decision that changes the spec's shape and
  can't be settled by a sensible default. The usual case: a **Deferred
  decision** or _(to confirm)_ item in `tech-stack.md` that this phase is the
  first to depend on (e.g. ORM, auth tokens, web CSS, Flutter state
  management). If several apply, put the most important one in the question
  and propose defaults for the rest.
- Make smaller decisions yourself. Record them in the Decisions table and
  point them out in step 5.

## 4. Write the spec

Create `specs/<today>-<slug>/` with three files. Title each file
`# Phase <N> — <Feature Name>: <Requirements|Plan|Validation>`.

Use the design's words (home, owner, fund keeper, grocery fund, home fund,
cost per meal, deposit, credit). Write sections only for the parts the phase
is tagged with: no Flutter tasks for a `[backend] [web]` phase.

### `requirements.md`: scope, decisions, context

- `## Context`: where this phase sits in the roadmap, what earlier phases
  delivered, and which mission goals it serves. Link `../mission.md`,
  `../roadmap.md`, `../tech-stack.md`, and the `colivo-design` screens it
  implements.
- `## Scope`: **In scope** and **Out of scope** bullet lists. Each UI item
  cites
  `[tech-stack.md → Responsive design](../tech-stack.md#responsive-design)`.
- `## Features` with a `### <feature>` per feature when the phase has more
  than one. Each lists its business rules from
  `colivo-design/requirements.md` and who may do it (owner, fund keeper,
  member).
- `## API`: a `| Method | Path | Role | Request | Response |` table for the
  new or changed endpoints under `/api/v1/`, with error codes.
- `## Data model` (or `## Data model changes`): a table of tables and
  columns, with types (money is `numeric(12,2)`), indexes, constraints,
  foreign-key behaviour, the `home_id` scope, and soft-delete/history columns.
- `## Decisions`: a `| Decision | Choice | Why |` table, including the user's
  answers from step 3.
- `## Constraints`: the project conventions, plus:
  - fetch current docs with `ctx7` for every library the phase touches
    (FastAPI, Pydantic, SQLAlchemy, Alembic, Ember, Flutter …) before coding;
  - money is `Decimal`, never float, and every money change is one database
    transaction;
  - every query is scoped to the current home, and roles are checked in the
    router;
  - nothing is erased: edits and deletes keep history;
  - `api/openapi.json` is exported and the web/mobile clients regenerated
    after any endpoint change;
  - config comes from env vars, with `.env.example` updated and no secrets
    committed;
  - Alembic migrations apply cleanly to the previous phase's database.

### `plan.md`: numbered task groups

- Short intro: the branch, and the per-group gate (`make test`, `make lint`,
  `make format-check` green, then a conventional commit with no
  Co-Authored-By or AI attribution lines). For Phase 0, the gate starts once
  group 1 has created the Makefile.
- `## 1. Groundwork`: fetch the relevant docs with `ctx7`, plus any
  settings/env, Alembic migration, router mounting, constants, and Docker
  Compose changes.
- `## 2. <slice> (slice 1)`, `## 3. …`: one group per vertical slice, in
  the order the user chose. Inside each group, order the tasks data → API →
  contract → web → mobile, naming the real files
  (`backend/app/domains/<domain>/{models,schemas,service,router}.py`,
  `backend/migrations/…`, `api/openapi.json`, `web/app/routes/…`,
  `web/app/components/…`, `web/app/services/…`,
  `mobile/lib/features/<feature>/…`). Each group ends with a **Tests:** task
  naming files in `backend/tests/<domain>/`, `web/tests/…`, and
  `mobile/test/…`.
- Last group, `## N. Verify and document`: run `validation.md`; update
  `specs/tech-stack.md` (record decisions under **Decided in Phase <N>** or
  the relevant section, turn _(to confirm)_ into decided, remove resolved
  **Deferred decisions**, add **Known limitations**), `README.md`, and
  `specs/roadmap.md` (mark the phase `✅ Complete`); add a `CHANGELOG.md`
  entry.

### `validation.md`: how to know it's done and mergeable

- Opening line: the clean-checkout setup (`cp .env.example .env`,
  `docker compose up -d`, `cd backend && uv sync && uv run alembic upgrade head`,
  `cd web && npm ci`, and `cd mobile && flutter pub get` if the phase is
  tagged `[mobile]`), and that the migrations apply to the previous phase's
  database.
- `## Automated checks`: a `| Check | Command | Pass criteria |` table: tests
  (`make test`), lint (`make lint`: Ruff, ESLint, ember-template-lint, Glint,
  `flutter analyze`), format (`make format-check`), `alembic check` (no
  missing migration), OpenAPI contract up to date, web build, plus anything
  the user added, such as CI green.
- `### Required tests`: grouped by feature or layer (service, API, web,
  mobile). Each bullet is a concrete, checkable behaviour, including edge
  cases and failure paths. Always include, where they apply:
  - wrong role → 403; another home's data → 404 and never leaked;
  - invalid input → 422 with a clear message;
  - money results match the October 2026 spreadsheet to the paisa;
  - edits and deletes keep history.
- `## Manual checks`: numbered. Always include an end-to-end walkthrough
  against the `colivo-design` screens; web at **320px / 768px / 1280px** in
  every colour scheme the design supports; Flutter on a small phone
  (360×640) and a large phone if `[mobile]`; keyboard-only use on web; and a
  polish/Lighthouse check.
- `## Done means`: all checks pass; tech-stack, README, roadmap, and
  changelog are updated; `api/openapi.json` is current; no secrets, `.env`,
  or database files are committed.

Then run `npx prettier --write specs/<today>-<slug>`.

## 5. Stop for review

Don't commit. Tell the user:

- the branch and directory created;
- one line per file on what it covers;
- a numbered list of the decisions **you** made (the ones they weren't asked
  about), so they can push back;
- that they can say "commit it". The commit is then
  `docs(specs): add phase <N> <slug> spec` with only the spec directory
  staged, and no Co-Authored-By or AI attribution lines.
