import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { ContactKind } from '../../services/members';
import { codeErrorFrom, type CodeError } from '../../utils/code-error';
import { refusalFrom, type Refusal } from '../../utils/refusal';
import { eq } from '../../utils/template';
import CodeErrors from '../auth/code-errors';
import CodeField from '../auth/code-field';
import Button from '../ui/button';
import Field from '../ui/field';
import FormError from '../ui/form-error';
import TextInput from '../ui/text-input';

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
  /** Why the API refused this row, other than its code. */
  message: string | null;
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
  /** Why the code for the row being confirmed was refused, if it was. */
  @tracked codeError: CodeError | null = null;
  /** Any other refusal, and the row it is about. */
  @tracked refused: { kind: ContactKind; refusal: Refusal } | null = null;

  get rows(): Row[] {
    return [this.row('phone', 'Phone'), this.row('email', 'Email')];
  }

  /** A row; the one they don't have yet is "(optional)", as in the design. */
  row(kind: ContactKind, name: string): Row {
    const label = this.args[kind] === null ? `${name} (optional)` : name;
    const message =
      this.refused?.kind === kind ? this.refused.refusal.message : null;
    return { kind, label, value: this.valueOf(kind), message };
  }

  valueOf(kind: ContactKind): string {
    return this.typed[kind] ?? this.args[kind] ?? '';
  }

  @action type(kind: ContactKind, value: string): void {
    this.typed = { ...this.typed, [kind]: value };
  }

  /** Both exist, so either can go; the last way to log in can't. */
  get canRemove(): boolean {
    return this.args.phone !== null && this.args.email !== null;
  }

  @action
  async remove(kind: ContactKind): Promise<void> {
    await this.args.onRemove(kind);
  }

  @action setCode(value: string): void {
    this.code = value;
  }

  @action
  async submit(kind: ContactKind, event: SubmitEvent): Promise<void> {
    event.preventDefault();
    await this.refusable(kind, () =>
      this.confirming === kind ? this.confirm(kind) : this.sendCode(kind),
    );
  }

  async sendCode(kind: ContactKind): Promise<void> {
    await this.args.onSendCode(this.valueOf(kind));
    this.confirming = kind;
  }

  async confirm(kind: ContactKind): Promise<void> {
    await this.args.onSave(this.valueOf(kind), this.code);
    this.stopConfirming();
    this.typed = { ...this.typed, [kind]: undefined };
  }

  /** Run a step for ``kind``'s row; a refusal shows there, not as a crash. */
  async refusable(kind: ContactKind, step: () => Promise<void>): Promise<void> {
    this.codeError = null;
    this.refused = null;
    try {
      await step();
    } catch (error) {
      this.codeError = codeErrorFrom(error);
      if (this.codeError) return;
      const refusal = refusalFrom(error);
      if (!refusal) throw error;
      this.refused = { kind, refusal };
    }
  }

  @action
  async sendNewCode(): Promise<void> {
    const kind = this.confirming;
    if (kind) await this.refusable(kind, () => this.sendCode(kind));
  }

  @action stopConfirming(): void {
    this.confirming = null;
    this.code = '';
    this.codeError = null;
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
            <CodeField
              @value={{this.code}}
              @onInput={{this.setCode}}
              @invalid={{if this.codeError true false}}
            >
              <Button
                type="submit"
                data-test-contact-save={{row.kind}}
              >Save</Button>
            </CodeField>
            {{#if this.codeError}}
              <CodeErrors
                @error={{this.codeError}}
                @onSendNewCode={{this.sendNewCode}}
                @onUseDifferentContact={{this.stopConfirming}}
              />
            {{/if}}
          {{else}}
            <Button
              type="submit"
              @variant="secondary"
              class="self-start"
              data-test-contact-send-code={{row.kind}}
            >Send code</Button>
          {{/if}}
          {{#if row.message}}
            <FormError data-test-contact-error>{{row.message}}</FormError>
          {{/if}}
          {{#if this.canRemove}}
            <Button
              @variant="danger-link"
              class="self-start"
              data-test-contact-remove={{row.kind}}
              {{on "click" (fn this.remove row.kind)}}
            >Remove</Button>
          {{/if}}
        </form>
      {{/each}}
    </div>
  </template>
}
