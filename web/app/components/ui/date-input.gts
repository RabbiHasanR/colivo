import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';

interface DateInputSignature {
  Element: HTMLInputElement;
  Args: { value: string; onInput: (value: string) => void };
}

const CLASSES =
  'min-h-touch w-full rounded-xl border border-line bg-surface px-3 text-base ' +
  'text-ink focus-visible:outline-2 focus-visible:outline-offset-1 ' +
  'focus-visible:outline-primary';

/** A date, with the phone's own date picker; the value is `2026-11-21`. */
export default class DateInput extends Component<DateInputSignature> {
  @action
  changed(event: Event): void {
    this.args.onInput((event.target as HTMLInputElement).value);
  }

  <template>
    <input
      type="date"
      class={{CLASSES}}
      value={{@value}}
      ...attributes
      {{on "input" this.changed}}
      {{on "change" this.changed}}
    />
  </template>
}
