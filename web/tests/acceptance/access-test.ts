import { module, test } from 'qunit';
import { currentURL, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  newHomeSetup,
  notLoggedIn,
} from 'colivo-web/tests/helpers/accounts';

module('Acceptance | access', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test('a visitor who is not logged in is sent to log-in', async function (assert) {
    // GIVEN nobody is logged in
    // WHEN  a visitor opens the home page
    // THEN  they are sent to the log-in page
    worker.use(notLoggedIn);

    await visit('/');

    assert.strictEqual(currentURL(), '/log-in');
  });

  test('someone logged in who opens log-in is sent home', async function (assert) {
    // GIVEN the owner is logged in
    // WHEN  they open the log-in page
    // THEN  they are sent to their home instead
    worker.use(loggedInAs('owner'));

    await visit('/log-in');

    assert.strictEqual(currentURL(), '/');
  });
});
