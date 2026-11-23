import { expect, test } from '@playwright/test';
import { logIn, randomPhone, signUp, todayInDhaka } from './helpers';

/**
 * Phase 1's journey (specs/testing.md → Test levels): a real browser, the
 * real web app and the real backend from `docker compose up`. No mocks.
 *
 * Two browser contexts, one per person, as on two phones: the member stays
 * logged in on theirs while the owner deactivates them.
 */

test('the owner signs up, adds a member who logs in, then deactivates them', async ({
  browser,
}) => {
  // GIVEN the backend, PostgreSQL and Redis are running (docker compose up)
  // WHEN  an owner signs up and adds Maruf; Maruf logs in on his own phone
  //       and checks his details; the owner then deactivates him
  // THEN  each step shows on the right screen, and Maruf's open page goes to
  //       log-in on its next request
  const ownerPhone = randomPhone('0171');
  const marufPhone = randomPhone('0181');
  const owner = await (await browser.newContext()).newPage();
  const maruf = await (await browser.newContext()).newPage();

  await signUp(owner, ownerPhone);
  await expect(owner.locator('[data-test-welcome-greeting]')).toHaveText(
    'Welcome, Rabbi',
  );

  await owner.locator('[data-test-nav-members]').click();
  await owner.locator('[data-test-add-member-name]').fill('Maruf');
  await owner.locator('[data-test-add-member-contact]').fill(marufPhone.local);
  await owner.locator('[data-test-add-member-joined-on]').fill(todayInDhaka());
  await owner.locator('[data-test-add-member-submit]').click();
  await expect(owner.locator('[data-test-member-row="Maruf"]')).toBeVisible();

  await logIn(maruf, marufPhone);
  await expect(maruf).toHaveURL(/\/welcome$/);
  await expect(maruf.locator('[data-test-first-log-in-check]')).toContainText(
    'Journey Flat',
  );
  await maruf.locator('[data-test-go-to-my-home]').click();
  await expect(maruf.locator('[data-test-welcome-greeting]')).toHaveText(
    'Welcome, Maruf',
  );

  await owner.locator('[data-test-deactivate="Maruf"]').click();
  await owner.locator('[data-test-deactivate-confirm]').click();
  await owner.locator('[data-test-tab="past"]').click();
  await expect(owner.locator('[data-test-member-row="Maruf"]')).toBeVisible();

  // Maruf opens the app again on his phone: its first request is refused.
  await maruf.goto('/');
  await expect(maruf).toHaveURL(/\/log-in$/);
});
