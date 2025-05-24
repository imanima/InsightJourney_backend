from typing import Optional

class ServiceError(Exception):
    """Base exception for all service errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class DatabaseError(ServiceError):
    """Raised when there are issues with database operations."""
    pass

class SessionError(ServiceError):
    """Raised when there are issues with session operations."""
    pass

class ValidationError(ServiceError):
    """Raised when input validation fails."""
    pass

class AuthenticationError(ServiceError):
    """Raised when there are authentication issues."""
    pass

class NotFoundError(ServiceError):
    """Raised when a requested resource is not found."""
    pass

def handle_error(error: Exception, context: str = "") -> dict:
    """Convert exceptions to standardized error responses."""
    if isinstance(error, ServiceError):
        return {
            "error": str(error),
            "error_code": error.error_code,
            "details": error.details,
            "context": context
        }
    else:
        return {
            "error": str(error),
            "error_code": "INTERNAL_ERROR",
            "details": {"type": type(error).__name__},
            "context": context
        } 