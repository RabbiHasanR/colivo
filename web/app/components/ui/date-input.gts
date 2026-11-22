import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { CONTROL_CLASSES } from './control-classes';

interface DateInputSignature {
  Element: HTMLInputElement;
  Args: { value: string; onInput: (value: string) => void };
}

/** A date, with the phone's own date picker; the value is `2026-11-21`. */
export default class DateInput extends Component<DateInputSignature> {
  @action
  changed(event: Event): void {
    this.args.onInput((event.target as HTMLInputElement).value);
  }

  <template>
    <input
      type="date"
      class={{CONTROL_CLASSES}}
      value={{@value}}
      ...attributes
      {{on "input" this.changed}}
      {{on "change" this.changed}}
    />
  </template>
}
