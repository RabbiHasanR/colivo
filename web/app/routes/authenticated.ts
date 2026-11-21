import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../services/session';

/** Every page behind log-in: a visitor who isn't logged in goes to log-in. */
export default class AuthenticatedRoute extends Route {
  @service declare router: RouterService;
  @service declare session: SessionService;

  async beforeModel(): Promise<void> {
    if (!(await this.session.load())) {
      this.router.transitionTo('log-in');
    }
  }
}
