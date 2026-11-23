import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type CurrentHomeService from '../services/current-home';
import type { HomeChoice } from '../services/current-home';
import { ApiError } from '../utils/api-error';

/**
 * "Choose a home" (Phase 1b), outside `authenticated`: its guard would send
 * a tab with no home back here. Nobody logged in (401) goes to log-in.
 */
export default class ChooseHomeRoute extends Route {
  @service declare router: RouterService;
  @service declare currentHome: CurrentHomeService;

  async model(): Promise<HomeChoice[]> {
    try {
      return await this.currentHome.loadHomes();
    } catch (error) {
      if (error instanceof ApiError && error.kind === 'unauthorized') {
        this.router.transitionTo('log-in');
        return [];
      }
      throw error;
    }
  }
}
