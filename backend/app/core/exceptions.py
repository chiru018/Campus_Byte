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
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
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


class ConflictException(CampusByteException):
    def __init__(self, detail: str, error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class BusinessRuleException(CampusByteException):
    def __init__(self, detail: str, error_code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )


class AuthenticationException(CampusByteException):
    def __init__(
        self,
        detail: str = "Could not validate authentication credentials.",
        error_code: str = "AUTHENTICATION_REQUIRED",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="Invalid email or password.",
            error_code="INVALID_CREDENTIALS",
        )


class TokenExpiredException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="Authentication token has expired. Please log in again.",
            error_code="TOKEN_EXPIRED",
        )


class TokenRevokedException(AuthenticationException):
    def __init__(self):
        super().__init__(
            detail="Authentication token has been revoked. Please log in again.",
            error_code="TOKEN_REVOKED",
        )


class AuthorizationException(CampusByteException):
    def __init__(
        self,
        detail: str = "You do not have permission to perform this action.",
        error_code: str = "FORBIDDEN",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


class InactiveAccountException(CampusByteException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or suspended. Please contact campus support.",
            error_code="ACCOUNT_INACTIVE",
        )
