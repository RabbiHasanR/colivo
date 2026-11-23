import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { member, type Member } from 'colivo-web/tests/helpers/members';
import EditMemberForm from 'colivo-web/components/members/edit-member-form';

module('Integration | Component | members/edit-member-form', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test("sends a member's new name and join date, then tells the page", async function (assert) {
    // GIVEN Maruf, joined 21 Nov 2026, and an API that saves changes
    // WHEN  the owner opens his edit form, renames him and moves the date to 1 Nov
    // THEN  the form started from his details, the changes are sent to his
    //       member id, and the page is told
    const maruf = member();
    const sent: Array<[string, unknown]> = [];
    worker.use(
      http.patch('*/api/v1/members/:id', async ({ params, request }) => {
        sent.push([String(params['id']), await request.json()]);
        return HttpResponse.json({
          success: true,
          message: 'Member changed',
          data: member({ name: 'Maruf Hossain', joined_on: '2026-11-01' }),
        });
      }),
    );
    let saved: Member | null = null;
    const onSaved = (changed: Member) => (saved = changed);
    await render(
      <template>
        <EditMemberForm @member={{maruf}} @onSaved={{onSaved}} />
      </template>,
    );

    assert.dom('[data-test-edit-member-name]').hasValue('Maruf');
    assert.dom('[data-test-edit-member-joined-on]').hasValue('2026-11-21');
    await fillIn('[data-test-edit-member-name]', 'Maruf Hossain');
    await fillIn('[data-test-edit-member-joined-on]', '2026-11-01');
    await click('[data-test-edit-member-submit]');

    assert.deepEqual(sent, [
      [maruf.id, { name: 'Maruf Hossain', joined_on: '2026-11-01' }],
    ]);
    assert.strictEqual((saved as Member | null)?.name, 'Maruf Hossain');
  });

  test('shows the log-in read-only for a member who is also in another home', async function (assert) {
    // GIVEN Maruf, whose log-in this home may not change (he is in another home)
    // WHEN  the owner opens his Edit tab
    // THEN  his phone and email are shown as text with "Only they can …",
    //       and there is nothing to type in or send
    const maruf = member({
      email: 'maruf@example.com',
      contact_editable: false,
    });
    const onSaved = () => {};
    await render(
      <template>
        <EditMemberForm @member={{maruf}} @onSaved={{onSaved}} />
      </template>,
    );

    assert.dom('[data-test-contact-value="phone"]').hasText('+8801812345678');
    assert
      .dom('[data-test-contact-value="email"]')
      .hasText('maruf@example.com');
    assert
      .dom('[data-test-contact-note]')
      .hasText('Only they can change their log-in, from My profile.');
    assert.dom('[data-test-contact-input]').doesNotExist();
    assert.dom('[data-test-contact-remove]').doesNotExist();
  });

  test('tells the owner to reactivate a past member to change their log-in', async function (assert) {
    // GIVEN Maruf was deactivated, so his log-in can't be changed
    // WHEN  the owner opens his Edit tab
    // THEN  his phone shows as text with "Reactivate them to change their log-in."
    const maruf = member({ status: 'inactive', contact_editable: false });
    const onSaved = () => {};
    await render(
      <template>
        <EditMemberForm @member={{maruf}} @onSaved={{onSaved}} />
      </template>,
    );

    assert.dom('[data-test-contact-value="phone"]').hasText('+8801812345678');
    assert
      .dom('[data-test-contact-note]')
      .hasText('Reactivate them to change their log-in.');
  });
});
