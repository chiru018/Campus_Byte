import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class RevokedToken(Base):
    """
    Server-side token denylist tracking revoked JWT tokens by jti.
    Prevents re-use of logged-out tokens before their natural expiration.
    """
    __tablename__ = "revoked_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<RevokedToken jti={self.jti} user_id={self.user_id}>"
