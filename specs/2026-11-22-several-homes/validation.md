# Phase 1b — A Person in Several Homes: Validation

Setup from a clean checkout: `cp .env.example .env`, `docker compose up -d`,
`cd backend && uv sync && uv run alembic upgrade head`,
`cd web && pnpm install --frozen-lockfile`. `alembic upgrade head` must
apply this phase's migration cleanly to a Phase 1 database that has homes
and members in it.

## Behaviours

**Gate 1** of [testing.md](../testing.md#spec-time-feature-spec). Money
against the October 2026 spreadsheet doesn't apply yet: no money is
recorded in this phase. Phase 1's behaviours still hold, except the three
this phase replaces (Phase 1's B5, B23 and B36's "active in another home"
case), which B1, B3 and B4 below supersede.

### Several active homes

- B1 — The owner or a manager adds someone who is active in another home;
  they become a member of this home too and get an SMS or email saying they
  were added to it. [backend] [web]
- B2 — Adding a phone or email that is already an active member of this
  home is refused with "Already a member of this home." [backend] [web]
- B3 — A person who is active in another home can sign up; a new home is
  created with them as its owner, and their other homes are unchanged.
  [backend] [web]
- B4 — The owner or a manager reactivates a past member who has since
  joined another home; it is refused only if another active member has the
  same name. [backend] [web]
- B5 — A person in two homes appears in each home's members list under the
  name that home gave them, and neither home sees the other home's name,
  role or dates for them. [backend]
- B6 — Changing, deactivating or reactivating a person in one home changes
  nothing in their other homes. [backend]

### Choose a home

- B7 — A person active in one home logs in and lands on it straight away,
  as before. [backend] [web]
- B8 — A person active in several homes logs in and sees "Choose a home",
  with each home's name, area and their role there; choosing one opens that
  home. [backend] [web]
- B9 — The first log-in check is shown once per home: the first time a
  person opens a home they were added to, they check their details for that
  home. [backend] [web]

### Switch homes

- B10 — A person in several homes switches home from the home name in the
  shell; the menu lists their other active homes, and choosing one opens its
  home page. Someone in one home sees no menu. [backend] [web]
- B11 — Each browser tab keeps its own home: switching in one tab doesn't
  change another, and reloading a tab keeps its home. A new tab opens on the
  last home chosen. [web]
- B12 — Log-out in one tab logs out every tab; the next log-in starts from
  the log-in answer (the only home, or "Choose a home"), never a remembered
  home. [web]

### Current home on every request

- B13 — For a person in several homes, a request that doesn't say which
  home is refused with "Choose a home" and changes nothing. [backend]
- B14 — A request naming a home the person isn't active in is refused (403)
  and says nothing about that home, whether it exists or not. [backend]
- B15 — Someone removed from the home a tab is showing, while still active
  in another, is taken to "Choose a home" with "You're no longer a member of
  <home>", even when only one home is left; they stay logged in. [backend]
  [web]
- B16 — Someone removed from their last active home is logged out at once,
  even in a tab that is open, and logging in again gets "Not added yet".
  [backend] [web]
- B17 — What a person may do follows their role in the chosen home: the
  owner of one home who is a member of another can't open Members there
  (403, and the link isn't offered). [backend] [web]
- B18 — A home in the wrong form is refused with a clear message (422).
  [backend]
- B19 — The browser lets the web app send which home it is in, and the API
  still answers only the web app's own address. [backend]

### Security review follow-ups

None. The `/security-review` of 23 Nov 2026 (the branch, and Phase 1's
deferred 22 Nov web changes, `121f0b9` included) found no High or Medium
finding. Its one product note (anyone can be added to a home, revealing
nothing about them) is in
[tech-stack.md → Known limitations](../tech-stack.md#known-limitations).

## Automated checks

| Check                     | Command                                                                                           | Pass criteria                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fast tests                | `make test-fast`                                                                                  | All pass; backend under 60 s, web under 90 s                                                   |
| All tests with end-to-end | `docker compose up -d && make test`                                                               | All pass, the accounts and several-homes journeys included; none skipped                       |
| Lint                      | `make lint`                                                                                       | Ruff, pyright, ESLint, ember-template-lint, Stylelint, Glint clean                             |
| Format                    | `make format-check`                                                                               | Ruff format and Prettier report no changes                                                     |
| No missing migration      | `make backend-migrations-check`                                                                   | "No new upgrade operations detected"                                                           |
| Migrations up and down    | `cd backend && uv run alembic downgrade base && uv run alembic upgrade head` on the test database | Both succeed                                                                                   |
| Phase 1 data migrates     | `alembic downgrade -1`, seed a Phase 1 home with members, `alembic upgrade head`                  | Succeeds; every Phase 1 member still logs in to their home                                     |
| Contract and web types    | `make api-export api-types && git diff --exit-code api/ web/app/data/types/`                      | No diff                                                                                        |
| Web build                 | `cd web && pnpm build`                                                                            | Succeeds                                                                                       |
| CI                        | `CI OK` on the pull request                                                                       | Green                                                                                          |
| Security review           | `/security-review` on the branch, with Phase 1's deferred 22 Nov web changes                      | No open high or medium finding; each finding fixed (test first) or recorded with the user's OK |

## TDD record

Every group's section in `tests.md` (groups 2 and 3) is complete: each
selected test is ✅, each unticked test has its reason, and no `xfail` or
`test.todo` mark is left. Each Phase 1 test changed because FR-85 was
replaced is named in `tests.md` with what changed and why, and was approved
at Gate 2. Group 1 is groundwork and has no tests.

## Manual checks

1. **End-to-end walkthrough against the design.** Sign up as Rabbi and
   create "Our Flat" (`colivo-design/web/WebAuth.html`). Log out; sign up
   with a second phone as Karim and create "Green House"; add Rabbi's phone
   to Green House as a member (`WebMembers.html`). Log out; log in as Rabbi:
   "Choose a home" lists Our Flat (Owner) and Green House (Member). Open
   Green House: the first log-in check, then its home page with no Members
   link. Switch to Our Flat from the shell's home name (`WebHomeEmpty.html`):
   Members is there.
2. **Two tabs.** With Rabbi on Our Flat in tab 1, open tab 2 and switch it
   to Green House. Reload tab 1: still Our Flat. Open a third tab: Green
   House. Log out in tab 2; tab 1's next click goes to log-in.
3. **Removed from one home.** With Rabbi's tab on Green House, Karim
   deactivates Rabbi there. Rabbi's next click shows "Choose a home" with
   "You're no longer a member of Green House" and only Our Flat to choose;
   Rabbi is still logged in.
4. **Widths.** "Choose a home", the shell's home menu and Members at
   **320px, 768px and 1280px**, in the light scheme (the design's only one):
   no horizontal page scroll, long home names wrap or are cut with an
   ellipsis, the menu fits the screen, every tap target is at least
   44×44px.
5. **Keyboard only.** Choose a home and switch homes using only the
   keyboard: visible focus ring, the home menu opens with Enter or Space,
   moves with the arrow keys, closes with Escape, and focus returns to the
   home name.
6. **Private window.** In a private window (storage may be refused), log in
   as a person with several homes: the picker works, and a reload asks
   again instead of breaking.
7. **Polish and Lighthouse.** Lighthouse (mobile) on "Choose a home" and a
   home page with the switcher: no accessibility or best-practice failures,
   no console errors, and the wording matches [Screens](requirements.md#screens).

## Done means

- Every automated check above passes and every manual check is done.
- `specs/data-model.md` (`membership`'s indexes marked _built_ and matching
  the migration), `specs/tech-stack.md`, `README.md`, `specs/roadmap.md`
  (Phase 1b complete), `colivo-design/requirements.md` (FR-83's change line)
  and `CHANGELOG.md` are updated.
- `api/openapi.json` is current.
- No secrets, `.env`, database files, codes or session tokens are
  committed.
