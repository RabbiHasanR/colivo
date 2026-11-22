export type ApiErrorKind =
  | 'rule' // 400: the request breaks a business rule
  | 'unauthorized' // 401
  | 'forbidden' // 403
  | 'not-found' // 404
  | 'conflict' // 409
  | 'validation' // 422
  | 'too-many' // 429: too many tries; wait and try again
  | 'server' // 5xx
  | 'network' // no response at all
  | 'unknown';

/**
 * The one error type the rest of the app has to know about. Thrown by the
 * data layer (data/handlers/errors.ts); a plain class, so components and
 * services may check for it too.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number | null,
    readonly kind: ApiErrorKind,
    /** Field name -> messages, filled for 422 responses. */
    readonly fieldErrors: Record<string, string[]> = {},
    /** The envelope's `data`, when an error response carries some (health: 503). */
    readonly data: unknown = undefined,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
