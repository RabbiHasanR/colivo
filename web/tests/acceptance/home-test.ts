import { module, test } from 'qunit';
import { click, currentURL, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { loggedInAs, newHomeSetup } from 'colivo-web/tests/helpers/accounts';
import { membersApi } from 'colivo-web/tests/helpers/members';

module('Acceptance | home', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test('owner starts "Add members" from the setup checklist', async function (assert) {
    // GIVEN the owner of a new home is logged in
    // WHEN  they press "Start ›" on the "Add members" step
    // THEN  Members opens; steps without a page yet have no "Start ›"
    worker.use(loggedInAs('owner'), ...membersApi());

    await visit('/');
    assert.dom('[data-test-setup-start]').exists({ count: 1 });
    await click('[data-test-setup-start="members"]');

    assert.strictEqual(currentURL(), '/members');
  });
});
