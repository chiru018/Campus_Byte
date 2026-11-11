import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_optional_url(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip():
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
            raise ValueError("Image URL must start with http://, https://, or /")
    return v


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Restaurant commercial name")
    description: Optional[str] = Field(None, max_length=1000, description="Description of cuisine and outlet")
    address: str = Field(..., min_length=3, max_length=255, description="Physical campus or outlet address")
    contact_number: str = Field(..., min_length=5, max_length=20, description="Contact phone number")
    image_url: Optional[str] = Field(None, max_length=500, description="Hero image or logo URL")

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, v: Optional[str]) -> Optional[str]:
        return validate_optional_url(v)


class RestaurantCreate(RestaurantBase):
    # Optional owner_id for backwards compatibility; in Phase 4 authenticated endpoints,
    # the owner_id is automatically assigned from the authenticated user token.
    owner_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Owner user UUID (assigned server-side from JWT authentication)",
    )
    is_open: bool = Field(default=True, description="Initial availability status")


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    address: Optional[str] = Field(None, min_length=3, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=5, max_length=20)
    image_url: Optional[str] = Field(None, max_length=500)
    is_open: Optional[bool] = None

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, v: Optional[str]) -> Optional[str]:
        return validate_optional_url(v)


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


class RestaurantStatsResponse(BaseModel):
    restaurant_id: uuid.UUID
    restaurant_name: str
    is_open: bool
    total_menu_items: int
    available_menu_items: int
    unavailable_menu_items: int
    profile_completion_percentage: int
