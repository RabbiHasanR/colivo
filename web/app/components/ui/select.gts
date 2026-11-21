import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectSignature {
  Element: HTMLSelectElement;
  Args: {
    options: SelectOption[];
    value: string;
    onChange: (value: string) => void;
  };
}

const CLASSES =
  'min-h-touch w-full rounded-xl border border-line bg-surface px-3 text-base ' +
  'text-ink focus-visible:outline-2 focus-visible:outline-offset-1 ' +
  'focus-visible:outline-primary';

/** A drop-down list of `@options`. */
export default class Select extends Component<SelectSignature> {
  @action
  changed(event: Event): void {
    this.args.onChange((event.target as HTMLSelectElement).value);
  }

  <template>
    <select class={{CLASSES}} ...attributes {{on "change" this.changed}}>
      {{! Not "as |option|": in a strict template that would shadow <option>. }}
      {{#each @options as |choice|}}
        <option value={{choice.value}} selected={{eq choice.value @value}}>
          {{choice.label}}
        </option>
      {{/each}}
    </select>
  </template>
}
