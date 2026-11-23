import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type SessionService from '../../services/session';
import type { Me } from '../../services/session';

/**
 * My profile: anyone logged in. It reads who they are again each time it
 * opens, so a phone or email changed elsewhere (Members, another browser)
 * shows at once.
 */
export default class AuthenticatedProfileRoute extends Route {
  @service declare session: SessionService;

  model(): Promise<Me> {
    return this.session.reloadMe();
  }
}
