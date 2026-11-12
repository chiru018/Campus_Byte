import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeliveryStatus, VehicleType, PartnerAvailability, PaymentMethod, PaymentStatus, OrderStatus
from app.schemas.order_item import OrderItemResponse
from app.schemas.order import OrderStatusHistoryResponse


class DeliveryPartnerBase(BaseModel):
    vehicle_type: VehicleType = Field(default=VehicleType.BICYCLE)
    vehicle_registration_number: Optional[str] = Field(None, max_length=50)
    availability_status: PartnerAvailability = Field(default=PartnerAvailability.AVAILABLE)
    is_available: bool = Field(default=True)


class DeliveryPartnerCreate(DeliveryPartnerBase):
    user_id: uuid.UUID


class DeliveryPartnerUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    vehicle_registration_number: Optional[str] = None
    is_available: Optional[bool] = None
    availability_status: Optional[PartnerAvailability] = None


class DeliveryPartnerProfileUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    vehicle_registration_number: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)


class AvailabilityUpdateRequest(BaseModel):
    availability_status: PartnerAvailability = Field(
        ..., description="Desired operational state: OFFLINE, AVAILABLE, or BUSY"
    )


class DeliveryPartnerResponse(DeliveryPartnerBase):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryStatsResponse(BaseModel):
    available_requests_count: int = 0
    active_delivery_count: int = 0
    completed_deliveries_count: int = 0
    total_deliveries_count: int = 0
    total_cod_collected: Decimal = Decimal("0.00")
    availability_status: PartnerAvailability = PartnerAvailability.AVAILABLE


class AvailableDeliveryOrderResponse(BaseModel):
    order_id: uuid.UUID
    restaurant_name: str
    restaurant_address: str
    restaurant_phone: Optional[str] = None
    delivery_area: str
    delivery_address: str
    item_count: int
    items_summary: str
    total_amount: Decimal
    payment_method: PaymentMethod
    created_at: datetime
    ready_for_pickup_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AvailableDeliveryOrderListResponse(BaseModel):
    orders: List[AvailableDeliveryOrderResponse]
    total: int
    page: int = 1
    size: int = 20


class ActiveDeliveryResponse(BaseModel):
    order_id: uuid.UUID
    assignment_id: uuid.UUID
    order_status: OrderStatus
    delivery_status: DeliveryStatus
    restaurant_name: str
    restaurant_address: str
    restaurant_phone: Optional[str] = None
    customer_name: str
    customer_phone: Optional[str] = None
    delivery_address: str
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    cod_collected: bool = False
    items: List[OrderItemResponse] = []
    item_count: int = 0
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    out_for_delivery_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    status_history: List[OrderStatusHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DeliveryAssignmentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    delivery_partner_id: uuid.UUID
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    started_delivery_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivery_status: DeliveryStatus

    model_config = ConfigDict(from_attributes=True)


class DeliveryCompleteRequest(BaseModel):
    confirm_delivered: bool = Field(True, description="Confirmation of physical handover to customer")
    confirm_cash_collected: Optional[bool] = Field(None, description="Confirmation of COD payment collection")
    collected_amount: Optional[Decimal] = Field(None, description="Actual cash amount collected from customer")


class CODConfirmRequest(BaseModel):
    confirm_cash_collected: bool = Field(True, description="Confirmation of physical cash receipt")
    collected_amount: Decimal = Field(..., gt=0, description="Exact currency amount collected")


class CODStatusResponse(BaseModel):
    order_id: uuid.UUID
    is_cod: bool
    total_amount: Decimal
    payment_status: PaymentStatus
    cod_collected: bool
    cod_collected_at: Optional[datetime] = None
    cod_collected_by_name: Optional[str] = None


class DeliveryHistoryItemResponse(BaseModel):
    order_id: uuid.UUID
    assignment_id: uuid.UUID
    restaurant_name: str
    delivery_address: str
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    order_status: OrderStatus
    delivery_status: DeliveryStatus
    cod_collected: bool = False
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryHistoryListResponse(BaseModel):
    items: List[DeliveryHistoryItemResponse]
    total: int
    page: int = 1
    size: int = 20
