import { ApiError } from './api-error';

/** Why the API refused a form: messages per field (422), or one message. */
export interface Refusal {
  fieldErrors: Record<string, string[]>;
  message: string | null;
}

/**
 * What a form shows for a failed request, or null when it wasn't the API
 * refusing (no response, a bug): then the form lets the error through.
 */
export function refusalFrom(error: unknown): Refusal | null {
  if (!(error instanceof ApiError) || error.status === null) return null;
  if (error.kind === 'validation') {
    return { fieldErrors: error.fieldErrors, message: null };
  }
  return { fieldErrors: {}, message: error.message };
}
