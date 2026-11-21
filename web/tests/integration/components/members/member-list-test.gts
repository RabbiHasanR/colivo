import { module, test } from 'qunit';
import { click, find, findAll, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { member, owner, type Member } from 'colivo-web/tests/helpers/members';
import { me, type Role } from 'colivo-web/tests/helpers/accounts';
import MemberList from 'colivo-web/components/members/member-list';

module('Integration | Component | members/member-list', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

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

  test('the owner gives and takes away the Manager role', async function (assert) {
    // GIVEN "Our Flat": Maruf (a member) and Hijam (a manager)
    // WHEN  the owner looks at the list and presses "Make manager" for Maruf;
    //       then a manager looks at the list
    // THEN  the owner sees the right button for each and Maruf's new role is
    //       sent; a manager sees no role buttons
    const session = this.owner.lookup('service:session');
    const hijam = member({
      id: '01a1fd00-0000-7000-8000-000000000012',
      name: 'Hijam',
      role: 'manager',
    });
    const maruf = member();
    const members = [maruf, hijam];
    const sent: Array<[string, unknown]> = [];
    worker.use(
      http.put('*/api/v1/members/:id/role', async ({ params, request }) => {
        sent.push([String(params['id']), await request.json()]);
        return HttpResponse.json({
          success: true,
          message: 'Role changed',
          data: member({ role: 'manager' }),
        });
      }),
    );
    const changed: Member[] = [];
    const onRoleChanged = (each: Member) => changed.push(each);
    const list = <template>
      <MemberList @members={{members}} @onRoleChanged={{onRoleChanged}} />
    </template>;

    session.me = me('owner');
    await render(list);
    assert.dom('[data-test-role-change="Maruf"]').hasText('Make manager');
    assert.dom('[data-test-role-change="Hijam"]').hasText('Remove manager');
    await click('[data-test-role-change="Maruf"]');
    session.me = me('manager');
    await render(list);

    assert.deepEqual(sent, [[maruf.id, { role: 'manager' }]]);
    assert.deepEqual(
      changed.map((each) => each.role),
      ['manager'],
    );
    assert.strictEqual(findAll('[data-test-role-change]').length, 0);
  });
});
