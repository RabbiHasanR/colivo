import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

type Schemas = components['schemas'];
/** A member of the home, for the members list (`MemberOut`). */
export type Member = Schemas['MemberOut'];
export type MemberFields = Schemas['MemberIn'];
export type MemberChanges = Schemas['MemberUpdateIn'];
export type NewRole = Schemas['RoleIn']['role'];
/** Which way to log in a change is about: `phone` or `email`. */
export type ContactKind = Schemas['ContactKind'];

/**
 * Members are plain data, not WarpDrive records: every request skips the
 * cache and the list is read again on each visit (group 4 design sketch).
 */
const NO_CACHE = { [SkipCache]: true as const };

function jsonBody(
  method: 'POST' | 'PATCH' | 'PUT',
  path: string,
  body: unknown,
) {
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

/** Deactivate a member from a date (today or earlier). */
export function deactivateMember(id: string, on: string) {
  return jsonBody('POST', `members/${id}/deactivate`, { on });
}

/** Reactivate a member from the date charges start again. */
export function reactivateMember(id: string, on: string) {
  return jsonBody('POST', `members/${id}/reactivate`, { on });
}

/** Give or take away the Manager role (the owner only). */
export function changeRole(id: string, role: NewRole) {
  return jsonBody('PUT', `members/${id}/role`, { role });
}

/** Send a code to a member's new phone or email, to confirm it. */
export function requestMemberContactCode(id: string, contact: string) {
  return jsonBody('POST', `members/${id}/contact/code`, { contact });
}

/** Save a member's new phone or email with the code sent to it. */
export function setMemberContact(id: string, contact: string, code: string) {
  return jsonBody('PUT', `members/${id}/contact`, { contact, code });
}

/** Stop a member logging in with their phone or their email. */
export function removeMemberContact(id: string, kind: ContactKind) {
  return {
    url: apiUrl(`members/${id}/contact/${kind}`),
    method: 'DELETE' as const,
    cacheOptions: NO_CACHE,
  };
}
