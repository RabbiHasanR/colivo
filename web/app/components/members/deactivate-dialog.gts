import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import { todayIn } from '../../utils/dates';
import { DEFAULT_TIME_ZONE } from '../../utils/months';
import { refusalFrom, type Refusal } from '../../utils/refusal';
import Button from '../ui/button';
import DateInput from '../ui/date-input';
import Dialog from '../ui/dialog';
import Field from '../ui/field';
import FormError from '../ui/form-error';
import Stack from '../ui/stack';

interface DeactivateDialogSignature {
  Args: {
    member: Member;
    /** The current time; tests fix it. */
    now?: Date;
    onDone: (member: Member) => void;
    onCancel: () => void;
  };
}

/**
 * Deactivate a member from a date (FR-92): they can't log in after it, and
 * can be reactivated at any time.
 */
export default class DeactivateDialog extends Component<DeactivateDialogSignature> {
  @service declare members: MembersService;

  @tracked typedOn: string | null = null;
  @tracked refusal: Refusal | null = null;

  get on(): string {
    return (
      this.typedOn ?? todayIn(this.args.now ?? new Date(), DEFAULT_TIME_ZONE)
    );
  }

  @action setOn(value: string): void {
    this.typedOn = value;
  }

  @action
  async confirm(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    this.refusal = null;
    let done: Member;
    try {
      done = await this.members.deactivate(this.args.member.id, this.on);
    } catch (error) {
      this.refusal = refusalFrom(error);
      if (!this.refusal) throw error;
      return;
    }
    this.args.onDone(done);
  }

  <template>
    <Dialog
      @title="Deactivate {{@member.name}}?"
      @onClose={{@onCancel}}
      data-test-deactivate-dialog
    >
      <form {{on "submit" this.confirm}}>
        <Stack>
          <p class="text-sm leading-normal text-muted">They can't log in from
            this date. You can reactivate them at any time.</p>
          <Field @label="From" as |id|>
            <DateInput
              id={{id}}
              @value={{this.on}}
              @onInput={{this.setOn}}
              data-test-deactivate-on
            />
          </Field>
          {{#if this.refusal.message}}
            <FormError>{{this.refusal.message}}</FormError>
          {{/if}}
          <div class="flex flex-wrap justify-end gap-2">
            <Button
              @variant="secondary"
              data-test-deactivate-cancel
              {{on "click" @onCancel}}
            >Cancel</Button>
            <Button
              type="submit"
              data-test-deactivate-confirm
            >Deactivate</Button>
          </div>
        </Stack>
      </form>
    </Dialog>
  </template>
}
