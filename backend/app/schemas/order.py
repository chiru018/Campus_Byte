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
    changed_by_role: Optional[str] = None
    notes: Optional[str] = None
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


class OrderRejectRequest(BaseModel):
    reason: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Mandatory reason explaining why the kitchen cannot fulfill this order",
    )


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus
    reason: Optional[str] = Field(None, max_length=255)


class OrderResponse(OrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    restaurant_id: uuid.UUID
    restaurant_name: Optional[str] = None
    delivery_partner_id: Optional[uuid.UUID] = None
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    order_status: OrderStatus
    idempotency_key: Optional[str] = None
    rejection_reason: Optional[str] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    preparing_at: Optional[datetime] = None
    ready_for_pickup_at: Optional[datetime] = None
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


class RestaurantOrderStatsResponse(BaseModel):
    total_orders: int = 0
    pending_orders: int = 0
    accepted_orders: int = 0
    preparing_orders: int = 0
    ready_for_pickup_orders: int = 0
    rejected_orders: int = 0
    cancelled_orders: int = 0
    delivered_orders: int = 0


class NewOrdersNotificationResponse(BaseModel):
    new_orders_count: int = 0
    pending_orders: List[OrderResponse] = []
    latest_cursor: Optional[datetime] = None
