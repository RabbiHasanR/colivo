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
