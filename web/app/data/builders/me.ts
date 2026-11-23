import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

/** Who is logged in, and in which home (`GET /me`). */
export type Me = components['schemas']['MeOut'];
export type Role = Me['membership']['role'];
/** One of the person's homes, to choose or switch to (Phase 1b). */
export type HomeChoice = components['schemas']['HomeChoiceOut'];
/** The phone and email the person logs in with (Phase 1c). */
export type MePerson = components['schemas']['MePersonOut'];
/** Which way to log in: `phone` or `email`. */
export type ContactKind = components['schemas']['ContactKind'];

/** Who is logged in. Not a stored record, so it skips the cache. */
export function getMe() {
  return {
    url: apiUrl('me'),
    method: 'GET' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}

/** Fix your own name; this also finishes the first log-in check. */
export function updateMe(name: string) {
  return {
    url: apiUrl('me'),
    method: 'PATCH' as const,
    body: JSON.stringify({ name }),
    headers: new Headers({ 'Content-Type': 'application/json' }),
    cacheOptions: { [SkipCache]: true as const },
  };
}

/** The logged-in person's homes (`GET /me/homes`); needs no home chosen. */
export function getMyHomes() {
  return {
    url: apiUrl('me/homes'),
    method: 'GET' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}

/** A JSON request to `path` under the API, never cached. */
function jsonRequest(method: 'POST' | 'PUT', path: string, body: unknown) {
  return {
    url: apiUrl(path),
    method,
    body: JSON.stringify(body),
    headers: new Headers({ 'Content-Type': 'application/json' }),
    cacheOptions: { [SkipCache]: true as const },
  };
}

/** Send a code to your new phone or email (Phase 1c); needs no home. */
export function requestMyContactCode(contact: string) {
  return jsonRequest('POST', 'me/contact/code', { contact });
}

/** Save your new phone or email with the code sent to it. */
export function setMyContact(contact: string, code: string) {
  return jsonRequest('PUT', 'me/contact', { contact, code });
}

/** Stop logging in with your phone or your email. */
export function removeMyContact(kind: ContactKind) {
  return {
    url: apiUrl(`me/contact/${kind}`),
    method: 'DELETE' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}
