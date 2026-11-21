import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

type Schemas = components['schemas'];
/** A member of the home, for the members list (`MemberOut`). */
export type Member = Schemas['MemberOut'];
export type MemberFields = Schemas['MemberIn'];
export type MemberChanges = Schemas['MemberUpdateIn'];

/**
 * Members are plain data, not WarpDrive records: every request skips the
 * cache and the list is read again on each visit (group 4 design sketch).
 */
const NO_CACHE = { [SkipCache]: true as const };

function jsonBody(method: 'POST' | 'PATCH', path: string, body: unknown) {
  return {
    url: apiUrl(path),
    method,
    body: JSON.stringify(body),
    headers: new Headers({ 'Content-Type': 'application/json' }),
    cacheOptions: NO_CACHE,
  };
}

/** Everyone in the home (owner and managers only). */
export function listMembers() {
  return {
    url: apiUrl('members'),
    method: 'GET' as const,
    cacheOptions: NO_CACHE,
  };
}

/** Add a member; they get an SMS or email. */
export function addMember(fields: MemberFields) {
  return jsonBody('POST', 'members', fields);
}

/** Change a member's name or join date. */
export function updateMember(id: string, changes: MemberChanges) {
  return jsonBody('PATCH', `members/${id}`, changes);
}
