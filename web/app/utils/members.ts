interface Someone {
  role: 'owner' | 'manager' | 'member';
}

/**
 * Whether `viewer` may deactivate `member` (FR-80, FR-63, FR-64): nobody
 * deactivates the owner, and only the owner deactivates a manager. The API
 * enforces the same; the page only hides what would be refused.
 */
export function canDeactivate(
  viewer: Someone | null,
  member: Someone,
): boolean {
  if (!viewer || member.role === 'owner') return false;
  return member.role !== 'manager' || viewer.role === 'owner';
}
