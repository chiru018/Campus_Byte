import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import FoodCategory


def validate_optional_url(v: Optional[str]) -> Optional[str]:
    if v is not None and v.strip():
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
            raise ValueError("Image URL must start with http://, https://, or /")
    return v


# Canonical set of valid food categories
VALID_CATEGORY_SET = {c.value for c in FoodCategory}

CATEGORY_ALIASES = {
    "MAINS": FoodCategory.OTHER.value,
    "MAIN": FoodCategory.OTHER.value,
    "SIDES": FoodCategory.FAST_FOOD.value,
    "SIDE": FoodCategory.FAST_FOOD.value,
    "DRINKS": FoodCategory.BEVERAGES.value,
    "DRINK": FoodCategory.BEVERAGES.value,
    "SNACKS": FoodCategory.FAST_FOOD.value,
}


def normalize_food_category(v: Any) -> str:
    if not v or not str(v).strip():
        raise ValueError("Category is required.")
    cleaned = str(v).strip().upper().replace(" ", "_").replace("-", "_")
    if cleaned in VALID_CATEGORY_SET:
        return cleaned
    if cleaned in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cleaned]
    allowed_list = ", ".join(sorted(VALID_CATEGORY_SET))
    raise ValueError(f"Invalid food category '{v}'. Allowed categories are: {allowed_list}")


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Name of dish or item")
    description: Optional[str] = Field(None, max_length=1000, description="Item description and ingredients")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Price in currency units (must be > 0)")
    category: str = Field(..., min_length=1, max_length=50, description="Menu category (e.g. BIRYANI, BURGERS, BEVERAGES)")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    is_available: bool = Field(default=True, description="Item stock availability flag")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Any) -> str:
        return normalize_food_category(v)

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, v: Optional[str]) -> Optional[str]:
        return validate_optional_url(v)


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_food_category(v)
        return v

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, v: Optional[str]) -> Optional[str]:
        return validate_optional_url(v)


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


class CategoryResponse(BaseModel):
    key: str
    label: str
