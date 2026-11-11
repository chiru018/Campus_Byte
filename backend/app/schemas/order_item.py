import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class OrderItemBase(BaseModel):
    menu_item_id: uuid.UUID
    item_name: str = Field(..., min_length=1, max_length=120)
    unit_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)


class OrderItemCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(..., gt=0, description="Quantity ordered (must be > 0)")


class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    order_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

