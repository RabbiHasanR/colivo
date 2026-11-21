const SHORT_DATE = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
});

/** A date from the API (`2026-11-21`) as people read it: `21 Nov 2026`. */
export function formatDate(isoDate: string | null | undefined): string {
  if (!isoDate) return '';
  return SHORT_DATE.format(new Date(`${isoDate}T00:00:00Z`));
}
