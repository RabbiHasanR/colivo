import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { Member } from '../../services/members';
import { eq } from '../../utils/template';
import Button from '../ui/button';
import MemberList from './member-list';

type Tab = 'current' | 'past';

interface MemberTabsSignature {
  Args: {
    members: Member[];
    onEdit?: (member: Member) => void;
    onDeactivate?: (member: Member) => void;
    onReactivate?: (member: Member) => void;
  };
}

/** Current and Past members (colivo-design/web/WebMembers.html), one list each. */
export default class MemberTabs extends Component<MemberTabsSignature> {
  @tracked tab: Tab = 'current';

  get shown(): Member[] {
    const status = this.tab === 'current' ? 'active' : 'inactive';
    return this.args.members.filter((member) => member.status === status);
  }

  get currentCount(): number {
    return this.args.members.filter((member) => member.status === 'active')
      .length;
  }

  get pastCount(): number {
    return this.args.members.length - this.currentCount;
  }

  @action
  show(tab: Tab): void {
    this.tab = tab;
  }

  <template>
    <section data-test-member-tabs>
      <div role="group" aria-label="Which members">
        <Button
          @variant={{if (eq this.tab "current") "primary" "secondary"}}
          aria-pressed={{if (eq this.tab "current") "true" "false"}}
          data-test-tab="current"
          {{on "click" (fn this.show "current")}}
        >Current ({{this.currentCount}})</Button>
        <Button
          @variant={{if (eq this.tab "past") "primary" "secondary"}}
          aria-pressed={{if (eq this.tab "past") "true" "false"}}
          data-test-tab="past"
          {{on "click" (fn this.show "past")}}
        >Past ({{this.pastCount}})</Button>
      </div>
      <MemberList
        @members={{this.shown}}
        @onEdit={{@onEdit}}
        @onDeactivate={{@onDeactivate}}
        @onReactivate={{@onReactivate}}
      />
    </section>
  </template>
}
