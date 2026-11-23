import { HOME_HEADER } from '../config';
import type { Handler, NextFn, RequestContext } from './types';

/**
 * Sends every API request with the session cookie, and never a token.
 *
 * The log-in lives in an httpOnly cookie that page scripts can't read
 * (specs/tech-stack.md → Decided in Phase 1), so the browser attaches it:
 * `credentials: 'include'` lets it do so for the API's own origin.
 *
 * It also names the home this tab acts in, `X-Colivo-Home` (Phase 1b), from
 * `getHomeId`; the server checks it against the person's own homes.
 */
export function createAuthHandler(
  getHomeId: () => string | null = () => null,
): Handler {
  return {
    request<T>(context: RequestContext, next: NextFn<T>) {
      const headers = new Headers(context.request.headers);
      headers.set('Accept', 'application/json');
      headers.delete('Authorization');
      const homeId = getHomeId();
      if (homeId) headers.set(HOME_HEADER, homeId);
      return next({ ...context.request, headers, credentials: 'include' });
    },
  };
}
