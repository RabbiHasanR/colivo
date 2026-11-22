# Colivo — Testing (TDD)

Every behaviour in Colivo is built test-first. Specs say **what** to build
(`specs/<date>-<slug>/`); this file says **how** it is built. The `/tdd` skill
runs this process one `plan.md` group at a time.

## Commands

The root `Makefile` runs every part. Each part also has its own targets.

| Command             | Runs                                                                      |
| ------------------- | ------------------------------------------------------------------------- |
| `make test-fast`    | `backend-test-fast` + `web-test-fast` (no end-to-end)                     |
| `make test`         | Every suite, end-to-end included                                          |
| `make lint`         | Ruff + pyright (backend); ESLint, template lint, Glint (web)              |
| `make format-check` | Ruff format (backend); Prettier (web)                                     |
| `make api-types`    | Regenerates `web/app/data/types/api.generated.ts` from `api/openapi.json` |

Mobile targets are added in the first `[mobile]` phase.

## Backend

| Setting                 | Value                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| System type             | REST API (FastAPI)                                                                                                                                                                                                       |
| Language and framework  | Python 3.14, FastAPI, SQLModel, Pydantic v2                                                                                                                                                                              |
| Test framework          | pytest; FastAPI `TestClient` for API tests (endpoints are sync)                                                                                                                                                          |
| Fast tests              | `make backend-test-fast` → `cd backend && uv run pytest -m "not slow"`                                                                                                                                                   |
| Coverage                | `cd backend && uv run pytest --cov=app --cov-report=term-missing`                                                                                                                                                        |
| Fast-test time budget   | Under 60 seconds                                                                                                                                                                                                         |
| Where tests live        | `backend/tests/<module>/test_service.py` (unit), `test_api.py` (integration), `test_e2e.py` (end-to-end); shared setup in `backend/tests/conftest.py`                                                                    |
| Slow marker             | `@pytest.mark.slow`                                                                                                                                                                                                      |
| Expected-failure marker | `@pytest.mark.xfail(strict=True, reason="acceptance: <requirement>")`                                                                                                                                                    |
| Test database           | Real PostgreSQL 16 from Docker Compose, a separate test database built with `alembic upgrade head` once per test session (so every run also checks the migrations). Each test runs in a transaction that is rolled back. |
| May be mocked           | SMS provider, email provider, any third-party API. PostgreSQL and Redis are ours, so tests use the real ones from Compose.                                                                                               |

Why `strict=True`: when the acceptance test starts passing, pytest fails the
run (XPASS), which forces the mark to be removed. Without it, a forgotten
xfail hides the test forever.

Why no SQLite: `numeric(12,2)`, constraints and transactions behave
differently there, and exact money is Colivo's core risk.

| Level       | Checks                                                                 | Where                 |
| ----------- | ---------------------------------------------------------------------- | --------------------- |
| Unit        | One business rule in `service.py` or a pure calculation; no HTTP       | `test_service.py`     |
| Integration | One endpoint in-process via `TestClient`, test DB rolled back per test | `test_api.py`         |
| End-to-end  | A full journey over real HTTP against `docker compose up`              | `test_e2e.py`, `slow` |

- **Unit:** business rules and calculations, e.g. cost per meal, split
  funding, lock after 5 wrong codes, money matching the October 2026
  spreadsheet to the paisa.
- **Integration:** what only the router can show: wrong role → 403, another
  home's data → 404 and never leaked, invalid input → 422, the
  `StandardResponse` shape, status codes.

## Web

The web follows the `ember-scaffold` skill
([tech-stack.md → Decided in Phase 0](tech-stack.md#decided-in-phase-0)).

| Setting                 | Value                                                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| System type             | Web SPA (Ember, Vite build) consuming the Colivo API                                                                         |
| Language and framework  | TypeScript, Ember, `.gts` components, Glint, WarpDrive, Tailwind CSS v4                                                      |
| Test framework          | QUnit + `@ember/test-helpers`; MSW for the network; Playwright for end-to-end                                                |
| Fast tests              | `make web-test-fast` → `cd web && pnpm test`                                                                                 |
| End-to-end              | `make web-e2e` → `cd web && pnpm exec playwright test` (backend running)                                                     |
| Fast-test time budget   | Under 90 seconds                                                                                                             |
| Where tests live        | `web/tests/unit/`, `web/tests/integration/components/`, `web/tests/acceptance/`, `web/e2e/`; helpers in `web/tests/helpers/` |
| Slow tests              | Everything in `web/e2e/`                                                                                                     |
| Expected-failure marker | `test.todo('acceptance: <requirement>', …)`                                                                                  |
| May be mocked           | The HTTP boundary only, with MSW. Never the app's own services, components or utils.                                         |

`test.todo` is the web's strict xfail: the run passes while the test fails,
and fails as soon as it passes, which forces the mark's removal.

| Level           | Checks                                                                                       | Where                               |
| --------------- | -------------------------------------------------------------------------------------------- | ----------------------------------- |
| Web unit        | Pure functions in `utils/` (money in ৳, dates), service logic, data handlers and builders    | `web/tests/unit/`                   |
| Web integration | One component: error message, disabled submit, role-based visibility, empty and error states | `web/tests/integration/components/` |
| Web acceptance  | The group's main requirement through real routes and templates, API mocked with MSW          | `web/tests/acceptance/`             |
| End-to-end      | The phase's main journey in a real browser against the real backend, no mocks                | `web/e2e/`                          |

- **Business calculations are tested only in the backend.** The web tests
  that it shows what the API returns and handles 400, 403, 404, 409 and 422.
  Testing a calculation in both would test one behaviour twice (rule 7).
- **Keeping mocks honest:** `make api-types` regenerates the API types from
  `api/openapi.json`; every MSW response is typed with them, so a changed
  contract fails `make lint`. The end-to-end test uses no mocks.
- **Layout is not test-driven, but it is not optional.** Build each screen
  from its design (`colivo-design/web/`, `colivo-design/mobile/` for
  Flutter); test what the user can do on it. A group's web (or mobile) half
  is not done until each of its screens matches its design, checked with a
  screenshot at a phone width and a desktop width, with every difference
  agreed with the user (`requirements.md → Screens`). Widths and colours are
  checked again by hand in `validation.md → Manual checks`.

## Core rules

1. **Test first.** No behaviour is added or changed unless a failing test
   requires it. Refactoring, configuration and scaffolding are not behaviour.
2. **See it fail.** Run each new test before writing code; it must fail for
   the expected reason (not an import error or a broken setup).
3. **Minimum code.** Write only enough to pass the failing test.
4. **Refactor on green.** Clean up only while every test passes, then rerun.
   The current acceptance test (xfail or `test.todo`) is the only test
   allowed to stay red, and only one is red at a time.
5. **One test at a time.** One behaviour, one test, one cycle.
6. **Test behaviour, not implementation.** Tests use public entry points
   (service functions, endpoints, rendered components, routes) and survive
   internal refactors.
7. **One behaviour, one test.** Don't test the same behaviour twice, in one
   layer or across layers.
8. **Independent tests.** Each test sets up its own data and passes alone or
   in any order.
9. **Never weaken a test to get green.** Don't delete, skip or loosen a
   failing test. If a test is wrong, say why and ask first.
10. **Logic out of the edges.** Business rules live in `service.py`; routers
    and models stay thin. On the web, routes and templates stay thin and
    logic lives in `utils/` and services (see
    [tech-stack.md → Project conventions](tech-stack.md#project-conventions)).
11. **Fast tests stay fast.** Inside each part's time budget; slow tests are
    tagged or live in `web/e2e/`.
12. **Pin legacy code first.** Before changing untested code, write
    characterisation tests that record what it does now.

## Test levels

Many unit tests, fewer integration tests, very few end-to-end tests. This is
a shape, not a quota. **One end-to-end test per phase, at the top layer the
phase has:** a Playwright journey in a `[web]` phase (it goes through the
real backend too), an HTTP journey in a backend-only phase.

## Workflow

### Spec time (`/feature-spec`)

**Gate 0:** when a phase changes tables, its data model is discussed and
approved with the user first, then recorded in [data-model.md](data-model.md).
Its database rules become behaviours.

`validation.md → ## Behaviours` lists every behaviour as a numbered plain
sentence (`B1`, `B2`, …), including error and permission cases. One list
covers backend and web. **Gate 1:** the user approves this list with the
spec. No test cases yet; they depend on the design and would go stale.

### Build time (`/tdd`, one `plan.md` group per run)

Groups are built one at a time, and inside a group the backend comes first,
then the API contract, then the web. Not the whole backend of a phase first:
API mistakes show up while the code is fresh, and every group is demoable.

```text
0. Design sketch (backend + web) ............................ user confirms
1. tests.md: the group's backend AND web test cases .......... GATE 2

── BACKEND ─────────────────────────────────────────────────
2. Acceptance test (integration) → run → red → xfail(strict=True)
3. Per behaviour, one test at a time:
     red → green → refactor → tick in tests.md
     behaviour done → test-fast, lint, format-check → commit → STOP for review
4. Acceptance passes → remove xfail → make test-fast

── CONTRACT ────────────────────────────────────────────────
5. Export api/openapi.json → make api-types → commit chore(api): …

── WEB ─────────────────────────────────────────────────────
6. Acceptance test (web acceptance, MSW) → run → red → test.todo
7. Per behaviour, one test at a time:
     red → green → refactor → tick in tests.md
     behaviour done → test-fast, lint, format-check → commit → STOP for review
8. Acceptance passes → remove test.todo → make test-fast

Last group of the phase → end-to-end test → validation.md in full
```

Details:

- **Red/green runs** use the part's fast tests (`make backend-test-fast` or
  `make web-test-fast`). Before each commit, run `make test-fast`,
  `make lint` and `make format-check`.
- **Commits:** one per behaviour per part, e.g. `feat(accounts): lock log-in
after 5 wrong codes` and `feat(web): show locked log-in message`. No
  Co-Authored-By or AI attribution lines.
- **A behaviour can have tests in both parts.** Its backend tests run in the
  backend half and its web tests in the web half.
- **If the web needs an API change,** go back to the backend: a red test,
  the fix, then the contract step. Never work around the API in the web.
- **Backend-only groups and phases** skip steps 5–8.
- **The schema follows the agreed data model**
  ([data-model.md](data-model.md), agreed at Gate 0). A test adds a column or
  table only in the agreed shape, in the group's one migration. If a test
  shows the model is wrong, stop and ask; never change the schema silently.
- **Database rules are behaviours.** A unique, check or foreign-key rule
  gets its own test, like any other rule.

For a bug fix: first a failing test that reproduces the bug, then the fix.
The test stays as a regression test.

### `tests.md` format

```markdown
## Group 3 — Log-in

Backend acceptance: `backend/tests/accounts/test_api.py::test_member_logs_in_with_one_time_code`
Web acceptance: `web/tests/acceptance/log-in-test.ts` › member logs in with a one-time code

### B3 — Log-in locks after 5 wrong codes

- [x] T3.1 unit — `test_sixth_attempt_rejected_after_five_wrong_codes`
- [x] T3.2 integration — `POST /api/v1/auth/verify` returns 429 when locked
- [ ] T3.3 unit — `test_lock_expires_after_15_minutes` _(skipped: out of scope)_
- [x] T3.4 web integration — log-in form shows "Too many tries, wait 15 minutes" on 429
```

Levels: `unit`, `integration`, `web unit`, `web integration`,
`web acceptance`, `e2e`. `[x]` = selected at Gate 2. Done tests get ✅ after
the name. An unticked test keeps its line with the reason, so the decision is
recorded.

## Test format

Name each test after the behaviour. Structure it as GIVEN / WHEN / THEN, with
one action per test.

```python
def test_cost_per_meal_divides_grocery_spend_by_total_meals(session):
    """
    GIVEN grocery spend of 3000.00 and 60 meals in the month
    WHEN  cost per meal is calculated
    THEN  it is 50.00
    """
    assert cost_per_meal(session, home_id=1, month="2026-10") == Decimal("50.00")
```

```ts
test('member cannot see the close-month button', async function (assert) {
  // GIVEN a logged-in member (not the owner)
  // WHEN  the month summary is rendered
  // THEN  the close-month button is absent
  await render(<template><MonthSummary @role="member" @summary={{summary}} /></template>);
  assert.dom('[data-test-close-month]').doesNotExist();
});
```

Several bad inputs for one rule go in one parameterised test
(`@pytest.mark.parametrize`, or a loop over cases in QUnit). Web tests select
elements by `data-test-*`, never by CSS class.

## Mocks, data and coverage

- **Mock only external services.** Backend: SMS, email, third-party APIs.
  Web: the Colivo API, through MSW only. Never mock Colivo's own modules;
  such tests pass when the real code is broken.
- **Fresh state per test:** backend fixtures in `conftest.py` create the
  data and the rolled-back transaction removes it; web MSW handlers are reset
  after every test.
- **Readable data:** small, obvious values that make the expected result
  easy to check.
- **Schema validation:** trust Pydantic; don't hand-test every field rule.
  One 422 test per endpoint is enough.
- **Coverage is a guide:** below about 70%, look for untested behaviour.
  Never write tests only to raise the number.

## Reporting

Each cycle is reported in this order, so the test-first sequence is visible:

1. The behaviour, in one sentence.
2. The new test, and the output showing it fails.
3. The code change, and the output showing all fast tests pass.
4. Any refactor, and confirmation that tests still pass.

Ask before adding a dependency, changing an existing test, or when a
requirement is unclear.

## Done means

- Every selected test in `tests.md` was seen failing first and is now ✅.
- Every acceptance test passes with no xfail or `test.todo` mark.
- Error, permission and home-scoping cases are tested.
- Fast tests are inside each part's time budget; slow tests are tagged.
- `make lint` and `make format-check` pass.
- `make test` passes with no skipped or weakened tests.
