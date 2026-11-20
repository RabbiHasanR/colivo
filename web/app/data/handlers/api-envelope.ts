import type { Handler, NextFn, RequestContext } from './types';

/**
 * The only file that knows the backend's StandardResponse envelope
 * ({ success, message, data, errors? }, specs/tech-stack.md → API response
 * format). Pages and services get the inner `data` and never see the envelope.
 *
 * Normalising stored resources into the store's cache shape comes with the
 * first resource (Phase 1).
 */
export function unwrapData(body: unknown): unknown {
  if (body !== null && typeof body === 'object' && 'data' in body) {
    return body.data;
  }
  return body;
}

export function createEnvelopeHandler(): Handler {
  return {
    async request<T>(context: RequestContext, next: NextFn<T>) {
      const doc = await next(context.request);
      return unwrapData(doc.content) as T;
    },
  };
}
