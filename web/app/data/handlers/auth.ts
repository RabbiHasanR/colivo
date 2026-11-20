import type { Handler, NextFn, RequestContext } from './types';

/**
 * Adds the session's bearer token to every request.
 *
 * What a 401 does (log out, go to log-in) is decided with log-in in Phase 1.
 *
 * @param getToken returns the current token, or null when logged out
 */
export function createAuthHandler(getToken: () => string | null): Handler {
  return {
    request<T>(context: RequestContext, next: NextFn<T>) {
      const headers = new Headers(context.request.headers);
      headers.set('Accept', 'application/json');

      const token = getToken();
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }

      return next({ ...context.request, headers });
    },
  };
}
