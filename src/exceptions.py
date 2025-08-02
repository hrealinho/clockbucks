from typing import Any, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger("clockbucks.exceptions")


class ClockBucksException(Exception):
    """Base exception for Clock Bucks application."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(ClockBucksException):
    """Raised when data validation fails."""

    pass


class NotFoundError(ClockBucksException):
    """Raised when a resource is not found."""

    pass


class DuplicateError(ClockBucksException):
    """Raised when trying to create a duplicate resource."""

    pass


class CalculationError(ClockBucksException):
    """Raised when meeting cost calculation fails."""

    pass


class DatabaseError(ClockBucksException):
    """Raised when database operations fail."""

    pass


class ConfigurationError(ClockBucksException):
    """Raised when configuration is invalid."""

    pass


# HTTP Exception mapping
def map_exception_to_http(exc: ClockBucksException) -> HTTPException:
    """Map custom exceptions to HTTP exceptions."""

    error_mappings = {
        ValidationError: (400, "Validation Error"),
        NotFoundError: (404, "Resource Not Found"),
        DuplicateError: (409, "Resource Already Exists"),
        CalculationError: (422, "Calculation Error"),
        DatabaseError: (500, "Database Error"),
        ConfigurationError: (500, "Configuration Error"),
    }

    status_code, default_detail = error_mappings.get(
        type(exc), (500, "Internal Server Error")
    )

    detail = {
        "message": exc.message,
        "error_code": exc.error_code,
        "details": exc.details,
    }

    logger.error(
        f"Exception occurred: {exc.message}", extra={"error_details": exc.details}
    )

    return HTTPException(status_code=status_code, detail=detail)
