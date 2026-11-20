import { module, test } from 'qunit';
import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import ServerStatusMessage from 'colivo-web/components/health/server-status';
import type { ServerStatus } from 'colivo-web/services/server-status';

module('Integration | Component | health/server-status', function (hooks) {
  setupRenderingTest(hooks);

  test('shows which part is down, or that the server cannot be reached', async function (assert) {
    // GIVEN a server status that is not "connected"
    // WHEN  the status message is rendered
    // THEN  it says what is wrong, in plain words
    const cases: Array<[ServerStatus, string]> = [
      [
        { kind: 'degraded', down: ['database'] },
        'Server problem: the database is down',
      ],
      [{ kind: 'unreachable' }, "Can't reach the server"],
    ];

    for (const [status, text] of cases) {
      await render(
        <template><ServerStatusMessage @status={{status}} /></template>,
      );

      assert.dom('[data-test-server-status]').hasText(text);
    }
  });
});
