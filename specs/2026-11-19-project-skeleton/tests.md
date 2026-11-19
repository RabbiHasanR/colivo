# Phase 0 — Project Skeleton: Tests

## Group 4 — Health check

Backend acceptance: `backend/tests/health/test_api.py::test_health_reports_database_and_redis_ok`
Web acceptance: `web/tests/acceptance/start-page-test.ts` › visitor sees the server is connected

### B1 — The health check answers 200 with the database and Redis both "ok", inside the standard envelope

- [x] T1.1 integration — `test_health_reports_database_and_redis_ok` ✅ (the backend acceptance test)

### B2 — When the database or Redis can't be reached, the health check answers 503, still in the envelope, and says which one is down

- [x] T2.1 unit — `test_health_reports_the_dependency_that_is_down` ✅ (parametrised: database, redis; real engine/client on a closed port)
- [x] T2.2 integration — `test_health_answers_503_when_the_database_is_down` ✅ — `GET /api/v1/health` returns 503 with `success: false` and `data.database == "down"`

### B3 — The health check answers within a few seconds even when a dependency is down

- [x] T3.1 unit — `test_health_check_gives_up_after_the_timeout` ✅ (parametrised: database, redis; blackholed address, answers `down` in under 5 s)

### B4 — An unknown address under /api/v1/ answers 404 in the envelope

- [x] T4.1 integration — `test_unknown_path_answers_404_in_the_envelope` ✅

### B5 — An unexpected server error answers 500 in the envelope with a generic message and no internal details

- [x] T5.1 integration — `test_unexpected_error_answers_500_without_internals` (own app from `create_app()` with a route that raises)

### B6 — The API contract shows every response wrapped in the envelope

- [x] T6.1 integration — `test_openapi_describes_health_inside_the_envelope` (200 and 503 schemas are `StandardResponse[HealthOut]`)
- [ ] T6.2 web — generated types match the contract _(skipped: checked by `make api-types` leaving no diff, an automated check, not a test)_

### B7 — The web app's address may call the API from the browser; other addresses get no CORS permission

- [x] T7.1 integration — `test_only_the_web_origin_gets_cors_permission` (parametrised: the configured web origin is allowed, `https://other.example` is not)

### B8 — The web reads the data out of the envelope; pages never see the envelope

- [x] T8.1 web unit — envelope handler returns the inner data
- [ ] T8.2 web unit — envelope handler normalises a list to JSON:API resources _(skipped: no stored resource until Phase 1; built test-first with the first one)_

### B9 — API errors reach pages as plain errors: 422 as field errors, 400 as a business-rule error, 409 as a conflict, anything else as a general error

- [x] T9.1 web unit — error handler turns 422 `"<loc>: <msg>"` strings into field errors
- [x] T9.2 web unit — error handler maps 400, 409 and other statuses to their kinds (loop over cases)
- [x] T9.3 web unit — error handler maps a failed fetch to a network error
- [ ] T9.4 web unit — error handler keeps the envelope data of a failed response _(skipped: covered through the public service by T11.2)_

### B10 — A request carries the session's token as a bearer token when there is one, and no token when there isn't

- [x] T10.1 web unit — auth handler sends the token only when the session has one (two cases)
- [ ] T10.2 web unit — auth handler reports a 401 _(skipped: log-in and what a 401 does are Phase 1)_

### B11 — The start page shows "Server connected" when healthy, which part is down when not, and "Can't reach the server" when there is no answer

- [x] T11.1 web acceptance — visitor sees the server is connected (the web acceptance test; also asserts the page sits in the shell)
- [x] T11.2 web unit — server status service reports which part is down on a 503 (real store, MSW)
- [x] T11.3 web unit — server status service reports unreachable when there is no answer (MSW network error)
- [x] T11.4 web integration — server status shows "the database is down" and "Can't reach the server" (loop over the two statuses)

### B12 — Every page sits in the Colivo shell; below 1024px its menu button opens and closes the sidebar

- [x] T12.1 web integration — app shell menu button opens and closes the sidebar (`aria-expanded` and sidebar state toggle)
- [ ] T12.2 web integration — app shell renders the page content _(skipped: covered by T11.1)_
- [ ] T12.3 web integration — `ui/button` calls its action _(skipped: exercised by T12.1; disabled state gets its test with the first form in Phase 1)_
