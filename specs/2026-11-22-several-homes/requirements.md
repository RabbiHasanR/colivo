# Phase 1b — A Person in Several Homes: Requirements

## Context

Phase 1b sits between Phase 1 and Phase 2 in the [roadmap](../roadmap.md).
Phase 1 delivered sign-up, log-in with a one-time code, the cookie session
in Redis, members and roles, and deactivate and reactivate. It kept the
MVP's rule that a person is active in at most one home (FR-85), enforced by
a unique index on `membership(person_id)`.

This phase replaces that rule (decided 21 Nov 2026, after Phase 1's
security review). One person can be an active member of several homes at
once: a cook's helper in two messes, a manager who runs two flats, or an
owner who is also a member of a friend's home. After logging in, they choose
which home to use, and they switch homes from the app shell. It serves the
[mission](../mission.md)'s promise "One person can be a member of several
homes and chooses which home after logging in", and it is done now, before
Phase 2, so every later module is built on "the current home" from the
start.

It also changes how every request knows its home: the web says which home
in an `X-Colivo-Home` header, and the server checks the person is active
there. This is the core of home isolation (NFR-03), so the phase ends with a
`/security-review`, which also covers Phase 1's deferred 22 Nov web
changes.

Design references (colivo-design's v1 was "one home per account", so there
is no screen for choosing or switching homes; see [Screens](#screens)):

- `colivo-design/web/WebAuth.html`: the log-in layout the home picker
  follows, and the sign-up note this phase rewords.
- `colivo-design/web/WebHomeEmpty.html`: the app shell whose home name
  becomes the home switcher.
- `colivo-design/web/WebMembers.html`: the row style the picker's home rows
  reuse; "Add a member", whose refusal changes.

Technical rules: [tech-stack.md](../tech-stack.md); schema:
[data-model.md](../data-model.md).

## Scope

**In scope**

- Drop "one active home per person" (FR-85): a phone or email active in
  another home can be added, can sign up for a new home, and can be
  reactivated.
- Adding a phone or email that is already an active member of **this** home
  is refused (409).
- Log-in with one active home goes straight there, as now; with several, a
  **Choose a home** page lists them
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- Every home-scoped request names its home in `X-Colivo-Home`; the server
  checks the person is active there, and uses the role in that home.
- A **home switcher** in the app shell for people in more than one home
  ([tech-stack.md → Responsive design](../tech-stack.md#responsive-design)).
- Each browser tab keeps its own home; a new tab opens on the last home
  chosen.
- Removed from the home a tab shows while still active in another: the tab
  moves to another home and the person stays logged in.
- `/security-review` of the branch, including Phase 1's deferred 22 Nov web
  changes (the restyle, log-in tabs, the add-or-edit card, and the 403 role
  re-check in `data/handlers/error-watch.ts` / `session.recheckRole`).

**Out of scope**

- **Creating another home while logged in** (a "Create a new home" action in
  the picker or switcher): not chosen for this phase. A person who wants a
  second home of their own logs out and signs up, which now works.
- **Going straight to the last home used** after log-in: not chosen. A
  person in several homes always sees the picker after log-in; the last
  home is only where a new tab starts.
- Changing a member's phone or email (Phase 1c).
- Leaving a home yourself; only the owner or a manager deactivates (Phase 7
  brings notice and settlement).
- Profile photo, ID documents, rooms (Phase 2).
- Bearer tokens for the mobile app (Phase 10 sends the same header).

## Features

### Several active homes

Who: the owner and managers (adding, reactivating); anyone (sign-up).

- A person can be an active member of any number of homes. Each home has
  its own membership: its own name for them, role, status, stays and first
  log-in check (FR-86). Nothing is shared between homes except the phone or
  email they log in with.
- **Add a member** (FR-79): a phone or email active in another home is
  added like anyone else, and gets the SMS or email saying they were added
  to this home. An active member of **this** home is refused: "Already a
  member of this home." A past member of this home is still refused with
  "reactivate instead" (Phase 1, unchanged).
- **Sign-up** (FR-83): a person active in another home can sign up; a new
  home is created with them as its owner, and their other homes are
  unchanged. A person can therefore own several homes.
- **Reactivate** (FR-92): no longer refused because the member is active in
  another home; still refused when another active member has the same name.
- Changing, deactivating or reactivating a person in one home changes
  nothing in their other homes, and no home sees another home's name, role
  or dates for them (NFR-03).

### Choose a home

Who: anyone logged in.

- Log-in (FR-84) with one active home goes straight to it, as in Phase 1.
- With several active homes, log-in shows **Choose a home**: each home's
  name, area and the person's role there. Choosing one opens its home page,
  or its first log-in check if this is the first time (FR-86).
- With no active home, "Not added yet" (FR-87), as in Phase 1.

### Switch homes

Who: anyone active in more than one home.

- The home name in the shell (sidebar, and the top bar on phones) opens a
  menu of the person's other active homes. Choosing one opens that home's
  home page. Someone in one home sees the name only, no menu.
- **Each browser tab keeps its own home.** Switching in one tab doesn't
  change another tab; a reload stays on the tab's home. A new tab opens on
  the last home chosen in this browser, or the picker if that home is no
  longer one of theirs.
- Log-out in any tab ends the session, so every tab is logged out on its
  next request (Phase 1). The last home chosen is forgotten on log-out, and
  the next log-in starts from the log-in answer, never from a remembered
  home.

### Current home on every request

Who: the API, for every logged-in request.

- The log-in session stays "who you are" (`person_id` in Redis). The home
  is chosen per request with the `X-Colivo-Home` header, which holds a home
  id. The header only chooses among the person's own homes; the cookie still
  decides who they are.
- The server finds the person's **active** membership in that home, and
  everything after uses it: the role check (`require_role`), and every
  query scoped to `membership.home_id`.
- No header: with exactly one active home, that home is used (Phase 1
  clients and tests work unchanged); with several, the request is refused
  with 409 "Choose a home" and changes nothing.
- A home the person isn't active in (deactivated meanwhile, or never a
  member): 403 "You're no longer a member of this home", which says nothing
  about whether that home exists. The web then moves the tab to another of
  their homes, or the picker.
- No active home at all: 401, logged out at once (Phase 1's FR-80 rule).
- Endpoints that need no home: health, `/auth/*`, `GET /me/homes`.

## Screens

Every screen follows its design. colivo-design has no screens for several
homes; the shape below was agreed with the user on 22 Nov 2026 (Phase 1b
spec).

| Screen                  | Design file                                               | Differences                                                                                                                                                                                                                                                                                                               |
| ----------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Choose a home (new)     | `web/WebAuth.html` (layout), `web/WebMembers.html` (rows) | No design of its own. A "Choose a home" card in the log-in page's layout, one row per home (name, area, the person's role there, as a role pill), styled like the Members rows; each row is a tap target. A notice above the card when the person was just removed from a home ("You're no longer a member of Our Flat"). |
| App shell               | `web/WebHomeEmpty.html`                                   | For a person in several homes, the home name under "Colivo" in the sidebar is a button that opens a small menu of their other homes; on phones the top bar shows the home name under "Colivo" with the same menu. For one home, the name stays plain text. Everything else as agreed in Phase 1.                          |
| Log in or create a home | `web/WebAuth.html`                                        | The note under "Create your home" changes from "One account can own one home for now. If your number is already in a home, log in instead." to "Already in a home? You can still create your own, and choose between them when you log in." The rest as agreed in Phase 1.                                                |
| Members & roles         | `web/WebMembers.html`, `web/WebPastMembers.html`          | None new. "Add a member" shows "Already a member of this home." for a duplicate. The Phase 1 differences still apply.                                                                                                                                                                                                     |

## API

All responses use the `StandardResponse` envelope
([tech-stack.md → API response format](../tech-stack.md#api-response-format)).
"Logged in" means a valid session cookie whose person has at least one
active membership; otherwise 401.

**The `X-Colivo-Home` header** (a home id) is read by `current_membership`
on every home-scoped endpoint, which is every endpoint not listed as "no
home" below:

| Header                                        | Person's active homes | Result                                                                      |
| --------------------------------------------- | --------------------- | --------------------------------------------------------------------------- |
| Absent                                        | One                   | That home                                                                   |
| Absent                                        | Several               | 409 "Choose a home", `data.reason = "choose_home"`; nothing read or written |
| A home they're active in                      | Any                   | That home                                                                   |
| A home they're not active in, or no such home | Any                   | 403 "You're no longer a member of this home", `data.reason = "not_in_home"` |
| Not a UUID                                    | Any                   | 422                                                                         |
| Any                                           | None                  | 401                                                                         |

New and changed endpoints (the rest of Phase 1's table is unchanged, and
now acts in the header's home):

| Method | Path                              | Role                | Request             | Response                                                                                                                                                                                                                                                   |
| ------ | --------------------------------- | ------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/v1/auth/log-in`             | None                | `{ contact, code }` | 200 `LogInOut`: `homes` (`list[HomeChoiceOut]`: `id`, `name`, `area`, `role`), and `me` (`MeOut`) when there is exactly one home, else null; the session cookie. 400 wrong or expired code. 404 "Not added yet". 422. 429 locked. **Changed:** was `MeOut` |
| POST   | `/api/v1/auth/sign-up`            | None                | unchanged           | 201 `MeOut` for the new home and the session cookie. **Changed:** no longer 409 for someone active in another home                                                                                                                                         |
| GET    | `/api/v1/me/homes`                | Logged in (no home) | —                   | 200 `list[HomeChoiceOut]`: the person's active homes, by name. **New**                                                                                                                                                                                     |
| GET    | `/api/v1/me`                      | Logged in           | header              | 200 `MeOut`, which gains `homes` (`list[HomeChoiceOut]`) for the switcher. 403, 409 as in the header table                                                                                                                                                 |
| POST   | `/api/v1/members`                 | Owner, manager      | unchanged           | 201 `MemberOut`. **Changed:** 409 "Already a member of this home" for an active member of this home; someone active elsewhere is added                                                                                                                     |
| POST   | `/api/v1/members/{id}/reactivate` | Owner, manager      | unchanged           | 200 `MemberOut`. **Changed:** no longer 409 for someone active in another home                                                                                                                                                                             |

No home: `GET /api/v1/health`, `POST /api/v1/auth/*`, `GET /api/v1/me/homes`.
`MeOut`, `HomeChoiceOut` and `MemberOut` never include another home's data:
`homes` lists only the person's own active homes, with the name and area of
the home and their own role there.

CORS: `X-Colivo-Home` joins the explicit `allow_headers` list in
`backend/app/main.py` (never `*`).

## Data model changes

The full schema is in [data-model.md](../data-model.md#membership-phase-1-built);
this is the delta, agreed at Gate 0 on 22 Nov 2026.

| Table        | Change                                                                                                                             | Group and migration          |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `membership` | Drop the unique index `uq_membership_active_person_id` (`person_id WHERE status = 'active'`), "one active home per person" (FR-85) | 2 · `<rev>_several_homes.py` |
| `membership` | Add the index `ix_membership_active_person_id` (`person_id WHERE status = 'active'`, not unique): a person's active homes          | 2 · `<rev>_several_homes.py` |
| —            | No column changes; Redis sessions unchanged (`person_id`, `expires_at`)                                                            | —                            |

Group 3 (choose and switch) has no migration: the current home travels in
a header and needs no storage. Phase 1's data is valid under the new rules
(they are looser). The downgrade recreates the unique index; it fails only
if someone is by then active in two homes, which is acceptable for a
development or test database.

Contested choice, agreed at Gate 0 (22 Nov 2026): **the client names the
home on every request** (`X-Colivo-Home`), instead of the Redis session
holding the current membership, or the home in every API path.

- Each browser tab is independent: a form in a tab showing Our Flat saves to
  Our Flat even after another tab switched to Green House. With the home in
  the session, the switch in one tab would silently move every tab, and a
  write could land in the wrong home; with money from Phase 4, that is the
  worst failure this phase could add.
- No server state and no switch endpoint; the Flutter app (Phase 10) sends
  the same header with its bearer token.
- Without the header, a person with one home works as in Phase 1, so
  Phase 1's clients and tests stay valid.
- Rejected: the home in the session (one home for every tab sharing the
  cookie), and `/api/v1/homes/{home_id}/…` paths (rewrites every Phase 1
  endpoint, its contract and tests, for the same guarantee).

## Decisions

| Decision                       | Choice                                                                                                                                                                                                                                                                                                                               | Why                                                                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Scope                          | Several active homes (add, sign-up, reactivate), choose a home, switch homes, the security review; not "create another home while logged in" or "go straight to the last home"                                                                                                                                                       | User's choice. The two left out add a second sign-up path and one more stored rule; logging out and signing up covers the first    |
| Groups                         | Groundwork → several active homes → choose and switch → verify                                                                                                                                                                                                                                                                       | User's choice. Group 2 makes several homes possible with real data, so group 3's picker and switcher have something to choose from |
| Merge bar                      | The usual gate, CI green, and `/security-review` of the branch, including the deferred 22 Nov web changes                                                                                                                                                                                                                            | User's choice. This phase changes how every request picks its home, the core of home isolation                                     |
| Screens                        | "Choose a home" card in the log-in layout; the shell's home name opens a menu of the other homes                                                                                                                                                                                                                                     | User's choice; colivo-design has no several-homes screens                                                                          |
| Current home                   | `X-Colivo-Home` header per request, checked against the person's active memberships; session unchanged                                                                                                                                                                                                                               | Agreed at Gate 0; see [Data model changes](#data-model-changes)                                                                    |
| No header, several homes       | 409 `choose_home`; nothing read or written; the server never guesses                                                                                                                                                                                                                                                                 | Agreed at Gate 0. A missing header can turn a save into a refusal, never send it to the wrong home                                 |
| Header names a home not theirs | 403 `not_in_home`, the same answer whether or not the home exists                                                                                                                                                                                                                                                                    | Agreed at Gate 0. The web needs a signal distinct from "your role can't do this", and nobody learns which home ids exist           |
| No active home                 | 401                                                                                                                                                                                                                                                                                                                                  | Agreed at Gate 0; keeps Phase 1's "deactivated means logged out at once" for a person in one home                                  |
| Log-in response                | `LogInOut`: `homes` always, `me` only for one home                                                                                                                                                                                                                                                                                   | Refines Gate 0's "one response model": `MeOut` stays non-null everywhere else, so pages never handle a half-empty `me`             |
| Homes for the switcher         | `MeOut.homes`, plus `GET /me/homes` (no header) for the picker                                                                                                                                                                                                                                                                       | The shell gets everything in one `GET /me`; the picker needs the list exactly when no home can be named                            |
| Where the web keeps the home   | `sessionStorage` (this tab) and `localStorage` (last home chosen, where a new tab starts), read in `services/current-home.ts`, every access in `try/catch`                                                                                                                                                                           | Per-tab homes need per-tab storage; private windows can refuse storage, and the app then asks again instead of breaking            |
| Header in the data layer       | `createAuthHandler(getHomeId)`: the store passes a getter from `current-home`, so `data/` never imports a service                                                                                                                                                                                                                    | Keeps the one-way dependency rule (`eslint-plugin-boundaries`)                                                                     |
| Sign-up while active elsewhere | Allowed; the person can own several homes. FR-83's "one account owns one home" gets a Phase 1b change line in `colivo-design/requirements.md`                                                                                                                                                                                        | Roadmap Phase 1b: "Sign-up … no longer refuse[s] someone active in another home"                                                   |
| Duplicate in this home         | 409 "Already a member of this home." (active); the Phase 1 "reactivate instead" 409 for a past member stays                                                                                                                                                                                                                          | Roadmap Phase 1b; the one-membership-per-home constraint already guards it                                                         |
| Phase 1 tests that pin FR-85   | Changed, not deleted, and asked for at group 2's Gate 2: `test_member_active_in_another_home_cannot_be_added`, `test_reactivating_someone_active_in_another_home_is_refused`, the sign-up refusal in `test_service.py`, and the web's 409 tests in `add-member-form-test.gts`, `sign-up-form-test.gts`, `reactivate-dialog-test.gts` | The rule they pin is replaced on purpose (testing.md rule 9: ask before changing a test)                                           |
| Choosing in the picker         | Pure web: sets the tab's home, then `GET /me`; no "switch" call                                                                                                                                                                                                                                                                      | The header needs no server state                                                                                                   |

## Constraints

- Follow [tech-stack.md → Project conventions](../tech-stack.md#project-conventions):
  `CoreRouter` only, `set_response_message` on every endpoint, business
  rules in `service.py`, roles checked in the router, config only through
  `app.core.config.settings`.
- Fetch current docs with `ctx7` for every library this phase touches
  (FastAPI: header dependencies and CORS `allow_headers`; Alembic: dropping
  and creating partial indexes; Ember: router service and route guards;
  WarpDrive: request handlers and headers; MSW: reading request headers;
  Playwright: several pages in one browser context) before coding, at the
  installed version.
- Every behaviour is built test-first, as in [testing.md](../testing.md).
- The schema follows [data-model.md](../data-model.md); a change to it is
  agreed with the user first.
- Money is `Decimal`, never float, and every money change is one database
  transaction (no money yet; every member change is still one transaction
  with its `change_log` row).
- Every query is scoped to the current home (the membership the header
  chose), and roles are checked in the router against the role in that
  home.
- Nothing is erased: memberships are deactivated, never deleted, and every
  change keeps history in `change_log`.
- `api/openapi.json` is exported and the web types regenerated
  (`make api-types`) after any endpoint change; the mobile client comes with
  the first `[mobile]` phase.
- Config comes from env vars, with `.env.example` updated and no secrets
  committed (this phase adds none).
- The Alembic migration applies cleanly to Phase 1's database.
- No new dependency is expected; anything added is asked first.
