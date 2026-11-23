# Phase 1c — Change a Member's Phone or Email: Requirements

## Context

Phase 1c sits between Phase 1b and Phase 2 in the [roadmap](../roadmap.md).
Phase 1 delivered sign-up, log-in with a one-time code, members and roles,
and an Edit tab on Members & roles that changes only a member's name and
join date (FR-86). Phase 1b let one person be active in several homes, and
made the current home travel per request in `X-Colivo-Home`.

A person logs in with one phone **or** one email today: sign-up and "Add a
member" take one, and nothing changes it afterwards. A typo made when adding
someone, a lost SIM, or a new email can't be fixed (asked for on 22 Nov
2026, while checking Phase 1's Members page). This phase lets:

- the owner or a manager **add, change or remove** a member's phone or email
  from the Edit tab;
- anyone **add, change or remove** their own on a new **My profile** page;
- a person have a phone **and** an email, and log in with either.

Every new phone or email is proven with a one-time code sent to it. A phone
or email belongs to the person, not to one home (Phase 1b), so a change
alters how they log in to every home they are in; for someone in another
home, only they may change it. It serves the [mission](../mission.md)'s
"anyone logs in with a phone or email and a one-time code" and keeps each
home's data separate (NFR-03).

Design references:

- `colivo-design/web/WebMembers.html`: Members & roles; the Edit tab (a
  Phase 1 difference with no design of its own) gains the log-in fields.
- `colivo-design/web/WebProfile.html`: **My profile**, the "My details"
  card (Name, Phone, Email).
- `colivo-design/web/WebAuth.html`: the code field and its errors, reused
  for confirming a new phone or email.
- `colivo-design/web/WebHomeEmpty.html`: the app shell, whose name card
  opens My profile.

Technical rules: [tech-stack.md](../tech-stack.md); schema:
[data-model.md](../data-model.md).

## Scope

**In scope**

- A person can have a phone, an email, or both, and logs in with either.
- The owner or a manager adds a missing phone or email to a member, changes
  either, or removes one while the other remains, from the Edit tab on
  Members & roles
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- Anyone adds, changes or removes their own phone or email, and fixes their
  name, on **My profile**, opened from their name in the sidebar
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- Every added or changed phone or email is confirmed with a one-time code
  sent to it, under FR-94's limits.
- For someone also in another home (now or in the past), only they can
  change their log-in; the owner and managers see it read-only.
- A change or removal ends the person's other open sessions; the person is
  told on their old and new phone or email; every change is kept in each
  home's history (FR-27).
- `/security-review` of the branch.

**Out of scope**

- Sign-up and "Add a member" with both a phone and an email at once: they
  still take one; the other is added afterwards.
- Merging two people who turn out to be the same human (two accounts).
- Profile photo, ID document and room on My profile (Phase 2).
- Preferences on My profile: notification settings (out of v1) and language
  (later).
- A real SMS or email provider (still a Deferred decision; the development
  notifier is used).
- Bearer tokens for the mobile app (Phase 10).

## Features

### A phone, an email, or both

Who: everyone.

- A person has at least one way to log in: a phone, an email, or both. Log-in
  (FR-84) works with either, each with its own code, wrong-code count and
  lock (FR-94, unchanged).
- Each phone and each email belongs to at most one person (the `person`
  table's unique rules). Sign-up and "Add a member" still take one.

### The owner or a manager changes a member's log-in

Who: the owner and managers; a manager can't change the owner's (Phase 1's
"only the owner can change the owner's details").

- **Add** the one the member lacks, or **change** either: type the new phone
  or email, press **Send code**; the code goes to the new phone or email,
  and the owner or manager types it (the member reads it out). The change is
  saved only with the right code.
- **Remove** one while the other remains; no code is needed (nothing new is
  proven). The last way to log in can't be removed: "They need a phone or an
  email to log in."
- A new phone replaces the old phone, a new email the old email. Switching
  from phone to email is two steps: add the email, then remove the phone.
- Refused:
  - a member who is also in another home, now or in the past: "Only they can
    change their log-in, from My profile." (403), checked before any code
    is sent. The Edit tab shows both fields read-only with that note and
    never names the other home;
  - a past member: "Reactivate them first." (400);
  - the phone or email they already have: "That's already their phone or
    email." (400);
  - a phone or email someone else logs in with: "Someone else logs in with
    that phone or email." (409), told only after the right code, so nobody
    can use this to check whether a number has a Colivo account;
  - a phone or email in the wrong form (422);
  - another home's member (404, never revealed).
- Codes follow FR-94: 6 digits, 5 minutes, 5 wrong tries then a 15-minute
  lock, one a minute and 5 an hour. A change code is bound to whose log-in
  changes and to what; it can't log anyone in, and a log-in code can't
  confirm a change. The send limit is shared with log-in codes per phone or
  email, so nobody can flood a number by mixing the two.
- A change or removal ends every open session of the member (they log in
  again with what they have now); adding one leaves them logged in.
- The member is told: an addition or change goes to their existing phone or
  email, with the new one partly hidden ("…678", "r…@gmail.com"), and to the
  new one; a removal goes to the removed one.
- Each addition, change and removal is one `change_log` row (FR-27): who,
  when, the old and new value.

### My profile

Who: anyone logged in, for themselves.

- Opened from the name card in the sidebar (and the top bar's on phones).
  Shows their initials, name, role and "member since" in the current home,
  and their phone and email.
- **Name:** fixed with the existing `PATCH /me` (FR-86), in this home only.
- **Phone and email:** add, change or remove their own, with the same code,
  refusals, limits and notices as above, except "another home", which
  doesn't apply to yourself. A change or removal ends their **other**
  sessions; this browser stays logged in.
- Their log-in is the same in every home, so a change made here applies to
  all of them, and each home they are in (active or past) gets its own
  `change_log` row under their membership there.
- Works for a person in several homes without choosing one: the phone and
  email calls need no home (`current_person`).

## Screens

Every screen follows its design. Differences agreed with the user on
23 Nov 2026 (Phase 1c spec, Gate 0):

| Screen               | Design file                                      | Differences                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Members & roles      | `web/WebMembers.html`, `web/WebPastMembers.html` | The Edit tab (Phase 1's difference) gains **Phone** and **Email** fields under Name and Joined on, each showing the current value; the one missing is labelled "(optional)". Each has **Send code**, then a 6-digit code field (as on log-in) and **Save**, and a **Remove** link while both exist. For someone in another home both are read-only with "Only they can change their log-in, from My profile."; for a past member, with "Reactivate them to change their log-in." (agreed at group 2's design sketch). The members list shows no phone or email, as designed (B19 dropped while building group 2). The Phase 1 and 1b differences still apply. |
| My profile (new)     | `web/WebProfile.html`                            | "My details" card: initials instead of a photo (Phase 2); the subtitle has no room ("Owner · member since September 2026"); no ID document row (Phase 2); Phone and Email as in the design, the missing one labelled "(optional)", each with Send code → code → Save and a Remove link while both exist; Name has its own Save. No Preferences card (notification settings out of v1, language later).                                                                                                                                                                                                                                                        |
| App shell            | `web/WebHomeEmpty.html`                          | The name card in the sidebar (and the phone top bar's name) is a link to My profile. Everything else as agreed in Phases 1 and 1b.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Log in (code errors) | `web/WebAuth.html`, `web/WebAuthErrors.html`     | None new: the code field and its wrong, expired, locked and too-soon messages are reused for confirming a phone or email.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

## API

All responses use the `StandardResponse` envelope
([tech-stack.md → API response format](../tech-stack.md#api-response-format)).
`{channel}` is `phone` or `email`. Members endpoints act in the
`X-Colivo-Home` home (Phase 1b); `/me/contact…` need no home.

| Method | Path                                     | Role                | Request             | Response                                                                                                                                                                                                                                             |
| ------ | ---------------------------------------- | ------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/v1/members/{id}/contact/code`      | Owner, manager      | `{ contact }`       | 200 `CodeSentOut`, the same whether or not someone else has it. 400 same as now, past member. 403 member in another home, manager → owner, member role. 404 another home's member. 422. 429 too soon, hourly limit, locked (`CodeErrorOut`). **New** |
| PUT    | `/api/v1/members/{id}/contact`           | Owner, manager      | `{ contact, code }` | 200 `MemberOut`; sets the phone or the email, whichever kind `contact` is, and ends the member's sessions if it replaced one. 400 wrong or expired code (`CodeErrorOut`). 403, 404 as above. 409 someone else has it. 422. 429 locked. **New**       |
| DELETE | `/api/v1/members/{id}/contact/{channel}` | Owner, manager      | —                   | 200 `MemberOut`; ends the member's sessions. 400 the last way to log in, or they have none of that kind. 403, 404 as above. 422 unknown channel. **New**                                                                                             |
| POST   | `/api/v1/me/contact/code`                | Logged in (no home) | `{ contact }`       | 200 `CodeSentOut`. 400 same as now. 422. 429. **New**                                                                                                                                                                                                |
| PUT    | `/api/v1/me/contact`                     | Logged in (no home) | `{ contact, code }` | 200 `MePersonOut` (`phone`, `email`); ends the person's other sessions if it replaced one. 400 wrong or expired code. 409 someone else has it. 422. 429. **New**                                                                                     |
| DELETE | `/api/v1/me/contact/{channel}`           | Logged in (no home) | —                   | 200 `MePersonOut`; ends the person's other sessions. 400 the last way to log in, or none of that kind. 422. **New**                                                                                                                                  |
| GET    | `/api/v1/me`                             | Logged in           | header              | 200 `MeOut`; `person` gains `email`. **Changed**                                                                                                                                                                                                     |
| GET    | `/api/v1/members`                        | Owner, manager      | unchanged           | 200 `list[MemberOut]`; `MemberOut` gains `contact_editable` (whether this owner or manager may change the member's log-in). **Changed**                                                                                                              |

`contact_editable` is false for a member also in another home, a past
member, and the owner when a manager asks. It says nothing about which other
home.

## Data model changes

The full schema is in [data-model.md](../data-model.md#person-phase-1-built);
this is the delta, agreed at Gate 0 on 23 Nov 2026.

| Table / store | Change                                                                                                                                                                   | Group and migration           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- |
| `person`      | No column change. A person may now have both `phone` and `email`; the existing `CHECK phone IS NOT NULL OR email IS NOT NULL` becomes the "last way to log in" rule      | —                             |
| `membership`  | Add `ix_membership_person_id` on `(person_id)`: "is this person in any other home, active or past?"; drop `ix_membership_active_person_id`, which the new index replaces | 2 · `<rev>_change_contact.py` |
| `change_log`  | No schema change: each addition, change or removal is a row with `entity = membership`, one per home the person is in, `old_values` / `new_values` like `{"email": …}`   | —                             |
| Redis         | `otp:change:{person_id}:{contact}` and its wrong-count and lock keys for change codes; `person_sessions:{person_id}`, the set of a person's sessions                     | 2 (no migration)              |

Phase 1b's data is valid unchanged. Group 3 (My profile) has no migration.
The downgrade recreates `ix_membership_active_person_id` and drops the new
index.

Contested choices, agreed at Gate 0 (23 Nov 2026):

- **History is one `change_log` row per home the person is in**, under their
  membership there, not one row with a new `person` entity. A self-change by
  someone in two homes leaves proof in both, and the entity CHECK needs no
  migration. Rejected: `entity = person` (only the home where it was made
  would see it).
- **A change or removal ends the other sessions.** The usual rule after a
  log-in changes ("log out other devices"), and it protects someone whose
  phone was lost or stolen. Adding one ends nothing: nothing was taken away.
  Needs the `person_sessions` set, because sessions are keyed by token hash.
  Rejected: keeping sessions (a lost phone stays logged in).
- **"Someone else has it" only after the right code**, as log-in does, so no
  member can probe whether a number has a Colivo account. Rejected: checking
  before the code.
- **The owner or manager types the code** the member reads out, and the
  change is saved at once. Rejected: a pending change until the member logs
  in with it (a pending column, and the old one keeps working meanwhile).
- **Only the person may change the log-in of someone also in another
  home.** Otherwise one home's owner could set a member's phone to their own
  and log in as them in every other home. Rejected: the old contact confirms
  (doesn't help someone who lost their number), and no rule.

## Decisions

| Decision                          | Choice                                                                                                                                                  | Why                                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Scope                             | Owner/manager edit, My profile self-edit, a phone and an email per person; every new one confirmed with a code                                          | User's choice (23 Nov 2026)                                                                                           |
| Groups                            | Groundwork → owner or manager changes a member's log-in → My profile → verify                                                                           | Agreed at Gate 0. Group 2 builds the code-confirmed change once; group 3 reuses it for yourself                       |
| Merge bar                         | The usual gate, CI green, and `/security-review` of the branch                                                                                          | User's choice. This phase changes who can log in as whom; account takeover is its main risk                           |
| Someone in another home           | Only they change their log-in; the owner and managers get 403 and see it read-only                                                                      | User's choice; stops a cross-home takeover                                                                            |
| Code confirmation                 | Every added or changed phone or email, for both the owner/manager and the self path; removal needs none                                                 | User's choice; a typo or a stranger's number can't take over a member's data                                          |
| Who types the owner's code        | The owner or manager, read out by the member; saved at once                                                                                             | Agreed at Gate 0; no pending state                                                                                    |
| Sessions after a change           | Change and removal end the other sessions (all of the member's for the owner path; all but this browser for yourself); adding ends none                 | Agreed at Gate 0                                                                                                      |
| "Taken" answer                    | 409 only after the right code; the code request answers the same either way                                                                             | Agreed at Gate 0; Phase 1's account-enumeration rule                                                                  |
| History                           | One `change_log` row per home the person is in, `entity = membership`                                                                                   | Agreed at Gate 0                                                                                                      |
| Index                             | `ix_membership_person_id` (full) replaces `ix_membership_active_person_id` (partial)                                                                    | Agreed at Gate 0; one index serves both "any other home" and "active homes"                                           |
| "Another home"                    | Any membership in another home, active or past                                                                                                          | A past member there can be reactivated, and would then log in with what this home set                                 |
| Past members                      | The owner or a manager can't change a past member's log-in: reactivate first (400)                                                                      | Settled at Gate 0; the notice reaches someone who can act on it                                                       |
| Same value                        | 400 "That's already their phone or email."                                                                                                              | Settled at Gate 0; sending a code for no change only spends the person's hourly limit                                 |
| Code keys                         | Change codes in `otp:change:{person_id}:{contact}` with their own wrong count and lock; the send limit `otp:sent:{contact}` is shared with log-in codes | Settled at Gate 0; a change code can't log in, and a number can't be flooded by mixing the two                        |
| Notices                           | Addition or change: the existing phone or email (new value partly hidden) and the new one; removal: the removed one                                     | Roadmap ("told on both"); partly hidden in case the old phone is in the wrong hands                                   |
| Self path needs no home           | `/me/contact…` on `current_person`; `MePersonOut` gains `email`                                                                                         | A log-in isn't tied to one home                                                                                       |
| Editing your own row on Members   | Counts as yourself: the "another home" rule doesn't apply                                                                                               | You are "that person"                                                                                                 |
| `contact_editable` on `MemberOut` | The web shows the Edit tab's log-in fields read-only from it, instead of finding out from a 403                                                         | One source for the rule; it reveals only that a member is in some other home, never which                             |
| One editor for both pages         | `components/contact/contact-editor.gts`, given the send, save and remove actions by its page                                                            | The Edit tab and My profile have the same fields and flow; it reuses `auth/code-field.gts` and `auth/code-errors.gts` |

## Constraints

- Follow [tech-stack.md → Project conventions](../tech-stack.md#project-conventions):
  `CoreRouter` only, `set_response_message` on every endpoint, business
  rules in `service.py`, roles checked in the router, config only through
  `app.core.config.settings`.
- Fetch current docs with `ctx7` for every library this phase touches, at the
  installed version, before coding: FastAPI (enum path parameters, `DELETE`
  routes), redis-py (sets: `SADD`, `SMEMBERS`, `EXPIRE`, pipelines), Alembic
  (dropping a partial index and creating a full one), Ember (a new route
  under `authenticated`, `LinkTo`), WarpDrive (request builders for `PUT`
  and `DELETE`), MSW (handlers for the new endpoints), Playwright (reading
  codes from `dev:outbox`).
- Every behaviour is built test-first, as in [testing.md](../testing.md).
- The schema follows [data-model.md](../data-model.md); a change to it is
  agreed with the user first.
- Money is `Decimal`, never float, and every money change is one database
  transaction (no money yet; each contact change is one transaction with its
  `change_log` rows, and sessions end only after it commits).
- Every query is scoped to the current home, and roles are checked in the
  router; the "another home" check looks at the person's memberships but
  never returns anything about them.
- Nothing is erased: a removed phone or email is kept in `change_log`.
- `api/openapi.json` is exported and the web types regenerated
  (`make api-types`) after any endpoint change; the mobile client comes with
  the first `[mobile]` phase.
- Config comes from env vars, with `.env.example` updated and no secrets
  committed (this phase adds none).
- The Alembic migration applies cleanly to Phase 1b's database.
- No new dependency is expected; anything added is asked first.
