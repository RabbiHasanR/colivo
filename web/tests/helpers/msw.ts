import { setupWorker } from 'msw/browser';
import type { RequestHandler } from 'msw';

/**
 * Network mocking for fast tests (specs/testing.md → Web). MSW intercepts
 * fetch at the network boundary, so the real store, handlers, routes and
 * components all run.
 *
 *   module('Acceptance | start page', function (hooks) {
 *     setupApplicationTest(hooks);
 *     setupMsw(hooks);
 *
 *     test('…', async function (assert) {
 *       worker.use(http.get('*\/api/v1/health', () => HttpResponse.json(body)));
 *     });
 *   });
 *
 * Type every response body with app/data/types/api.generated.ts, so a changed
 * API contract fails `make lint` instead of passing silently.
 */
export const worker = setupWorker();

let started: Promise<unknown> | null = null;

/** An HTTP request with no handler is a test bug only when it calls the API. */
function isApiRequest(frame: { protocol: string; data: unknown }): boolean {
  if (frame.protocol !== 'http') {
    return false;
  }
  const { request } = frame.data as { request: Request };
  return new URL(request.url).pathname.startsWith('/api/');
}

/**
 * Start the worker once per test run and reset its handlers after each test.
 *
 * @param hooks The QUnit hooks of the module.
 * @param defaultHandlers Handlers every test in the module starts with.
 */
export function setupMsw(
  hooks: NestedHooks,
  ...defaultHandlers: RequestHandler[]
): void {
  hooks.before(async function () {
    started ??= worker.start({
      quiet: true,
      // MSW v3: onUnhandledFrame replaces v2's onUnhandledRequest.
      onUnhandledFrame({ frame, defaults }) {
        if (isApiRequest(frame)) {
          defaults.error();
        }
      },
    });
    await started;
  });

  hooks.beforeEach(function () {
    worker.use(...defaultHandlers);
  });

  hooks.afterEach(function () {
    worker.resetHandlers();
  });
}
