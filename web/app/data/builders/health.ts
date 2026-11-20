import { SkipCache } from '@warp-drive/core/types/request';
import { apiUrl } from '../config';

/** The backend's health check. Not a stored record, so it skips the cache. */
export function healthCheck() {
  return {
    url: apiUrl('health'),
    method: 'GET' as const,
    cacheOptions: { [SkipCache]: true as const },
  };
}
