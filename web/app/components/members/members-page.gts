import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import AddMemberForm from './add-member-form';
import DeactivateDialog from './deactivate-dialog';
import EditMemberForm from './edit-member-form';
import MemberTabs from './member-tabs';

interface MembersPageSignature {
  Args: { members: Member[] };
}

/** Members & roles (colivo-design/web/WebMembers.html). */
export default class MembersPage extends Component<MembersPageSignature> {
  @service declare members: MembersService;

  /** The list read again after a change; until then, the route's. */
  @tracked reloaded: Member[] | null = null;
  /** The member whose details are being changed, if any. */
  @tracked editing: Member | null = null;
  /** The member being deactivated (the dialog is open), if any. */
  @tracked deactivating: Member | null = null;

  get shown(): Member[] {
    return this.reloaded ?? this.args.members;
  }

  @action
  async reload(): Promise<void> {
    this.editing = null;
    this.deactivating = null;
    this.reloaded = await this.members.list();
  }

  @action
  askToDeactivate(member: Member): void {
    this.deactivating = member;
  }

  @action
  closeDialogs(): void {
    this.deactivating = null;
  }

  @action
  edit(member: Member): void {
    this.editing = member;
  }

  <template>
    <h1>Members &amp; roles</h1>
    <MemberTabs
      @members={{this.shown}}
      @onEdit={{this.edit}}
      @onDeactivate={{this.askToDeactivate}}
    />
    {{#if this.deactivating}}
      <DeactivateDialog
        @member={{this.deactivating}}
        @onDone={{this.reload}}
        @onCancel={{this.closeDialogs}}
      />
    {{/if}}
    {{#if this.editing}}
      <section aria-labelledby="edit-member-title">
        <h2 id="edit-member-title">Change {{this.editing.name}}</h2>
        <EditMemberForm @member={{this.editing}} @onSaved={{this.reload}} />
      </section>
    {{/if}}
    <section aria-labelledby="add-member-title">
      <h2 id="add-member-title">Add a member</h2>
      <AddMemberForm @onAdded={{this.reload}} />
    </section>
  </template>
}
