/**
 * The log-in token. Phase 0 has no log-in, so there is never a token; Phase 1
 * decides where it is kept (specs/tech-stack.md → Deferred decisions → Auth
 * tokens) and turns this into a session service.
 */
export function readToken(): string | null {
  return null;
}
