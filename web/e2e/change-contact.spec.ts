import { expect, test, type Page } from '@playwright/test';
import { addMember, codeSentTo, logIn, randomPhone, signUp } from './helpers';

/**
 * Phase 1c's journey (specs/testing.md → Test levels): changing the phone or
 * email someone logs in with, with the real web app and the real backend
 * from `docker compose up`. No mocks; codes come from the development outbox.
 */

/** In the `kind` row of the log-in editor, change it to `typed`, with its code. */
async function changeWithCode(
  page: Page,
  kind: 'phone' | 'email',
  typed: string,
  codeTo: string,
) {
  const row = page.locator(`[data-test-contact-row="${kind}"]`);
  await page.locator(`[data-test-contact-input="${kind}"]`).fill(typed);
  await page.locator(`[data-test-contact-send-code="${kind}"]`).click();
  await row.locator('[data-test-code-field]').fill(await codeSentTo(codeTo));
  await page.locator(`[data-test-contact-save="${kind}"]`).click();
}

test("the owner adds a member's email, and the member changes their own phone", async ({
  browser,
}) => {
  // GIVEN Rabbi owns "Journey Flat" and added Maruf by phone
  // WHEN  Rabbi adds Maruf's email on the Edit tab with its code; Maruf logs
  //       in with that email and changes his phone on My profile
  // THEN  the old phone is "Not added yet", and Rabbi's Edit tab shows
  //       Maruf's new phone and his email
  // Log-in and change codes share one send a minute per phone or email
  // (FR-94), so the email's log-in code waits a minute after its change code.
  test.setTimeout(150_000);
  const marufPhone = randomPhone('0181');
  const newPhone = randomPhone('0161');
  const marufEmail = `maruf.${Date.now()}@example.com`;
  const rabbi = await (await browser.newContext()).newPage();
  const maruf = await (await browser.newContext()).newPage();

  await signUp(rabbi, randomPhone('0171'));
  await addMember(rabbi, { name: 'Maruf', phone: marufPhone });
  await rabbi.locator('[data-test-edit-member="Maruf"]').click();
  await changeWithCode(rabbi, 'email', marufEmail, marufEmail);
  await expect(rabbi.locator('[data-test-contact-input="email"]')).toHaveValue(
    marufEmail,
  );

  await maruf.waitForTimeout(61_000);
  await logIn(maruf, marufEmail);
  await maruf.locator('[data-test-go-to-my-home]').click();
  await maruf.locator('[data-test-nav-profile]:visible').click();
  await changeWithCode(maruf, 'phone', newPhone.local, newPhone.e164);
  await expect(maruf.locator('[data-test-contact-input="phone"]')).toHaveValue(
    newPhone.e164,
  );

  const again = await (await browser.newContext()).newPage();
  await logIn(again, marufPhone);
  await expect(again.locator('[data-test-not-added]')).toBeVisible();

  // Playwright's page reload, not a WarpDrive record (the rule's false match).
  // eslint-disable-next-line warp-drive/no-legacy-request-patterns
  await rabbi.reload();
  await rabbi.locator('[data-test-edit-member="Maruf"]').click();
  await expect(rabbi.locator('[data-test-contact-input="phone"]')).toHaveValue(
    newPhone.e164,
  );
  await expect(rabbi.locator('[data-test-contact-input="email"]')).toHaveValue(
    marufEmail,
  );
});
