import { expect, test } from '@playwright/test';

/**
 * Smoke check until Phase 1's journey (web/e2e/accounts.spec.ts, group 5)
 * replaces it: a real browser, the real web app and the real backend from
 * `docker compose up`. No mocks.
 */
test('visitor is sent to the log-in page', async ({ page }) => {
  // GIVEN the backend, PostgreSQL and Redis are running (docker compose up)
  // WHEN  a visitor who isn't logged in opens the web app
  // THEN  the real backend says nobody is logged in, and they land on log-in
  //       inside the Colivo shell
  await page.goto('/');

  await expect(page).toHaveURL(/\/log-in$/);
  await expect(page.locator('[data-test-app-shell]')).toBeVisible();
  await expect(page.locator('[data-test-create-home]')).toBeVisible();
});
