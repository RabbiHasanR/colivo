import Component from '@glimmer/component';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import Button from '../ui/button';

interface RoleEditorSignature {
  Args: { member: Member; onChanged: (member: Member) => void };
}

/** The owner makes a member a manager, or a manager a member (FR-63). */
export default class RoleEditor extends Component<RoleEditorSignature> {
  @service declare members: MembersService;

  get isManager(): boolean {
    return this.args.member.role === 'manager';
  }

  @action
  async toggle(): Promise<void> {
    const changed = await this.members.changeRole(
      this.args.member.id,
      this.isManager ? 'member' : 'manager',
    );
    this.args.onChanged(changed);
  }

  <template>
    <Button
      @variant="link"
      data-test-role-change={{@member.name}}
      {{on "click" this.toggle}}
    >{{if this.isManager "Remove manager" "Make manager"}}</Button>
  </template>
}
