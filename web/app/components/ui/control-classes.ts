/**
 * The look shared by every one-line form control (TextInput, Select,
 * DateInput), from colivo-design/web: 46px tall, 10px corners, a brown
 * border when the value was refused (`aria-invalid="true"`).
 */
const CONTROL_BASE =
  'h-[46px] w-full min-w-0 rounded-field border border-field bg-surface px-3 ' +
  'text-ink placeholder:text-faint ' +
  'focus-visible:outline-2 focus-visible:outline-offset-1 ' +
  'focus-visible:outline-primary ' +
  'aria-invalid:border-[1.5px] aria-invalid:border-owes';

export const CONTROL_CLASSES = `${CONTROL_BASE} text-[15px]`;

/** The 6-digit code: bigger, spaced-out digits (WebAuth.html). */
export const CODE_CONTROL_CLASSES = `${CONTROL_BASE} text-lg tracking-[6px]`;
