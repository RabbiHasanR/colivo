import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { Member } from '../../services/members';
import { eq } from '../../utils/template';
import Card from '../ui/card';
import { SEGMENT_TRACK, segmentClasses } from '../ui/segment-classes';
import MemberList from './member-list';

type Tab = 'current' | 'past';

interface MemberTabsSignature {
  Args: {
    members: Member[];
    onEdit?: (member: Member) => void;
    onDeactivate?: (member: Member) => void;
    onReactivate?: (member: Member) => void;
    onRoleChanged?: (member: Member) => void;
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
    <section class="flex flex-col gap-4" data-test-member-tabs>
      <div role="group" aria-label="Which members" class={{SEGMENT_TRACK}}>
        <button
          type="button"
          class={{segmentClasses (eq this.tab "current")}}
          aria-pressed={{if (eq this.tab "current") "true" "false"}}
          data-test-tab="current"
          {{on "click" (fn this.show "current")}}
        >Current ({{this.currentCount}})</button>
        <button
          type="button"
          class={{segmentClasses (eq this.tab "past")}}
          aria-pressed={{if (eq this.tab "past") "true" "false"}}
          data-test-tab="past"
          {{on "click" (fn this.show "past")}}
        >Past ({{this.pastCount}})</button>
      </div>
      <Card class="flex min-w-0 flex-col">
        <h2 class="px-4 pt-3.5 pb-1.5 font-sans text-base font-semibold">
          {{if (eq this.tab "current") "Current members" "Past members"}}
        </h2>
        <MemberList
          @members={{this.shown}}
          @onEdit={{@onEdit}}
          @onDeactivate={{@onDeactivate}}
          @onReactivate={{@onReactivate}}
          @onRoleChanged={{@onRoleChanged}}
        />
      </Card>
    </section>
  </template>
}
