import { module, test } from 'qunit';
import { click, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { loggedInAs, newHomeSetup } from 'colivo-web/tests/helpers/accounts';
import { membersApi } from 'colivo-web/tests/helpers/members';

module('Acceptance | members', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test('owner adds a member', async function (assert) {
    // GIVEN the owner of "Our Flat" is logged in; only they are a member
    // WHEN  they open Members and add Maruf by phone, joining 21 Nov 2026
    // THEN  Maruf shows in the members list
    worker.use(loggedInAs('owner'), ...membersApi());

    await visit('/members');
    await fillIn('[data-test-add-member-name]', 'Maruf');
    await fillIn('[data-test-add-member-contact]', '01812 345678');
    await fillIn('[data-test-add-member-joined-on]', '2026-11-21');
    await click('[data-test-add-member-submit]');

    assert.dom('[data-test-member-row]').exists({ count: 2 });
    assert.dom('[data-test-member-row="Maruf"]').exists();
  });
});
