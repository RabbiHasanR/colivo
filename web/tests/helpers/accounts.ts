import { http, HttpResponse } from 'msw';
import type { components } from 'colivo-web/data/types/api.generated';

/**
 * Typed API bodies for accounts and the new home, shared by web tests.
 * Typed with the generated API types, so a changed contract fails `make lint`.
 */
type Schemas = components['schemas'];
export type MeBody = Schemas['StandardResponse_MeOut_'];
export type Me = Schemas['MeOut'];
export type Role = Me['membership']['role'];

type MeMembership = Me['membership'];

export const OUR_FLAT_ID = '01a1fd00-0000-7000-8000-000000000001';

/**
 * Who is logged in: Rabbi Hasan, owner of "Our Flat" (OF-4827), or Maruf
 * for a member. Details are checked unless `membership` says otherwise.
 */
export function me(
  role: Role = 'owner',
  membership: Partial<MeMembership> = {},
): Me {
  return {
    person: { phone: '+8801712345678', email: null },
    membership: {
      id: '01a1fd00-0000-7000-8000-000000000002',
      name: role === 'member' ? 'Maruf' : 'Rabbi Hasan',
      role,
      status: 'active',
      joined_on: role === 'member' ? '2026-09-01' : '2026-11-01',
      added_by_name: role === 'owner' ? null : 'Rabbi Hasan',
      details_checked: true,
      ...membership,
    },
    home: {
      id: OUR_FLAT_ID,
      code: 'OF-4827',
      name: 'Our Flat',
      area: 'Mirpur',
      first_month: '2026-11-01',
    },
    homes: [{ id: OUR_FLAT_ID, name: 'Our Flat', area: 'Mirpur', role }],
  };
}

export function meBody(
  role: Role = 'owner',
  membership: Partial<MeMembership> = {},
): MeBody {
  return { success: true, message: 'Logged in', data: me(role, membership) };
}

export const notLoggedInBody: MeBody = {
  success: false,
  message: 'Log in first.',
  errors: ['Log in first.'],
};

export const codeSentBody: Schemas['StandardResponse_CodeSentOut_'] = {
  success: true,
  message: 'Code sent',
  data: { channel: 'sms', expires_in_seconds: 300, resend_in_seconds: 60 },
};

export const newHomeSetupBody: Schemas['StandardResponse_SetupOut_'] = {
  success: true,
  message: 'Setup checklist',
  data: {
    steps: [
      { key: 'home_created', done: true },
      { key: 'members', done: false },
      { key: 'rooms', done: false },
      { key: 'rules', done: false },
      { key: 'bills', done: false },
    ],
  },
};

/** `GET /me` answers 401: nobody is logged in. */
export const notLoggedIn = http.get('*/api/v1/me', () =>
  HttpResponse.json(notLoggedInBody, { status: 401 }),
);

/** `GET /me` answers with someone logged in, as `role`. */
export function loggedInAs(
  role: Role = 'owner',
  membership: Partial<MeMembership> = {},
) {
  return http.get('*/api/v1/me', () =>
    HttpResponse.json(meBody(role, membership)),
  );
}

/** The new home's checklist, for the owner and managers. */
export const newHomeSetup = http.get('*/api/v1/home/setup', () =>
  HttpResponse.json(newHomeSetupBody),
);

// --- A person in two homes (Phase 1b) -------------------------------------

export type HomeChoice = Schemas['HomeChoiceOut'];
export type LogInBody = Schemas['StandardResponse_LogInOut_'];

export const GREEN_HOUSE_ID = '01a1fd00-0000-7000-8000-0000000000a2';

/** "Our Flat" as a home to choose, where Rabbi is the owner. */
export const ourFlat: HomeChoice = {
  id: OUR_FLAT_ID,
  name: 'Our Flat',
  area: 'Mirpur',
  role: 'owner',
};

/** Rabbi's homes: owner of "Our Flat", member of "Green House". */
export const twoHomes: HomeChoice[] = [
  { id: GREEN_HOUSE_ID, name: 'Green House', area: null, role: 'member' },
  ourFlat,
];

/** Who Rabbi is in one of `twoHomes`. */
export function meIn(
  homeId: string,
  homes: HomeChoice[] = twoHomes,
  membership: Partial<MeMembership> = {},
): Me {
  const choice = homes.find((home) => home.id === homeId)!;
  const base = me(choice.role, { name: 'Rabbi Hasan', ...membership });
  return {
    ...base,
    home: { ...base.home, id: choice.id, name: choice.name, area: choice.area },
    homes,
  };
}

/** The log-in answer: the homes, and `me` only for one home. */
export function logInBody(homes: HomeChoice[], loggedIn: Me | null): LogInBody {
  return {
    success: true,
    message: 'Logged in',
    data: { homes, me: loggedIn },
  };
}

/** A refusal of the home a request named (or didn't), with its reason. */
export function homeRefusal(
  status: 403 | 409,
  reason: 'not_in_home' | 'choose_home',
) {
  const message =
    reason === 'choose_home'
      ? 'Choose a home.'
      : "You're no longer a member of this home.";
  return HttpResponse.json(
    { success: false, message, errors: [message], data: { reason } },
    { status },
  );
}

/**
 * The API for Rabbi in `homes`, answering each request for the home its
 * `X-Colivo-Home` header names, as the backend does: no header with several
 * homes is 409 choose_home; a home not in `homes` is 403 not_in_home.
 * `homes` may be changed by the test (removed from a home). Nobody is
 * logged in until `POST /auth/log-in`, unless `loggedIn` says so; the
 * homes in `unchecked` still have their first log-in check to do.
 */
export function homesApi(
  homes: HomeChoice[] = [...twoHomes],
  {
    loggedIn = false,
    unchecked = [],
  }: { loggedIn?: boolean; unchecked?: string[] } = {},
) {
  let session = loggedIn;
  const loggedOut = () => HttpResponse.json(notLoggedInBody, { status: 401 });
  return [
    http.post('*/api/v1/auth/codes', () => HttpResponse.json(codeSentBody)),
    http.post('*/api/v1/auth/log-in', () => {
      session = true;
      return HttpResponse.json(
        logInBody(homes, homes.length === 1 ? meIn(homes[0]!.id, homes) : null),
      );
    }),
    http.post('*/api/v1/auth/log-out', () => {
      session = false;
      return HttpResponse.json({ success: true, message: 'Logged out' });
    }),
    http.get('*/api/v1/me/homes', () =>
      session
        ? HttpResponse.json({
            success: true,
            message: 'Your homes',
            data: homes,
          })
        : loggedOut(),
    ),
    http.get('*/api/v1/me', ({ request }) => {
      if (!session) return loggedOut();
      const homeId = request.headers.get('X-Colivo-Home');
      if (!homeId && homes.length > 1) return homeRefusal(409, 'choose_home');
      const chosen = homeId ?? homes[0]?.id;
      if (!homes.some((home) => home.id === chosen)) {
        return homeRefusal(403, 'not_in_home');
      }
      return HttpResponse.json({
        success: true,
        message: 'Logged in',
        data: meIn(chosen!, homes, {
          details_checked: !unchecked.includes(chosen!),
        }),
      });
    }),
  ];
}

type MePerson = Schemas['MePersonOut'];

/**
 * `POST /me/contact/code`, `PUT /me/contact` and `DELETE /me/contact/:channel`
 * over one person starting as `person` (Phase 1c): any code is accepted, and
 * a contact with "@" is an email.
 */
export function myContactApi(
  person: MePerson = { phone: '+8801712345678', email: null },
) {
  const me = { ...person };
  const answer = () =>
    HttpResponse.json({ success: true, message: 'Log-in changed', data: me });
  return [
    http.post('*/api/v1/me/contact/code', () =>
      HttpResponse.json(codeSentBody),
    ),
    http.put('*/api/v1/me/contact', async ({ request }) => {
      const { contact } = (await request.json()) as Schemas['ContactChangeIn'];
      if (contact.includes('@')) me.email = contact;
      else me.phone = contact;
      return answer();
    }),
    http.delete('*/api/v1/me/contact/:channel', ({ params }) => {
      if (params['channel'] === 'email') me.email = null;
      else me.phone = null;
      return answer();
    }),
  ];
}
