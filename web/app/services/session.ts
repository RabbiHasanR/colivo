import Service, { service } from '@ember/service';
import { tracked } from '@glimmer/tracking';
import {
  logIn,
  logOut,
  requestCode,
  signUp,
  type CodeSent,
  type LogInAnswer,
  type SignUpFields,
} from '../data/builders/auth';
import { getMe, updateMe, type Me } from '../data/builders/me';
import { ApiError, refusalReason } from '../utils/api-error';

// For components, which don't import the data layer.
export type { Me, Role } from '../data/builders/me';
import type RouterService from '@ember/routing/router-service';
import type Store from './store';
import type CurrentHomeService from './current-home';

/**
 * Who is logged in. The log-in itself is an httpOnly cookie the browser
 * keeps; this service only knows what `GET /me` and sign-up said.
 */
export default class SessionService extends Service {
  @service declare store: Store;
  @service declare router: RouterService;
  @service declare currentHome: CurrentHomeService;

  @tracked me: Me | null = null;

  /** Whether the logged-in person is the home's owner. */
  get isOwner(): boolean {
    return this.me?.membership.role === 'owner';
  }

  /** Whether the logged-in person runs the home: the owner or a manager. */
  get isOwnerOrManager(): boolean {
    const role = this.me?.membership.role;
    return role === 'owner' || role === 'manager';
  }

  /**
   * Who is logged in, in this tab's home: asks `GET /me` once, then
   * remembers. When there is nobody to show, says where to go instead:
   * `log-in` when nobody is logged in (401); `choose-home` when the tab
   * names no home of theirs and they have several (409 choose_home), or
   * names one they're no longer in (403 not_in_home), Phase 1b.
   */
  async landing(): Promise<Me | 'log-in' | 'choose-home'> {
    if (this.me) return this.me;
    try {
      const { content } = await this.store.request<Me>(getMe());
      this.me = content;
      return content;
    } catch (error) {
      if (error instanceof ApiError && error.kind === 'unauthorized') {
        return 'log-in';
      }
      if (refusalReason(error)) return 'choose-home';
      throw error;
    }
  }

  /**
   * Open `homeId` in this tab, from "Choose a home" or the home switcher:
   * who they are there is read again, and its home page opens. The
   * `authenticated` route is refreshed so its guard runs for the new home
   * even when the tab was already inside it.
   */
  async openHome(homeId: string): Promise<void> {
    this.currentHome.choose(homeId);
    this.currentHome.leftHomeName = null;
    this.me = null;
    await this.router.transitionTo('authenticated.index');
    await this.router.refresh('authenticated');
  }

  async requestCode(contact: string): Promise<CodeSent> {
    const { content } = await this.store.request<CodeSent>(
      requestCode(contact),
    );
    return content;
  }

  /** Create a home; this tab then acts in it, even for someone in others. */
  async signUp(fields: SignUpFields): Promise<Me> {
    const { content } = await this.store.request<Me>(signUp(fields));
    this.currentHome.choose(content.home.id);
    this.me = content;
    return content;
  }

  /** Fix your own name and finish the first log-in check (FR-86). */
  async updateMe(name: string): Promise<Me> {
    const { content } = await this.store.request<Me>(updateMe(name));
    this.me = content;
    return content;
  }

  /**
   * Log in with a one-time code; the API sets the session cookie. A person
   * in one home acts in it at once; with several, they choose (Phase 1b).
   */
  async logIn(contact: string, code: string): Promise<LogInAnswer> {
    const { content } = await this.store.request<LogInAnswer>(
      logIn(contact, code),
    );
    if (content.me) {
      this.currentHome.choose(content.me.home.id);
      this.me = content.me;
    } else {
      // Several homes: they choose; never a home remembered from before.
      this.currentHome.forget();
    }
    return content;
  }

  /**
   * The session ended without a log-out here (a 401): forget who it was and
   * go to log-in. Nothing happens when nobody was logged in.
   */
  expire(): void {
    if (!this.me) return;
    this.me = null;
    this.router.transitionTo('log-in');
  }

  /**
   * A request was refused (403). Removed from this tab's home while still in
   * others (`not_in_home`): go to "Choose a home", saying which home they
   * left (Phase 1b). Otherwise their role may have changed: check it.
   */
  async forbidden(error: ApiError): Promise<void> {
    if (refusalReason(error) === 'not_in_home') {
      this.leftHome();
      return;
    }
    await this.recheckRole();
  }

  /** This tab's home removed them: "Choose a home" says so. */
  leftHome(): void {
    if (!this.me) return;
    this.currentHome.leftHomeName = this.me.home.name;
    this.me = null;
    this.router.transitionTo('choose-home');
  }

  /**
   * A request was refused (403): the owner may have changed this person's
   * role meanwhile. Ask `GET /me` again; if the role changed, re-run the
   * current page's access check, which sends them home from a page they may
   * no longer open (Members for a former manager).
   */
  async recheckRole(): Promise<void> {
    const before = this.me?.membership.role;
    if (!before) return;
    const { content } = await this.store.request<Me>(getMe());
    this.me = content;
    if (content.membership.role !== before) {
      this.router.refresh();
    }
  }

  /**
   * End the session in the API (it clears the cookie) and forget who it was,
   * and the home: the next log-in starts from its own answer.
   */
  async logOut(): Promise<void> {
    await this.store.request(logOut());
    this.me = null;
    this.currentHome.forget();
  }
}

declare module '@ember/service' {
  interface Registry {
    session: SessionService;
  }
}
