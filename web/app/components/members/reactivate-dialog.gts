import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import { refusalFrom, type Refusal } from '../../utils/refusal';
import Button from '../ui/button';
import DateInput from '../ui/date-input';
import Dialog from '../ui/dialog';
import Field from '../ui/field';
import FormError from '../ui/form-error';
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
  @tracked refusal: Refusal | null = null;

  @action setOn(value: string): void {
    this.on = value;
  }

  @action
  async confirm(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    this.refusal = null;
    let back: Member;
    try {
      back = await this.members.reactivate(this.args.member.id, this.on);
    } catch (error) {
      this.refusal = refusalFrom(error);
      if (!this.refusal) throw error;
      return;
    }
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
          <p class="text-sm leading-normal text-muted">They can log in again.
            Their charges start again from:</p>
          <Field @label="Charges start again on" as |id|>
            <DateInput
              id={{id}}
              required
              @value={{this.on}}
              @onInput={{this.setOn}}
              data-test-reactivate-on
            />
          </Field>
          {{#if this.refusal.message}}
            <FormError data-test-reactivate-error>
              {{this.refusal.message}}
            </FormError>
          {{/if}}
          <div class="flex flex-wrap justify-end gap-2">
            <Button
              @variant="secondary"
              data-test-reactivate-cancel
              {{on "click" @onCancel}}
            >Cancel</Button>
            <Button
              type="submit"
              data-test-reactivate-confirm
            >Reactivate</Button>
          </div>
        </Stack>
      </form>
    </Dialog>
  </template>
}
