import { module, test } from 'qunit';
import { http, HttpResponse } from 'msw';
import { setupTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import type { components } from 'colivo-web/data/types/api.generated';

type HealthBody = components['schemas']['StandardResponse_HealthOut_'];

module('Unit | Service | server-status', function (hooks) {
  setupTest(hooks);
  setupMsw(hooks);

  test('reports which part is down on a 503', async function (assert) {
    // GIVEN the API answers 503 with the database down
    // WHEN  the server status is checked (real store, network mocked)
    // THEN  it is "degraded" with the database listed as down
    const body: HealthBody = {
      success: false,
      message: 'Service unavailable',
      data: { database: 'down', redis: 'ok' },
    };
    worker.use(
      http.get('*/api/v1/health', () =>
        HttpResponse.json(body, { status: 503 }),
      ),
    );

    const status = await this.owner.lookup('service:server-status').check();

    assert.deepEqual(status, { kind: 'degraded', down: ['database'] });
  });

  test('reports unreachable when there is no answer', async function (assert) {
    // GIVEN the backend gives no answer at all (down, no network)
    // WHEN  the server status is checked
    // THEN  it is "unreachable"
    worker.use(http.get('*/api/v1/health', () => HttpResponse.error()));

    const status = await this.owner.lookup('service:server-status').check();

    assert.deepEqual(status, { kind: 'unreachable' });
  });
});
