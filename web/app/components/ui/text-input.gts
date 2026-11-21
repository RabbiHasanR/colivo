import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';

interface TextInputSignature {
  Element: HTMLInputElement;
  Args: { value: string; onInput: (value: string) => void };
}

const CLASSES =
  'min-h-touch w-full rounded-xl border border-line bg-surface px-3 text-base ' +
  'text-ink focus-visible:outline-2 focus-visible:outline-offset-1 ' +
  'focus-visible:outline-primary';

/** A one-line text box: `<TextInput @value={{this.name}} @onInput={{this.setName}} />` */
export default class TextInput extends Component<TextInputSignature> {
  @action
  changed(event: Event): void {
    this.args.onInput((event.target as HTMLInputElement).value);
  }

  <template>
    <input
      type="text"
      class={{CLASSES}}
      value={{@value}}
      ...attributes
      {{on "input" this.changed}}
    />
  </template>
}
