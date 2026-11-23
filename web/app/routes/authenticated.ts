import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type Transition from '@ember/routing/transition';
import type SessionService from '../services/session';

const WELCOME = 'authenticated.welcome';

/**
 * Every page behind log-in: a visitor who isn't logged in goes to log-in,
 * and a tab with no usable home to "Choose a home" (Phase 1b);
 * a member who hasn't checked their details sees the first log-in check
 * first (FR-86).
 */
export default class AuthenticatedRoute extends Route {
  @service declare router: RouterService;
  @service declare session: SessionService;

  async beforeModel(transition: Transition): Promise<void> {
    const me = await this.session.landing();
    if (typeof me === 'string') {
      this.router.transitionTo(me);
      return;
    }
    if (!me.membership.details_checked && transition.to?.name !== WELCOME) {
      this.router.transitionTo(WELCOME);
    }
  }
}
