import Component from '@glimmer/component';
import { service } from '@ember/service';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { Member } from '../../services/members';
import type SessionService from '../../services/session';
import type { Me } from '../../services/session';
import { formatDate } from '../../utils/dates';
import { canChangeStatus, canEditDetails } from '../../utils/members';
import { eq } from '../../utils/template';
import { roleLabel } from '../../utils/roles';
import Avatar from '../ui/avatar';
import Button from '../ui/button';
import Tag, { type TagTone } from '../ui/tag';
import ScrollBox from '../ui/scroll-box';
import RoleEditor from './role-editor';

const HEAD =
  'px-3.5 py-2.5 text-left text-xs font-medium whitespace-nowrap text-muted';
const CELL = 'px-3.5 py-[11px] text-left whitespace-nowrap';

/** Each role's pill colour, as in colivo-design/web/WebMembers.html. */
const ROLE_TONES: Record<string, TagTone> = {
  owner: 'dark',
  manager: 'blue',
  member: 'teal',
};

function roleTone(role: string): TagTone {
  return ROLE_TONES[role] ?? 'grey';
}

interface MemberListSignature {
  Args: {
    members: Member[];
    onEdit?: (member: Member) => void;
    onDeactivate?: (member: Member) => void;
    onReactivate?: (member: Member) => void;
    onRoleChanged?: (member: Member) => void;
  };
}

/** Members & roles (colivo-design/web/WebMembers.html), one row each. */
export default class MemberList extends Component<MemberListSignature> {
  @service declare session: SessionService;

  /** Who is looking at the list: what they may do depends on their role. */
  get viewer(): Member | Me['membership'] | null {
    return this.session.me?.membership ?? null;
  }

  <template>
    <ScrollBox>
      <table
        class="w-full border-collapse text-sm tabular-nums"
        data-test-member-list
      >
        <thead>
          <tr>
            <th scope="col" class={{HEAD}}>Name</th>
            <th scope="col" class={{HEAD}}>Role</th>
            <th scope="col" class={{HEAD}}>Status</th>
            <th scope="col" class={{HEAD}}>Joined</th>
            <th scope="col" class="{{HEAD}} text-right"><span
                class="sr-only"
              >Actions</span></th>
          </tr>
        </thead>
        <tbody>
          {{#each @members as |member|}}
            <tr
              class="border-t border-divider"
              data-test-member-row={{member.name}}
            >
              <th scope="row" class="{{CELL}} font-medium">
                <span class="inline-flex items-center gap-2.5">
                  <Avatar
                    @name={{member.name}}
                    @faded={{eq member.status "inactive"}}
                  />
                  {{member.name}}
                </span>
              </th>
              <td class={{CELL}}><Tag @tone={{roleTone member.role}}>{{roleLabel
                    member.role
                  }}</Tag></td>
              <td class={{CELL}}><Tag
                  @tone={{if (eq member.status "active") "teal" "grey"}}
                >{{roleLabel member.status}}</Tag></td>
              <td class={{CELL}}>{{formatDate member.joined_on}}</td>
              <td class="{{CELL}} text-right"><span
                  class="inline-flex justify-end gap-x-2"
                >
                  {{#if @onRoleChanged}}
                    {{! The owner's own role never changes (FR-63). }}
                    {{#if this.session.isOwner}}
                      {{#unless (eq member.role "owner")}}
                        <RoleEditor
                          @member={{member}}
                          @onChanged={{@onRoleChanged}}
                        />
                      {{/unless}}
                    {{/if}}
                  {{/if}}
                  {{#if @onEdit}}
                    {{#if (canEditDetails this.viewer member)}}
                      <Button
                        @variant="link"
                        aria-label="Change {{member.name}}"
                        data-test-edit-member={{member.name}}
                        {{on "click" (fn @onEdit member)}}
                      >Edit</Button>
                    {{/if}}
                  {{/if}}
                  {{#if (eq member.status "active")}}
                    {{#if @onDeactivate}}
                      {{#if (canChangeStatus this.viewer member)}}
                        <Button
                          @variant="danger-link"
                          aria-label="Deactivate {{member.name}}"
                          data-test-deactivate={{member.name}}
                          {{on "click" (fn @onDeactivate member)}}
                        >Deactivate</Button>
                      {{/if}}
                    {{/if}}
                  {{else if @onReactivate}}
                    {{#if (canChangeStatus this.viewer member)}}
                      <Button
                        @variant="link"
                        aria-label="Reactivate {{member.name}}"
                        data-test-reactivate={{member.name}}
                        {{on "click" (fn @onReactivate member)}}
                      >Reactivate</Button>
                    {{/if}}
                  {{/if}}
                </span></td>
            </tr>
          {{/each}}
        </tbody>
      </table>
    </ScrollBox>
  </template>
}
