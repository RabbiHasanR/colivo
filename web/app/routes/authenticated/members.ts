import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type MembersService from '../../services/members';
import type { Member } from '../../services/members';
import type SessionService from '../../services/session';

/** Members & roles, for the owner and managers; anyone else goes home. */
export default class AuthenticatedMembersRoute extends Route {
  @service declare members: MembersService;
  @service declare router: RouterService;
  @service declare session: SessionService;

  beforeModel(): void {
    if (!this.session.isOwnerOrManager) {
      this.router.transitionTo('authenticated.index');
    }
  }

  model(): Promise<Member[]> {
    return this.members.list();
  }
}
