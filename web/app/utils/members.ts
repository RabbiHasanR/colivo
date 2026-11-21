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
