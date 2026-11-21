import type { Handler, NextFn, RequestContext } from './types';
import { ApiError, type ApiErrorKind } from '../../utils/api-error';

export { ApiError, type ApiErrorKind };

const KIND_BY_STATUS: Record<number, ApiErrorKind> = {
  400: 'rule',
  401: 'unauthorized',
  403: 'forbidden',
  404: 'not-found',
  409: 'conflict',
  422: 'validation',
};

export function kindForStatus(status: number | null): ApiErrorKind {
  if (status === null) return 'network';
  if (status >= 500) return 'server';
  return KIND_BY_STATUS[status] ?? 'unknown';
}

/** The API's error body: the StandardResponse envelope with `errors`. */
interface ErrorBody {
  message?: unknown;
  errors?: unknown;
  data?: unknown;
}

/**
 * Reads the backend's 422 `errors` list, `["body.email: Field required"]`,
 * into `{ email: ["Field required"] }`. The first part of the location
 * (body, query, path) is dropped; a string without a location goes under
 * `base`. The only place that knows this format.
 */
export function fieldErrorsFrom(
  body: ErrorBody | null,
): Record<string, string[]> {
  const result: Record<string, string[]> = {};
  if (!Array.isArray(body?.errors)) return result;

  for (const entry of body.errors) {
    const text = String(entry);
    const separator = text.indexOf(': ');
    const location = separator === -1 ? '' : text.slice(0, separator);
    const message = separator === -1 ? text : text.slice(separator + 2);
    const field = location.split('.').slice(1).join('.') || 'base';
    (result[field] ??= []).push(message);
  }
  return result;
}

/**
 * The HTTP status of a failed request, or null when there was no response.
 * WarpDrive's fetch handler reports a network failure as status 0 and an
 * aborted request as 20: neither is an HTTP status.
 */
function httpStatusFrom(status: unknown): number | null {
  return typeof status === 'number' && status >= 100 ? status : null;
}

function isErrorBody(content: unknown): content is ErrorBody {
  return content !== null && typeof content === 'object';
}

function messageFrom(body: ErrorBody | null, fallback: string): string {
  return typeof body?.message === 'string' ? body.message : fallback;
}

/** Turns whatever the network layer throws into an ApiError. First in the chain. */
export const ErrorHandler: Handler = {
  async request<T>(context: RequestContext, next: NextFn<T>) {
    try {
      return await next(context.request);
    } catch (error) {
      if (error instanceof ApiError) throw error;

      const failure = error as { status?: unknown; content?: unknown } | null;
      const status = httpStatusFrom(failure?.status);
      const body = isErrorBody(failure?.content) ? failure.content : null;
      const kind = kindForStatus(status);

      throw new ApiError(
        messageFrom(body, 'Request failed'),
        status,
        kind,
        kind === 'validation' ? fieldErrorsFrom(body) : {},
        body?.data,
      );
    }
  },
};
