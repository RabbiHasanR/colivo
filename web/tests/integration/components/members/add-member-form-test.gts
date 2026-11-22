import { module, test } from 'qunit';
import { click, fillIn, find, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { member, type Member } from 'colivo-web/tests/helpers/members';
import { me, type Role } from 'colivo-web/tests/helpers/accounts';
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

  test('offers the Manager role to the owner only', async function (assert) {
    // GIVEN the owner, and then a manager, is logged in
    // WHEN  the add-member form is rendered for each
    // THEN  the owner can choose "Manager"; a manager can't (FR-64)
    const session = this.owner.lookup('service:session');
    const onAdded = () => {};
    const managerChoice = '[data-test-add-member-role] option[value="manager"]';
    const offered: Array<[Role, boolean]> = [];

    for (const role of ['owner', 'manager'] as const) {
      session.me = me(role);
      await render(<template><AddMemberForm @onAdded={{onAdded}} /></template>);
      offered.push([role, find(managerChoice) !== null]);
    }

    assert.deepEqual(offered, [
      ['owner', true],
      ['manager', false],
    ]);
  });

  test('shows why the API refused the member', async function (assert) {
    // GIVEN Maruf is already an active member of this home
    // WHEN  the owner tries to add him again
    // THEN  the form shows the API's 409 message, and the page isn't told
    const refusal = 'Already a member of this home.';
    worker.use(
      http.post('*/api/v1/members', () =>
        HttpResponse.json(
          { success: false, message: refusal, errors: [refusal] },
          { status: 409 },
        ),
      ),
    );
    let added = false;
    const onAdded = () => (added = true);
    await render(<template><AddMemberForm @onAdded={{onAdded}} /></template>);

    await fillInMaruf();
    await click('[data-test-add-member-submit]');

    assert.dom('[data-test-add-member-error]').hasText(refusal);
    assert.false(added);
  });

  test('shows 422 messages under their fields', async function (assert) {
    // GIVEN the API refuses the name and the contact
    // WHEN  the owner tries to add the member
    // THEN  each message shows under its own field
    worker.use(
      http.post('*/api/v1/members', () =>
        HttpResponse.json(
          {
            success: false,
            message: 'Validation Error',
            errors: [
              'body.name: String should have at least 1 character',
              'body.contact: Value error, Enter a phone number or an email.',
            ],
          },
          { status: 422 },
        ),
      ),
    );
    const onAdded = () => {};
    await render(<template><AddMemberForm @onAdded={{onAdded}} /></template>);

    await fillInMaruf();
    await click('[data-test-add-member-submit]');

    assert
      .dom('[data-test-field="name"] [data-test-field-error]')
      .hasText('String should have at least 1 character');
    assert
      .dom('[data-test-field="contact"] [data-test-field-error]')
      .hasText('Value error, Enter a phone number or an email.');
  });
});
