---
name: tdd
description: Build one plan.md group of the current Colivo phase test-first, as in specs/testing.md. Design sketch, Gate 2 on tests.md, then backend → contract → web, one behaviour per cycle, commit and stop after each. Resumes from tests.md. Run manually with an optional group number.
disable-model-invocation: true
allowed-tools: Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git rev-parse *), Bash(git add *), Bash(git commit *), Bash(make *), Bash(uv *), Bash(pnpm *), Bash(docker compose *), Bash(npx ctx7@latest *), Bash(npx prettier *), Bash(date *), Bash(ls *), Read, Glob, Grep, Write, Edit, AskUserQuestion
---

Build one `plan.md` group test-first. Extra instructions from the user, if
any: $ARGUMENTS (usually a group number, e.g. `3`).

`specs/testing.md` is the rulebook: core rules, test levels, test format,
the `tests.md` format, mocks, reporting and "Done means". This skill is only
the procedure around it. Never restate or override a rule from it; when this
file and `testing.md` differ, `testing.md` wins.

**Stops.** A run stops at each **STOP** below and waits for the user. The
next `/tdd` run (or "go on" in the same session) resumes from `tests.md`.

## 1. Locate

- `git status`, `git branch --show-current`, `git log --oneline -10`.
  - Uncommitted changes that are not this group's work in progress: stop and
    ask what to do with them.
  - On `main`: stop. Phases are built on their `phase-<N>-<slug>` branch,
    created by `/feature-spec`.
- The spec directory: the `specs/YYYY-MM-DD-<slug>/` whose slug matches the
  branch. Read in full:
  - its `requirements.md`, `plan.md`, `validation.md`, and `tests.md` if it
    exists;
  - `specs/testing.md`, `specs/data-model.md`, and `specs/tech-stack.md →
Project conventions`;
  - the `colivo-design/` screens and `colivo-design/requirements.md` rules
    named by the group;
  - the code the group touches (existing modules, tests, `conftest.py`, MSW
    handlers, migrations).

## 2. Resume

Progress lives only in `tests.md`, so a new session picks up exactly where
the last one stopped. Pick the group: the number in `$ARGUMENTS`, else the
first `plan.md` group that is not finished. Then:

| `tests.md` state for the group                           | Go to                |
| -------------------------------------------------------- | -------------------- |
| Scaffolding group (no **Behaviours:** line in `plan.md`) | 3, then 6.0          |
| No `## Group <N>` section                                | 3                    |
| Section exists, backend acceptance test not written      | 6.1                  |
| Section has selected tests without ✅                    | 6.2 at the first one |
| All backend tests ✅, backend acceptance still `xfail`   | 6.3                  |
| Backend done, contract not committed                     | 6.4                  |
| Web acceptance not written / web tests without ✅        | 6.5 / 6.6            |
| All ✅, web acceptance still `test.todo`                 | 6.7                  |
| Group done, it is the last slice group of the phase      | 7                    |

Tell the user in one line which group and step you are resuming at. If the
state is unclear (e.g. a test is ✅ but its commit is missing), stop and ask.

## 3. Fetch docs

Use `ctx7` (see the user's context7 rule) for the libraries this group
touches, one concept per query, at most 3 calls. Note the API details that
matter for the design sketch.

## 4. Design sketch — STOP

Present in chat, write nothing:

- **Backend:** module, `service.py` functions with signatures, endpoints
  (method, path, role, request, response, error codes), tables and the
  group's one migration, all matching `data-model.md`.
- **Web:** routes, components, builders/handlers, `utils/` functions.
- **Screens:** each screen's design file in `colivo-design/` and any
  difference from it, from `requirements.md → Screens`. A difference not
  listed there is asked about now, never decided while building.
- What is reused from earlier groups, and what is new.
- Choices you made, numbered, so the user can push back.

**STOP.** Wait for the user to confirm or change the sketch. If the sketch
needs a schema the data model does not have, say so and stop: the model is
changed with the user first, never silently.

## 5. Gate 2: tests.md — STOP

Draft the group's section in chat, in the `tests.md` format from
`testing.md`: both acceptance tests, then per behaviour (`B<n>` from
`validation.md`) its backend **and** web test cases with levels. Mark each
selected `[x]` or unselected `[ ]` with a reason. Check the draft against
`testing.md` before showing it:

- every behaviour of the group has at least one test;
- one behaviour, one test (no calculation tested on the web);
- error, permission (403), home-scoping (404) and one 422 per endpoint are
  covered; database rules have their own tests;
- test IDs `T<behaviour>.<n>`, names after the behaviour.

**STOP.** On approval, write the section into `tests.md` (create the file
with `# Phase <N> — <Feature>: Tests` if it does not exist), run
`npx prettier --write` on it, and commit
`docs(specs): add group <N> test cases`.

## 6. Build

Report every cycle in the four-part order of `testing.md → Reporting`, with
the real command output (trimmed to the relevant lines).

Before every commit run `make test-fast`, `make lint`, `make format-check`;
all green or no commit. Stage only this group's files. Commit messages are
conventional commits with no Co-Authored-By or AI attribution lines.

### 6.0 Scaffolding group

No tests (scaffolding and configuration are not behaviour). Do the tasks in
`plan.md` order, then run the commit gate and commit once, e.g.
`chore(backend): scaffold FastAPI app`. If the Makefile does not exist yet
(Phase 0 group 1), run the gate after the task that creates it; before that,
check each part with its own tool. **STOP** after the commit.

### Backend half

1. **Acceptance.** Write the backend acceptance test named in `plan.md`
   (integration level). Run it; it must fail for the expected reason. Mark
   it `@pytest.mark.xfail(strict=True, reason="acceptance: <requirement>")`.
   Commit `test(<module>): add <group> acceptance test`. **STOP** so the
   user can check the target before any behaviour is built.
2. **Per behaviour**, its selected backend tests, one test at a time:
   red → green → refactor (`testing.md` rules 1–5). A test that fails for
   the wrong reason (import error, broken fixture, missing table) is not
   red: fix the setup, rerun, and only then write code. After each test
   passes, add ✅ after its name in `tests.md`. When the behaviour's backend
   tests are all ✅: commit gate → `feat(<module>): <behaviour>` (code,
   tests and the `tests.md` tick together) → **STOP** for review.
3. **Close.** When the acceptance test XPASSes, remove the `xfail` mark,
   run `make backend-test-fast`, commit `test(<module>): pass <group>
acceptance`.

### Contract

4. Export `api/openapi.json` with the project's export command (Phase 0
   creates it; see `README.md`), run `make api-types`, commit
   `chore(api): update contract for <group>`. Skip 4–8 for a group or phase
   with no `[web]` tag.

### Web half

5. **Acceptance.** Write the web acceptance test (MSW, typed with the
   generated API types). Run it red for the expected reason, mark it
   `test.todo('acceptance: <requirement>', …)`, commit
   `test(web): add <group> acceptance test`. **STOP.**
6. **Per behaviour**, its selected web tests, exactly as in 6.2. Commit
   `feat(web): <behaviour>` → **STOP** for review.
7. **Match the design.** Style each of the group's screens from its
   `colivo-design/web/` file (shared pieces in `components/ui/`, tokens in
   `app.css`). Check each with a screenshot at 390px and 1440px against the
   design; fix what differs, ask about anything that can't match. Commit
   `style(web): match <screen> to colivo-design`.
8. **Close.** Remove `test.todo`, run `make web-test-fast`, commit
   `test(web): pass <group> acceptance`. Tell the user the group is done and
   which group is next.

### While building

- **The web needs an API change:** go back to the backend half: a red
  backend test for it, the fix, the commit gate, then step 4 again. Never
  work around the API in the web.
- **A test shows the data model is wrong:** stop and ask.
- **Ask first** before adding a dependency, changing or deleting an existing
  test, or when a requirement is unclear (`testing.md → Reporting`).
- **Review feedback** after a STOP: fix it with its own test if it is a
  behaviour change, then a follow-up commit (`fix(...)` or
  `refactor(...)`); amend only if the user asks.

## 7. End of phase

Only after the last slice group in `plan.md`:

1. Write the phase's one end-to-end test named in `plan.md`
   (`web/e2e/<journey>.spec.ts` for a `[web]` phase, else
   `backend/tests/<module>/test_e2e.py` marked `slow`). Run it against
   `docker compose up`; red first if the journey is not wired yet, then
   green. Commit `test(e2e): <journey>`.
2. Run `make test` and every row of `validation.md → Automated checks`.
   Report each as pass/fail with output for failures; fix failures with the
   normal cycle.
3. List the `validation.md → Manual checks` for the user to do by hand.
4. **STOP** and tell the user the remaining steps, which this skill does not
   do: the `plan.md` "Verify and document" group (data-model, tech-stack,
   README, roadmap), then **run `/changelog`** before merging the branch.
