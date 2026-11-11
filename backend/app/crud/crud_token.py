import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


def revoke_token(
    db: Session,
    jti: str,
    user_id: uuid.UUID,
    expires_at: datetime,
) -> RevokedToken:
    """Inserts a token jti into the revoked denylist."""
    revoked = RevokedToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(revoked)
    db.commit()
    db.refresh(revoked)
    return revoked


def is_token_revoked(db: Session, jti: str) -> bool:
    """Checks whether a token jti exists in the revoked denylist."""
    return db.scalar(select(RevokedToken).where(RevokedToken.jti == jti)) is not None


def cleanup_expired_revoked_tokens(db: Session) -> int:
    """Removes tokens that have passed their natural expiration date."""
    now = datetime.now(timezone.utc)
    result = db.execute(delete(RevokedToken).where(RevokedToken.expires_at < now))
    db.commit()
    return result.rowcount
