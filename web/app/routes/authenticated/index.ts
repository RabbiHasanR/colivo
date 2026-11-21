import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type CurrentHomeService from '../../services/current-home';
import type { Setup } from '../../services/current-home';
import type SessionService from '../../services/session';
import type { Me } from '../../services/session';

export interface HomeModel {
  me: Me;
  /** The setup checklist; only the owner and managers get one. */
  setup: Setup | null;
}

/** The home page. */
export default class AuthenticatedIndexRoute extends Route {
  @service declare session: SessionService;
  @service declare currentHome: CurrentHomeService;

  async model(): Promise<HomeModel> {
    const me = this.session.me as Me;
    const setup = this.session.isOwnerOrManager
      ? await this.currentHome.loadSetup()
      : null;
    return { me, setup };
  }
}
