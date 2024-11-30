"""
Custom exception hierarchy for DuckMail client.
"""

class DuckMailError(Exception):
    """Base exception for all DuckMail-related errors."""
    pass

class APIError(DuckMailError):
    """Raised when the API returns an error response."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)

class ConnectionError(DuckMailError):
    """Raised when there are network connectivity issues."""
    pass

class ValidationError(DuckMailError):
    """Raised when request or response validation fails."""
    pass
