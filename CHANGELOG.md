# Changelog

All notable changes to Colivo, grouped by date (newest first).

## 2026-11-19

- Added meal sessions and meal confirmation to the design, data model, scope, roadmap, and mobile and web screens.
- Added home contacts to the design, data model, and mobile and web screens.
- Added a fund kind to the data model.
- Added the `/changelog` skill and a rule to run it before every merge.

## 2026-11-17

- Adopted an outside-in TDD workflow in `specs/testing.md`, with review gates for behaviours and test cases.
- Adopted the ember-scaffold web layout, split the test settings into backend and web, and set the per-group build order: backend, contract, web.
- Added a data-model gate to `/feature-spec` and the living schema in `specs/data-model.md`.
- Added returns, exchanges and member corrections, with refunds counted only after the member confirms receipt, to the design, scope, roadmap, and mobile and web screens.
- Decided ledger money storage: balances are computed from entries, confirmed entries are never edited, and corrections are new linked entries.
- Tracked fund cash per holder, with several managers and fund keepers, cash handovers, and receiver confirmation of every payment, in the design, data model, scope, roadmap, and mobile and web screens.

## 2026-11-16

- Added the `/feature-spec` skill for writing roadmap phase specs.
- Adopted the fastapi-orm-scaffold backend layout (SQLModel, Alembic, uv) with the `StandardResponse` API format, and narrowed Phase 0 to backend and infra.

## 2026-11-14

- Added carry-forward, estimated bills and split funding rules to the requirements, and extended prior-month import to fund cash and unpaid bills.
- Added estimates, carry-forward and split funding to the design screens, and aligned the grocery fund display and October status.
- Added estimates, carry-forward and split funding to the specs.
- Pointed the tech-stack design paths to `colivo-design`.

## 2026-11-13

- Added the Colivo design reference.
- Added the specs scaffold: mission, roadmap and tech stack.
- Renamed the requirements title to Colivo.
