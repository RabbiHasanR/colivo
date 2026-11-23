import { module, test } from 'qunit';
import { click, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  myContactApi,
  newHomeSetup,
} from 'colivo-web/tests/helpers/accounts';

module('Acceptance | profile', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test.todo(
    'acceptance: person changes their own phone on My profile',
    async function (assert) {
      // GIVEN Rabbi Hasan is logged in with +8801712345678
      // WHEN  he opens My profile from his name, changes his phone and
      //       confirms it with the code
      // THEN  My profile shows the new phone
      worker.use(loggedInAs('owner'), ...myContactApi());

      await visit('/');
      await click('[data-test-nav-profile]');
      await fillIn('[data-test-contact-input="phone"]', '+8801912345678');
      await click('[data-test-contact-send-code="phone"]');
      await fillIn(
        '[data-test-contact-row="phone"] [data-test-code-field]',
        '123456',
      );
      await click('[data-test-contact-save="phone"]');

      assert
        .dom('[data-test-contact-input="phone"]')
        .hasValue('+8801912345678');
    },
  );
});
