import { module, test } from 'qunit';
import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { member, owner } from 'colivo-web/tests/helpers/members';
import MemberList from 'colivo-web/components/members/member-list';

module('Integration | Component | members/member-list', function (hooks) {
  setupRenderingTest(hooks);

  test("shows each member's name, role, status and join date", async function (assert) {
    // GIVEN "Our Flat": its owner, and Maruf, a member since 21 Nov 2026
    // WHEN  the members list is rendered
    // THEN  each row shows the name, role, status and join date
    const members = [owner, member()];

    await render(<template><MemberList @members={{members}} /></template>);

    assert.dom('[data-test-member-row]').exists({ count: 2 });
    assert
      .dom('[data-test-member-row="Rabbi Hasan"]')
      .includesText('Owner')
      .includesText('Active')
      .includesText('1 Nov 2026');
    assert
      .dom('[data-test-member-row="Maruf"]')
      .includesText('Member')
      .includesText('Active')
      .includesText('21 Nov 2026');
  });
});
