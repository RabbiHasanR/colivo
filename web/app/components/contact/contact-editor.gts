import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';
import CodeField from '../auth/code-field';
import Button from '../ui/button';
import Field from '../ui/field';
import TextInput from '../ui/text-input';

/** Which way to log in a row is about. */
export type ContactKind = 'phone' | 'email';

interface ContactEditorSignature {
  Args: {
    phone: string | null;
    email: string | null;
    editable: boolean;
    /** Send a code to the new phone or email. */
    onSendCode: (contact: string) => Promise<unknown>;
    /** Save the new phone or email with the code typed. */
    onSave: (contact: string, code: string) => Promise<unknown>;
    /** Stop logging in with the phone or the email. */
    onRemove: (kind: ContactKind) => Promise<unknown>;
  };
}

interface Row {
  kind: ContactKind;
  label: string;
  value: string;
}

/**
 * The phone and email someone logs in with (Phase 1c). A new one is saved
 * only with the code sent to it; the page decides whose log-in it is.
 */
export default class ContactEditor extends Component<ContactEditorSignature> {
  /** What was typed in each row, until it is saved. */
  @tracked typed: Partial<Record<ContactKind, string>> = {};
  /** The row waiting for its code, if any. */
  @tracked confirming: ContactKind | null = null;
  @tracked code = '';

  get rows(): Row[] {
    return [this.row('phone', 'Phone'), this.row('email', 'Email')];
  }

  /** A row; the one they don't have yet is "(optional)", as in the design. */
  row(kind: ContactKind, name: string): Row {
    const label = this.args[kind] === null ? `${name} (optional)` : name;
    return { kind, label, value: this.valueOf(kind) };
  }

  valueOf(kind: ContactKind): string {
    return this.typed[kind] ?? this.args[kind] ?? '';
  }

  @action type(kind: ContactKind, value: string): void {
    this.typed = { ...this.typed, [kind]: value };
  }

  @action setCode(value: string): void {
    this.code = value;
  }

  @action
  async submit(kind: ContactKind, event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const contact = this.valueOf(kind);
    if (this.confirming === kind) {
      await this.args.onSave(contact, this.code);
      this.confirming = null;
      this.code = '';
      return;
    }
    await this.args.onSendCode(contact);
    this.confirming = kind;
  }

  <template>
    <div class="flex flex-col gap-3" data-test-contact-editor>
      {{#each this.rows as |row|}}
        <form
          class="flex flex-col gap-2"
          data-test-contact-row={{row.kind}}
          {{on "submit" (fn this.submit row.kind)}}
        >
          <Field @label={{row.label}} as |id|>
            <TextInput
              id={{id}}
              @value={{row.value}}
              @onInput={{fn this.type row.kind}}
              data-test-contact-input={{row.kind}}
            />
          </Field>
          {{#if (eq this.confirming row.kind)}}
            <CodeField @value={{this.code}} @onInput={{this.setCode}}>
              <Button
                type="submit"
                data-test-contact-save={{row.kind}}
              >Save</Button>
            </CodeField>
          {{else}}
            <Button
              type="submit"
              @variant="secondary"
              class="self-start"
              data-test-contact-send-code={{row.kind}}
            >Send code</Button>
          {{/if}}
        </form>
      {{/each}}
    </div>
  </template>
}
