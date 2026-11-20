# colivo-web

The Colivo web app: Ember 7 (TypeScript, `.gts` components, Glint),
WarpDrive and Tailwind CSS v4.

Setup, commands and how work is done: see the [root README](../README.md).
Layout and rules: [specs/tech-stack.md → Project conventions](../specs/tech-stack.md#project-conventions).
Testing (QUnit, MSW, Playwright): [specs/testing.md → Web](../specs/testing.md#web).

```bash
pnpm start   # dev server on http://localhost:4200 (backend: docker compose up)
pnpm test    # unit, integration and acceptance tests
pnpm lint    # ESLint, template lint, Stylelint, Glint
pnpm build   # production build into dist/
```
