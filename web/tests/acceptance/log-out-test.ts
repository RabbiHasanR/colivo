import { module, test } from 'qunit';
import { click, currentURL, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  newHomeSetup,
  notLoggedIn,
} from 'colivo-web/tests/helpers/accounts';

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
});
