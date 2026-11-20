import { module, test } from 'qunit';
import { visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import type { components } from 'colivo-web/data/types/api.generated';

type HealthBody = components['schemas']['StandardResponse_HealthOut_'];

module('Acceptance | start page', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks);

  test('visitor sees the server is connected', async function (assert) {
    // GIVEN the API reports the database and Redis both ok
    // WHEN  a visitor opens the start page
    // THEN  it sits in the Colivo shell and says the server is connected
    const body: HealthBody = {
      success: true,
      message: 'Healthy',
      data: { database: 'ok', redis: 'ok' },
    };
    worker.use(http.get('*/api/v1/health', () => HttpResponse.json(body)));

    await visit('/');

    assert.dom('[data-test-app-shell]').exists();
    assert.dom('[data-test-server-status]').hasText('Server connected');
  });
});
