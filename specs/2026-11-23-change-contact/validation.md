# Phase 1c — Change a Member's Phone or Email: Validation

Setup from a clean checkout: `cp .env.example .env`, `docker compose up -d`,
`cd backend && uv sync && uv run alembic upgrade head`,
`cd web && pnpm install --frozen-lockfile`. `alembic upgrade head` must
apply this phase's migration cleanly to a Phase 1b database that has homes,
members and a person in two homes in it.

## Behaviours

**Gate 1** of [testing.md](../testing.md#spec-time-feature-spec). Money
against the October 2026 spreadsheet doesn't apply yet: no money is
recorded in this phase. Phase 1 and 1b behaviours still hold.

### A phone, an email, or both

- B1 — A person with both a phone and an email logs in with either one.
  [backend] [web]

### The owner or a manager changes a member's log-in

- B2 — The owner or a manager adds an email to a member who logs in with a
  phone (or a phone to one with an email): a code goes to the new one, and
  once it is typed the member can log in with either. [backend] [web]
- B3 — The owner or a manager changes a member's phone or email: after the
  code from the new one is typed, the member logs in with the new one and
  the old one no longer works. [backend] [web]
- B4 — The owner or a manager removes a member's phone or email while the
  other remains; the removed one no longer logs in. [backend] [web]
- B5 — The last way a member logs in can't be removed: "They need a phone or
  an email to log in." [backend] [web]
- B6 — A wrong code changes nothing and says how many tries are left; an
  expired code says so; after 5 wrong codes the new phone or email is locked
  for 15 minutes; a new code can be sent once a minute, 5 an hour.
  [backend] [web]
- B7 — A phone or email someone else logs in with is refused with "Someone
  else logs in with that phone or email.", and only after the right code;
  asking for the code answers the same either way. [backend] [web]
- B8 — Changing to the phone or email the member already has is refused:
  "That's already their phone or email." [backend] [web]
- B9 — The owner or a manager can't change the log-in of a member who is
  also in another home, now or in the past: "Only they can change their
  log-in, from My profile." The Edit tab shows their phone and email
  read-only with that note, and never says which home. [backend] [web]
- B10 — A manager can't change the owner's phone or email, and a member
  can't change anyone's (403). [backend] [web]
- B11 — Another home's member can't be changed, and the answer doesn't
  reveal they exist (404). [backend]
- B12 — A past member's log-in can't be changed: "Reactivate them first."
  [backend]
- B13 — A phone or email in the wrong form is refused with a clear message
  (422). [backend] [web]
- B14 — A code sent to confirm a change can't be used to log in, and a
  log-in code can't confirm a change. [backend]
- B15 — After the owner or a manager changes or removes a member's phone or
  email, every open session of that member ends; adding one leaves them
  logged in. [backend]
- B16 — The person is told: an addition or change goes to their existing
  phone or email (with the new one partly hidden) and to the new one; a
  removal goes to the one removed. [backend]
- B17 — Every addition, change and removal is kept in the home's history:
  who, when, and the old and new value. [backend]
- B18 — If two changes to the same new phone or email arrive at the same
  moment, one is saved and the other is told it is taken. [backend]
- B19 — _Dropped on 23 Nov 2026, while building group 2: the members list
  shows no phone or email (`WebMembers.html`); they are on the Edit tab._

### My profile

- B20 — Anyone logged in opens My profile from their name in the sidebar
  and sees their name, role, "member since", phone and email. [backend]
  [web]
- B21 — On My profile a person fixes their own name, for this home only.
  [web]
- B22 — A person adds, changes or removes their own phone or email on My
  profile, confirmed with a code sent to the new one, with the same refusals
  as B5–B8 and B13. [backend] [web]
- B23 — A person in several homes changes their own phone or email without
  choosing a home; it changes how they log in to every home, and each home's
  history keeps it under their membership there. [backend]
- B24 — After a person changes or removes their own phone or email, their
  other sessions end and the browser they used stays logged in. [backend]
  [web]

### Security review follow-ups

Filled in after the `/security-review` in group 4: each finding the user
accepts as a fix becomes a behaviour here, built test-first.

## Automated checks

| Check                     | Command                                                                                           | Pass criteria                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fast tests                | `make test-fast`                                                                                  | All pass; backend under 60 s, web under 90 s                                                   |
| All tests with end-to-end | `docker compose up -d && make test`                                                               | All pass, the accounts, several-homes and change-contact journeys included; none skipped       |
| Lint                      | `make lint`                                                                                       | Ruff, pyright, ESLint, ember-template-lint, Stylelint, Glint clean                             |
| Format                    | `make format-check`                                                                               | Ruff format and Prettier report no changes                                                     |
| No missing migration      | `make backend-migrations-check`                                                                   | "No new upgrade operations detected"                                                           |
| Migrations up and down    | `cd backend && uv run alembic downgrade base && uv run alembic upgrade head` on the test database | Both succeed                                                                                   |
| Phase 1b data migrates    | `alembic downgrade -1`, seed homes with members and a person in two homes, `alembic upgrade head` | Succeeds; everyone still logs in to their homes                                                |
| Contract and web types    | `make api-export api-types && git diff --exit-code api/ web/app/data/types/`                      | No diff                                                                                        |
| Web build                 | `cd web && pnpm build`                                                                            | Succeeds                                                                                       |
| CI                        | `CI OK` on the pull request                                                                       | Green                                                                                          |
| Security review           | `/security-review` on the branch                                                                  | No open high or medium finding; each finding fixed (test first) or recorded with the user's OK |

## TDD record

Every group's section in `tests.md` (groups 2 and 3) is complete: each
selected test is ✅, each unticked test has its reason, and no `xfail` or
`test.todo` mark is left. Any Phase 1 or 1b test changed by this phase (for
example one that pins "a person has one phone or email") is named in
`tests.md` with what changed and why, and was approved at Gate 2. Group 1 is
groundwork and has no tests.

## Manual checks

1. **End-to-end walkthrough against the design.** Sign up as Rabbi with a
   phone and create "Our Flat" (`colivo-design/web/WebAuth.html`). Add
   Maruf by phone (`WebMembers.html`). On Maruf's Edit tab, add an email:
   Send code, type the code from the outbox, Save; the Edit tab shows his
   phone and email. Log out; log in as Maruf with the email, then
   with the phone. Open My profile from the sidebar name
   (`WebProfile.html`), change the phone, confirm the code; the old phone now
   gets "Not added yet". Remove the email; Remove is gone from the phone.
2. **Another home.** Sign up as Karim with a second phone, create "Green
   House" and add Maruf's phone. Back in Our Flat as Rabbi, Maruf's Edit tab
   shows the phone and email read-only with "Only they can change their
   log-in, from My profile", and nothing names Green House. Maruf changes
   his email on My profile; both homes' history has the change.
3. **Sessions.** Log Maruf in on two browsers. Rabbi changes Maruf's phone:
   both browsers go to log-in on their next click. Log Maruf in on two
   browsers again; he removes his email on My profile in one: that one stays
   logged in, the other goes to log-in.
4. **Codes.** Type 5 wrong codes on the Edit tab: the lock message with its
   countdown. Ask for a second code at once: "once a minute". Let a code
   expire: "This code expired."
5. **Widths.** Members' Edit tab and My profile at **320px, 768px and
   1280px**, in the light scheme (the design's only one): no horizontal page
   scroll, long emails wrap or are cut with an ellipsis, the code field
   fits, every tap target is at least 44×44px.
6. **Keyboard only.** Change a phone on My profile and on the Edit tab using
   only the keyboard: visible focus ring, Send code, the code field and Save
   reachable in order, focus moves to the code field when the code is sent,
   and errors are read out.
7. **Polish and Lighthouse.** Lighthouse (mobile) on My profile and Members:
   no accessibility or best-practice failures, no console errors, and the
   wording matches [Screens](requirements.md#screens).

## Done means

- Every automated check above passes and every manual check is done.
- `specs/data-model.md` (`membership`'s index marked _built_ and matching
  the migration; the Redis keys recorded), `specs/tech-stack.md`,
  `README.md`, `specs/roadmap.md` (Phase 1c complete),
  `colivo-design/requirements.md` (a Phase 1c change line on FR-84 and
  FR-86) and `CHANGELOG.md` are updated.
- `api/openapi.json` is current.
- No secrets, `.env`, database files, codes or session tokens are
  committed.
