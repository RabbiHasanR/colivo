import { http, HttpResponse } from 'msw';
import type { components } from 'colivo-web/data/types/api.generated';
import { codeSentBody } from './accounts';

/** Typed API bodies for the members list, shared by web tests. */
type Schemas = components['schemas'];
export type Member = Schemas['MemberOut'];
export type MemberFields = Schemas['MemberIn'];
type ContactChange = Schemas['ContactChangeIn'];

/** A member of "Our Flat", with any field changed. */
export function member(fields: Partial<Member> = {}): Member {
  return {
    id: '01a1fd00-0000-7000-8000-000000000010',
    name: 'Maruf',
    phone: '+8801812345678',
    email: null,
    role: 'member',
    status: 'active',
    joined_on: '2026-11-21',
    contact_editable: true,
    ...fields,
  };
}

export const owner: Member = member({
  id: '01a1fd00-0000-7000-8000-000000000002',
  name: 'Rabbi Hasan',
  phone: '+8801712345678',
  role: 'owner',
  joined_on: '2026-11-01',
});

/**
 * `GET` and `POST /members` over an in-memory list starting with `members`:
 * a member added shows in the next list, as on the real API.
 */
export function membersApi(members: Member[] = [owner]) {
  const list = [...members];
  return [
    http.get('*/api/v1/members', () =>
      HttpResponse.json({ success: true, message: 'Members', data: list }),
    ),
    http.post('*/api/v1/members', async ({ request }) => {
      const fields = (await request.json()) as MemberFields;
      const added = member({
        id: `01a1fd00-0000-7000-8000-0000000001${list.length}`,
        name: fields.name,
        role: fields.role ?? 'member',
        joined_on: fields.joined_on,
      });
      list.push(added);
      return HttpResponse.json(
        { success: true, message: 'Member added', data: added },
        { status: 201 },
      );
    }),
    changeIn(list, 'put', 'role', (found, body) => {
      found.role = (body as { role: Member['role'] }).role;
    }),
    changeIn(list, 'post', 'deactivate', (found) => {
      found.status = 'inactive';
    }),
    changeIn(list, 'post', 'reactivate', (found) => {
      found.status = 'active';
    }),
    // Phase 1c: any code is accepted; a contact with "@" is an email.
    http.post('*/api/v1/members/:id/contact/code', () =>
      HttpResponse.json(codeSentBody),
    ),
    changeIn(list, 'put', 'contact', (found, body) => {
      const { contact } = body as ContactChange;
      if (contact.includes('@')) found.email = contact;
      else found.phone = contact;
    }),
    changeIn(list, 'delete', 'contact/:channel', (found, _body, params) => {
      if (params['channel'] === 'email') found.email = null;
      else found.phone = null;
    }),
  ];
}

/** A change to one member of the in-memory list, answered with the member. */
function changeIn(
  list: Member[],
  method: 'put' | 'post' | 'delete',
  action: string,
  apply: (
    member: Member,
    body: unknown,
    params: Record<string, unknown>,
  ) => void,
) {
  return http[method](
    `*/api/v1/members/:id/${action}`,
    async ({ params, request }) => {
      const found = list.find((each) => each.id === params['id']);
      if (!found) {
        return HttpResponse.json(
          { success: false, message: 'Member not found.' },
          { status: 404 },
        );
      }
      const body = method === 'delete' ? null : await request.json();
      apply(found, body, params);
      return HttpResponse.json({
        success: true,
        message: 'Changed',
        data: found,
      });
    },
  );
}
