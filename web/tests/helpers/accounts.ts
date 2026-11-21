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

/** Who is logged in: Rabbi Hasan, owner of "Our Flat" (OF-4827). */
export function me(role: Role = 'owner'): Me {
  return {
    person: { phone: '+8801712345678' },
    membership: {
      id: '01a1fd00-0000-7000-8000-000000000002',
      name: role === 'member' ? 'Maruf' : 'Rabbi Hasan',
      role,
      status: 'active',
    },
    home: {
      id: '01a1fd00-0000-7000-8000-000000000001',
      code: 'OF-4827',
      name: 'Our Flat',
      area: 'Mirpur',
      first_month: '2026-11-01',
    },
  };
}

export function meBody(role: Role = 'owner'): MeBody {
  return { success: true, message: 'Logged in', data: me(role) };
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
export function loggedInAs(role: Role = 'owner') {
  return http.get('*/api/v1/me', () => HttpResponse.json(meBody(role)));
}

/** The new home's checklist, for the owner and managers. */
export const newHomeSetup = http.get('*/api/v1/home/setup', () =>
  HttpResponse.json(newHomeSetupBody),
);
