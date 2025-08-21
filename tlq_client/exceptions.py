"""TLQ Client exceptions."""


class TLQError(Exception):
    """Base exception for TLQ client errors."""
    pass


class TLQConnectionError(TLQError):
    """Raised when connection to TLQ server fails."""
    pass


class TLQTimeoutError(TLQError):
    """Raised when request to TLQ server times out."""
    pass


class TLQServerError(TLQError):
    """Raised when TLQ server returns an error response."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class TLQValidationError(TLQError):
    """Raised when client-side validation fails."""
    pass