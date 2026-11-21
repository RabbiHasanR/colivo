import type { TOC } from '@ember/component/template-only';
import MembersPage from '../../components/members/members-page';
import type { Member } from '../../services/members';

const MembersTemplate: TOC<{ Args: { model: Member[] } }> = <template>
  <MembersPage @members={{@model}} />
</template>;

export default MembersTemplate;
