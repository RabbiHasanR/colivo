import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { member, type Member } from 'colivo-web/tests/helpers/members';
import ReactivateDialog from 'colivo-web/components/members/reactivate-dialog';

const KARIM = member({
  id: '01a1fd00-0000-7000-8000-000000000011',
  name: 'Karim',
  status: 'inactive',
});

module('Integration | Component | members/reactivate-dialog', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('sends the date charges start again, then tells the page', async function (assert) {
    // GIVEN Karim was deactivated, and the API reactivates members
    // WHEN  the owner reactivates him, charges starting again on 1 Dec 2026
    // THEN  that date is sent for Karim, and the page is told
    const sent: Array<[string, unknown]> = [];
    worker.use(
      http.post(
        '*/api/v1/members/:id/reactivate',
        async ({ params, request }) => {
          sent.push([String(params['id']), await request.json()]);
          return HttpResponse.json({
            success: true,
            message: 'Member reactivated',
            data: { ...KARIM, status: 'active' },
          });
        },
      ),
    );
    let done: Member | null = null;
    const onDone = (back: Member) => (done = back);
    const onCancel = () => {};
    await render(
      <template>
        <ReactivateDialog
          @member={{KARIM}}
          @onDone={{onDone}}
          @onCancel={{onCancel}}
        />
      </template>,
    );

    await fillIn('[data-test-reactivate-on]', '2026-12-01');
    await click('[data-test-reactivate-confirm]');

    assert.deepEqual(sent, [[KARIM.id, { on: '2026-12-01' }]]);
    assert.strictEqual((done as Member | null)?.status, 'active');
  });

  test("shows the API's 409 message", async function (assert) {
    // GIVEN another active member has Karim's name since he was deactivated
    // WHEN  the owner tries to reactivate him
    // THEN  the dialog shows why, and the page isn't told he's back
    const refusal = 'Someone in this home already has that name.';
    worker.use(
      http.post('*/api/v1/members/:id/reactivate', () =>
        HttpResponse.json(
          { success: false, message: refusal, errors: [refusal] },
          { status: 409 },
        ),
      ),
    );
    let done = false;
    const onDone = () => (done = true);
    const onCancel = () => {};
    await render(
      <template>
        <ReactivateDialog
          @member={{KARIM}}
          @onDone={{onDone}}
          @onCancel={{onCancel}}
        />
      </template>,
    );

    await fillIn('[data-test-reactivate-on]', '2026-12-01');
    await click('[data-test-reactivate-confirm]');

    assert.dom('[data-test-reactivate-error]').hasText(refusal);
    assert.false(done);
  });
});
