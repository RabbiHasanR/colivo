import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type ServerStatusService from '../services/server-status';
import type { ServerStatus } from '../services/server-status';

/** The start page (Phase 0): whether the web app can reach the backend. */
export default class IndexRoute extends Route {
  @service declare serverStatus: ServerStatusService;

  model(): Promise<ServerStatus> {
    return this.serverStatus.check();
  }
}
