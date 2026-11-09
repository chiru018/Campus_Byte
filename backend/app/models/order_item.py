import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    Numeric,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.menu_item import MenuItem


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
        CheckConstraint("unit_price > 0", name="check_order_item_unit_price_positive"),
        CheckConstraint("total_price > 0", name="check_order_item_total_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("menu_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} item_name={self.item_name} qty={self.quantity} total={self.total_price}>"
