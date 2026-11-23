import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { get } from '@ember/helper';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { ContactKind, Member } from '../../services/members';
import { refusalFrom, type Refusal } from '../../utils/refusal';
import ContactEditor from '../contact/contact-editor';
import Button from '../ui/button';
import DateInput from '../ui/date-input';
import Field from '../ui/field';
import FormError from '../ui/form-error';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';

interface EditMemberFormSignature {
  Args: {
    member: Member;
    onSaved: (member: Member) => void;
    /** Shows a Cancel button that closes the form without saving. */
    onCancel?: () => void;
    /** Their phone or email changed (Phase 1c); the page keeps the tab open. */
    onContactChanged?: (member: Member) => void;
  };
}

interface Draft {
  memberId: string;
  name?: string;
  joinedOn?: string;
}

/** Change a member's name or join date (FR-86), owner and managers only. */
export default class EditMemberForm extends Component<EditMemberFormSignature> {
  @service declare members: MembersService;

  /**
   * What was typed, and for whom. The page reuses this form when Edit is
   * pressed on someone else, so typing for one member never shows for another.
   */
  @tracked typed: Draft | null = null;
  @tracked refusal: Refusal | null = null;

  /** What was typed for the member shown now; nothing if it was for another. */
  get draft(): Draft | null {
    return this.typed?.memberId === this.args.member.id ? this.typed : null;
  }

  get name(): string {
    return this.draft?.name ?? this.args.member.name;
  }

  get joinedOn(): string {
    return this.draft?.joinedOn ?? this.args.member.joined_on ?? '';
  }

  get fieldErrors(): Record<string, string[]> {
    return this.refusal?.fieldErrors ?? {};
  }

  @action setName(value: string): void {
    this.typed = { ...this.draft, memberId: this.args.member.id, name: value };
  }

  @action setJoinedOn(value: string): void {
    this.typed = {
      ...this.draft,
      memberId: this.args.member.id,
      joinedOn: value,
    };
  }

  /** The member, as a list of one: the contact editor starts afresh per member. */
  get shownMember(): Member[] {
    return [this.args.member];
  }

  @action
  async sendContactCode(contact: string): Promise<void> {
    await this.members.sendContactCode(this.args.member.id, contact);
  }

  @action
  async saveContact(contact: string, code: string): Promise<void> {
    const changed = await this.members.setContact(
      this.args.member.id,
      contact,
      code,
    );
    this.args.onContactChanged?.(changed);
  }

  @action
  async removeContact(kind: ContactKind): Promise<void> {
    const changed = await this.members.removeContact(this.args.member.id, kind);
    this.args.onContactChanged?.(changed);
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    this.refusal = null;
    let saved: Member;
    try {
      saved = await this.members.update(this.args.member.id, {
        name: this.name,
        joined_on: this.joinedOn || null,
      });
    } catch (error) {
      this.refusal = refusalFrom(error);
      if (!this.refusal) throw error;
      return;
    }
    this.args.onSaved(saved);
  }

  <template>
    <form data-test-edit-member-form {{on "submit" this.submit}}>
      <Stack>
        <Field
          @label="Name"
          @errors={{get this.fieldErrors "name"}}
          data-test-field="name"
          as |id|
        >
          <TextInput
            id={{id}}
            @value={{this.name}}
            @onInput={{this.setName}}
            data-test-edit-member-name
          />
        </Field>
        <Field
          @label="Joined on"
          @errors={{get this.fieldErrors "joined_on"}}
          data-test-field="joined_on"
          as |id|
        >
          <DateInput
            id={{id}}
            @value={{this.joinedOn}}
            @onInput={{this.setJoinedOn}}
            data-test-edit-member-joined-on
          />
        </Field>
        {{#if this.refusal.message}}
          <FormError data-test-edit-member-error>
            {{this.refusal.message}}
          </FormError>
        {{/if}}
        <div class="flex flex-wrap justify-end gap-2">
          {{#if @onCancel}}
            <Button
              @variant="secondary"
              data-test-edit-member-cancel
              {{on "click" @onCancel}}
            >Cancel</Button>
          {{/if}}
          <Button type="submit" data-test-edit-member-submit>Save</Button>
        </div>
      </Stack>
    </form>
    {{#each this.shownMember key="id" as |shown|}}
      <ContactEditor
        @phone={{shown.phone}}
        @email={{shown.email}}
        @editable={{shown.contact_editable}}
        @onSendCode={{this.sendContactCode}}
        @onSave={{this.saveContact}}
        @onRemove={{this.removeContact}}
      />
    {{/each}}
  </template>
}
