import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';

interface CheckboxSignature {
  Element: HTMLInputElement;
  Args: { checked: boolean; onChange: (checked: boolean) => void };
  Blocks: { default: [] };
}

/** A tick box with its label: `<Checkbox @checked={{x}} @onChange={{y}}>I live here</Checkbox>` */
export default class Checkbox extends Component<CheckboxSignature> {
  @action
  changed(event: Event): void {
    this.args.onChange((event.target as HTMLInputElement).checked);
  }

  <template>
    <label class="flex min-h-touch items-center gap-3 text-sm text-ink">
      <input
        type="checkbox"
        class="size-5 accent-primary"
        checked={{@checked}}
        ...attributes
        {{on "change" this.changed}}
      />
      {{yield}}
    </label>
  </template>
}
