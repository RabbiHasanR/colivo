import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw } from 'colivo-web/tests/helpers/msw';
import { codeSentBody } from 'colivo-web/tests/helpers/accounts';
import LogInPage from 'colivo-web/components/auth/log-in-page';

const NOT_ADDED =
  "Not added yet. Ask your home's owner or manager to add you, or create a new home.";

/** Try to log in as 01712 345678, which no home uses. */
async function logInAsSomeoneNotAdded(): Promise<void> {
  await fillIn('[data-test-log-in-contact]', '01712 345678');
  await click('[data-test-log-in-send-code]');
  await fillIn('[data-test-log-in-form] [data-test-code-field]', '123456');
  await click('[data-test-log-in-submit]');
}

module('Integration | Component | auth/log-in-page', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(
    hooks,
    http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
    http.post('*/api/v1/auth/log-in', () =>
      HttpResponse.json(
        { success: false, message: NOT_ADDED, errors: [NOT_ADDED] },
        { status: 404 },
      ),
    ),
  );

  test('not added yet: ask the home, or create a home, or try another', async function (assert) {
    // GIVEN no home uses 01712 345678
    // WHEN  they log in with the right code, then pick "Create my own home",
    //       and (again) "Try another phone or email"
    // THEN  the page says no home uses the number and to ask its owner or
    //       manager; "Create my own home" fills the sign-up form's phone or
    //       email; "Try another" goes back to the first log-in step
    await render(<template><LogInPage /></template>);

    await logInAsSomeoneNotAdded();
    assert
      .dom('[data-test-not-added]')
      .includesText('No home uses 01712 345678 yet');
    assert
      .dom('[data-test-not-added]')
      .includesText('ask its owner or manager');
    await click('[data-test-create-own-home]');
    assert.dom('[data-test-sign-up-contact]').hasValue('01712 345678');

    await logInAsSomeoneNotAdded();
    await click('[data-test-try-another]');
    assert.dom('[data-test-log-in-contact]').hasValue('');
    assert.dom('[data-test-not-added]').doesNotExist();
  });
});
