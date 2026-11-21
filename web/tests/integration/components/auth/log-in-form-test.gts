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

  test('a wrong code says how many tries are left', async function (assert) {
    // GIVEN the API refuses the typed code with 3 tries left
    // WHEN  someone tries to log in with it
    // THEN  the form says the code isn't right and how many tries are left
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/log-in', () =>
        HttpResponse.json(
          {
            success: false,
            message: "That code isn't right.",
            errors: ["That code isn't right."],
            data: { reason: 'wrong', tries_left: 3 },
          },
          { status: 400 },
        ),
      ),
    );
    const onLoggedIn = () => {};
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);

    await sendCodeAndType('111111');
    await click('[data-test-log-in-submit]');

    assert
      .dom('[data-test-code-error]')
      .hasText("That code isn't right. 3 tries left.");
  });

  test('a locked phone shows the wait and offers another phone or email', async function (assert) {
    // GIVEN the API says the phone is locked for 14:52 after 5 wrong codes
    // WHEN  someone tries to log in, then presses "Use a different phone or email"
    // THEN  the form says so with the wait, then goes back to the first step
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/log-in', () =>
        HttpResponse.json(
          {
            success: false,
            message: 'Too many wrong codes. Try again later.',
            errors: ['Too many wrong codes. Try again later.'],
            data: { reason: 'locked', retry_in_seconds: 892 },
          },
          { status: 429 },
        ),
      ),
    );
    const onLoggedIn = () => {};
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);

    await sendCodeAndType('111111');
    await click('[data-test-log-in-submit]');
    assert.dom('[data-test-code-error]').includesText('Too many wrong codes');
    assert.dom('[data-test-code-error]').includesText('try again in 14:52');
    await click('[data-test-use-different-contact]');

    assert.dom('[data-test-log-in-contact]').hasValue('');
    assert.dom('[data-test-code-field]').doesNotExist();
    assert.dom('[data-test-log-in-send-code]').exists();
  });

  test('shows when a new code can be sent, then resends it', async function (assert) {
    // GIVEN a code was sent; first a new one can be sent in 60 seconds,
    //       then (another time) straight away
    // WHEN  the code step shows, and "Resend" is pressed when it is offered
    // THEN  it first shows "Resend in 1:00" and no Resend button; with no
    //       wait, Resend asks for a new code and says the old one is gone
    let resendIn = 60;
    let codeRequests = 0;
    worker.use(
      http.post('*/api/v1/auth/codes', () => {
        codeRequests += 1;
        return HttpResponse.json({
          ...codeSentBody,
          data: {
            channel: 'sms',
            expires_in_seconds: 300,
            resend_in_seconds: resendIn,
          },
        });
      }),
    );
    const onLoggedIn = () => {};
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);

    await sendCodeAndType('');
    assert
      .dom('[data-test-resend-wait]')
      .hasText("Didn't get it? Resend in 1:00");
    assert.dom('[data-test-resend]').doesNotExist();

    resendIn = 0;
    await render(<template><LogInForm @onLoggedIn={{onLoggedIn}} /></template>);
    await sendCodeAndType('');
    await click('[data-test-resend]');

    assert.strictEqual(codeRequests, 3, 'three codes were asked for');
    assert
      .dom('[data-test-code-resent]')
      .hasText('New code sent to 01712 345678. The old one no longer works.');
  });
});
