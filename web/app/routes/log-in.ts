import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../services/session';

/** Log in or create a home; someone already logged in goes home. */
export default class LogInRoute extends Route {
  @service declare router: RouterService;
  @service declare session: SessionService;

  async beforeModel(): Promise<void> {
    if (await this.session.load()) {
      this.router.transitionTo('authenticated.index');
    }
  }
}
