from datetime import timedelta

# One-time codes (FR-94).
CODE_LENGTH = 6
CODE_LIFETIME = timedelta(minutes=5)

# Log-in sessions.
SESSION_COOKIE = "colivo_session"
SESSION_LIFETIME = timedelta(days=30)
