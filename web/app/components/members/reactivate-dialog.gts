import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import Button from '../ui/button';
import DateInput from '../ui/date-input';
import Dialog from '../ui/dialog';
import Field from '../ui/field';
import Stack from '../ui/stack';

interface ReactivateDialogSignature {
  Args: {
    member: Member;
    onDone: (member: Member) => void;
    onCancel: () => void;
  };
}

/** Reactivate a member from the date charges start again (FR-92). */
export default class ReactivateDialog extends Component<ReactivateDialogSignature> {
  @service declare members: MembersService;

  @tracked on = '';

  @action setOn(value: string): void {
    this.on = value;
  }

  @action
  async confirm(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    const back = await this.members.reactivate(this.args.member.id, this.on);
    this.args.onDone(back);
  }

  <template>
    <Dialog
      @title="Reactivate {{@member.name}}?"
      @onClose={{@onCancel}}
      data-test-reactivate-dialog
    >
      <form {{on "submit" this.confirm}}>
        <Stack>
          <p>They can log in again. Their charges start again from:</p>
          <Field @label="Charges start again on" as |id|>
            <DateInput
              id={{id}}
              required
              @value={{this.on}}
              @onInput={{this.setOn}}
              data-test-reactivate-on
            />
          </Field>
          <Button type="submit" data-test-reactivate-confirm>Reactivate</Button>
          <Button
            @variant="secondary"
            data-test-reactivate-cancel
            {{on "click" @onCancel}}
          >Cancel</Button>
        </Stack>
      </form>
    </Dialog>
  </template>
}
