import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type { ContactKind } from '../../services/members';
import type ProfileService from '../../services/profile';
import type SessionService from '../../services/session';
import { formatMonth } from '../../utils/months';
import { roleLabel } from '../../utils/roles';
import ContactEditor from '../contact/contact-editor';
import Avatar from '../ui/avatar';
import Button from '../ui/button';
import Card from '../ui/card';
import Field from '../ui/field';
import TextInput from '../ui/text-input';

/**
 * My profile (colivo-design/web/WebProfile.html): who you are in this home,
 * and the phone and email you log in with everywhere (Phase 1c).
 */
export default class ProfilePage extends Component {
  @service declare session: SessionService;
  @service declare profile: ProfileService;

  /** The name being typed, until it is saved. */
  @tracked typedName: string | null = null;

  get name(): string {
    return this.session.me?.membership.name ?? '';
  }

  get nameValue(): string {
    return this.typedName ?? this.name;
  }

  @action setName(value: string): void {
    this.typedName = value;
  }

  /** Fix your own name in this home (FR-86, `PATCH /me`). */
  @action
  async saveName(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    await this.session.updateMe(this.nameValue);
    this.typedName = null;
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
      <form
        class="flex flex-wrap items-end gap-2"
        {{on "submit" this.saveName}}
      >
        <Field @label="Name" class="min-w-0 flex-1" as |id|>
          <TextInput
            id={{id}}
            @value={{this.nameValue}}
            @onInput={{this.setName}}
            data-test-profile-name-input
          />
        </Field>
        <Button type="submit" data-test-profile-name-save>Save</Button>
      </form>
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
