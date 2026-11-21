interface Someone {
  role: 'owner' | 'manager' | 'member';
}

/**
 * Whether `viewer` may deactivate or reactivate `member` (FR-80, FR-63,
 * FR-64): nobody changes the owner's status, and only the owner removes or
 * brings back a manager. The API enforces the same; the page only hides what
 * would be refused.
 */
export function canChangeStatus(
  viewer: Someone | null,
  member: Someone,
): boolean {
  if (!viewer || member.role === 'owner') return false;
  return member.role !== 'manager' || viewer.role === 'owner';
}

/**
 * Whether `viewer` may change `member`'s name or join date (FR-86): the owner
 * or a manager may, except that only the owner changes the owner's details.
 */
export function canEditDetails(
  viewer: Someone | null,
  member: Someone,
): boolean {
  if (!viewer) return false;
  return member.role !== 'owner' || viewer.role === 'owner';
}
