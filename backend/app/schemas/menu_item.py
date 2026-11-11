import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Name of dish or item")
    description: Optional[str] = Field(None, max_length=1000, description="Item description and ingredients")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Price in currency units (must be > 0)")
    category: str = Field(..., min_length=1, max_length=50, description="Menu category (e.g., Beverages, Mains, Snacks)")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    is_available: bool = Field(default=True, description="Item stock availability flag")


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None


class MenuItemAvailabilityUpdate(BaseModel):
    is_available: bool = Field(..., description="Target item availability flag")


class MenuItemResponse(MenuItemBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MenuItemListResponse(BaseModel):
    items: List[MenuItemResponse]
    total: int

