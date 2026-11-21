/** The first word of a person's name, to greet them: "Rabbi Hasan" → "Rabbi". */
export function firstName(name: string): string {
  return name.trim().split(/\s+/)[0] ?? name;
}
