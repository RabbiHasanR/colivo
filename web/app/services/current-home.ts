import Service, { service } from '@ember/service';
import { tracked } from '@glimmer/tracking';
import { getSetup, type Setup } from '../data/builders/home';
import { getMyHomes, type HomeChoice } from '../data/builders/me';
import type Store from './store';

/** Where a tab keeps its chosen home (sessionStorage: this tab only). */
export const TAB_HOME_KEY = 'colivo:home';
/** The last home chosen in this browser, where a new tab starts (localStorage). */
export const LAST_HOME_KEY = 'colivo:last-home';

// For components, which don't import the data layer.
export type { Setup, SetupStep } from '../data/builders/home';
export type { HomeChoice } from '../data/builders/me';

/** Reads a stored home id; storage can be refused (a private window). */
function readHome(storage: () => Storage, key: string): string | null {
  try {
    return storage().getItem(key);
  } catch {
    return null;
  }
}

/** Stores (or, for null, removes) a home id; a refused storage is ignored. */
function writeHome(
  storage: () => Storage,
  key: string,
  homeId: string | null,
): void {
  try {
    if (homeId === null) storage().removeItem(key);
    else storage().setItem(key, homeId);
  } catch {
    // Storage refused (a private window): the home stays for this page only.
  }
}

/**
 * The home this tab acts in (Phase 1b), and that home's setup checklist.
 *
 * Each tab keeps its own home in sessionStorage, so switching in one tab
 * never moves another; a new tab starts from the last home chosen in this
 * browser (localStorage). The data layer sends it as `X-Colivo-Home`.
 */
export default class CurrentHomeService extends Service {
  @service declare store: Store;

  /** The home this tab acts in; null until one is chosen. */
  @tracked homeId: string | null =
    readHome(() => sessionStorage, TAB_HOME_KEY) ??
    readHome(() => localStorage, LAST_HOME_KEY);

  /** Forget the home in this tab and for new tabs (log-out). */
  forget(): void {
    this.homeId = null;
    writeHome(() => sessionStorage, TAB_HOME_KEY, null);
    writeHome(() => localStorage, LAST_HOME_KEY, null);
  }

  /** The logged-in person's homes, to choose one (`GET /me/homes`). */
  async loadHomes(): Promise<HomeChoice[]> {
    const { content } = await this.store.request<HomeChoice[]>(getMyHomes());
    return content;
  }

  /** Act in `homeId` in this tab; new tabs start from it too. */
  choose(homeId: string): void {
    this.homeId = homeId;
    writeHome(() => sessionStorage, TAB_HOME_KEY, homeId);
    writeHome(() => localStorage, LAST_HOME_KEY, homeId);
  }

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
