import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeliveryStatus, VehicleType


class DeliveryPartnerBase(BaseModel):
    vehicle_type: VehicleType = Field(default=VehicleType.BICYCLE)
    is_available: bool = Field(default=True)


class DeliveryPartnerCreate(DeliveryPartnerBase):
    user_id: uuid.UUID


class DeliveryPartnerUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    is_available: Optional[bool] = None


class DeliveryPartnerResponse(DeliveryPartnerBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryAssignmentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    delivery_partner_id: uuid.UUID
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_status: DeliveryStatus

    model_config = ConfigDict(from_attributes=True)
