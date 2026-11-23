import { execFileSync } from 'node:child_process';
import { expect, type Page } from '@playwright/test';

/**
 * Steps shared by the end-to-end journeys (web/e2e/): real browser, real
 * backend from `docker compose up`, codes read from the development outbox.
 */

/** A phone as typed (`01712345678`) and as stored (`+8801712345678`). */
export interface Phone {
  local: string;
  e164: string;
}

/** A random Bangladeshi mobile number, so the journey can run again. */
export function randomPhone(prefix: '0161' | '0171' | '0181'): Phone {
  const rest = String(Math.floor(Math.random() * 10_000_000)).padStart(7, '0');
  const local = `${prefix}${rest}`;
  return { local, e164: `+880${local.slice(1)}` };
}

/** Today in Dhaka, as the date inputs take it: `2026-11-21`. */
export function todayInDhaka(): string {
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
export async function codeSentTo(to: string): Promise<string> {
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

export async function signUp(
  page: Page,
  phone: Phone,
  {
    name = 'Rabbi Hasan',
    home = 'Journey Flat',
  }: { name?: string; home?: string } = {},
) {
  await page.goto('/');
  await expect(page).toHaveURL(/\/log-in$/);
  await page.locator('[data-test-auth-tab="create-home"]').click();
  const form = page.locator('[data-test-sign-up-form]');
  await form.locator('[data-test-sign-up-name]').fill(name);
  await form.locator('[data-test-sign-up-contact]').fill(phone.local);
  await form.locator('[data-test-sign-up-home-name]').fill(home);
  await form.locator('[data-test-sign-up-send-code]').click();
  await form
    .locator('[data-test-code-field]')
    .fill(await codeSentTo(phone.e164));
  await form.locator('[data-test-sign-up-submit]').click();
  await expect(page).toHaveURL(/\/$/);
}

export async function logIn(page: Page, phone: Phone) {
  await page.goto('/log-in');
  const form = page.locator('[data-test-log-in-form]');
  await form.locator('[data-test-log-in-contact]').fill(phone.local);
  await form.locator('[data-test-log-in-send-code]').click();
  await form
    .locator('[data-test-code-field]')
    .fill(await codeSentTo(phone.e164));
  await form.locator('[data-test-log-in-submit]').click();
}

/** The owner on `page` adds `name` (`phone`) with `role`, joining today. */
export async function addMember(
  page: Page,
  {
    name,
    phone,
    role = 'member',
  }: { name: string; phone: Phone; role?: string },
) {
  await page.locator('[data-test-nav-members]').click();
  await page.locator('[data-test-add-member-name]').fill(name);
  await page.locator('[data-test-add-member-contact]').fill(phone.local);
  await page.locator('[data-test-add-member-joined-on]').fill(todayInDhaka());
  await page.locator('[data-test-add-member-role]').selectOption(role);
  await page.locator('[data-test-add-member-submit]').click();
  await expect(page.locator(`[data-test-member-row="${name}"]`)).toBeVisible();
}
