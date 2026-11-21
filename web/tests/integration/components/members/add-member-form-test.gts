import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { member, type Member } from 'colivo-web/tests/helpers/members';
import AddMemberForm from 'colivo-web/components/members/add-member-form';

/** Fill in Maruf: 01812 345678, joining 21 Nov 2026. */
async function fillInMaruf(): Promise<void> {
  await fillIn('[data-test-add-member-name]', 'Maruf');
  await fillIn('[data-test-add-member-contact]', '01812 345678');
  await fillIn('[data-test-add-member-joined-on]', '2026-11-21');
}

module('Integration | Component | members/add-member-form', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('sends the new member, then tells the page', async function (assert) {
    // GIVEN the API adds members
    // WHEN  the owner fills in Maruf and presses "Add member"
    // THEN  his name, phone, join date and role (member) are sent, and the
    //       page is told who was added
    const sent: unknown[] = [];
    worker.use(
      http.post('*/api/v1/members', async ({ request }) => {
        sent.push(await request.json());
        return HttpResponse.json(
          { success: true, message: 'Member added', data: member() },
          { status: 201 },
        );
      }),
    );
    let added: Member | null = null;
    const onAdded = (newMember: Member) => (added = newMember);
    await render(<template><AddMemberForm @onAdded={{onAdded}} /></template>);

    await fillInMaruf();
    await click('[data-test-add-member-submit]');

    assert.deepEqual(sent, [
      {
        name: 'Maruf',
        contact: '01812 345678',
        joined_on: '2026-11-21',
        role: 'member',
      },
    ]);
    assert.strictEqual((added as Member | null)?.name, 'Maruf');
  });
});
