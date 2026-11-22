/** The first word of a person's name, to greet them: "Rabbi Hasan" → "Rabbi". */
export function firstName(name: string): string {
  return name.trim().split(/\s+/)[0] ?? name;
}

/** An avatar's letters: first and last name's first letters, "Rabbi Hasan" → "RH". */
export function initials(name: string): string {
  const words = name.trim().split(/\s+/);
  const first = words[0] ?? '';
  const last = words.length > 1 ? (words[words.length - 1] ?? '') : '';
  return (first.charAt(0) + last.charAt(0)).toUpperCase();
}
