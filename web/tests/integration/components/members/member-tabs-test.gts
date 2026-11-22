import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { me } from 'colivo-web/tests/helpers/accounts';
import { member, owner } from 'colivo-web/tests/helpers/members';
import MemberTabs from 'colivo-web/components/members/member-tabs';

module('Integration | Component | members/member-tabs', function (hooks) {
  setupRenderingTest(hooks);

  test('current members with Deactivate, past members with Reactivate', async function (assert) {
    // GIVEN "Our Flat": its owner, Maruf (active) and Karim (deactivated)
    // WHEN  the owner looks at the Current tab, then the Past tab
    // THEN  Current lists the active members, with Deactivate for Maruf;
    //       Past lists Karim, with Reactivate
    this.owner.lookup('service:session').me = me('owner');
    const members = [
      owner,
      member(),
      member({
        id: '01a1fd00-0000-7000-8000-000000000011',
        name: 'Karim',
        status: 'inactive',
      }),
    ];
    const noop = () => {};
    await render(
      <template>
        <MemberTabs
          @members={{members}}
          @onDeactivate={{noop}}
          @onReactivate={{noop}}
        />
      </template>,
    );

    assert.dom('[data-test-member-row]').exists({ count: 2 }, 'two current');
    assert.dom('[data-test-member-row="Karim"]').doesNotExist();
    assert.dom('[data-test-deactivate="Maruf"]').exists();
    await click('[data-test-tab="past"]');

    assert.dom('[data-test-member-row]').exists({ count: 1 }, 'one past');
    assert.dom('[data-test-reactivate="Karim"]').exists();
    assert.dom('[data-test-deactivate="Karim"]').doesNotExist();
  });
});
