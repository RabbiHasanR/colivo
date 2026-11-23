import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { http } from 'msw';
import {
  GREEN_HOUSE_ID,
  homeRefusal,
  homesApi,
  newHomeSetup,
  notLoggedIn,
  ourFlat,
  twoHomes,
} from 'colivo-web/tests/helpers/accounts';
import { TAB_HOME_KEY } from 'colivo-web/services/current-home';

module('Acceptance | choose a home', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, notLoggedIn, newHomeSetup);

  test('person in two homes chooses one after log-in, then switches', async function (assert) {
    // GIVEN Rabbi owns "Our Flat" and is a member of "Green House"
    // WHEN  he logs in, chooses Green House, then switches to Our Flat
    // THEN  he sees "Choose a home", then each home he chose in the shell
    worker.use(...homesApi());

    await visit('/log-in');
    await fillIn('[data-test-log-in-contact]', '01712 345678');
    await click('[data-test-log-in-send-code]');
    await fillIn('[data-test-log-in-form] [data-test-code-field]', '123456');
    await click('[data-test-log-in-submit]');

    assert.strictEqual(currentURL(), '/choose-home');
    assert.dom('[data-test-home-choice]').exists({ count: 2 });

    await click('[data-test-home-choice="Green House"]');

    assert.strictEqual(currentURL(), '/');
    assert.dom('[data-test-shell-home]').hasText('Green House');

    await click('[data-test-home-switcher]');
    await click('[data-test-home-switch="Our Flat"]');

    assert.strictEqual(currentURL(), '/');
    assert.dom('[data-test-shell-home]').hasText('Our Flat');
  });

  test('a tab with no home chosen, for a person in several homes, opens "Choose a home"', async function (assert) {
    // GIVEN Rabbi is logged in, in Our Flat and Green House, and this tab has no home
    // WHEN  he opens the app
    // THEN  he is asked which home, with both listed
    worker.use(...homesApi(undefined, { loggedIn: true }));

    await visit('/');

    assert.strictEqual(currentURL(), '/choose-home');
    assert.dom('[data-test-home-choice]').exists({ count: 2 });
  });

  test('removed from the open home goes to "Choose a home" with a notice', async function (assert) {
    // GIVEN Rabbi manages "Green House" in this tab, and also owns "Our Flat"
    // WHEN  Green House removes him, and he then opens Members there
    // THEN  he is asked which home, told he's no longer in Green House, and
    //       only Our Flat is offered
    const homes = [{ ...twoHomes[0]!, role: 'manager' as const }, ourFlat];
    worker.use(
      ...homesApi(homes, { loggedIn: true }),
      http.get('*/api/v1/members', () => homeRefusal(403, 'not_in_home')),
    );
    sessionStorage.setItem(TAB_HOME_KEY, GREEN_HOUSE_ID);
    await visit('/');
    assert.dom('[data-test-shell-home]').includesText('Green House');

    homes.shift();
    await click('[data-test-nav-members]');

    assert.strictEqual(currentURL(), '/choose-home');
    assert
      .dom('[data-test-left-home]')
      .hasText("You're no longer a member of Green House.");
    assert.dom('[data-test-home-choice]').exists({ count: 1 });
    assert.dom('[data-test-home-choice="Our Flat"]').exists();
  });
});
