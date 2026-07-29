"""
blocklog.exceptions
~~~~~~~~~~~~~~~~~~~
Exceptions raised by the Blocklog SDK. All custom exceptions inherit from BlocklogError.
"""


class BlocklogError(Exception):
    """Base exception for all Blocklog SDK errors."""


class BlocklogCommitError(BlocklogError):
    """Raised when a decision context fails to commit to the backend."""


class BlocklogAuthError(BlocklogError):
    """Raised when authentication or authorization fails."""


class TransportError(BlocklogError):
    pass


class ValidationError(BlocklogError):
    pass


class AuthenticationError(BlocklogAuthError):
    pass


class AuthorizationError(BlocklogAuthError):
    pass


class NotFoundError(BlocklogError):
    pass


class ConflictError(BlocklogError):
    pass


class RateLimitError(BlocklogError):
    pass


class ServerError(BlocklogError):
    pass


def map_http_error(status_code: int, message: str) -> BlocklogError:
    if status_code in (400, 422):
        return ValidationError(message)
    if status_code == 401:
        return AuthenticationError(message)
    if status_code == 403:
        return AuthorizationError(message)
    if status_code == 404:
        return NotFoundError(message)
    if status_code == 409:
        return ConflictError(message)
    if status_code == 429:
        return RateLimitError(message)
    if status_code >= 500:
        return ServerError(message)
    return BlocklogError(message)
