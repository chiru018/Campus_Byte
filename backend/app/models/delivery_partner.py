import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import VehicleType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order import Order
    from app.models.delivery_assignment import DeliveryAssignment


class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SAEnum(VehicleType, native_enum=False, length=20),
        default=VehicleType.BICYCLE,
        nullable=False,
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="delivery_profile")
    assigned_orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="delivery_partner"
    )
    assignments: Mapped[List["DeliveryAssignment"]] = relationship(
        "DeliveryAssignment", back_populates="delivery_partner"
    )

    def __repr__(self) -> str:
        return f"<DeliveryPartner id={self.id} user_id={self.user_id} vehicle={self.vehicle_type}>"
