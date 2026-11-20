# Phase 0 — Project Skeleton: Validation

Setup from a clean checkout: `cp .env.example .env`, `docker compose up -d`,
`cd backend && uv sync && uv run alembic upgrade head`,
`cd web && pnpm install --frozen-lockfile`. Phase 0 is the first phase, so
there is no previous database to migrate; `alembic upgrade head` runs with
no revisions.

## Behaviours

**Gate 1** of [testing.md](../testing.md#spec-time-feature-spec). Not
applicable in Phase 0: roles (403), home scoping (404), money against the
October 2026 spreadsheet, and history. There is no home, person or entry
yet, and health is public. They start in Phase 1.

### Health check

- B1 — The health check answers 200 with the database and Redis both "ok",
  inside the standard envelope. [backend]
- B2 — When the database or Redis can't be reached, the health check answers
  503, still in the envelope, and says which one is down. [backend]
- B3 — The health check answers within a few seconds even when a dependency
  is down. [backend]

### API envelope and errors

- B4 — An unknown address under `/api/v1/` answers 404 in the envelope.
  [backend]
- B5 — An unexpected server error answers 500 in the envelope with a
  generic message and no internal details. [backend]
- B6 — The API contract shows every response wrapped in the envelope, so
  the web's generated types match what the API sends. [backend]
- B7 — The web app's address may call the API from the browser; other
  addresses get no CORS permission. [backend]

### Web data layer

- B8 — The web reads the `data` out of the envelope; pages never see the
  envelope. [web]
- B9 — API errors reach pages as plain errors: 422 as field errors, 400 as
  a business-rule error, 409 as a conflict, anything else as a general
  error. [web]
- B10 — A request carries the session's token as a bearer token when there
  is one, and no token when there isn't. [web]

### App shell and start page

- B11 — The start page shows "Server connected" when the server is healthy,
  which part is down when it is not, and "Can't reach the server" when
  there is no answer. [backend] [web]
- B12 — Every page sits in the Colivo shell; below 1024px its menu button
  opens and closes the sidebar. [web]

## Automated checks

| Check                     | Command                                                                                           | Pass criteria                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Fast tests                | `make test-fast`                                                                                  | All pass; backend under 60 s, web under 90 s            |
| All tests with end-to-end | `docker compose up -d && make test`                                                               | All pass, the smoke journey included; none skipped      |
| Lint                      | `make lint`                                                                                       | Ruff, pyright, ESLint, ember-template-lint, Glint clean |
| Format                    | `make format-check`                                                                               | Ruff format and Prettier report no changes              |
| No missing migration      | `cd backend && uv run alembic check`                                                              | "No new upgrade operations detected"                    |
| Migrations up and down    | `cd backend && uv run alembic downgrade base && uv run alembic upgrade head` on the test database | Both succeed                                            |
| Contract and web types    | `make api-export api-types && git diff --exit-code api/ web/app/data/types/`                      | No diff                                                 |
| Web build                 | `cd web && pnpm build`                                                                            | Succeeds                                                |
| CI                        | Both workflows on the pull request                                                                | Green                                                   |

## TDD record

Group 4's section in `tests.md` is complete: each selected test is ✅, each
unticked test has its reason, and no `xfail` or `test.todo` mark is left.
Groups 1, 2, 3 and 5 are scaffolding and have no tests.

## Manual checks

1. **End-to-end walkthrough.** From a fresh clone, follow the README setup.
   Open `http://localhost:8000/api/v1/health` and see both "ok"; open the
   web app and see "Server connected". Stop `postgres`
   (`docker compose stop postgres`): health answers 503 naming the database,
   and the start page says the database is down. Stop the backend: the
   start page says "Can't reach the server".
2. **Shell against the design.** Compare the shell with
   `colivo-design/web/WebHomeEmpty.html` (sidebar, name, content area,
   fonts, colours from `colivo-design/README.md → Design tokens`) at
   **320px, 768px and 1280px**, in the light scheme (the design's only
   one). No horizontal page scroll; the menu button is at least 44×44px.
3. **Keyboard only.** Tab to the menu button, open and close the sidebar
   with Enter and Space, see a visible focus ring, and reach every link in
   the open sidebar.
4. **Zoom.** The viewport meta never disables zoom; the page works at 200%
   browser zoom.
5. **Polish and Lighthouse.** Run Lighthouse on the start page (mobile):
   no accessibility or best-practice failures, no console errors, fonts load
   from the app itself (no third-party requests).
6. **CI path filters and gate.** On the pull request: a change only in
   `web/` runs only the Web job; only in `backend/` only the Backend job; in
   `api/` or the `Makefile` both; a docs-only change neither, and `CI OK` is
   green in every case. On `main` both jobs always run.

## Done means

- Every automated check above passes and every manual check is done.
- `specs/data-model.md`, `specs/tech-stack.md`, `colivo-design/requirements.md`
  (NFR-11), `README.md`, `specs/roadmap.md` and `CHANGELOG.md` are updated.
- `api/openapi.json` is current.
- No secrets, `.env` or database files are committed.
