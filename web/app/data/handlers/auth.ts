import type { Handler, NextFn, RequestContext } from './types';

/**
 * Sends every API request with the session cookie, and never a token.
 *
 * The log-in lives in an httpOnly cookie that page scripts can't read
 * (specs/tech-stack.md → Decided in Phase 1), so the browser attaches it:
 * `credentials: 'include'` lets it do so for the API's own origin.
 */
export function createAuthHandler(): Handler {
  return {
    request<T>(context: RequestContext, next: NextFn<T>) {
      const headers = new Headers(context.request.headers);
      headers.set('Accept', 'application/json');
      headers.delete('Authorization');
      return next({ ...context.request, headers, credentials: 'include' });
    },
  };
}
