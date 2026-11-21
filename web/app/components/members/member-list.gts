import type { TOC } from '@ember/component/template-only';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { Member } from '../../services/members';
import { formatDate } from '../../utils/dates';
import { roleLabel } from '../../utils/roles';
import Button from '../ui/button';
import ScrollBox from '../ui/scroll-box';

interface MemberListSignature {
  Args: { members: Member[]; onEdit?: (member: Member) => void };
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
            {{#if @onEdit}}
              <td>
                <Button
                  @variant="secondary"
                  aria-label="Change {{member.name}}"
                  data-test-edit-member={{member.name}}
                  {{on "click" (fn @onEdit member)}}
                >Edit</Button>
              </td>
            {{/if}}
          </tr>
        {{/each}}
      </tbody>
    </table>
  </ScrollBox>
</template>;

export default MemberList;
