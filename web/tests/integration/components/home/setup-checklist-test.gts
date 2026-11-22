import { module, test } from 'qunit';
import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { newHomeSetupBody } from 'colivo-web/tests/helpers/accounts';
import SetupChecklist from 'colivo-web/components/home/setup-checklist';

module('Integration | Component | home/setup-checklist', function (hooks) {
  setupRenderingTest(hooks);

  test('shows each step done or not, and how many are done', async function (assert) {
    // GIVEN a new home: only "home created" is done
    // WHEN  the setup checklist is rendered
    // THEN  every step shows with its words, done or not, and "1 of 5 done"
    const steps = newHomeSetupBody.data?.steps ?? [];

    await render(<template><SetupChecklist @steps={{steps}} /></template>);

    assert.dom('[data-test-setup-progress]').hasText('1 of 5 done');
    assert
      .dom('[data-test-setup-step]')
      .exists({ count: 5 }, 'one line per step');
    assert
      .dom('[data-test-setup-step="home_created"]')
      .hasAttribute('data-test-done')
      .includesText('Home created');
    assert
      .dom('[data-test-setup-step="members"]')
      .doesNotHaveAttribute('data-test-done')
      .includesText('Add members');
    assert
      .dom('[data-test-setup-step="rooms"]')
      .includesText('Add rooms and rent');
    assert.dom('[data-test-setup-step="rules"]').includesText('Set home rules');
    assert.dom('[data-test-setup-step="bills"]').includesText('Add bills');
  });
});
