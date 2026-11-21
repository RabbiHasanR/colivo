import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

type Schemas = components['schemas'];
export type SignUpFields = Schemas['SignUpIn'];
export type CodeSent = Schemas['CodeSentOut'];

/** A JSON POST that is not a stored record, so it skips the cache. */
function postJson(path: string, body: unknown) {
  return {
    url: apiUrl(path),
    method: 'POST' as const,
    body: JSON.stringify(body),
    headers: new Headers({ 'Content-Type': 'application/json' }),
    cacheOptions: { [SkipCache]: true as const },
  };
}

/** Send a one-time code to a phone or email. */
export function requestCode(contact: string) {
  return postJson('auth/codes', { contact });
}

/** Create a home; the person signing up becomes its owner and is logged in. */
export function signUp(fields: SignUpFields) {
  return postJson('auth/sign-up', fields);
}
