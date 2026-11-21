import { module, test } from 'qunit';
import { find, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { member, owner } from 'colivo-web/tests/helpers/members';
import { me, type Role } from 'colivo-web/tests/helpers/accounts';
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

  test('offers Deactivate only for members the viewer may deactivate', async function (assert) {
    // GIVEN "Our Flat": the owner, Hijam (a manager) and Maruf (a member)
    // WHEN  the owner, then a manager, looks at the list
    // THEN  nobody can deactivate the owner; the owner can deactivate Hijam
    //       and Maruf; a manager can deactivate Maruf only
    const session = this.owner.lookup('service:session');
    const members = [
      owner,
      member({
        id: '01a1fd00-0000-7000-8000-000000000012',
        name: 'Hijam',
        role: 'manager',
      }),
      member(),
    ];
    const onDeactivate = () => {};
    const offered: Array<[Role, string[]]> = [];

    for (const viewer of ['owner', 'manager'] as const) {
      session.me = me(viewer);
      await render(
        <template>
          <MemberList @members={{members}} @onDeactivate={{onDeactivate}} />
        </template>,
      );
      const names = members
        .map((each) => each.name)
        .filter((name) => find(`[data-test-deactivate="${name}"]`) !== null);
      offered.push([viewer, names]);
    }

    assert.deepEqual(offered, [
      ['owner', ['Hijam', 'Maruf']],
      ['manager', ['Maruf']],
    ]);
  });
});
