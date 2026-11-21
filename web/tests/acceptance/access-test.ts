import { module, test } from 'qunit';
import { currentURL, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  newHomeSetup,
  newHomeSetupBody,
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

  test("a member's home page has no checklist and never asks for it", async function (assert) {
    // GIVEN Maruf, a member (not the owner or a manager), is logged in
    // WHEN  he opens his home page
    // THEN  it has no setup checklist, and the app never asked the API for one
    let setupRequests = 0;
    worker.use(
      loggedInAs('member'),
      http.get('*/api/v1/home/setup', () => {
        setupRequests += 1;
        return HttpResponse.json(newHomeSetupBody);
      }),
    );

    await visit('/');

    assert.dom('[data-test-welcome-greeting]').hasText('Welcome, Maruf');
    assert.dom('[data-test-setup-checklist]').doesNotExist();
    assert.strictEqual(setupRequests, 0, 'no request for the checklist');
  });
});
