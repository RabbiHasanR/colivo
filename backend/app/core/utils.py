from fastapi import Request

DEFAULT_RESPONSE_MESSAGE = "Operation successful"


def set_response_message(request: Request, message: str) -> None:
    """Set the success message that ``CoreRouter`` puts in the envelope.

    Args:
        request: The current request.
        message: A short, user-facing message, e.g. "Home created".
    """
    request.state.response_message = message


def get_response_message(request: Request) -> str:
    """Return the message set with ``set_response_message``, or the default.

    Args:
        request: The current request.

    Returns:
        The message for the envelope.
    """
    return getattr(request.state, "response_message", DEFAULT_RESPONSE_MESSAGE)
