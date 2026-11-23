import { module, test } from 'qunit';
import { click, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  loggedInAs,
  me,
  myContactApi,
  newHomeSetup,
} from 'colivo-web/tests/helpers/accounts';
import { membersApi, owner } from 'colivo-web/tests/helpers/members';

module('Acceptance | profile', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test('person changes their own phone on My profile', async function (assert) {
    // GIVEN Rabbi Hasan is logged in with +8801712345678
    // WHEN  he opens My profile from his name, changes his phone and
    //       confirms it with the code
    // THEN  My profile shows the new phone
    worker.use(loggedInAs('owner'), ...myContactApi());

    await visit('/');
    await click('[data-test-nav-profile]');
    await fillIn('[data-test-contact-input="phone"]', '+8801912345678');
    await click('[data-test-contact-send-code="phone"]');
    await fillIn(
      '[data-test-contact-row="phone"] [data-test-code-field]',
      '123456',
    );
    await click('[data-test-contact-save="phone"]');

    assert.dom('[data-test-contact-input="phone"]').hasValue('+8801912345678');
  });

  test('My profile shows a phone you changed on Members', async function (assert) {
    // GIVEN Rabbi, the owner, changes his own phone on his row on Members
    //       (bug found in the manual check: My profile kept the old one)
    // WHEN  he then opens My profile
    // THEN  it shows the new phone, as the API now has it
    const server = { phone: '+8801712345678' };
    worker.use(
      http.get('*/api/v1/me', () =>
        HttpResponse.json({
          success: true,
          message: 'Logged in',
          data: {
            ...me('owner'),
            person: { phone: server.phone, email: null },
          },
        }),
      ),
      http.put('*/api/v1/members/:id/contact', () => {
        server.phone = '+8801912345678';
        return HttpResponse.json({
          success: true,
          message: 'Log-in changed',
          data: { ...owner, phone: server.phone },
        });
      }),
      ...membersApi([owner]),
    );

    await visit('/members');
    await click('[data-test-edit-member="Rabbi Hasan"]');
    await fillIn('[data-test-contact-input="phone"]', '+8801912345678');
    await click('[data-test-contact-send-code="phone"]');
    await fillIn(
      '[data-test-contact-row="phone"] [data-test-code-field]',
      '123456',
    );
    await click('[data-test-contact-save="phone"]');
    await click('[data-test-nav-profile]');

    assert.dom('[data-test-contact-input="phone"]').hasValue('+8801912345678');
  });
});
