/**
 * Where the API lives. VITE_API_HOST comes from web/.env.development (and the
 * production env later); empty means the same origin.
 */
const env = (import.meta as { env?: Record<string, string | undefined> }).env;

export const API_HOST = env?.['VITE_API_HOST'] ?? '';
export const API_NAMESPACE = '/api/v1';

export function apiUrl(path: string): string {
  return `${API_HOST}${API_NAMESPACE}/${path.replace(/^\/+/, '')}`;
}

/**
 * The request header naming the home a tab acts in (Phase 1b). The server
 * checks it against the logged-in person's homes; the cookie still says who
 * they are.
 */
export const HOME_HEADER = 'X-Colivo-Home';
