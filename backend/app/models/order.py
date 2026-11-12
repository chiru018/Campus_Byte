import uuid
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.restaurant import Restaurant
    from app.models.delivery_partner import DeliveryPartner
    from app.models.order_item import OrderItem
    from app.models.delivery_assignment import DeliveryAssignment
    from app.models.order_status_history import OrderStatusHistory


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="check_order_subtotal_non_negative"),
        CheckConstraint("delivery_fee >= 0", name="check_order_delivery_fee_non_negative"),
        CheckConstraint("total_amount >= 0", name="check_order_total_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    delivery_partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("delivery_partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    delivery_address: Mapped[str] = mapped_column(String(255), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod, native_enum=False, length=30),
        default=PaymentMethod.CASH_ON_DELIVERY,
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, native_enum=False, length=20),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )
    order_status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, native_enum=False, length=30),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    preparing_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ready_for_pickup_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    customer: Mapped["User"] = relationship(
        "User", back_populates="orders", foreign_keys=[customer_id]
    )
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="orders", foreign_keys=[restaurant_id]
    )
    delivery_partner: Mapped[Optional["DeliveryPartner"]] = relationship(
        "DeliveryPartner", back_populates="assigned_orders", foreign_keys=[delivery_partner_id]
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    delivery_assignments: Mapped[List["DeliveryAssignment"]] = relationship(
        "DeliveryAssignment", back_populates="order", cascade="all, delete-orphan"
    )
    status_history: Mapped[List["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.order_status} total={self.total_amount}>"

