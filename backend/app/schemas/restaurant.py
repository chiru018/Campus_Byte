import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Restaurant commercial name")
    description: Optional[str] = Field(None, max_length=1000, description="Description of cuisine and outlet")
    address: str = Field(..., min_length=3, max_length=255, description="Physical campus or outlet address")
    contact_number: str = Field(..., min_length=5, max_length=20, description="Contact phone number")
    image_url: Optional[str] = Field(None, max_length=500, description="Hero image or logo URL")


class RestaurantCreate(RestaurantBase):
    # Isolated temporary owner selection mechanism for Phase 2 development.
    # In Phase 3, owner_id will be automatically populated from authenticated JWT session.
    owner_id: uuid.UUID = Field(
        ...,
        description="Owner user UUID (Temporary Phase 2 manual selection; replaced by JWT auth in Phase 3)"
    )
    is_open: bool = Field(default=True, description="Initial availability status")


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    address: Optional[str] = Field(None, min_length=3, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=5, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)
    is_open: Optional[bool] = None


class RestaurantAvailabilityUpdate(BaseModel):
    is_open: bool = Field(..., description="Target open/closed availability state")


class RestaurantResponse(RestaurantBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    is_open: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RestaurantListResponse(BaseModel):
    restaurants: List[RestaurantResponse]
    total: int
    page: int
    size: int

