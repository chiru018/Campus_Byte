from typing import Any, Optional
from fastapi import HTTPException, status


class CampusByteException(HTTPException):
    """Base application exception for Campus Byte."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra: Optional[Any] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or "APP_ERROR"
        self.extra = extra


class ResourceNotFoundException(CampusByteException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' was not found.",
            error_code="RESOURCE_NOT_FOUND",
        )


class DuplicateResourceException(CampusByteException):
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists.",
            error_code="DUPLICATE_RESOURCE",
        )


class BusinessRuleException(CampusByteException):
    def __init__(self, detail: str, error_code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )
