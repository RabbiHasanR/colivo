import { module, test } from 'qunit';
import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { me } from 'colivo-web/tests/helpers/accounts';
import Welcome from 'colivo-web/components/home/welcome';

module('Integration | Component | home/welcome', function (hooks) {
  setupRenderingTest(hooks);

  test('greets the person and shows the home name and its Home ID', async function (assert) {
    // GIVEN Rabbi Hasan, owner of "Our Flat" (Home ID OF-4827)
    // WHEN  the welcome block is rendered
    // THEN  it greets him by first name and shows the home and its Home ID
    const owner = me('owner');

    await render(<template><Welcome @me={{owner}} /></template>);

    assert.dom('[data-test-welcome-greeting]').hasText('Welcome, Rabbi');
    assert.dom('[data-test-welcome-home]').hasText('Our Flat');
    assert.dom('[data-test-welcome-home-id]').hasText('Home ID OF-4827');
  });
});
