# Phase 1 — Accounts and Log-in: Validation

Setup from a clean checkout: `cp .env.example .env`, `docker compose up -d`,
`cd backend && uv sync && uv run alembic upgrade head`,
`cd web && pnpm install --frozen-lockfile`. The Phase 0 database has no
revisions; `alembic upgrade head` must apply this phase's migrations to it
cleanly.

## Behaviours

**Gate 1** of [testing.md](../testing.md#spec-time-feature-spec). Money
against the October 2026 spreadsheet doesn't apply yet: no money is
recorded in this phase.

### Owner sign-up

- B1 — An owner signs up with their name, a phone or email, a 6-digit code,
  a home name, an optional area and the first month; the home is created,
  they are its owner and they are logged in. [backend] [web]
- B2 — With "I live here too" ticked, the owner is a paying member from the
  first month; without it, the owner runs the home and is never charged.
  [backend] [web]
- B3 — The first month can only be the current month or the next one.
  [backend] [web]
- B4 — Each home gets a unique Home ID like OF-4827, shown on the new-home
  page. [backend] [web]
- B5 — Signing up with a phone or email that is active in another home is
  refused with "log in instead". [backend] [web]

### One-time codes

- B6 — Asking for a code sends a 6-digit code by SMS to a phone or by email
  to an email address, and gives the same answer whether or not anyone uses
  that phone or email. [backend] [web]
- B7 — A phone in local form (01712 345678) and in international form
  (+880 1712 345678) is the same person; an email ignores letter case.
  [backend]
- B8 — A code is used once: after a log-in or sign-up it no longer works.
  [backend]
- B9 — A code works for 5 minutes; after that the screen says "This code
  expired" and offers a new one. [backend] [web]
- B10 — A wrong code says how many tries are left; after 5 wrong codes the
  phone or email is locked for 15 minutes and the screen shows how long to
  wait. [backend] [web]
- B11 — A new code can be sent once a minute and 5 times an hour, and it
  replaces the old one; the screen shows when the next one can be sent.
  [backend] [web]

### Log-in and session

- B12 — A person with an active membership logs in with their phone or email
  and a code, and lands on their home. [backend] [web]
- B13 — A phone or email with no active membership (never added, or
  deactivated) gets "Not added yet", with "ask your home's owner or manager"
  and "Create my own home". [backend] [web]
- B14 — A log-in lasts 30 days from the last use, and log-out ends it at
  once. [backend] [web]
- B15 — The log-in is kept in a cookie that page scripts can't read, and only
  the web app's own address may send it. [backend]
- B16 — Everything except the health check, codes, sign-up and log-in needs
  a log-in (401); a logged-out visitor to any page is sent to log-in.
  [backend] [web]

### New home

- B17 — The owner and managers see the setup checklist: "Home created" done,
  "Add members" done once anyone besides the owner is active, and rooms and
  rent, home rules and bills not done yet. [backend] [web]
- B18 — Members don't get the setup checklist (403, and it isn't shown).
  [backend] [web]
- B19 — Every empty list on the home page says what will appear there and,
  where it helps, offers the one action that fills it. [web]

### Members

- B20 — The owner or a manager adds a member with a name, a phone or email
  and a join date; the member gets an SMS or email saying they can log in.
  [backend] [web]
- B21 — Only the owner can add someone as a manager; a manager adds members
  only (403). [backend] [web]
- B22 — Members can't see or change the members list (403, and the Members
  page isn't offered). [backend] [web]
- B23 — A phone or email that is active in another home can't be added.
  [backend] [web]
- B24 — Someone who is a deactivated member of this home can't be added
  again; the message says to reactivate them instead. [backend] [web]
- B25 — Two active members of a home can't have the same name, ignoring
  letter case. [backend] [web]
- B26 — The owner or a manager changes a member's name or join date; the join
  date can't be after the end of their first stay. [backend] [web]
- B27 — On their first log-in a member sees their home, role, join date and
  who added them, and can fix their name; after that they go straight to
  their home. [backend] [web]
- B28 — A member of another home, or an id that doesn't exist, gives 404,
  and nothing about the other home is shown. [backend]
- B29 — An empty name, a name over 80 characters, or something that isn't a
  phone or email is refused with a clear message (422). [backend] [web]
- B30 — Every change to a member (added, name, join date, role,
  deactivated, reactivated) keeps who made it, when, and the old and new
  values. [backend]

### Roles

- B31 — The owner makes a member a manager and takes the role away; anyone
  else gets 403. [backend] [web]
- B32 — The owner's own role can't be changed; a home always has exactly one
  owner. [backend] [web]

### Deactivate and reactivate

- B33 — The owner or a manager deactivates a member from a chosen date
  (today or earlier, not before the start of their current stay) after a
  confirmation; the member can't log in from then on, even on a device where
  they were logged in. [backend] [web]
- B34 — The owner can't be deactivated, and a manager can't deactivate
  another manager. [backend] [web]
- B35 — The owner or a manager reactivates a deactivated member with the
  date charges start again (after the date they were deactivated); they can
  log in again. [backend] [web]
- B36 — Reactivating is refused while the member is active in another home,
  or while another active member has the same name. [backend] [web]
- B37 — The members page lists current and past members on separate tabs,
  with Deactivate on current members and Reactivate on past ones.
  [backend] [web]

### Security review follow-ups (agreed 21 Nov 2026)

- B38 — A manager can't reactivate another manager: bringing a manager back
  is the owner's call, as removing one is. [backend] [web]
- B39 — A manager can't change the owner's name or join date. [backend]
  [web]
- B40 — In production the backend refuses to start with the development
  notifier, which logs one-time codes in plain text. [backend]

## Automated checks

| Check                     | Command                                                                                           | Pass criteria                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fast tests                | `make test-fast`                                                                                  | All pass; backend under 60 s, web under 90 s                                                   |
| All tests with end-to-end | `docker compose up -d && make test`                                                               | All pass, the accounts journey included; none skipped                                          |
| Lint                      | `make lint`                                                                                       | Ruff, pyright, ESLint, ember-template-lint, Stylelint, Glint clean                             |
| Format                    | `make format-check`                                                                               | Ruff format and Prettier report no changes                                                     |
| No missing migration      | `make backend-migrations-check`                                                                   | "No new upgrade operations detected"                                                           |
| Migrations up and down    | `cd backend && uv run alembic downgrade base && uv run alembic upgrade head` on the test database | Both succeed                                                                                   |
| Check constraints match   | Part of `make test-fast`                                                                          | Each `CHECK (col IN …)` equals its `StrEnum`                                                   |
| Contract and web types    | `make api-export api-types && git diff --exit-code api/ web/app/data/types/`                      | No diff                                                                                        |
| Web build                 | `cd web && pnpm build`                                                                            | Succeeds                                                                                       |
| CI                        | `CI OK` on the pull request                                                                       | Green                                                                                          |
| Security review           | `/security-review` on the branch                                                                  | No open high or medium finding; each finding fixed (test first) or recorded with the user's OK |

_Deferred on 22 Nov 2026 (user's decision): the security review of the 22 Nov web changes (the restyle, log-in tabs, the add-or-edit card, and the 403 role re-check in `error-watch.ts` / `session.recheckRole`) moves to Phase 1b. The earlier Phase 1 review covered the backend._

## TDD record

Every group's section in `tests.md` (groups 2–5) is complete: each selected
test is ✅, each unticked test has its reason, and no `xfail` or `test.todo`
mark is left. Group 1 is groundwork and has no tests.

## Manual checks

1. **End-to-end walkthrough against the design.** From a fresh clone,
   follow the README setup. Sign up as an owner
   (`colivo-design/web/WebAuth.html`), read the code from the development
   outbox (`docker compose exec redis redis-cli LRANGE dev:outbox 0 4`),
   land on the new home (`WebHomeEmpty.html`) and see the Home ID. Add a
   member and a manager (`WebMembers.html`). Log out; log in as the member,
   pass the first log-in check (`colivo-design/mobile/Login.html`), and see
   no Members page. Try a wrong code 5 times and see the lock
   (`WebAuthErrors.html`). Log in as the owner and deactivate the member;
   the member's open tab is sent to log-in on its next request; reactivate
   them.
2. **Widths.** Every page above at **320px, 768px and 1280px**, in the light
   scheme (the design's only one): no horizontal page scroll, the members
   table scrolls inside its own box, the log-in tabs and forms fit, every tap
   target is at least 44×44px.
3. **Keyboard only.** Sign up, log in, enter the code, add a member and
   deactivate one using only the keyboard: visible focus ring, the
   confirmation dialog traps focus and closes with Escape, focus returns to
   the button that opened it.
4. **Code input.** On a phone, the code field opens the number pad and
   offers the code from the SMS (`autocomplete="one-time-code"`,
   `inputmode="numeric"`).
5. **Cookie.** In the browser's developer tools the session cookie is
   `HttpOnly`, `SameSite=Lax`, and `Secure` when `ENVIRONMENT` is not
   `development`; `document.cookie` doesn't show it.
6. **Polish and Lighthouse.** Lighthouse (mobile) on the log-in, new-home
   and members pages: no accessibility or best-practice failures, no
   console errors, and the wording matches the design (FR-97).

## Done means

- Every automated check above passes and every manual check is done.
- `specs/data-model.md` (tables marked _built_ and matching the
  migrations), `specs/tech-stack.md`, `README.md`, `specs/roadmap.md`
  (Phase 1 complete, fund keepers moved to Phase 4) and `CHANGELOG.md` are
  updated.
- `api/openapi.json` is current.
- No secrets, `.env`, database files, codes or session tokens are
  committed.
