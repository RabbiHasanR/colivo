import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  newHomeSetup,
  notLoggedInBody,
} from 'colivo-web/tests/helpers/accounts';
import { member, membersApi, owner } from 'colivo-web/tests/helpers/members';

module('Acceptance | member status', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test.todo(
    'acceptance: manager deactivates and reactivates a member',
    async function (assert) {
      // GIVEN a manager of "Our Flat" is logged in; Maruf is an active member
      // WHEN  they deactivate Maruf, find him under Past and reactivate him
      //       from 1 Dec 2026
      // THEN  Maruf is back among the current members
      worker.use(loggedInAs('manager'), ...membersApi([owner, member()]));

      await visit('/members');
      await click('[data-test-deactivate="Maruf"]');
      await click('[data-test-deactivate-confirm]');
      await click('[data-test-tab="past"]');
      assert
        .dom('[data-test-member-row="Maruf"]')
        .exists('Maruf is a past member');
      await click('[data-test-reactivate="Maruf"]');
      await fillIn('[data-test-reactivate-on]', '2026-12-01');
      await click('[data-test-reactivate-confirm]');
      await click('[data-test-tab="current"]');

      assert
        .dom('[data-test-member-row="Maruf"]')
        .exists('Maruf is current again');
    },
  );

  test('a page whose session ended goes to log-in', async function (assert) {
    // GIVEN a manager has the Members page open
    // WHEN  their session ends (they were deactivated elsewhere) and they
    //       press Deactivate for Maruf
    // THEN  the API answers 401, and the app goes to the log-in page
    worker.use(loggedInAs('manager'), ...membersApi([owner, member()]));
    await visit('/members');
    worker.use(
      http.all('*/api/v1/*', () =>
        HttpResponse.json(notLoggedInBody, { status: 401 }),
      ),
    );

    await click('[data-test-deactivate="Maruf"]');
    await click('[data-test-deactivate-confirm]');

    assert.strictEqual(currentURL(), '/log-in');
  });
});
