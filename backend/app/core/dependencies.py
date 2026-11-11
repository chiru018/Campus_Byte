import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationException,
    TokenExpiredException,
    TokenRevokedException,
    InactiveAccountException,
)
import app.crud.crud_user as crud_user
import app.crud.crud_token as crud_token

# Optional HTTPBearer to allow Swagger UI Authorize button and standard Authorization header
http_bearer = HTTPBearer(auto_error=False)


def extract_raw_token(
    request: Request,
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> str:
    """
    Extracts the JWT access token from either:
    1. Authorization: Bearer <token> header (standard API & tests)
    2. HttpOnly Cookie 'campus_byte_access_token' (secure browser sessions)
    """
    if bearer_creds and bearer_creds.credentials:
        return bearer_creds.credentials

    # Fallback to cookie
    cookie_token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    raise AuthenticationException("Authentication required. Please provide a valid Bearer token or session cookie.")


def get_current_user(
    token: str = Depends(extract_raw_token),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolves and validates authenticated user identity against the database:
    1. Validates signature, expiration, and payload claims.
    2. Checks server-side token denylist to reject revoked tokens.
    3. Resolves subject user ID in PostgreSQL.
    4. Enforces active account status.
    """
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise AuthenticationException("Invalid or malformed authentication token.")

    jti = payload.get("jti")
    if not jti or crud_token.is_token_revoked(db, jti):
        raise TokenRevokedException()

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Token subject claim missing.")

    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise AuthenticationException("Malformed token subject identifier.")

    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise AuthenticationException("Authenticated user account no longer exists.")

    if not user.is_active:
        raise InactiveAccountException()

    return user

