/**
 * Short month names, fixed here: browsers' own `en-GB` names change with
 * their locale data (newer Chrome writes "Sept"); the design says "Sep".
 */
const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
];

/** A date from the API (`2026-11-21`) as people read it: `21 Nov 2026`. */
export function formatDate(isoDate: string | null | undefined): string {
  if (!isoDate) return '';
  const [year, month, day] = isoDate.split('-').map(Number);
  return `${day} ${MONTHS[(month ?? 1) - 1]} ${year}`;
}

/** Today's date where the home is (NFR-10), as the API takes it: `2026-11-21`. */
export function todayIn(now: Date, timeZone: string): string {
  // en-CA writes dates as YYYY-MM-DD.
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone,
  }).format(now);
}
