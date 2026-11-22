from datetime import timedelta

# One-time codes (FR-94).
CODE_LENGTH = 6
CODE_LIFETIME = timedelta(minutes=5)
CODE_MAX_WRONG = 5
CODE_LOCK = timedelta(minutes=15)
CODE_RESEND_AFTER = timedelta(minutes=1)
CODE_MAX_PER_HOUR = 5
CODE_SEND_WINDOW = timedelta(hours=1)

# Log-in sessions.
SESSION_COOKIE = "colivo_session"
SESSION_LIFETIME = timedelta(days=30)
