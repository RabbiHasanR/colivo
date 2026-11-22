import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { CONTROL_CLASSES } from './control-classes';

interface TextInputSignature {
  Element: HTMLInputElement;
  Args: { value: string; onInput: (value: string) => void };
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
      class={{CONTROL_CLASSES}}
      value={{@value}}
      ...attributes
      {{on "input" this.changed}}
    />
  </template>
}
