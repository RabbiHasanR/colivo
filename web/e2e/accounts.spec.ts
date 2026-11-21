import { execFileSync } from 'node:child_process';
import { expect, test, type Page } from '@playwright/test';

/**
 * Phase 1's journey (specs/testing.md → Test levels): a real browser, the
 * real web app and the real backend from `docker compose up`. No mocks.
 *
 * Two browser contexts, one per person, as on two phones: the member stays
 * logged in on theirs while the owner deactivates them.
 */

/** A random Bangladeshi mobile number, so the journey can run again. */
function randomPhone(prefix: '0171' | '0181'): { local: string; e164: string } {
  const rest = String(Math.floor(Math.random() * 10_000_000)).padStart(7, '0');
  const local = `${prefix}${rest}`;
  return { local, e164: `+880${local.slice(1)}` };
}

/** Today in Dhaka, as the date inputs take it: `2026-11-21`. */
function todayInDhaka(): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Dhaka',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

interface OutboxMessage {
  to: string;
  text: string;
}

/**
 * The last one-time code the backend's development notifier sent to `to`
 * (it keeps every message in the Redis list `dev:outbox`, newest first).
 */
async function codeSentTo(to: string): Promise<string> {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    const raw = execFileSync(
      'docker',
      [
        'compose',
        'exec',
        '-T',
        'redis',
        'redis-cli',
        'LRANGE',
        'dev:outbox',
        '0',
        '20',
      ],
      { encoding: 'utf8' },
    );
    for (const line of raw.split('\n').filter(Boolean)) {
      const message = JSON.parse(line) as OutboxMessage;
      const code = /\b(\d{6})\b/.exec(message.text)?.[1];
      if (message.to === to && code) return code;
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`No code was sent to ${to}`);
}

async function signUp(page: Page, phone: { local: string; e164: string }) {
  await page.goto('/');
  await expect(page).toHaveURL(/\/log-in$/);
  const form = page.locator('[data-test-sign-up-form]');
  await form.locator('[data-test-sign-up-name]').fill('Rabbi Hasan');
  await form.locator('[data-test-sign-up-contact]').fill(phone.local);
  await form.locator('[data-test-sign-up-home-name]').fill('Journey Flat');
  await form.locator('[data-test-sign-up-send-code]').click();
  await form
    .locator('[data-test-code-field]')
    .fill(await codeSentTo(phone.e164));
  await form.locator('[data-test-sign-up-submit]').click();
  await expect(page).toHaveURL(/\/$/);
}

async function logIn(page: Page, phone: { local: string; e164: string }) {
  await page.goto('/log-in');
  const form = page.locator('[data-test-log-in-form]');
  await form.locator('[data-test-log-in-contact]').fill(phone.local);
  await form.locator('[data-test-log-in-send-code]').click();
  await form
    .locator('[data-test-code-field]')
    .fill(await codeSentTo(phone.e164));
  await form.locator('[data-test-log-in-submit]').click();
}

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
