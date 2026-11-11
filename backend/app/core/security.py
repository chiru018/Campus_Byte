import re
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.core.config import settings

# Initialize Argon2 Password Hasher (Argon2id)
_password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def validate_password_strength(password: str) -> None:
    """
    Enforces Campus Byte password security policy:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+[\]\\/`~;']", password):
        raise ValueError("Password must contain at least one special character.")


def get_password_hash(password: str) -> str:
    """Computes a cryptographically secure Argon2id hash."""
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored hash.
    Supports primary Argon2id hashes, with fallback support for PBKDF2 hashes.
    """
    if not hashed_password:
        return False

    # Check for Argon2
    if hashed_password.startswith("$argon2"):
        try:
            return _password_hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    # Fallback to PBKDF2 (for Phase 2 legacy hashes)
    if hashed_password.startswith("pbkdf2:"):
        try:
            algorithm, salt, stored_hash = hashed_password.split("$")
            parts = algorithm.split(":")
            iterations = int(parts[2])
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            )
            return secrets.compare_digest(derived.hex(), stored_hash)
        except Exception:
            return False

    return False


def create_access_token(
    user_id: uuid.UUID,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, str, datetime]:
    """
    Generates a cryptographically signed JWT access token.
    Returns:
        (token_string, jti_identifier, expiration_datetime)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jti = str(uuid.uuid4())
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "role": str(role),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "jti": jti,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti, expire


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and verifies a JWT token.
    Raises:
        jwt.ExpiredSignatureError: when token is expired.
        jwt.InvalidTokenError: when signature or structure is invalid.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "role", "exp", "iat", "jti"]},
    )
