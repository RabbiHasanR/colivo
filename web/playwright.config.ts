import { defineConfig, devices } from '@playwright/test';

/**
 * End-to-end tests (web/e2e/) run in a real browser against the real backend
 * (`docker compose up`), with no mocks. One main journey per phase
 * (specs/testing.md → Test levels).
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: process.env['CI'] ? 1 : 0,
  reporter: process.env['CI'] ? 'line' : 'list',
  use: {
    baseURL: process.env['WEB_URL'] ?? 'http://localhost:4200',
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  // Starts the web dev server for local runs. The API must already be up.
  webServer: {
    command: 'pnpm start',
    url: 'http://localhost:4200',
    // Locally reuse a running `pnpm start`; in CI always start a fresh one
    // (Playwright's documented default).
    reuseExistingServer: !process.env['CI'],
    timeout: 120_000,
  },
});
