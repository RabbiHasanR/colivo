import { module, test } from 'qunit';
import { click, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { loggedInAs, newHomeSetup } from 'colivo-web/tests/helpers/accounts';
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
});
