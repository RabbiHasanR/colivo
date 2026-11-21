/** A role as people read it: `owner` → `Owner`. */
export function roleLabel(role: string): string {
  return role.charAt(0).toUpperCase() + role.slice(1);
}
