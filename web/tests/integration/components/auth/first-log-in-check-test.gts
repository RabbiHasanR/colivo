import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { me, meBody } from 'colivo-web/tests/helpers/accounts';
import FirstLogInCheck from 'colivo-web/components/auth/first-log-in-check';

module('Integration | Component | auth/first-log-in-check', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('shows where they were added, then sends their name', async function (assert) {
    // GIVEN Maruf was added to "Our Flat" as a member from 1 Sep 2026 by
    //       Rabbi Hasan, and hasn't checked his details
    // WHEN  his first log-in check is shown, he fixes his name and goes on
    // THEN  it shows the home, role, join date and who added him, sends his
    //       name, and tells the page he's done
    const sent: unknown[] = [];
    worker.use(
      http.patch('*/api/v1/me', async ({ request }) => {
        sent.push(await request.json());
        return HttpResponse.json(meBody('member', { name: 'Maruf Hossain' }));
      }),
    );
    const maruf = me('member', { details_checked: false });
    let checked = false;
    const onChecked = () => (checked = true);
    await render(
      <template>
        <FirstLogInCheck @me={{maruf}} @onChecked={{onChecked}} />
      </template>,
    );

    assert
      .dom('[data-test-first-log-in-check]')
      .includesText('You were added to')
      .includesText('Our Flat')
      .includesText('Member')
      .includesText('From 1 Sep 2026')
      .includesText('Added by Rabbi Hasan');
    assert.dom('[data-test-first-log-in-name]').hasValue('Maruf');
    await fillIn('[data-test-first-log-in-name]', 'Maruf Hossain');
    await click('[data-test-go-to-my-home]');

    assert.deepEqual(sent, [{ name: 'Maruf Hossain' }]);
    assert.true(checked);
  });
});
