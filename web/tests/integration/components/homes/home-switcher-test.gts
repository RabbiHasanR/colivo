import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import {
  GREEN_HOUSE_ID,
  ourFlat,
  twoHomes,
} from 'colivo-web/tests/helpers/accounts';
import HomeSwitcher from 'colivo-web/components/homes/home-switcher';

module('Integration | Component | homes/home-switcher', function (hooks) {
  setupRenderingTest(hooks);

  test('lists the other homes and switches to the chosen one', async function (assert) {
    // GIVEN Rabbi is in Our Flat, and also in Green House
    // WHEN  he opens the home menu and picks Green House
    // THEN  the menu lists only Green House, and Green House is chosen
    let chosen: string | null = null;
    const onChoose = (homeId: string) => (chosen = homeId);
    await render(
      <template>
        <HomeSwitcher
          @current={{ourFlat}}
          @homes={{twoHomes}}
          @onChoose={{onChoose}}
        />
      </template>,
    );
    assert.dom('[data-test-home-switcher]').hasText('Our Flat');
    assert.dom('[data-test-home-switch]').doesNotExist('closed at first');

    await click('[data-test-home-switcher]');

    assert.dom('[data-test-home-switch]').exists({ count: 1 });
    await click('[data-test-home-switch="Green House"]');
    assert.strictEqual(chosen, GREEN_HOUSE_ID);
  });
});
