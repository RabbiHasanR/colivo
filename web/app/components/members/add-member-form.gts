import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type SessionService from '../../services/session';
import type { Member } from '../../services/members';
import Button from '../ui/button';
import DateInput from '../ui/date-input';
import Field from '../ui/field';
import Select from '../ui/select';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';

interface AddMemberFormSignature {
  Args: { onAdded: (member: Member) => void };
}

type NewRole = 'member' | 'manager';

const ROLE_CHOICES: Array<{ value: NewRole; label: string }> = [
  { value: 'member', label: 'Member' },
  { value: 'manager', label: 'Manager' },
];

/**
 * "Add a member" from colivo-design/web/WebMembers.html: they get an SMS or
 * email so they can log in (FR-79).
 */
export default class AddMemberForm extends Component<AddMemberFormSignature> {
  @service declare members: MembersService;
  @service declare session: SessionService;

  /** Only the owner makes managers (FR-64); a manager adds members only. */
  get roleChoices(): typeof ROLE_CHOICES {
    return this.session.isOwner
      ? ROLE_CHOICES
      : ROLE_CHOICES.filter((choice) => choice.value === 'member');
  }

  @tracked name = '';
  @tracked contact = '';
  @tracked joinedOn = '';
  @tracked role: NewRole = 'member';

  @action setName(value: string): void {
    this.name = value;
  }

  @action setContact(value: string): void {
    this.contact = value;
  }

  @action setJoinedOn(value: string): void {
    this.joinedOn = value;
  }

  @action setRole(value: string): void {
    this.role = value as NewRole;
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const added = await this.members.add({
      name: this.name,
      contact: this.contact,
      joined_on: this.joinedOn,
      role: this.role,
    });
    this.args.onAdded(added);
  }

  <template>
    <form data-test-add-member-form {{on "submit" this.submit}}>
      <Stack>
        <Field @label="Name" data-test-field="name" as |id|>
          <TextInput
            id={{id}}
            @value={{this.name}}
            @onInput={{this.setName}}
            data-test-add-member-name
          />
        </Field>
        <Field @label="Phone or email" data-test-field="contact" as |id|>
          <TextInput
            id={{id}}
            @value={{this.contact}}
            @onInput={{this.setContact}}
            data-test-add-member-contact
          />
        </Field>
        <Field @label="Joins on" data-test-field="joined_on" as |id|>
          <DateInput
            id={{id}}
            @value={{this.joinedOn}}
            @onInput={{this.setJoinedOn}}
            data-test-add-member-joined-on
          />
        </Field>
        <Field @label="Role" as |id|>
          <Select
            id={{id}}
            @options={{this.roleChoices}}
            @value={{this.role}}
            @onChange={{this.setRole}}
            data-test-add-member-role
          />
        </Field>
        <Button type="submit" data-test-add-member-submit>Add member</Button>
      </Stack>
    </form>
  </template>
}
