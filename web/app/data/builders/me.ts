import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

/** Who is logged in, and in which home (`GET /me`). */
export type Me = components['schemas']['MeOut'];
export type Role = Me['membership']['role'];

/** Who is logged in. Not a stored record, so it skips the cache. */
export function getMe() {
  return {
    url: apiUrl('me'),
    method: 'GET' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}
