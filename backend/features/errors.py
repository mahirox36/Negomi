from __future__ import annotations

from typing import Optional
from fastapi import HTTPException

class DashboardError(HTTPException):
    """Base exception for dashboard errors"""
    def __init__(self, message: str, status_code: int = 500, code: Optional[int] = None) -> None:
        super().__init__(status_code=status_code, detail={"message": message, "code": code})

class AuthenticationError(DashboardError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=401, code=code)

class AuthorizationError(DashboardError):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=403, code=code)

class ResourceNotFoundError(DashboardError):
    """Raised when requested resource is not found"""
    def __init__(self, message: str = "Resource not found", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=404, code=code)

class ValidationError(DashboardError):
    """Raised when request validation fails"""
    def __init__(self, message: str = "Validation failed", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=400, code=code)

class RateLimitError(DashboardError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=429, code=code)

class StorageError(DashboardError):
    """Raised when storage operations fail"""
    def __init__(self, message: str = "Storage operation failed", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=500, code=code)

class ConfigurationError(DashboardError):
    """Raised when there's a configuration issue"""
    def __init__(self, message: str = "Configuration error", code: Optional[int] = None) -> None:
        super().__init__(message=message, status_code=500, code=code)