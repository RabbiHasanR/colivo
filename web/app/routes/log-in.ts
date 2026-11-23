import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../services/session';

/**
 * Log in or create a home; someone already logged in goes home, or to
 * "Choose a home" when the tab has none of theirs yet.
 */
export default class LogInRoute extends Route {
  @service declare router: RouterService;
  @service declare session: SessionService;

  async beforeModel(): Promise<void> {
    const me = await this.session.landing();
    if (me === 'choose-home') this.router.transitionTo('choose-home');
    else if (me !== 'log-in') this.router.transitionTo('authenticated.index');
  }
}
