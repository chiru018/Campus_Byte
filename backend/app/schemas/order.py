import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.schemas.order_item import OrderItemCreate, OrderItemResponse


class OrderStatusHistoryResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    previous_status: Optional[str] = None
    new_status: str
    changed_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    delivery_address: str = Field(..., min_length=5, max_length=255, description="Delivery location / room / hostel")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH_ON_DELIVERY)


class OrderCreate(OrderBase):
    restaurant_id: uuid.UUID
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of items with quantity")
    idempotency_key: Optional[str] = Field(None, max_length=64, description="Client-generated unique token to avoid duplicate submissions")


class OrderCancelRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255, description="Optional cancellation reason")


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus
    reason: Optional[str] = Field(None, max_length=255)


class OrderResponse(OrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    restaurant_name: Optional[str] = None
    delivery_partner_id: Optional[uuid.UUID] = None
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    order_status: OrderStatus
    idempotency_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
    status_history: List[OrderStatusHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int = 1
    size: int = 20
