import { module, test } from 'qunit';
import { createEnvelopeHandler } from 'colivo-web/data/handlers/api-envelope';
import type { NextFn } from 'colivo-web/data/handlers/types';

/** A `next` that answers with `content`, as WarpDrive's fetch handler would. */
function respondWith<T>(content: T): NextFn<T> {
  return (request) => Promise.resolve({ request, content });
}

module('Unit | Data | handlers', function () {
  test('envelope handler returns the inner data', async function (assert) {
    // GIVEN a response in the StandardResponse envelope
    // WHEN  it passes through the envelope handler
    // THEN  only its data comes out
    const handler = createEnvelopeHandler();

    const result = await handler.request(
      { request: {} },
      respondWith({
        success: true,
        message: 'Healthy',
        data: { database: 'ok', redis: 'ok' },
      }),
    );

    assert.deepEqual(result, { database: 'ok', redis: 'ok' });
  });
});
