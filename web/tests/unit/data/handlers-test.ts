import { module, test } from 'qunit';
import { createEnvelopeHandler } from 'colivo-web/data/handlers/api-envelope';
import { createAuthHandler } from 'colivo-web/data/handlers/auth';
import {
  ApiError,
  ErrorHandler,
  type ApiErrorKind,
} from 'colivo-web/data/handlers/errors';
import type { AppRequest, NextFn } from 'colivo-web/data/handlers/types';

/** A `next` that answers with `content`, as WarpDrive's fetch handler would. */
function respondWith<T>(content: T): NextFn<T> {
  return (request) => Promise.resolve({ request, content });
}

/** A `next` that fails like WarpDrive's fetch handler: status + parsed body. */
function failWith(status: number, content: unknown): NextFn<never> {
  return () =>
    Promise.reject(
      Object.assign(new Error('Request failed'), { status, content }),
    );
}

/** Run the error handler on a failing `next` and return what it threw. */
async function errorFrom(next: NextFn<never>): Promise<unknown> {
  try {
    await ErrorHandler.request({ request: {} }, next);
  } catch (error) {
    return error;
  }
  throw new Error('expected the request to fail');
}

module('Unit | Data | handlers', function () {
  test('envelope handler returns the inner data', async function (assert) {
    // GIVEN a response in the StandardResponse envelope
    // WHEN  it passes through the envelope handler
    // THEN  only its data comes out
    const handler = createEnvelopeHandler();

    // The envelope handler changes the shape, so the result is untyped here.
    const result: unknown = await handler.request(
      { request: {} },
      respondWith({
        success: true,
        message: 'Healthy',
        data: { database: 'ok', redis: 'ok' },
      }),
    );

    assert.deepEqual(result, { database: 'ok', redis: 'ok' });
  });

  test('error handler turns 422 "<loc>: <msg>" strings into field errors', async function (assert) {
    // GIVEN the API's 422 body: errors as "<loc>: <msg>" strings
    // WHEN  a request fails with it
    // THEN  an ApiError of kind "validation" carries the messages per field
    const error = await errorFrom(
      failWith(422, {
        success: false,
        message: 'Validation Error',
        errors: ['body.email: Field required', 'body.name: String too short'],
      }),
    );

    assert.true(error instanceof ApiError);
    const apiError = error as ApiError;
    assert.strictEqual(apiError.kind, 'validation');
    assert.strictEqual(apiError.message, 'Validation Error');
    assert.deepEqual(apiError.fieldErrors, {
      email: ['Field required'],
      name: ['String too short'],
    });
  });

  test('error handler maps 400, 409 and other statuses to their kinds', async function (assert) {
    // GIVEN error responses with different statuses
    // WHEN  a request fails with each
    // THEN  the ApiError kind tells pages what happened
    const cases: Array<[number, ApiErrorKind]> = [
      [400, 'rule'],
      [401, 'unauthorized'],
      [403, 'forbidden'],
      [404, 'not-found'],
      [409, 'conflict'],
      [500, 'server'],
      [503, 'server'],
      [418, 'unknown'],
    ];

    for (const [status, kind] of cases) {
      const error = (await errorFrom(
        failWith(status, { success: false, message: 'No' }),
      )) as ApiError;

      assert.strictEqual(error.kind, kind, `${status} is ${kind}`);
    }
  });

  test('error handler maps a failed fetch to a network error', async function (assert) {
    // GIVEN no response at all (server down, no connection)
    // WHEN  fetch rejects without a status
    // THEN  an ApiError of kind "network" is thrown
    const error = (await errorFrom(() =>
      Promise.reject(new TypeError('Failed to fetch')),
    )) as ApiError;

    assert.strictEqual(error.kind, 'network');
    assert.strictEqual(error.status, null);
  });

  test('auth handler sends cookies and no Authorization header', async function (assert) {
    // GIVEN a request to the API, even one that still carries an old bearer token
    // WHEN  it passes through the auth handler
    // THEN  it goes with the session cookie (credentials: include) and no
    //       Authorization header: the log-in lives in an httpOnly cookie
    let sent: AppRequest | undefined;

    await createAuthHandler().request(
      {
        request: {
          url: '/api/v1/me',
          headers: new Headers({ Authorization: 'Bearer stale' }),
        },
      },
      (request) => {
        sent = request;
        return Promise.resolve({ content: null });
      },
    );

    assert.strictEqual(sent?.credentials, 'include');
    assert.strictEqual(sent?.headers?.get('Authorization') ?? null, null);
  });
});
