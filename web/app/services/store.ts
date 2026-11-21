import { service } from '@ember/service';
import { useLegacyStore } from '@warp-drive/legacy';
import { JSONAPICache } from '@warp-drive/json-api';
import type { Handler as WarpDriveHandler } from '@warp-drive/core/request';
import { ErrorHandler } from '../data/handlers/errors';
import { createAuthHandler } from '../data/handlers/auth';
import { createEnvelopeHandler } from '../data/handlers/api-envelope';
import { createSessionEndHandler } from '../data/handlers/session-end';
import type { Handler } from '../data/handlers/types';
import type SessionService from './session';

/**
 * Our handlers use the small structural types in data/handlers/types.ts, so
 * their unit tests need no store. WarpDrive's own types differ only in the
 * generic return (Future vs Promise, ResponseInfo); the acceptance tests
 * run these handlers in the real store, which proves they fit at runtime.
 * This is the one place the two are joined.
 */
function asWarpDriveHandler(handler: Handler): WarpDriveHandler {
  return handler as unknown as WarpDriveHandler;
}

/** Set by the store once it exists, so the handler can reach the session. */
let onSessionEnded: () => void = () => {};

/**
 * Requests go through: session end -> errors -> auth -> envelope -> fetch
 * (added by useLegacyStore). Only app/data talks HTTP.
 */
const BaseStore = useLegacyStore({
  linksMode: false,
  cache: JSONAPICache,
  handlers: [
    createSessionEndHandler(() => onSessionEnded()),
    ErrorHandler,
    createAuthHandler(),
    createEnvelopeHandler(),
  ].map(asWarpDriveHandler),
  schemas: [],
});

/**
 * The app's store. A 401 on any request means the session ended: the session
 * service then forgets who was logged in and goes to log-in.
 */
export default class Store extends BaseStore {
  @service declare session: SessionService;

  constructor(...args: ConstructorParameters<typeof BaseStore>) {
    super(...args);
    onSessionEnded = () => this.session.expire();
  }
}
