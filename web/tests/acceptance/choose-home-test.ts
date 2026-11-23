import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  homesApi,
  newHomeSetup,
  notLoggedIn,
} from 'colivo-web/tests/helpers/accounts';

module('Acceptance | choose a home', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, notLoggedIn, newHomeSetup);

  test.todo(
    'acceptance: person in two homes chooses one after log-in, then switches',
    async function (assert) {
      // GIVEN Rabbi owns "Our Flat" and is a member of "Green House"
      // WHEN  he logs in, chooses Green House, then switches to Our Flat
      // THEN  he sees "Choose a home", then each home he chose in the shell
      worker.use(...homesApi());

      await visit('/log-in');
      await fillIn('[data-test-log-in-contact]', '01712 345678');
      await click('[data-test-log-in-send-code]');
      await fillIn('[data-test-log-in-form] [data-test-code-field]', '123456');
      await click('[data-test-log-in-submit]');

      assert.strictEqual(currentURL(), '/choose-home');
      assert.dom('[data-test-home-choice]').exists({ count: 2 });

      await click('[data-test-home-choice="Green House"]');

      assert.strictEqual(currentURL(), '/');
      assert.dom('[data-test-shell-home]').hasText('Green House');

      await click('[data-test-home-switcher]');
      await click('[data-test-home-switch="Our Flat"]');

      assert.strictEqual(currentURL(), '/');
      assert.dom('[data-test-shell-home]').hasText('Our Flat');
    },
  );
});
