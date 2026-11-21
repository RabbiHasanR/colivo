import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { codeSentBody, meBody } from 'colivo-web/tests/helpers/accounts';
import LogInForm from 'colivo-web/components/auth/log-in-form';

/** Ask for a code for 01712 345678 and type `code`. */
async function sendCodeAndType(code: string): Promise<void> {
  await fillIn('[data-test-log-in-contact]', '01712 345678');
  await click('[data-test-log-in-send-code]');
  await fillIn('[data-test-code-field]', code);
}

module('Integration | Component | auth/log-in-form', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('sends a code, then logs in with it', async function (assert) {
    // GIVEN the API sends a code and accepts it
    // WHEN  someone enters their phone, sends the code, types it and logs in
    // THEN  the code step says where it went, the contact and code are sent,
    //       and the page is told they are logged in
    const sent: unknown[] = [];
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/log-in', async ({ request }) => {
        sent.push(await request.json());
        return HttpResponse.json(meBody('owner'));
      }),
    );
    let loggedIn = false;
    const onLoggedIn = () => (loggedIn = true);
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);

    await sendCodeAndType('123456');
    assert.dom('[data-test-code-sent-to]').hasText('Sent to 01712 345678');
    await click('[data-test-log-in-submit]');

    assert.deepEqual(sent, [{ contact: '01712 345678', code: '123456' }]);
    assert.true(loggedIn);
  });

  test('an expired code says so and offers a new one', async function (assert) {
    // GIVEN the API says the typed code expired
    // WHEN  someone tries to log in with it, then presses "Send a new code"
    // THEN  the form says the code expired, and a new code is asked for
    let codeRequests = 0;
    worker.use(
      http.post('*/api/v1/auth/codes', () => {
        codeRequests += 1;
        return HttpResponse.json(codeSentBody);
      }),
      http.post('*/api/v1/auth/log-in', () =>
        HttpResponse.json(
          {
            success: false,
            message: 'This code expired. Codes work for 5 minutes.',
            errors: ['This code expired. Codes work for 5 minutes.'],
            data: { reason: 'expired' },
          },
          { status: 400 },
        ),
      ),
    );
    const onLoggedIn = () => {};
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);

    await sendCodeAndType('123456');
    await click('[data-test-log-in-submit]');
    assert
      .dom('[data-test-code-error]')
      .hasText('This code expired. Codes work for 5 minutes.');
    await click('[data-test-send-new-code]');

    assert.strictEqual(codeRequests, 2, 'a new code was asked for');
  });
});
