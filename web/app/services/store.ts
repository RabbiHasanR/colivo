import { useLegacyStore } from '@warp-drive/legacy';
import { JSONAPICache } from '@warp-drive/json-api';
import type { Handler as WarpDriveHandler } from '@warp-drive/core/request';
import { ErrorHandler } from '../data/handlers/errors';
import { createAuthHandler } from '../data/handlers/auth';
import { createEnvelopeHandler } from '../data/handlers/api-envelope';
import type { Handler } from '../data/handlers/types';

/**
 * Our handlers use the small structural types in data/handlers/types.ts, so
 * their unit tests need no store. WarpDrive's own types differ only in the
 * generic return (Future vs Promise, ResponseInfo); the server-status tests
 * run these handlers in the real store, which proves they fit at runtime.
 * This is the one place the two are joined.
 */
function asWarpDriveHandler(handler: Handler): WarpDriveHandler {
  return handler as unknown as WarpDriveHandler;
}

/**
 * Requests go through: errors -> auth -> envelope -> fetch (added by
 * useLegacyStore). Only app/data talks HTTP.
 */
const Store = useLegacyStore({
  linksMode: false,
  cache: JSONAPICache,
  handlers: [
    ErrorHandler,
    createAuthHandler(),
    createEnvelopeHandler(),
  ].map(asWarpDriveHandler),
  schemas: [],
});

type Store = InstanceType<typeof Store>;

export default Store;
