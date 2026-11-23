import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import {
  codeSentBody,
  loggedInAs,
  meBody,
  meIn,
  newHomeSetup,
  newHomeSetupBody,
  notLoggedIn,
  OUR_FLAT_ID,
} from 'colivo-web/tests/helpers/accounts';

module('Acceptance | sign up', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, notLoggedIn, newHomeSetup);

  test('owner creates a home and lands on the new-home page', async function (assert) {
    // GIVEN nobody is logged in, and the API accepts the code and the sign-up
    // WHEN  the owner fills in "Create your home", sends the code and enters it
    // THEN  they land on their new home: its name, Home ID, setup checklist
    //       and the empty states of a brand-new home
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/sign-up', () => {
        worker.use(loggedInAs('owner'));
        return HttpResponse.json(meBody('owner'), { status: 201 });
      }),
    );

    await visit('/log-in');
    await click('[data-test-auth-tab="create-home"]');
    await fillIn('[data-test-sign-up-name]', 'Rabbi Hasan');
    await fillIn('[data-test-sign-up-contact]', '01712 345678');
    await fillIn('[data-test-sign-up-home-name]', 'Our Flat');
    await click('[data-test-sign-up-send-code]');
    await fillIn('[data-test-code-field]', '123456');
    await click('[data-test-sign-up-submit]');

    assert.strictEqual(currentURL(), '/');
    assert.dom('[data-test-welcome-home]').hasText('Our Flat');
    assert.dom('[data-test-welcome-home-id]').hasText('Home ID OF-4827');
    assert
      .dom('[data-test-setup-step="home_created"]')
      .hasAttribute('data-test-done');
    assert.dom('[data-test-empty-state="meals"]').exists();
    assert.dom('[data-test-empty-state="inbox"]').exists();
  });

  test('signing up for another home opens the new home', async function (assert) {
    // GIVEN Rabbi is a member of "Green House" and logged out
    // WHEN  he signs up and creates "Our Flat"
    // THEN  he lands in Our Flat, and its requests name Our Flat
    let named: string | null = null;
    worker.use(
      http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
      http.post('*/api/v1/auth/sign-up', () =>
        HttpResponse.json(
          { success: true, message: 'Home created', data: meIn(OUR_FLAT_ID) },
          { status: 201 },
        ),
      ),
      http.get('*/api/v1/home/setup', ({ request }) => {
        named = request.headers.get('X-Colivo-Home');
        return HttpResponse.json(newHomeSetupBody);
      }),
    );

    await visit('/log-in');
    await click('[data-test-auth-tab="create-home"]');
    await fillIn('[data-test-sign-up-name]', 'Rabbi Hasan');
    await fillIn('[data-test-sign-up-contact]', '01712 345678');
    await fillIn('[data-test-sign-up-home-name]', 'Our Flat');
    await click('[data-test-sign-up-send-code]');
    await fillIn('[data-test-code-field]', '123456');
    await click('[data-test-sign-up-submit]');

    assert.dom('[data-test-welcome-home]').hasText('Our Flat');
    assert.strictEqual(named, OUR_FLAT_ID);
  });
});
