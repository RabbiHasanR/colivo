import { ApiError, type ApiErrorKind } from '../../utils/api-error';
import type { Handler, NextFn, RequestContext } from './types';

/**
 * Tells the app about one kind of failed request, wherever it was made: a
 * 401 means the session ended (logged out elsewhere, or deactivated, FR-80);
 * a 403 can mean the person's role changed meanwhile. First in the chain, so
 * it sees the ApiError the error handler made. The error still reaches the
 * caller.
 *
 * @param kind the error kind to watch for
 * @param onError called with the error, on every request that fails with it
 */
export function createErrorWatchHandler(
  kind: ApiErrorKind,
  onError: (error: ApiError) => void,
): Handler {
  return {
    async request<T>(context: RequestContext, next: NextFn<T>) {
      try {
        return await next(context.request);
      } catch (error) {
        if (error instanceof ApiError && error.kind === kind) {
          onError(error);
        }
        throw error;
      }
    },
  };
}
