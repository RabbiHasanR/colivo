/** A role as people read it: `owner` → `Owner`. */
export function roleLabel(role: string): string {
  return role.charAt(0).toUpperCase() + role.slice(1);
}

/** A role's pill colour (a `Tag` tone), as in colivo-design/web/WebMembers.html. */
export type RoleTone = 'dark' | 'blue' | 'teal' | 'grey';

const ROLE_TONES: Record<string, RoleTone> = {
  owner: 'dark',
  manager: 'blue',
  member: 'teal',
};

/** The pill colour for `role`: `owner` → `dark`; an unknown role is grey. */
export function roleTone(role: string): RoleTone {
  return ROLE_TONES[role] ?? 'grey';
}
