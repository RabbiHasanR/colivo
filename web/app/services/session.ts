import Service, { service } from '@ember/service';
import { tracked } from '@glimmer/tracking';
import {
  requestCode,
  signUp,
  type CodeSent,
  type SignUpFields,
} from '../data/builders/auth';
import type { Me } from '../data/builders/me';

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
}

declare module '@ember/service' {
  interface Registry {
    session: SessionService;
  }
}
