import uuid
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant
    from app.models.order_item import OrderItem


class MenuItem(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        CheckConstraint("price > 0", name="check_menu_item_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
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
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="menu_items"
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="menu_item"
    )

    def __repr__(self) -> str:
        return f"<MenuItem id={self.id} name={self.name} price={self.price} is_available={self.is_available}>"
