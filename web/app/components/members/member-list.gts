import type { TOC } from '@ember/component/template-only';
import type { Member } from '../../services/members';
import { formatDate } from '../../utils/dates';
import { roleLabel } from '../../utils/roles';
import ScrollBox from '../ui/scroll-box';

interface MemberListSignature {
  Args: { members: Member[] };
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
        </tr>
      </thead>
      <tbody>
        {{#each @members as |member|}}
          <tr data-test-member-row={{member.name}}>
            <th scope="row">{{member.name}}</th>
            <td>{{roleLabel member.role}}</td>
            <td>{{roleLabel member.status}}</td>
            <td>{{formatDate member.joined_on}}</td>
          </tr>
        {{/each}}
      </tbody>
    </table>
  </ScrollBox>
</template>;

export default MemberList;
