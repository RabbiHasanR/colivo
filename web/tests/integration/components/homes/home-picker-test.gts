import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { GREEN_HOUSE_ID, twoHomes } from 'colivo-web/tests/helpers/accounts';
import HomePicker from 'colivo-web/components/homes/home-picker';

module('Integration | Component | homes/home-picker', function (hooks) {
  setupRenderingTest(hooks);

  test("lists each home's name, area and role, and chooses the tapped one", async function (assert) {
    // GIVEN Rabbi is a member of "Green House" and owns "Our Flat" (Mirpur)
    // WHEN  the picker shows his homes and he taps Green House
    // THEN  each row shows the home, its area and his role; Green House is chosen
    let chosen: string | null = null;
    const onChoose = (homeId: string) => (chosen = homeId);
    await render(
      <template>
        <HomePicker @homes={{twoHomes}} @onChoose={{onChoose}} />
      </template>,
    );

    assert.dom('[data-test-home-choice]').exists({ count: 2 });
    assert
      .dom('[data-test-home-choice="Our Flat"]')
      .includesText('Our Flat')
      .includesText('Mirpur')
      .includesText('Owner');
    assert.dom('[data-test-home-choice="Green House"]').includesText('Member');

    await click('[data-test-home-choice="Green House"]');

    assert.strictEqual(chosen, GREEN_HOUSE_ID);
  });
});
