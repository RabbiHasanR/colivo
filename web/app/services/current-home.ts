import Service, { service } from '@ember/service';
import { getSetup, type Setup } from '../data/builders/home';
import type Store from './store';

/** Where a tab keeps its chosen home (sessionStorage: this tab only). */
export const TAB_HOME_KEY = 'colivo:home';
/** The last home chosen in this browser, where a new tab starts (localStorage). */
export const LAST_HOME_KEY = 'colivo:last-home';

// For components, which don't import the data layer.
export type { Setup, SetupStep } from '../data/builders/home';

/** The logged-in member's home: its setup checklist. */
export default class CurrentHomeService extends Service {
  @service declare store: Store;

  /** The setup checklist (owner and managers only; members get 403). */
  async loadSetup(): Promise<Setup> {
    const { content } = await this.store.request<Setup>(getSetup());
    return content;
  }
}

declare module '@ember/service' {
  interface Registry {
    'current-home': CurrentHomeService;
  }
}
