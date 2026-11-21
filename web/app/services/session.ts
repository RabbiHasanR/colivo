import Service, { service } from '@ember/service';
import { tracked } from '@glimmer/tracking';
import {
  logIn,
  logOut,
  requestCode,
  signUp,
  type CodeSent,
  type SignUpFields,
} from '../data/builders/auth';
import { getMe, type Me } from '../data/builders/me';
import { ApiError } from '../utils/api-error';

// For components, which don't import the data layer.
export type { Me, Role } from '../data/builders/me';
import type Store from './store';

/**
 * Who is logged in. The log-in itself is an httpOnly cookie the browser
 * keeps; this service only knows what `GET /me` and sign-up said.
 */
export default class SessionService extends Service {
  @service declare store: Store;

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
   * Who is logged in: asks `GET /me` once, then remembers. Null when nobody
   * is (401).
   */
  async load(): Promise<Me | null> {
    if (this.me) return this.me;
    try {
      const { content } = await this.store.request<Me>(getMe());
      this.me = content;
    } catch (error) {
      if (error instanceof ApiError && error.kind === 'unauthorized') {
        return null;
      }
      throw error;
    }
    return this.me;
  }

  async requestCode(contact: string): Promise<CodeSent> {
    const { content } = await this.store.request<CodeSent>(
      requestCode(contact),
    );
    return content;
  }

  async signUp(fields: SignUpFields): Promise<Me> {
    const { content } = await this.store.request<Me>(signUp(fields));
    this.me = content;
    return content;
  }

  /** Log in with a one-time code; the API sets the session cookie. */
  async logIn(contact: string, code: string): Promise<Me> {
    const { content } = await this.store.request<Me>(logIn(contact, code));
    this.me = content;
    return content;
  }

  /** End the session in the API (it clears the cookie) and forget who it was. */
  async logOut(): Promise<void> {
    await this.store.request(logOut());
    this.me = null;
  }
}

declare module '@ember/service' {
  interface Registry {
    session: SessionService;
  }
}
