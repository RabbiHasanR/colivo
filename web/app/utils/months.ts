/** A new home's time zone (NFR-10); the backend's `home.time_zone` default. */
export const DEFAULT_TIME_ZONE = 'Asia/Dhaka';

export interface MonthChoice {
  /** The month's 1st, as the API takes it: `2026-11-01`. */
  value: string;
  /** What the person reads: `November 2026`. */
  label: string;
}

const LABEL = new Intl.DateTimeFormat('en', {
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
});

/** The year and month (1–12) that `now` falls in, in `timeZone`. */
function yearAndMonth(now: Date, timeZone: string): [number, number] {
  const parts = new Intl.DateTimeFormat('en', {
    year: 'numeric',
    month: 'numeric',
    timeZone,
  }).formatToParts(now);
  const part = (type: string) =>
    Number(parts.find((each) => each.type === type)?.value);
  return [part('year'), part('month')];
}

function choice(year: number, month: number): MonthChoice {
  const first = new Date(Date.UTC(year, month - 1, 1));
  return {
    value: first.toISOString().slice(0, 10),
    label: LABEL.format(first),
  };
}

/**
 * The months a new home may start in: this month and next, in the home's
 * time zone (the backend refuses any other, FR-83).
 */
export function firstMonthChoices(now: Date, timeZone: string): MonthChoice[] {
  const [year, month] = yearAndMonth(now, timeZone);
  const next: [number, number] =
    month === 12 ? [year + 1, 1] : [year, month + 1];
  return [choice(year, month), choice(...next)];
}

/** The month `now` falls in, in `timeZone`, as people read it: `November 2026`. */
export function thisMonthLabel(now: Date, timeZone: string): string {
  return choice(...yearAndMonth(now, timeZone)).label;
}

/** A date from the API (`2026-11-21`) as its month: `November 2026`. */
export function formatMonth(isoDate: string): string {
  const [year, month] = isoDate.split('-').map(Number);
  return choice(year ?? 1970, month ?? 1).label;
}
