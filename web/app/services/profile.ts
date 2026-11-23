import Service, { service } from '@ember/service';
import {
  removeMyContact,
  requestMyContactCode,
  setMyContact,
  type ContactKind,
  type MePerson,
} from '../data/builders/me';
import type SessionService from './session';
import type Store from './store';

/** Your own phone and email, changed on My profile (Phase 1c). */
export default class ProfileService extends Service {
  @service declare store: Store;
  @service declare session: SessionService;

  /** Send a code to your new phone or email. */
  async sendContactCode(contact: string): Promise<void> {
    await this.store.request(requestMyContactCode(contact));
  }

  /** Save your new phone or email with its code. */
  async setContact(contact: string, code: string): Promise<void> {
    const { content } = await this.store.request<MePerson>(
      setMyContact(contact, code),
    );
    this.showPerson(content);
  }

  /** Stop logging in with your phone or your email. */
  async removeContact(kind: ContactKind): Promise<void> {
    const { content } = await this.store.request<MePerson>(
      removeMyContact(kind),
    );
    this.showPerson(content);
  }

  /** The page and the shell show the phone and email the API answered. */
  showPerson(person: MePerson): void {
    const me = this.session.me;
    if (me) this.session.me = { ...me, person };
  }
}

declare module '@ember/service' {
  interface Registry {
    profile: ProfileService;
  }
}
