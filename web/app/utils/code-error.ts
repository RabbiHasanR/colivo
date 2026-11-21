import { ApiError } from './api-error';

/** Why a one-time code, or a new one, was refused (the API's CodeErrorOut). */
export interface CodeError {
  reason: 'wrong' | 'expired' | 'locked' | 'too_soon' | 'hourly_limit';
  message: string;
  triesLeft: number | null;
  retryInSeconds: number | null;
}

const REASONS = new Set([
  'wrong',
  'expired',
  'locked',
  'too_soon',
  'hourly_limit',
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object';
}

function numberOrNull(value: unknown): number | null {
  return typeof value === 'number' ? value : null;
}

/** The refused code an API error describes, or null for any other error. */
export function codeErrorFrom(error: unknown): CodeError | null {
  if (!(error instanceof ApiError) || !isRecord(error.data)) return null;
  const { reason, tries_left, retry_in_seconds } = error.data;
  if (typeof reason !== 'string' || !REASONS.has(reason)) return null;
  return {
    reason: reason as CodeError['reason'],
    message: error.message,
    triesLeft: numberOrNull(tries_left),
    retryInSeconds: numberOrNull(retry_in_seconds),
  };
}

/** "3 tries left." / "1 try left.", or nothing when the API sent no count. */
export function triesLeftText(triesLeft: number | null): string {
  if (triesLeft === null) return '';
  return `${triesLeft} ${triesLeft === 1 ? 'try' : 'tries'} left.`;
}
