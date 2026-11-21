import type { TOC } from '@ember/component/template-only';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { Member } from '../../services/members';
import { formatDate } from '../../utils/dates';
import { eq } from '../../utils/template';
import { roleLabel } from '../../utils/roles';
import Button from '../ui/button';
import ScrollBox from '../ui/scroll-box';

interface MemberListSignature {
  Args: {
    members: Member[];
    onEdit?: (member: Member) => void;
    onDeactivate?: (member: Member) => void;
    onReactivate?: (member: Member) => void;
  };
}

/** Members & roles (colivo-design/web/WebMembers.html), one row each. */
const MemberList: TOC<MemberListSignature> = <template>
  <ScrollBox>
    <table data-test-member-list>
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Role</th>
          <th scope="col">Status</th>
          <th scope="col">Joined</th>
          {{#if @onEdit}}<th scope="col"><span
                class="sr-only"
              >Change</span></th>{{/if}}
        </tr>
      </thead>
      <tbody>
        {{#each @members as |member|}}
          <tr data-test-member-row={{member.name}}>
            <th scope="row">{{member.name}}</th>
            <td>{{roleLabel member.role}}</td>
            <td>{{roleLabel member.status}}</td>
            <td>{{formatDate member.joined_on}}</td>
            <td>
              {{#if @onEdit}}
                <Button
                  @variant="secondary"
                  aria-label="Change {{member.name}}"
                  data-test-edit-member={{member.name}}
                  {{on "click" (fn @onEdit member)}}
                >Edit</Button>
              {{/if}}
              {{#if (eq member.status "active")}}
                {{#if @onDeactivate}}
                  <Button
                    @variant="secondary"
                    aria-label="Deactivate {{member.name}}"
                    data-test-deactivate={{member.name}}
                    {{on "click" (fn @onDeactivate member)}}
                  >Deactivate</Button>
                {{/if}}
              {{else if @onReactivate}}
                <Button
                  @variant="secondary"
                  aria-label="Reactivate {{member.name}}"
                  data-test-reactivate={{member.name}}
                  {{on "click" (fn @onReactivate member)}}
                >Reactivate</Button>
              {{/if}}
            </td>
          </tr>
        {{/each}}
      </tbody>
    </table>
  </ScrollBox>
</template>;

export default MemberList;
