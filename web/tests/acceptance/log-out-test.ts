import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  homesApi,
  loggedInAs,
  newHomeSetup,
  notLoggedIn,
  OUR_FLAT_ID,
} from 'colivo-web/tests/helpers/accounts';
import { TAB_HOME_KEY } from 'colivo-web/services/current-home';

module('Acceptance | log out', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, loggedInAs('owner'), newHomeSetup);

  test('owner logs out from the shell and is back on log-in', async function (assert) {
    // GIVEN the owner is logged in, on their home page
    // WHEN  they press "Log out" in the shell
    // THEN  the API ends the session and they are back on the log-in page
    let loggedOut = false;
    worker.use(
      http.post('*/api/v1/auth/log-out', () => {
        loggedOut = true;
        worker.use(notLoggedIn);
        return HttpResponse.json({ success: true, message: 'Logged out' });
      }),
    );
    await visit('/');
    assert.dom('[data-test-shell-person]').hasText('Rabbi Hasan · Owner');

    await click('[data-test-log-out]');

    assert.true(loggedOut, 'the session was ended');
    assert.strictEqual(currentURL(), '/log-in');
  });

  test('after log-out, a log-in with several homes shows "Choose a home", not the old home', async function (assert) {
    // GIVEN Rabbi, in Our Flat and Green House, is logged in to Our Flat in this tab
    // WHEN  he logs out, then logs in again
    // THEN  he is asked which home, instead of landing in Our Flat
    worker.use(...homesApi(undefined, { loggedIn: true }));
    sessionStorage.setItem(TAB_HOME_KEY, OUR_FLAT_ID);
    await visit('/');
    assert.dom('[data-test-shell-home]').includesText('Our Flat');

    await click('[data-test-log-out]');
    await fillIn('[data-test-log-in-contact]', '01712 345678');
    await click('[data-test-log-in-send-code]');
    await fillIn('[data-test-log-in-form] [data-test-code-field]', '123456');
    await click('[data-test-log-in-submit]');

    assert.strictEqual(currentURL(), '/choose-home');
  });
});
