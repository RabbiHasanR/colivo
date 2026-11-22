/**
 * The segmented switch from colivo-design/web (Current | Past, Log in |
 * Create a home): a grey track, the chosen segment white. The caller sets
 * the track's display: `inline-flex` to fit its tabs, `grid` to fill the row.
 */
export const SEGMENT_TRACK = 'gap-1 rounded-xl bg-tag-rent p-1';

export function segmentClasses(selected: boolean): string {
  const base =
    'inline-flex min-h-9 items-center justify-center rounded-[9px] px-4 text-sm ' +
    'focus-visible:outline-2 focus-visible:outline-primary';
  return selected
    ? `${base} bg-surface font-semibold text-ink`
    : `${base} font-medium text-muted hover:text-ink`;
}
