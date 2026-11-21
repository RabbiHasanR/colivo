import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { member, type Member } from 'colivo-web/tests/helpers/members';
import DeactivateDialog from 'colivo-web/components/members/deactivate-dialog';

// 21 Nov 2026, 16:00 in Dhaka.
const NOW = new Date('2026-11-21T10:00:00Z');

module('Integration | Component | members/deactivate-dialog', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('starts at today; Confirm deactivates, Cancel sends nothing', async function (assert) {
    // GIVEN Maruf, and an API that deactivates members
    // WHEN  the owner opens his deactivate dialog and confirms (then, again,
    //       opens it and cancels)
    // THEN  it starts at today, Confirm sends that date and tells the page,
    //       and Cancel sends nothing
    const maruf = member();
    const sent: Array<[string, unknown]> = [];
    worker.use(
      http.post(
        '*/api/v1/members/:id/deactivate',
        async ({ params, request }) => {
          sent.push([String(params['id']), await request.json()]);
          return HttpResponse.json({
            success: true,
            message: 'Member deactivated',
            data: member({ status: 'inactive' }),
          });
        },
      ),
    );
    const events: string[] = [];
    const onDone = (done: Member) => events.push(`done ${done.status}`);
    const onCancel = () => events.push('cancelled');
    const dialog = <template>
      <DeactivateDialog
        @member={{maruf}}
        @now={{NOW}}
        @onDone={{onDone}}
        @onCancel={{onCancel}}
      />
    </template>;

    await render(dialog);
    assert.dom('[data-test-deactivate-on]').hasValue('2026-11-21');
    await click('[data-test-deactivate-confirm]');
    await render(dialog);
    await click('[data-test-deactivate-cancel]');

    assert.deepEqual(sent, [[maruf.id, { on: '2026-11-21' }]]);
    assert.deepEqual(events, ['done inactive', 'cancelled']);
  });
});
