import Service, { service } from '@ember/service';
import { ApiError } from '../data/handlers/errors';
import { healthCheck } from '../data/builders/health';
import type Store from './store';

export type Dependency = 'database' | 'redis';

/** What the start page shows about the backend. */
export type ServerStatus =
  | { kind: 'connected' }
  | { kind: 'degraded'; down: Dependency[] }
  | { kind: 'unreachable' };

type Health = Record<Dependency, 'ok' | 'down'>;

const DEPENDENCIES: Dependency[] = ['database', 'redis'];

function isHealth(data: unknown): data is Health {
  return data !== null && typeof data === 'object' && 'database' in data;
}

/** Asks the backend's health check whether the server and its parts are up. */
export default class ServerStatusService extends Service {
  @service declare store: Store;

  async check(): Promise<ServerStatus> {
    try {
      await this.store.request(healthCheck());
      return { kind: 'connected' };
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 503 &&
        isHealth(error.data)
      ) {
        const health = error.data;
        return {
          kind: 'degraded',
          down: DEPENDENCIES.filter((part) => health[part] === 'down'),
        };
      }
      if (error instanceof ApiError && error.kind === 'network') {
        return { kind: 'unreachable' };
      }
      throw error;
    }
  }
}

declare module '@ember/service' {
  interface Registry {
    'server-status': ServerStatusService;
  }
}
