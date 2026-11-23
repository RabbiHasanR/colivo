import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
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
});
