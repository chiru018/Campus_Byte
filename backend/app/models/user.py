import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.delivery_partner import DeliveryPartner
    from app.models.order import Order
    from app.models.order_status_history import OrderStatusHistory


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False, length=30),
        default=UserRole.CUSTOMER,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    restaurant: Mapped[Optional["Restaurant"]] = relationship(
        "Restaurant", back_populates="owner", uselist=False
    )
    delivery_profile: Mapped[Optional["DeliveryPartner"]] = relationship(
        "DeliveryPartner", back_populates="user", uselist=False
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="customer", foreign_keys="Order.customer_id"
    )
    status_changes: Mapped[List["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory", back_populates="changed_by_user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"

