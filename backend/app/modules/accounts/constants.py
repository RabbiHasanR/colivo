from datetime import timedelta

# One-time codes (FR-94).
CODE_LENGTH = 6
CODE_LIFETIME = timedelta(minutes=5)
CODE_MAX_WRONG = 5
CODE_LOCK = timedelta(minutes=15)
CODE_RESEND_AFTER = timedelta(minutes=1)
CODE_MAX_PER_HOUR = 5
CODE_SEND_WINDOW = timedelta(hours=1)

# Codes that confirm a new phone or email (Phase 1c) live under their own
# prefix, bound to whose log-in changes, so they can never log anyone in.
CHANGE_CODE_PREFIX = "otp:change"

# Log-in sessions.
SESSION_COOKIE = "colivo_session"
SESSION_LIFETIME = timedelta(days=30)
# The set of one person's session keys, so a change to their log-in can end
# them all, or all but one (Phase 1c).
PERSON_SESSIONS_PREFIX = "person_sessions"

# The home a request acts in (Phase 1b): a home id, checked against the
# logged-in person's active memberships; it only chooses among their homes.
HOME_HEADER = "X-Colivo-Home"
