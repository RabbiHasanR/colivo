/**
 * Minimal structural types for request handlers.
 *
 * They match the shape WarpDrive's RequestManager expects
 * ({ request(context, next) }), but are declared locally so handlers and
 * their unit tests don't depend on a WarpDrive package path.
 */
export interface AppRequest {
  url?: string;
  method?: string;
  headers?: Headers;
  body?: BodyInit | null;
  /** WarpDrive operation name: query, findRecord, createRecord, … */
  op?: string;
  options?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface RequestContext {
  request: AppRequest;
}

export interface StructuredDocument<T> {
  request?: AppRequest;
  response?: Response | null;
  content: T;
}

export type NextFn<T = unknown> = (
  request: AppRequest,
) => Promise<StructuredDocument<T>>;

export interface Handler {
  request<T>(
    context: RequestContext,
    next: NextFn<T>,
  ): Promise<T | StructuredDocument<T>>;
}
