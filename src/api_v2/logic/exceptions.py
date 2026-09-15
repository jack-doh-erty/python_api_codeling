class LogicError(Exception):
    """Base exception for all API logic errors"""
    pass


class DuplicateResourceError(LogicError):
    """Raised when attempting to create a resource that already exists"""
    pass

class ResourceNotFoundError(LogicError):
    """ raised when the requested resource doesn't exist"""
    pass


class InvalidFileError(LogicError):
    """Raised when an uploaded file fails validation."""
    pass


class AuthenticationError(LogicError):
    """Raised when supplied authentication credentials are invalid."""
    pass


class TokenExpiredError(LogicError):
    """Raised when an authentication token has expired."""
    pass


class TokenInvalidError(LogicError):
    """Raised when an authentication token is invalid."""
    pass


# Mapping of exception types to HTTP status codes
EXCEPTION_TO_HTTP_STATUS = {
    DuplicateResourceError: 409,  # Conflict
    ResourceNotFoundError: 404,
    InvalidFileError: 400,
    AuthenticationError: 401,
    TokenExpiredError: 401,
    TokenInvalidError: 401,
    LogicError: 500,  # Internal Server Error (default)
}


def get_error_response(exception: Exception) -> tuple[int, dict]:
    """
    Convert an exception to an appropriate HTTP status code and error response.

    Args:
        exception: The exception that was raised

    Returns:
        tuple: (status_code, error_response_dict)
    """
    # Find most specific exception type in the mapping
    for exception_type, status_code in EXCEPTION_TO_HTTP_STATUS.items():
        if isinstance(exception, exception_type):
            return status_code, {"error": str(exception)}

    # Default fallback for unexpected exceptions
    return 500, {"error": "An unexpected error occurred"}
