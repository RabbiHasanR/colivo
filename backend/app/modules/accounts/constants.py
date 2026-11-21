from datetime import timedelta

# One-time codes (FR-94).
CODE_LENGTH = 6
CODE_LIFETIME = timedelta(minutes=5)
CODE_MAX_WRONG = 5
CODE_LOCK = timedelta(minutes=15)

# Log-in sessions.
SESSION_COOKIE = "colivo_session"
SESSION_LIFETIME = timedelta(days=30)
