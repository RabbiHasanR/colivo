import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import AppShell from 'colivo-web/components/layout/app-shell';

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
});
