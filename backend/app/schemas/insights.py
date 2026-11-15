import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MonthlySpendItem(BaseModel):
    month: str  # e.g. "2026-11" or "Nov 2026"
    amount: Decimal
    order_count: int


class SpendingSummaryResponse(BaseModel):
    total_spent: Decimal
    total_orders: int
    completed_orders: int
    average_order_value: Decimal
    highest_spending_month: Optional[str] = None
    monthly_spending: List[MonthlySpendItem]


class PopularDishItem(BaseModel):
    menu_item_id: Optional[uuid.UUID] = None
    dish_name: str
    category: str
    total_quantity: int
    total_spent: Decimal


class FavouriteRestaurantItem(BaseModel):
    restaurant_id: uuid.UUID
    restaurant_name: str
    order_count: int
    total_spent: Decimal


class CategoryFrequencyItem(BaseModel):
    category: str
    order_count: int
    total_items: int


class OrderingPatternsResponse(BaseModel):
    top_dishes: List[PopularDishItem]
    favourite_restaurants: List[FavouriteRestaurantItem]
    top_categories: List[CategoryFrequencyItem]
    order_frequency_per_month: float


class RecommendedDishItem(BaseModel):
    menu_item_id: uuid.UUID
    dish_name: str
    restaurant_id: uuid.UUID
    restaurant_name: str
    price: Decimal
    category: str
    image_url: Optional[str] = None
    reason: str


class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendedDishItem]
    favourite_categories: List[str]


class AiNarrativeResponse(BaseModel):
    narrative: str
    source: str  # "gemini" or "rule_based"
    generated_at: str
    key_highlights: List[str]

