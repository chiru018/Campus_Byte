import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import DeliveryStatus

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.delivery_partner import DeliveryPartner


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    delivery_partner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("delivery_partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    picked_up_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        SAEnum(DeliveryStatus, native_enum=False, length=20),
        default=DeliveryStatus.ASSIGNED,
        nullable=False,
        index=True,
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order", back_populates="delivery_assignments"
    )
    delivery_partner: Mapped["DeliveryPartner"] = relationship(
        "DeliveryPartner", back_populates="assignments"
    )

    def __repr__(self) -> str:
        return f"<DeliveryAssignment id={self.id} order_id={self.order_id} status={self.delivery_status}>"

