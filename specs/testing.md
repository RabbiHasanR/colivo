# Colivo — Testing (TDD)

Every behaviour in Colivo is built test-first. Specs say **what** to build
(`specs/<date>-<slug>/`); this file says **how** it is built. The `/tdd` skill
runs this process one `plan.md` group at a time.

## Project settings

| Setting                         | Value                                                                                                                                                 |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| System type                     | Backend REST API (FastAPI). Web and mobile rows are added in their first phase.                                                                       |
| Language and framework          | Python 3.12, FastAPI, SQLModel, Pydantic v2                                                                                                           |
| Test framework                  | pytest; FastAPI `TestClient` for API tests (endpoints are sync)                                                                                       |
| Fast tests (unit + integration) | `make test-fast` → `cd backend && uv run pytest -m "not slow"`                                                                                        |
| All tests, with end-to-end      | `make test`                                                                                                                                           |
| Coverage                        | `cd backend && uv run pytest --cov=app --cov-report=term-missing`                                                                                     |
| Lint and type checks            | `make lint` (Ruff + pyright) and `make format-check`                                                                                                  |
| Fast-test time budget           | Under 60 seconds                                                                                                                                      |
| Where tests live                | `backend/tests/<module>/test_service.py` (unit), `test_api.py` (integration), `test_e2e.py` (end-to-end); shared setup in `backend/tests/conftest.py` |
| Slow marker                     | `@pytest.mark.slow`                                                                                                                                   |
| Expected-failure marker         | `@pytest.mark.xfail(strict=True, reason="acceptance: <requirement>")`                                                                                 |
| Test database                   | Real PostgreSQL 16 from Docker Compose, a separate test database. Each test runs in a transaction that is rolled back.                                |
| May be mocked                   | SMS provider, email provider, any third-party API. PostgreSQL and Redis are ours, so tests use the real ones from Compose.                            |

Why `strict=True`: when the acceptance test starts passing, pytest fails the
run (XPASS), which forces the mark to be removed. Without it, a forgotten
xfail hides the test forever.

Why no SQLite: `numeric(12,2)`, constraints and transactions behave
differently there, and exact money is Colivo's core risk.

## Core rules

1. **Test first.** No behaviour is added or changed unless a failing test
   requires it. Refactoring, configuration and scaffolding are not behaviour.
2. **See it fail.** Run each new test before writing code; it must fail for
   the expected reason (not an import error or a broken setup).
3. **Minimum code.** Write only enough to pass the failing test.
4. **Refactor on green.** Clean up only while every test passes, then rerun.
   The group's xfail acceptance test is the only test allowed to stay red.
5. **One test at a time.** One behaviour, one test, one cycle.
6. **Test behaviour, not implementation.** Tests call public entry points
   (service functions, endpoints) and survive internal refactors.
7. **One behaviour, one test.** Don't test the same behaviour twice.
8. **Independent tests.** Each test sets up its own data and passes alone or
   in any order.
9. **Never weaken a test to get green.** Don't delete, skip or loosen a
   failing test. If a test is wrong, say why and ask first.
10. **Logic out of the edges.** Business rules live in `service.py`; routers
    and models stay thin (see
    [tech-stack.md → Project conventions](tech-stack.md#project-conventions)).
11. **Fast tests stay fast.** Inside the time budget; slow tests get
    `@pytest.mark.slow`.
12. **Pin legacy code first.** Before changing untested code, write
    characterisation tests that record what it does now.

## Test levels

Many unit tests, fewer integration tests, very few end-to-end tests. This is
a shape, not a quota.

| Level       | Checks                                                                 | Where                 | Runs                           |
| ----------- | ---------------------------------------------------------------------- | --------------------- | ------------------------------ |
| Unit        | One business rule in `service.py` or a pure calculation; no HTTP       | `test_service.py`     | Every change (`test-fast`)     |
| Integration | One endpoint in-process via `TestClient`, test DB rolled back per test | `test_api.py`         | Every change (`test-fast`)     |
| End-to-end  | A full user journey over real HTTP against `docker compose up`         | `test_e2e.py`, `slow` | End of phase, before merge, CI |

Which level a behaviour gets:

- **Unit:** business rules and calculations, e.g. cost per meal, split
  funding, lock after 5 wrong codes, money matching the October 2026
  spreadsheet to the paisa.
- **Integration:** what only the router can show: wrong role → 403, another
  home's data → 404 and never leaked, invalid input → 422, the
  `StandardResponse` shape, status codes.
- **End-to-end:** one per phase, the phase's main journey across several
  endpoints with real state between steps.

When each level is written, per `plan.md` group:

```
Group start
 ├─ 1. Acceptance test: INTEGRATION, written first, red, marked xfail
 ├─ 2. Inner loop per behaviour: UNIT (business rule) or INTEGRATION (edge rule)
 └─ 3. Acceptance test passes → remove xfail
Phase end (last group)
 └─ 4. One END-TO-END test for the main journey, tagged slow
```

## Workflow

### Spec time (`/feature-spec`)

`validation.md → ## Behaviours` lists every behaviour as a numbered plain
sentence (`B1`, `B2`, …), including error and permission cases.
**Gate 1:** the user approves this list with the spec. No test cases yet;
they depend on the design and would go stale.

### Build time (`/tdd`, one `plan.md` group per run)

1. **Sketch the design** for the group: modules, tables, where the logic
   lives. Confirm it.
2. **Write `specs/<date>-<slug>/tests.md`**: for each of the group's
   behaviours, its test cases as checkboxes with a level and a test name.
   **Gate 2:** the user ticks what to build and unticks what to skip.
3. **Acceptance test:** one integration test naming the group's main
   requirement. Run it, show it fails, mark it xfail.
4. **For each ticked test, one at a time:**
   1. Write the test. Run it. Show the red output.
   2. Write the minimum code. Run `make test-fast`. Show green.
   3. Refactor if useful. Run `make test-fast` again.
   4. Tick it as done in `tests.md`.
5. **When all of a behaviour's tests are green:** run `make lint` and
   `make format-check`, commit (`feat(<module>): <behaviour>`), and **stop
   for the user's review** before the next behaviour.
6. **Close the group:** when the acceptance test passes, remove its xfail and
   run `make test-fast`.
7. **Last group of the phase:** add the end-to-end test, then run
   `validation.md` in full.

For a bug fix: first a failing test that reproduces the bug, then the fix.
The test stays as a regression test.

### `tests.md` format

```markdown
## Group 2 — Log-in

Acceptance: `test_api.py::test_member_logs_in_with_one_time_code` (xfail until green)

### B3 — Log-in locks after 5 wrong codes

- [x] T3.1 unit — `test_sixth_attempt_rejected_after_five_wrong_codes`
- [x] T3.2 integration — `POST /api/v1/auth/verify` returns 429 when locked
- [ ] T3.3 unit — `test_lock_expires_after_15_minutes` _(skipped: out of scope)_
```

`[x]` = selected at Gate 2. Done tests get ✅ after the name. An unticked
test keeps its line with the reason, so the decision is recorded.

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

Several bad inputs for one rule go in one `@pytest.mark.parametrize` test.

## Mocks, data and coverage

- **Mock only external services:** SMS, email, third-party APIs. Never mock
  Colivo's own modules; such tests pass when the real code is broken.
- **Fresh state per test:** fixtures in `conftest.py` create the data; the
  rolled-back transaction removes it.
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
- Every group's acceptance test passes with no xfail mark.
- Error, permission and home-scoping cases are tested.
- Fast tests are inside the time budget; slow tests are tagged.
- `make lint` and `make format-check` pass.
- `make test` passes with no skipped or weakened tests.
