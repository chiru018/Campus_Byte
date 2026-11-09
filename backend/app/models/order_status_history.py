import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.user import User


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="status_history")
    changed_by_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="status_changes"
    )

    def __repr__(self) -> str:
        return f"<OrderStatusHistory id={self.id} order_id={self.order_id} new_status={self.new_status}>"
