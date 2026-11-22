/** Seconds left to wait, as on colivo-design/web/WebAuthErrors.html: `14:52`. */
export function formatCountdown(seconds: number): string {
  const left = Math.max(0, Math.ceil(seconds));
  const minutes = Math.floor(left / 60);
  const rest = String(left % 60).padStart(2, '0');
  return `${minutes}:${rest}`;
}
