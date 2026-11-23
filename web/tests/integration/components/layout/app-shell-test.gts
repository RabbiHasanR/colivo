import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import AppShell from 'colivo-web/components/layout/app-shell';
import {
  meIn,
  OUR_FLAT_ID,
  ourFlat,
  twoHomes,
} from 'colivo-web/tests/helpers/accounts';

module('Integration | Component | layout/app-shell', function (hooks) {
  setupRenderingTest(hooks);

  test('menu button opens and closes the sidebar', async function (assert) {
    // GIVEN the Colivo shell (the menu button is for screens below 1024px)
    // WHEN  the menu button is pressed, then pressed again
    // THEN  it opens the sidebar it controls, then closes it
    await render(
      <template>
        <AppShell>Page</AppShell>
      </template>,
    );
    const sidebarId = document
      .querySelector('[data-test-sidebar]')
      ?.getAttribute('id');

    assert
      .dom('[data-test-menu-button]')
      .hasAttribute('aria-controls', sidebarId ?? 'missing');
    assert
      .dom('[data-test-menu-button]')
      .hasAttribute('aria-expanded', 'false');

    await click('[data-test-menu-button]');
    assert.dom('[data-test-menu-button]').hasAttribute('aria-expanded', 'true');
    assert.dom('[data-test-sidebar]').hasAttribute('data-open', 'true');

    await click('[data-test-menu-button]');
    assert
      .dom('[data-test-menu-button]')
      .hasAttribute('aria-expanded', 'false');
    assert.dom('[data-test-sidebar]').hasAttribute('data-open', 'false');
  });

  for (const [name, homes, shown] of [
    ['one home', [ourFlat], false],
    ['two homes', twoHomes, true],
  ] as const) {
    test(`shows the home switcher only for a person in several homes (${name})`, async function (assert) {
      // GIVEN Rabbi is in Our Flat, his only home or one of two
      // WHEN  the shell is shown
      // THEN  it names Our Flat; the name opens a home menu only with two homes
      const session = this.owner.lookup('service:session');
      session.me = meIn(OUR_FLAT_ID, [...homes]);

      await render(
        <template>
          <AppShell>Page</AppShell>
        </template>,
      );

      assert.dom('[data-test-shell-home]').includesText('Our Flat');
      if (shown) assert.dom('[data-test-home-switcher]').exists();
      else assert.dom('[data-test-home-switcher]').doesNotExist();
    });
  }
});
