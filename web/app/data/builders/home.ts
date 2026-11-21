import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';
import type { components } from '../types/api.generated';

/** The new-home checklist (`GET /home/setup`). */
export type Setup = components['schemas']['SetupOut'];
export type SetupStep = components['schemas']['SetupStep'];

/** The home's setup checklist. Not a stored record, so it skips the cache. */
export function getSetup() {
  return {
    url: apiUrl('home/setup'),
    method: 'GET' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}
