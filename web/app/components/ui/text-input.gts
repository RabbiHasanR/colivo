import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { CODE_CONTROL_CLASSES, CONTROL_CLASSES } from './control-classes';

interface TextInputSignature {
  Element: HTMLInputElement;
  /** `@code`: the 6-digit one-time code's bigger, spaced-out digits. */
  Args: { value: string; onInput: (value: string) => void; code?: boolean };
}

/** A one-line text box: `<TextInput @value={{this.name}} @onInput={{this.setName}} />` */
export default class TextInput extends Component<TextInputSignature> {
  @action
  changed(event: Event): void {
    this.args.onInput((event.target as HTMLInputElement).value);
  }

  <template>
    <input
      type="text"
      class={{if @code CODE_CONTROL_CLASSES CONTROL_CLASSES}}
      value={{@value}}
      ...attributes
      {{on "input" this.changed}}
    />
  </template>
}
