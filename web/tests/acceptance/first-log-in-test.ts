import { module, test } from 'qunit';
import { click, currentURL, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { loggedInAs, meBody } from 'colivo-web/tests/helpers/accounts';

module('Acceptance | first log-in', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks);

  test('a member checks their details once, then goes straight home', async function (assert) {
    // GIVEN Maruf was added to "Our Flat" and hasn't checked his details
    // WHEN  he opens the app, goes on from the check, and opens the app again
    // THEN  he first sees the check, then his home; the second time, his home
    worker.use(
      loggedInAs('member', { details_checked: false }),
      http.patch('*/api/v1/me', () => {
        worker.use(loggedInAs('member'));
        return HttpResponse.json(meBody('member'));
      }),
    );

    await visit('/');
    assert.strictEqual(currentURL(), '/welcome', 'the check comes first');
    await click('[data-test-go-to-my-home]');
    assert.strictEqual(currentURL(), '/', 'then the home');
    await visit('/');

    assert.strictEqual(currentURL(), '/', 'straight home the next time');
    assert.dom('[data-test-welcome-greeting]').hasText('Welcome, Maruf');
  });
});
