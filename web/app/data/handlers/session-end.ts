import { ApiError } from '../../utils/api-error';
import type { Handler, NextFn, RequestContext } from './types';

/**
 * Tells the app when the session ended without a log-out here: any request
 * answered 401 (logged out elsewhere, or deactivated, FR-80). First in the
 * chain, so it sees the ApiError the error handler made. The error still
 * reaches the caller.
 *
 * @param onEnded called on every 401
 */
export function createSessionEndHandler(onEnded: () => void): Handler {
  return {
    async request<T>(context: RequestContext, next: NextFn<T>) {
      try {
        return await next(context.request);
      } catch (error) {
        if (error instanceof ApiError && error.kind === 'unauthorized') {
          onEnded();
        }
        throw error;
      }
    },
  };
}
