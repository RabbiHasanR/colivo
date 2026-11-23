import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type SessionService from '../../services/session';
import type { Member } from '../../services/members';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';
import Card from '../ui/card';
import { SEGMENT_TRACK, segmentClasses } from '../ui/segment-classes';
import AddMemberForm from './add-member-form';
import DeactivateDialog from './deactivate-dialog';
import EditMemberForm from './edit-member-form';
import MemberTabs from './member-tabs';
import ReactivateDialog from './reactivate-dialog';

interface MembersPageSignature {
  Args: { members: Member[] };
}

/** Members & roles (colivo-design/web/WebMembers.html). */
export default class MembersPage extends Component<MembersPageSignature> {
  @service declare members: MembersService;
  @service declare session: SessionService;

  /** The list read again after a change; until then, the route's. */
  @tracked reloaded: Member[] | null = null;
  /** The member whose details are being changed, if any. */
  @tracked editing: Member | null = null;
  /** While editing, which tab of the add-or-edit card is open. */
  @tracked formTab: 'add' | 'edit' = 'add';
  /** The member being deactivated (the dialog is open), if any. */
  @tracked deactivating: Member | null = null;
  /** The member being reactivated (the dialog is open), if any. */
  @tracked reactivating: Member | null = null;

  get shown(): Member[] {
    return this.reloaded ?? this.args.members;
  }

  @action
  async reload(): Promise<void> {
    this.editing = null;
    this.deactivating = null;
    this.reactivating = null;
    this.formTab = 'add';
    this.reloaded = await this.members.list();
  }

  @action
  askToDeactivate(member: Member): void {
    this.deactivating = member;
  }

  @action
  askToReactivate(member: Member): void {
    this.reactivating = member;
  }

  @action
  closeDialogs(): void {
    this.deactivating = null;
    this.reactivating = null;
  }

  @action
  edit(member: Member): void {
    this.editing = member;
    this.formTab = 'edit';
  }

  @action
  showFormTab(tab: 'add' | 'edit'): void {
    this.formTab = tab;
  }

  /** The member whose edit form is showing: being edited, on the Edit tab. */
  get shownForEdit(): Member | null {
    return this.formTab === 'edit' ? this.editing : null;
  }

  /** A contact change keeps the Edit tab open on the changed member. */
  @action
  async contactChanged(member: Member): Promise<void> {
    this.reloaded = await this.members.list();
    this.editing =
      this.reloaded.find((each) => each.id === member.id) ?? member;
  }

  @action
  cancelEdit(): void {
    this.editing = null;
    this.formTab = 'add';
  }

  <template>
    <header class="flex flex-col gap-1">
      <p class="text-[13px] text-muted">{{if
          this.session.isOwner
          "You're the owner"
          "You're a manager"
        }}</p>
      <h1 class="text-3xl font-semibold">Members &amp; roles</h1>
    </header>
    <div class="flex flex-wrap items-start gap-4">
      <div class="flex min-w-0 flex-[999_1_640px] flex-col gap-4">
        <MemberTabs
          @members={{this.shown}}
          @onEdit={{this.edit}}
          @onDeactivate={{this.askToDeactivate}}
          @onReactivate={{this.askToReactivate}}
          @onRoleChanged={{this.reload}}
        />
      </div>
      <div class="flex min-w-0 flex-[1_1_340px] flex-col gap-4">
        <Card
          class="flex flex-col gap-3 p-4"
          aria-labelledby="member-form-title"
        >
          {{#if this.editing}}
            <div
              role="tablist"
              aria-label="Add or edit a member"
              class="{{SEGMENT_TRACK}} grid grid-cols-2"
            >
              <button
                type="button"
                role="tab"
                aria-selected={{if this.shownForEdit "false" "true"}}
                class={{segmentClasses (eq this.formTab "add")}}
                data-test-member-form-tab="add"
                {{on "click" (fn this.showFormTab "add")}}
              >Add member</button>
              <button
                type="button"
                role="tab"
                aria-selected={{if this.shownForEdit "true" "false"}}
                class={{segmentClasses (eq this.formTab "edit")}}
                data-test-member-form-tab="edit"
                {{on "click" (fn this.showFormTab "edit")}}
              >Edit {{this.editing.name}}</button>
            </div>
          {{/if}}
          {{#if this.shownForEdit}}
            <h2 id="member-form-title" class="sr-only">Edit
              {{this.shownForEdit.name}}</h2>
            <EditMemberForm
              @member={{this.shownForEdit}}
              @onSaved={{this.reload}}
              @onCancel={{this.cancelEdit}}
              @onContactChanged={{this.contactChanged}}
            />
          {{else}}
            <h2
              id="member-form-title"
              class="font-sans text-base font-semibold"
            >Add a member</h2>
            <AddMemberForm @onAdded={{this.reload}} />
          {{/if}}
        </Card>
      </div>
    </div>
    {{#if this.deactivating}}
      <DeactivateDialog
        @member={{this.deactivating}}
        @onDone={{this.reload}}
        @onCancel={{this.closeDialogs}}
      />
    {{/if}}
    {{#if this.reactivating}}
      <ReactivateDialog
        @member={{this.reactivating}}
        @onDone={{this.reload}}
        @onCancel={{this.closeDialogs}}
      />
    {{/if}}
  </template>
}
