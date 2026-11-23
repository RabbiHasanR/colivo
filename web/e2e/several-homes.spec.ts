import { expect, test, type Page } from '@playwright/test';
import { addMember, logIn, randomPhone, signUp } from './helpers';

/**
 * Phase 1b's journey (specs/testing.md → Test levels): a person in two
 * homes, with the real web app and the real backend from `docker compose
 * up`. No mocks.
 *
 * Karim owns Green House and Lina owns Our Flat; each adds Rabbi. Rabbi
 * uses two tabs (pages) of one browser, which share his log-in but each
 * keep their own home.
 */

/** The home this page's shell names. */
function shellHome(page: Page) {
  return page.locator('[data-test-shell-home]:visible');
}

/** Open the home on `page`, passing its first log-in check if shown. */
async function arriveHome(page: Page) {
  const check = page.locator('[data-test-go-to-my-home]');
  const greeting = page.locator('[data-test-welcome-greeting]');
  await expect(check.or(greeting)).toBeVisible();
  if (await check.isVisible()) await check.click();
  await expect(greeting).toHaveText('Welcome, Rabbi');
}

test('a person in two homes chooses one, switches in another tab, and is told when removed', async ({
  browser,
}) => {
  // GIVEN Karim owns "Green House" and makes Rabbi a manager there; Lina
  //       owns "Our Flat" and adds Rabbi as a member
  // WHEN  Rabbi logs in, chooses Green House, opens Our Flat in a second tab,
  //       and Karim then deactivates him in Green House
  // THEN  log-in asks which home; each tab keeps its home after a reload;
  //       the Green House tab's next request asks which home, saying why
  const rabbiPhone = randomPhone('0161');
  const karim = await (await browser.newContext()).newPage();
  const lina = await (await browser.newContext()).newPage();
  const rabbiBrowser = await browser.newContext();
  const tabOne = await rabbiBrowser.newPage();

  await signUp(karim, randomPhone('0171'), {
    name: 'Karim',
    home: 'Green House',
  });
  await addMember(karim, { name: 'Rabbi', phone: rabbiPhone, role: 'manager' });
  await signUp(lina, randomPhone('0181'), { name: 'Lina', home: 'Our Flat' });
  await addMember(lina, { name: 'Rabbi', phone: rabbiPhone });

  await logIn(tabOne, rabbiPhone);
  await expect(tabOne).toHaveURL(/\/choose-home$/);
  await expect(tabOne.locator('[data-test-home-choice]')).toHaveCount(2);
  await tabOne.locator('[data-test-home-choice="Green House"]').click();
  await arriveHome(tabOne);
  await expect(shellHome(tabOne)).toContainText('Green House');

  const tabTwo = await rabbiBrowser.newPage();
  await tabTwo.goto('/');
  await expect(shellHome(tabTwo)).toContainText('Green House');
  await tabTwo.locator('[data-test-home-switcher]:visible').click();
  await tabTwo.locator('[data-test-home-switch="Our Flat"]:visible').click();
  await arriveHome(tabTwo);
  await expect(shellHome(tabTwo)).toContainText('Our Flat');

  await tabOne.reload();
  await expect(shellHome(tabOne)).toContainText('Green House');

  await karim.locator('[data-test-deactivate="Rabbi"]').click();
  await karim.locator('[data-test-deactivate-confirm]').click();
  await karim.locator('[data-test-tab="past"]').click();
  await expect(karim.locator('[data-test-member-row="Rabbi"]')).toBeVisible();

  await tabOne.locator('[data-test-nav-members]:visible').click();
  await expect(tabOne).toHaveURL(/\/choose-home$/);
  await expect(tabOne.locator('[data-test-left-home]')).toHaveText(
    "You're no longer a member of Green House.",
  );
  await expect(tabOne.locator('[data-test-home-choice]')).toHaveCount(1);
});
