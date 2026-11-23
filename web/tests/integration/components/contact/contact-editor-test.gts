import { module, test } from 'qunit';
import { click, fillIn, render, typeIn } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { codeSentBody } from 'colivo-web/tests/helpers/accounts';
import { member } from 'colivo-web/tests/helpers/members';
import ContactEditor from 'colivo-web/components/contact/contact-editor';
import type { TestContext } from '@ember/test-helpers';

const MARUF = member();

/** The editor for Maruf, wired to the real members service (MSW answers). */
async function renderFor(
  context: TestContext,
  contact: { phone: string | null; email: string | null },
) {
  const members = context.owner.lookup('service:members');
  const sendCode = (value: string) => members.sendContactCode(MARUF.id, value);
  const save = (value: string, code: string) =>
    members.setContact(MARUF.id, value, code);
  const remove = (kind: 'phone' | 'email') =>
    members.removeContact(MARUF.id, kind);
  await render(
    <template>
      <ContactEditor
        @phone={{contact.phone}}
        @email={{contact.email}}
        @editable={{true}}
        @onSendCode={{sendCode}}
        @onSave={{save}}
        @onRemove={{remove}}
      />
    </template>,
  );
}

module('Integration | Component | contact/contact-editor', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('sends a code to a new email, then saves it with the code', async function (assert) {
    // GIVEN Maruf logs in with a phone only
    // WHEN  the owner types his email, presses Send code, types the code, Save
    // THEN  the code field shows only after Send code, and the email and the
    //       code are sent
    const sent: unknown[] = [];
    worker.use(
      http.post('*/api/v1/members/:id/contact/code', async ({ request }) => {
        sent.push(['code', await request.json()]);
        return HttpResponse.json(codeSentBody);
      }),
      http.put('*/api/v1/members/:id/contact', async ({ request }) => {
        sent.push(['save', await request.json()]);
        return HttpResponse.json({
          success: true,
          message: 'Log-in changed',
          data: member({ email: 'maruf@example.com' }),
        });
      }),
    );
    await renderFor(this, { phone: MARUF.phone, email: null });

    assert
      .dom('[data-test-contact-row="email"] [data-test-code-field]')
      .doesNotExist();
    await fillIn('[data-test-contact-input="email"]', 'maruf@example.com');
    await click('[data-test-contact-send-code="email"]');
    assert
      .dom('[data-test-contact-row="email"] [data-test-code-field]')
      .exists();
    await fillIn(
      '[data-test-contact-row="email"] [data-test-code-field]',
      '123456',
    );
    await click('[data-test-contact-save="email"]');

    assert.deepEqual(sent, [
      ['code', { contact: 'maruf@example.com' }],
      ['save', { contact: 'maruf@example.com', code: '123456' }],
    ]);
  });

  test('labels the one they lack "(optional)"', async function (assert) {
    // GIVEN Maruf logs in with a phone only
    // WHEN  his log-in is shown
    // THEN  the phone is "Phone" and the email "Email (optional)"
    await renderFor(this, { phone: MARUF.phone, email: null });

    assert.dom('[data-test-contact-row="phone"] label').hasText('Phone');
    assert
      .dom('[data-test-contact-row="email"] label')
      .hasText('Email (optional)');
  });

  test('offers Remove only while both exist, and removes that one', async function (assert) {
    // GIVEN Maruf logs in with a phone and an email
    // WHEN  his log-in is shown, and the owner presses Remove on the email
    // THEN  both rows offer Remove, and the email's removal is sent
    const removed: unknown[] = [];
    worker.use(
      http.delete('*/api/v1/members/:id/contact/:channel', ({ params }) => {
        removed.push(params['channel']);
        return HttpResponse.json({
          success: true,
          message: 'Log-in changed',
          data: member({ email: null }),
        });
      }),
    );
    await renderFor(this, { phone: MARUF.phone, email: 'maruf@example.com' });

    assert.dom('[data-test-contact-remove]').exists({ count: 2 });
    await click('[data-test-contact-remove="email"]');

    assert.deepEqual(removed, ['email']);
  });

  test('offers no Remove for the only way to log in', async function (assert) {
    // GIVEN Maruf logs in with a phone only
    // WHEN  his log-in is shown
    // THEN  nothing offers Remove: the last way to log in can't go
    await renderFor(this, { phone: MARUF.phone, email: null });

    assert.dom('[data-test-contact-remove]').doesNotExist();
  });

  /** Type ``value`` in the ``kind`` row, send a code, and type ``code``. */
  async function confirmWith(kind: string, value: string, code: string) {
    await fillIn(`[data-test-contact-input="${kind}"]`, value);
    await click(`[data-test-contact-send-code="${kind}"]`);
    await fillIn(
      `[data-test-contact-row="${kind}"] [data-test-code-field]`,
      code,
    );
    await click(`[data-test-contact-save="${kind}"]`);
  }

  test('shows why a code was refused, with the tries left', async function (assert) {
    // GIVEN Maruf logs in with a phone; the API refuses the code as wrong
    // WHEN  the owner saves his new email with that code
    // THEN  the email row says the code isn't right and 4 tries are left
    worker.use(
      http.post('*/api/v1/members/:id/contact/code', () =>
        HttpResponse.json(codeSentBody),
      ),
      http.put('*/api/v1/members/:id/contact', () =>
        HttpResponse.json(
          {
            success: false,
            message: "That code isn't right.",
            data: { reason: 'wrong', tries_left: 4 },
          },
          { status: 400 },
        ),
      ),
    );
    await renderFor(this, { phone: MARUF.phone, email: null });

    await confirmWith('email', 'maruf@example.com', '000000');

    assert
      .dom('[data-test-contact-row="email"] [data-test-code-error]')
      .hasText("That code isn't right. 4 tries left.");
  });

  test('says when someone else logs in with that phone or email', async function (assert) {
    // GIVEN the API answers 409: the right code, but the email is taken
    // WHEN  the owner saves Maruf's new email with the code
    // THEN  the email row says someone else logs in with it
    const taken = 'Someone else logs in with that phone or email.';
    worker.use(
      http.post('*/api/v1/members/:id/contact/code', () =>
        HttpResponse.json(codeSentBody),
      ),
      http.put('*/api/v1/members/:id/contact', () =>
        HttpResponse.json(
          { success: false, message: taken, errors: [taken] },
          { status: 409 },
        ),
      ),
    );
    await renderFor(this, { phone: MARUF.phone, email: null });

    await confirmWith('email', 'rabbi@example.com', '123456');

    assert
      .dom('[data-test-contact-row="email"] [data-test-contact-error]')
      .hasText(taken);
  });

  test('offers Send code only once the value differs from the current one', async function (assert) {
    // GIVEN Maruf logs in with +8801812345678
    // WHEN  his phone is shown, then changed, then typed back as it was
    // THEN  Send code shows only while the typed phone is a new one
    await renderFor(this, { phone: MARUF.phone, email: null });
    const sendPhone = '[data-test-contact-send-code="phone"]';

    assert.dom(sendPhone).doesNotExist();
    await fillIn('[data-test-contact-input="phone"]', '+8801912345678');
    assert.dom(sendPhone).exists();
    await fillIn('[data-test-contact-input="phone"]', '+8801812345678');
    assert.dom(sendPhone).doesNotExist();
  });

  test('shows why a new phone or email was refused as not valid', async function (assert) {
    // GIVEN the API answers 422: what was typed isn't a phone or an email
    // WHEN  the owner types "01812" as Maruf's new phone and presses Send code
    // THEN  the phone row says to enter a phone number or an email
    const notValid = 'Value error, Enter a phone number or an email.';
    worker.use(
      http.post('*/api/v1/members/:id/contact/code', () =>
        HttpResponse.json(
          {
            success: false,
            message: 'Validation Error',
            errors: [`body.contact: ${notValid}`],
          },
          { status: 422 },
        ),
      ),
    );
    await renderFor(this, { phone: MARUF.phone, email: null });

    await fillIn('[data-test-contact-input="phone"]', '01812');
    await click('[data-test-contact-send-code="phone"]');

    assert
      .dom('[data-test-contact-row="phone"] [data-test-field-error]')
      .hasText(notValid);
  });

  test('keeps the field focused while you type', async function (assert) {
    // GIVEN Maruf's phone in the editor (bug found in the manual check)
    // WHEN  a new number is typed into it, key by key
    // THEN  the phone field still has the focus, holding all of it
    await renderFor(this, { phone: MARUF.phone, email: null });

    await typeIn('[data-test-contact-input="phone"]', '9');

    assert.dom('[data-test-contact-input="phone"]').isFocused();
    assert.dom('[data-test-contact-input="phone"]').hasValue('+88018123456789');
  });
});
