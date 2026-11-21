import Component from '@glimmer/component';
import { guidFor } from '@ember/object/internals';

interface FieldSignature {
  Element: HTMLDivElement;
  Args: { label: string; hint?: string; errors?: string[] };
  Blocks: { default: [id: string] };
}

/**
 * A labelled form control with an optional hint and error messages:
 *
 *   <Field @label="Your name" @errors={{this.errors.name}} as |id|>
 *     <TextInput id={{id}} @value={{this.name}} @onInput={{this.setName}} />
 *   </Field>
 */
export default class Field extends Component<FieldSignature> {
  readonly id = `${guidFor(this)}-control`;

  <template>
    <div class="flex flex-col gap-1" ...attributes>
      <label for={{this.id}} class="text-sm font-medium text-ink">
        {{@label}}
      </label>
      {{yield this.id}}
      {{#if @hint}}
        <p class="text-sm text-muted">{{@hint}}</p>
      {{/if}}
      {{#each @errors as |error|}}
        <p class="text-sm text-owes-ink" data-test-field-error>{{error}}</p>
      {{/each}}
    </div>
  </template>
}
