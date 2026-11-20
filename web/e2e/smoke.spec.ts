import { expect, test } from '@playwright/test';

/**
 * Phase 0's one end-to-end journey (specs/testing.md → Test levels): a real
 * browser, the real web app and the real backend from `docker compose up`.
 * No mocks.
 */
test('visitor sees the server is connected', async ({ page }) => {
  // GIVEN the backend, PostgreSQL and Redis are running (docker compose up)
  // WHEN  a visitor opens the web app
  // THEN  the start page, inside the Colivo shell, says the server is connected
  await page.goto('/');

  await expect(page.locator('[data-test-app-shell]')).toBeVisible();
  await expect(page.locator('[data-test-server-status]')).toHaveText(
    'Server connected',
  );
});
