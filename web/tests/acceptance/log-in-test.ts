import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  codeSentBody,
  logInBody,
  loggedInAs,
  me,
  newHomeSetup,
  newHomeSetupBody,
  notLoggedIn,
  OUR_FLAT_ID,
  ourFlat,
} from 'colivo-web/tests/helpers/accounts';

module('Acceptance | log in', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, notLoggedIn, newHomeSetup);

  test('owner logs back in with a one-time code', async function (assert) {
    // GIVEN the owner of "Our Flat", their only home, is logged out
    // WHEN  they enter their phone, send the code, type it and log in
    // THEN  they land on their home, and its requests name Our Flat
    let named: string | null = null;
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/log-in', () => {
        worker.use(loggedInAs('owner'));
        return HttpResponse.json(logInBody([ourFlat], me('owner')));
      }),
      http.get('*/api/v1/home/setup', ({ request }) => {
        named = request.headers.get('X-Colivo-Home');
        return HttpResponse.json(newHomeSetupBody);
      }),
    );

    await visit('/log-in');
    await fillIn('[data-test-log-in-contact]', '01712 345678');
    await click('[data-test-log-in-send-code]');
    await fillIn('[data-test-log-in-form] [data-test-code-field]', '123456');
    await click('[data-test-log-in-submit]');

    assert.strictEqual(currentURL(), '/');
    assert.dom('[data-test-welcome-greeting]').hasText('Welcome, Rabbi');
    assert.strictEqual(named, OUR_FLAT_ID);
  });
});
