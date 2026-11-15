import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    order_id: uuid.UUID = Field(..., description="ID of the qualifying delivered order")
    restaurant_id: Optional[uuid.UUID] = Field(None, description="Optional restaurant ID")
    rating: int = Field(..., ge=1, le=5, description="Integer rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment, max 1000 characters")


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Integer rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment, max 1000 characters")


class ReviewResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    customer_name: Optional[str] = None
    restaurant_id: uuid.UUID
    restaurant_name: Optional[str] = None
    order_id: uuid.UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RestaurantReviewSummary(BaseModel):
    restaurant_id: uuid.UUID
    restaurant_name: str
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]
    reviews: List[ReviewResponse]

