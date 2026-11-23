import { module, test } from 'qunit';
import { click, fillIn, render } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { me, meBody } from 'colivo-web/tests/helpers/accounts';
import ProfilePage from 'colivo-web/components/profile/profile-page';

module('Integration | Component | profile/profile-page', function (hooks) {
  setupRenderingTest(hooks);
  setupMsw(hooks);

  test('shows who you are: name, role, member since, phone and email', async function (assert) {
    // GIVEN Rabbi Hasan, the owner, living here since 1 Nov 2026, with a
    //       phone and an email
    // WHEN  My profile is shown
    // THEN  it shows his name, "Owner · member since November 2026", and
    //       his phone and email in their fields
    const session = this.owner.lookup('service:session');
    const rabbi = me('owner', { joined_on: '2026-11-01' });
    session.me = {
      ...rabbi,
      person: { phone: '+8801712345678', email: 'rabbi@example.com' },
    };

    await render(<template><ProfilePage /></template>);

    assert.dom('[data-test-profile-name]').hasText('Rabbi Hasan');
    assert
      .dom('[data-test-profile-subtitle]')
      .hasText('Owner · member since November 2026');
    assert.dom('[data-test-contact-input="phone"]').hasValue('+8801712345678');
    assert
      .dom('[data-test-contact-input="email"]')
      .hasValue('rabbi@example.com');
  });

  test("shows just the role for an owner who doesn't live in the home", async function (assert) {
    // GIVEN Rabbi Hasan owns Our Flat but doesn't live there (no join date)
    // WHEN  My profile is shown
    // THEN  the line under his name is just "Owner"
    const session = this.owner.lookup('service:session');
    session.me = me('owner', { joined_on: null });

    await render(<template><ProfilePage /></template>);

    assert.dom('[data-test-profile-subtitle]').hasText('Owner');
  });

  test('saves your new name and shows it', async function (assert) {
    // GIVEN Rabbi Hasan on My profile; the API saves names
    // WHEN  he changes his name to "Rabbi H." and presses Save
    // THEN  the new name is sent, and My profile shows it
    const sent: unknown[] = [];
    worker.use(
      http.patch('*/api/v1/me', async ({ request }) => {
        sent.push(await request.json());
        return HttpResponse.json(meBody('owner', { name: 'Rabbi H.' }));
      }),
    );
    this.owner.lookup('service:session').me = me('owner');

    await render(<template><ProfilePage /></template>);
    await fillIn('[data-test-profile-name-input]', 'Rabbi H.');
    await click('[data-test-profile-name-save]');

    assert.deepEqual(sent, [{ name: 'Rabbi H.' }]);
    assert.dom('[data-test-profile-name]').hasText('Rabbi H.');
  });
});
