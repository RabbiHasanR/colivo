# Colivo

> Meal rate, rent, bills, members, bazar — manage any mess, hostel, PG or
> shared flat.

Colivo replaces the spreadsheet a shared home keeps by hand. Members log their
own meals, groceries and payments; the app works out each member's bill from
the cost per meal, rent and utility bills, and keeps the home fund and grocery
fund honest. See [specs/mission.md](specs/mission.md) for the full scope and
[specs/roadmap.md](specs/roadmap.md) for the build order.

## What's in the repo

| Folder           | Holds                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| `backend/`       | REST API: Python 3.14, FastAPI, SQLModel, Alembic, PostgreSQL 16, Redis 7   |
| `web/`           | Web app: Ember 7 (TypeScript, `.gts`), WarpDrive, Tailwind CSS v4           |
| `api/`           | `openapi.json`, the API contract exported from the backend (never edit it)  |
| `infra/`         | Dockerfiles and the PostgreSQL init script                                  |
| `specs/`         | Mission, roadmap, tech stack, testing rules, data model, one folder a phase |
| `colivo-design/` | Screen designs (web and mobile) and the behaviour rules (`requirements.md`) |

The stack and every decision behind it: [specs/tech-stack.md](specs/tech-stack.md).

## Set up from a clean checkout

You need:

- **Docker** with Compose v2 (`docker compose`)
- **uv** (Python packages and Python itself):
  `python3 -m pip install --user uv`, or see
  [the uv docs](https://docs.astral.sh/uv/). Make sure `~/.local/bin` is on
  your `PATH`.
- **Node.js 24** and **pnpm** through corepack: `corepack enable pnpm` (the
  version comes from `web/package.json → packageManager`)
- **Google Chrome**, for the web tests

Then:

```bash
cp .env.example .env              # local settings; never commit .env
docker compose up -d              # PostgreSQL, Redis and the backend
cd backend && uv sync && cd ..    # installs Python 3.14 and the packages
cd web && pnpm install --frozen-lockfile && cd ..
cd web && pnpm exec playwright install chromium --only-shell && cd ..   # end-to-end browser
```

Check it works:

- API: <http://localhost:8000/api/v1/health> answers with the database and
  Redis both `ok`. Interactive docs: <http://localhost:8000/docs>.
- Web: `cd web && pnpm start`, then open <http://localhost:4200>. The start
  page says **Server connected**.

## Everyday commands

Run `make` to list every target. The ones you'll use most:

| Command             | Does                                                              |
| ------------------- | ----------------------------------------------------------------- |
| `make test-fast`    | Backend and web fast tests (no end-to-end)                        |
| `make test`         | Every suite, end-to-end included (needs `docker compose up`)      |
| `make lint`         | Ruff and pyright; ESLint, template lint, Stylelint, Glint         |
| `make format-check` | Ruff format; Prettier                                             |
| `make api-export`   | Write `api/openapi.json` from the backend, after changing the API |
| `make api-types`    | Regenerate the web's API types from `api/openapi.json`            |

Before every commit: `make test-fast lint format-check`, all green.

Per part:

- Backend: `cd backend && uv run pytest`, `uv run alembic upgrade head`,
  `uv add <package>`. The backend in Compose reloads when you save a file.
- Web: `cd web && pnpm start` (dev server), `pnpm test`, `pnpm build`.

## How work is done here

Spec-driven and test-first:

1. Each roadmap phase gets a spec in `specs/<date>-<slug>/`, written with
   `/feature-spec`. Database design is agreed before any table is written
   ([specs/data-model.md](specs/data-model.md)).
2. Each phase is built one `plan.md` group at a time with `/tdd`: a failing
   test first, then the code, one behaviour per commit. The rules are in
   [specs/testing.md](specs/testing.md).
3. `CHANGELOG.md` is kept with `/changelog`, run before merging a branch.

Commits use conventional commits (`feat`, `fix`, `refactor`, `test`, `docs`,
`chore`, `ci`, …).

## Branches and CI

- One branch per phase, `phase-<N>-<slug>`, pushed early with a draft pull
  request. Merged into `main` with a merge commit.
- CI (`.github/workflows/ci.yml`) runs on every pull request and every push to
  `main`. It runs only the parts a change touches (everything on `main`); the
  **`CI OK`** check is the one that must be green to merge.
- `main` is protected: changes arrive through pull requests, and
  `.github/CODEOWNERS` requires the owner's review.

## Troubleshooting

- **Port already in use** (another PostgreSQL or Redis on your machine): set
  `POSTGRES_PORT`, `REDIS_PORT` or `BACKEND_PORT` in `.env`, and update the
  matching URL (`DATABASE_URL`, `TEST_DATABASE_URL`, `REDIS_URL`).
- **`make` can't find `uv`:** `~/.local/bin` isn't on your `PATH`.
- **Tests say the test database doesn't exist:** the PostgreSQL init script
  only runs on a fresh volume. Create it once with
  `docker compose exec postgres psql -U colivo -c "CREATE DATABASE colivo_test"`,
  or start over with `docker compose down -v` (deletes local data).
- **Tests inside the backend container don't work:** by design, the image
  has no test tools. Run tests on your machine with `make test-fast`.
