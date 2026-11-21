import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import AddMemberForm from './add-member-form';
import MemberList from './member-list';

interface MembersPageSignature {
  Args: { members: Member[] };
}

/** Members & roles (colivo-design/web/WebMembers.html). */
export default class MembersPage extends Component<MembersPageSignature> {
  @service declare members: MembersService;

  /** The list read again after a change; until then, the route's. */
  @tracked reloaded: Member[] | null = null;

  get shown(): Member[] {
    return this.reloaded ?? this.args.members;
  }

  @action
  async reload(): Promise<void> {
    this.reloaded = await this.members.list();
  }

  <template>
    <h1>Members &amp; roles</h1>
    <MemberList @members={{this.shown}} />
    <section aria-labelledby="add-member-title">
      <h2 id="add-member-title">Add a member</h2>
      <AddMemberForm @onAdded={{this.reload}} />
    </section>
  </template>
}
