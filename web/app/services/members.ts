import Service, { service } from '@ember/service';
import {
  addMember,
  listMembers,
  updateMember,
  type Member,
  type MemberChanges,
  type MemberFields,
} from '../data/builders/members';
import type Store from './store';

// For components, which don't import the data layer.
export type {
  Member,
  MemberChanges,
  MemberFields,
} from '../data/builders/members';

/** The home's members, for the owner and managers. */
export default class MembersService extends Service {
  @service declare store: Store;

  async list(): Promise<Member[]> {
    const { content } = await this.store.request<Member[]>(listMembers());
    return content;
  }

  async add(fields: MemberFields): Promise<Member> {
    const { content } = await this.store.request<Member>(addMember(fields));
    return content;
  }

  async update(id: string, changes: MemberChanges): Promise<Member> {
    const { content } = await this.store.request<Member>(
      updateMember(id, changes),
    );
    return content;
  }
}

declare module '@ember/service' {
  interface Registry {
    members: MembersService;
  }
}
