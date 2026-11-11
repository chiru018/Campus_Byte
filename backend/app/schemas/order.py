import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.schemas.order_item import OrderItemCreate, OrderItemResponse


class OrderBase(BaseModel):
    delivery_address: str = Field(..., min_length=3, max_length=255)
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH_ON_DELIVERY)


class OrderCreate(OrderBase):
    restaurant_id: uuid.UUID
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus
    reason: Optional[str] = Field(None, max_length=255)


class OrderResponse(OrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    delivery_partner_id: Optional[uuid.UUID] = None
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    order_status: OrderStatus
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int

