import Component from '@glimmer/component';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type { ContactKind } from '../../services/members';
import type ProfileService from '../../services/profile';
import type SessionService from '../../services/session';
import { formatMonth } from '../../utils/months';
import { roleLabel } from '../../utils/roles';
import ContactEditor from '../contact/contact-editor';
import Avatar from '../ui/avatar';
import Card from '../ui/card';

/**
 * My profile (colivo-design/web/WebProfile.html): who you are in this home,
 * and the phone and email you log in with everywhere (Phase 1c).
 */
export default class ProfilePage extends Component {
  @service declare session: SessionService;
  @service declare profile: ProfileService;

  get name(): string {
    return this.session.me?.membership.name ?? '';
  }

  get phone(): string | null {
    return this.session.me?.person.phone ?? null;
  }

  get email(): string | null {
    return this.session.me?.person.email ?? null;
  }

  /** "Owner · member since November 2026"; no date for an owner not living here. */
  get subtitle(): string {
    const membership = this.session.me?.membership;
    if (!membership) return '';
    const role = roleLabel(membership.role);
    const since = membership.joined_on;
    return since ? `${role} · member since ${formatMonth(since)}` : role;
  }

  @action
  async sendContactCode(contact: string): Promise<void> {
    await this.profile.sendContactCode(contact);
  }

  @action
  async saveContact(contact: string, code: string): Promise<void> {
    await this.profile.setContact(contact, code);
  }

  @action
  async removeContact(kind: ContactKind): Promise<void> {
    await this.profile.removeContact(kind);
  }

  <template>
    <header class="flex flex-col gap-1">
      <h1 class="text-3xl font-semibold">My profile</h1>
    </header>
    <Card
      class="flex max-w-[720px] min-w-0 flex-col gap-4 p-4"
      aria-labelledby="my-details-title"
    >
      <h2 id="my-details-title" class="font-sans text-base font-semibold">My
        details</h2>
      <div class="flex items-center gap-3.5">
        <Avatar @name={{this.name}} @size="lg" />
        <div class="flex min-w-0 flex-col gap-0.5">
          <span
            class="truncate text-lg font-semibold"
            data-test-profile-name
          >{{this.name}}</span>
          <span
            class="text-[13px] text-muted"
            data-test-profile-subtitle
          >{{this.subtitle}}</span>
        </div>
      </div>
      <ContactEditor
        @phone={{this.phone}}
        @email={{this.email}}
        @editable={{true}}
        @onSendCode={{this.sendContactCode}}
        @onSave={{this.saveContact}}
        @onRemove={{this.removeContact}}
      />
    </Card>
  </template>
}
