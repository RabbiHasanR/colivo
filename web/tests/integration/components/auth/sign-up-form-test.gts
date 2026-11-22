import { module, test } from 'qunit';
import { click, fillIn, render, select } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { codeSentBody, meBody } from 'colivo-web/tests/helpers/accounts';
import SignUpForm from 'colivo-web/components/auth/sign-up-form';

const NOW = new Date('2026-11-21T10:00:00Z');

/** Fill in "Create your home" for Rabbi Hasan's "Our Flat". */
async function fillInOurFlat(): Promise<void> {
  await fillIn('[data-test-sign-up-name]', 'Rabbi Hasan');
  await fillIn('[data-test-sign-up-contact]', '01712 345678');
  await fillIn('[data-test-sign-up-home-name]', 'Our Flat');
  await fillIn('[data-test-sign-up-area]', 'Mirpur');
  await select('[data-test-sign-up-first-month]', '2026-12-01');
  await click('[data-test-sign-up-lives-here]');
}

module('Integration | Component | auth/sign-up-form', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('sends a code, then creates the home with every field', async function (assert) {
    // GIVEN the API accepts a code request and the sign-up
    // WHEN  the owner fills in the form, sends the code, types it and creates
    //       the home (December, not living there)
    // THEN  the code step says where the code went, every field goes with the
    //       code, and the page is told the owner signed up
    const sent: unknown[] = [];
    worker.use(
      http.post('*/api/v1/auth/codes', async ({ request }) => {
        sent.push(['codes', await request.json()]);
        return HttpResponse.json(codeSentBody);
      }),
      http.post('*/api/v1/auth/sign-up', async ({ request }) => {
        sent.push(['sign-up', await request.json()]);
        return HttpResponse.json(meBody('owner'), { status: 201 });
      }),
    );
    let signedUp = false;
    const onSignedUp = () => (signedUp = true);
    await render(
      <template>
        <SignUpForm @now={{NOW}} @onSignedUp={{onSignedUp}} />
      </template>,
    );

    await fillInOurFlat();
    await click('[data-test-sign-up-send-code]');
    assert.dom('[data-test-code-sent-to]').hasText('Sent to 01712 345678');
    await fillIn('[data-test-code-field]', '123456');
    await click('[data-test-sign-up-submit]');

    assert.deepEqual(sent, [
      ['codes', { contact: '01712 345678' }],
      [
        'sign-up',
        {
          contact: '01712 345678',
          code: '123456',
          name: 'Rabbi Hasan',
          home_name: 'Our Flat',
          area: 'Mirpur',
          first_month: '2026-12-01',
          lives_here: false,
        },
      ],
    ]);
    assert.true(signedUp);
  });

  test('shows 422 messages under their fields', async function (assert) {
    // GIVEN the API refuses the sign-up: the name and home name are too long
    // WHEN  the owner sends the code and tries to create the home
    // THEN  each message shows under its own field
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/sign-up', () =>
        HttpResponse.json(
          {
            success: false,
            message: 'Validation Error',
            errors: [
              'body.name: String should have at most 80 characters',
              'body.home_name: String should have at most 80 characters',
            ],
          },
          { status: 422 },
        ),
      ),
    );
    const onSignedUp = () => {};
    await render(
      <template>
        <SignUpForm @now={{NOW}} @onSignedUp={{onSignedUp}} />
      </template>,
    );

    await fillInOurFlat();
    await click('[data-test-sign-up-send-code]');
    await fillIn('[data-test-code-field]', '123456');
    await click('[data-test-sign-up-submit]');

    assert
      .dom('[data-test-field="name"] [data-test-field-error]')
      .hasText('String should have at most 80 characters');
    assert
      .dom('[data-test-field="home_name"] [data-test-field-error]')
      .hasText('String should have at most 80 characters');
  });

  test("shows the API's refusal above the button", async function (assert) {
    // GIVEN the API refuses the first month (400), e.g. the month turned over
    // WHEN  the owner creates the home
    // THEN  the form shows the API's message above the button
    const refusal = 'The first month must be this month or next.';
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/sign-up', () =>
        HttpResponse.json(
          { success: false, message: refusal, errors: [refusal] },
          { status: 400 },
        ),
      ),
    );
    const onSignedUp = () => {};
    await render(
      <template>
        <SignUpForm @now={{NOW}} @onSignedUp={{onSignedUp}} />
      </template>,
    );

    await fillInOurFlat();
    await click('[data-test-sign-up-send-code]');
    await fillIn('[data-test-code-field]', '123456');
    await click('[data-test-sign-up-submit]');

    assert.dom('[data-test-sign-up-error]').hasText(refusal);
  });

  test('shows a refused contact under its field, until it is fixed', async function (assert) {
    // GIVEN the API refuses "hello" as a phone or email, and accepts a phone
    // WHEN  the owner sends a code to "hello", then fixes it and sends again
    // THEN  the message shows under "Phone or email", then goes away and the
    //       code step opens
    worker.use(
      http.post('*/api/v1/auth/codes', async ({ request }) => {
        const { contact } = (await request.json()) as { contact: string };
        if (contact === 'hello') {
          return HttpResponse.json(
            {
              success: false,
              message: 'Validation Error',
              errors: [
                'body.contact: Value error, Enter a phone number or an email.',
              ],
            },
            { status: 422 },
          );
        }
        return HttpResponse.json(codeSentBody);
      }),
    );
    const onSignedUp = () => {};
    await render(
      <template>
        <SignUpForm @now={{NOW}} @onSignedUp={{onSignedUp}} />
      </template>,
    );
    await fillInOurFlat();

    await fillIn('[data-test-sign-up-contact]', 'hello');
    await click('[data-test-sign-up-send-code]');
    assert
      .dom('[data-test-field="contact"] [data-test-field-error]')
      .hasText('Value error, Enter a phone number or an email.');

    await fillIn('[data-test-sign-up-contact]', '01712 345678');
    await click('[data-test-sign-up-send-code]');
    assert.dom('[data-test-field-error]').doesNotExist();
    assert.dom('[data-test-code-sent-to]').hasText('Sent to 01712 345678');
  });
});
