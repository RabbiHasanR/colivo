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
  Element: HTMLDivElement;
  Args: {
    phone: string | null;
    email: string | null;
    editable: boolean;
    /** Why they can't be changed here, shown when not ``editable``. */
    note?: string;
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
  /** "Phone" or "Email", as shown when nothing can be typed. */
  name: string;
  /** The field's label: "(optional)" on the one they don't have yet. */
  label: string;
  value: string;
  /** Why the API refused this row, other than its code. */
  message: string | null;
  /** What was wrong with the phone or email typed (422). */
  errors: string[];
  /** Something new was typed, so a code can be sent to it. */
  changed: boolean;
  /** The design's hint in an empty field. */
  placeholder: string;
}

// The placeholders colivo-design uses (WebMembers.html, WebProfile.html).
const PLACEHOLDERS: Record<ContactKind, string> = {
  phone: '01XXXXXXXXX',
  email: 'name@email.com',
};

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

  /** The rows to change, only when this page may change them. */
  get editableRows(): Row[] {
    return this.args.editable ? this.rows : [];
  }

  /** A row; the one they don't have yet is "(optional)", as in the design. */
  row(kind: ContactKind, name: string): Row {
    const label = this.args[kind] === null ? `${name} (optional)` : name;
    const refusal = this.refused?.kind === kind ? this.refused.refusal : null;
    const message = refusal?.message ?? null;
    const errors = refusal?.fieldErrors['contact'] ?? [];
    const value = this.valueOf(kind);
    const changed = value.trim() !== '' && value !== (this.args[kind] ?? '');
    const placeholder = PLACEHOLDERS[kind];
    return { kind, name, label, value, message, errors, changed, placeholder };
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
    <div class="flex flex-col gap-3" data-test-contact-editor ...attributes>
      {{#unless @editable}}
        <dl class="flex flex-col gap-2 text-sm">
          {{#each this.rows key="kind" as |row|}}
            <div class="flex flex-col gap-0.5">
              <dt class="text-xs text-muted">{{row.name}}</dt>
              <dd class="break-words" data-test-contact-value={{row.kind}}>{{if
                  row.value
                  row.value
                  "—"
                }}</dd>
            </div>
          {{/each}}
        </dl>
        {{#if @note}}
          <p class="text-xs text-muted" data-test-contact-note>{{@note}}</p>
        {{/if}}
      {{/unless}}
      {{#each this.editableRows key="kind" as |row|}}
        <form
          class="flex flex-col gap-2"
          data-test-contact-row={{row.kind}}
          {{on "submit" (fn this.submit row.kind)}}
        >
          <Field @label={{row.label}} @errors={{row.errors}} as |id|>
            <TextInput
              id={{id}}
              @value={{row.value}}
              @onInput={{fn this.type row.kind}}
              placeholder={{row.placeholder}}
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
          {{else if row.changed}}
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
