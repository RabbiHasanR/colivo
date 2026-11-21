import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';

/** Members & roles, for the owner and managers. */
export default class AuthenticatedMembersRoute extends Route {
  @service declare members: MembersService;

  model(): Promise<Member[]> {
    return this.members.list();
  }
}
