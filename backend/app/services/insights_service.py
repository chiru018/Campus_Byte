import uuid
import logging
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.enums import OrderStatus
from app.core.config import settings
from app.schemas.insights import (
    SpendingSummaryResponse,
    MonthlySpendItem,
    OrderingPatternsResponse,
    PopularDishItem,
    FavouriteRestaurantItem,
    CategoryFrequencyItem,
    RecommendationsResponse,
    RecommendedDishItem,
    AiNarrativeResponse,
)

logger = logging.getLogger(__name__)


def get_spending_summary(db: Session, customer_id: uuid.UUID) -> SpendingSummaryResponse:
    """Computes real historical spending analytics isolated for the authenticated customer."""
    # Fetch all orders for this customer
    stmt = (
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.asc())
    )
    orders = list(db.scalars(stmt).all())

    total_orders = len(orders)
    completed_orders = [o for o in orders if o.order_status == OrderStatus.DELIVERED.value]
    total_spent = sum((o.total_amount for o in completed_orders), Decimal("0.00"))
    avg_order_value = (
        round(total_spent / Decimal(len(completed_orders)), 2)
        if completed_orders
        else Decimal("0.00")
    )

    # Group by month (YYYY-MM)
    monthly_map: Dict[str, Dict[str, Decimal | int]] = defaultdict(
        lambda: {"amount": Decimal("0.00"), "count": 0}
    )

    for o in completed_orders:
        month_key = o.created_at.strftime("%Y-%m")
        monthly_map[month_key]["amount"] += o.total_amount
        monthly_map[month_key]["count"] += 1

    monthly_spending = [
        MonthlySpendItem(
            month=m,
            amount=round(data["amount"], 2),
            order_count=data["count"],
        )
        for m, data in sorted(monthly_map.items())
    ]

    highest_spending_month = None
    if monthly_spending:
        highest_spending_month = max(monthly_spending, key=lambda x: x.amount).month

    return SpendingSummaryResponse(
        total_spent=round(total_spent, 2),
        total_orders=total_orders,
        completed_orders=len(completed_orders),
        average_order_value=avg_order_value,
        highest_spending_month=highest_spending_month,
        monthly_spending=monthly_spending,
    )


def get_ordering_patterns(db: Session, customer_id: uuid.UUID) -> OrderingPatternsResponse:
    """Analyzes customer ordering habits, favorite dishes, restaurants, and top food categories."""
    # Completed orders
    completed_orders_stmt = (
        select(Order.id, Order.restaurant_id, Order.total_amount, Order.created_at)
        .where(Order.customer_id == customer_id, Order.order_status == OrderStatus.DELIVERED.value)
    )
    completed_rows = db.execute(completed_orders_stmt).all()
    completed_order_ids = [row[0] for row in completed_rows]

    if not completed_order_ids:
        return OrderingPatternsResponse(
            top_dishes=[],
            favourite_restaurants=[],
            top_categories=[],
            order_frequency_per_month=0.0,
        )

    # 1. Top Dishes
    items_stmt = (
        select(OrderItem, MenuItem)
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.id, isouter=True)
        .where(OrderItem.order_id.in_(completed_order_ids))
    )
    item_rows = db.execute(items_stmt).all()

    dish_stats = defaultdict(lambda: {"qty": 0, "spent": Decimal("0.00"), "category": "Food", "id": None})
    cat_stats = defaultdict(lambda: {"count": 0, "items": 0})

    for oi, mi in item_rows:
        dish_name = oi.item_name
        cat = mi.category if mi else "Food"
        dish_stats[dish_name]["qty"] += oi.quantity
        dish_stats[dish_name]["spent"] += oi.total_price
        dish_stats[dish_name]["category"] = cat
        dish_stats[dish_name]["id"] = oi.menu_item_id

        cat_stats[cat]["count"] += 1
        cat_stats[cat]["items"] += oi.quantity

    top_dishes = [
        PopularDishItem(
            menu_item_id=info["id"],
            dish_name=name,
            category=info["category"],
            total_quantity=info["qty"],
            total_spent=round(info["spent"], 2),
        )
        for name, info in sorted(dish_stats.items(), key=lambda x: x[1]["qty"], reverse=True)[:5]
    ]

    top_categories = [
        CategoryFrequencyItem(
            category=c,
            order_count=data["count"],
            total_items=data["items"],
        )
        for c, data in sorted(cat_stats.items(), key=lambda x: x[1]["items"], reverse=True)[:5]
    ]

    # 2. Favourite Restaurants
    rest_stats = defaultdict(lambda: {"count": 0, "spent": Decimal("0.00")})
    for _, r_id, tot, _ in completed_rows:
        rest_stats[r_id]["count"] += 1
        rest_stats[r_id]["spent"] += tot

    favourite_restaurants = []
    for r_id, stats in sorted(rest_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:3]:
        rest = db.get(Restaurant, r_id)
        favourite_restaurants.append(
            FavouriteRestaurantItem(
                restaurant_id=r_id,
                restaurant_name=rest.name if rest else "Campus Outlet",
                order_count=stats["count"],
                total_spent=round(stats["spent"], 2),
            )
        )

    # 3. Order frequency per month
    if completed_rows:
        dates = [r[3] for r in completed_rows if r[3]]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            days_span = max((max_date - min_date).days, 1)
            months_span = max(days_span / 30.0, 1.0)
            order_frequency = round(len(completed_rows) / months_span, 1)
        else:
            order_frequency = float(len(completed_rows))
    else:
        order_frequency = 0.0

    return OrderingPatternsResponse(
        top_dishes=top_dishes,
        favourite_restaurants=favourite_restaurants,
        top_categories=top_categories,
        order_frequency_per_month=order_frequency,
    )


def get_personalized_recommendations(db: Session, customer_id: uuid.UUID) -> RecommendationsResponse:
    """Recommends active menu items based on previous category preferences and popular campus dishes."""
    # Find customer's top ordered categories & dishes
    patterns = get_ordering_patterns(db, customer_id)
    fav_cats = [c.category for c in patterns.top_categories]
    ordered_dish_ids = {d.menu_item_id for d in patterns.top_dishes if d.menu_item_id}

    # Query active menu items
    base_stmt = select(MenuItem, Restaurant).join(Restaurant, MenuItem.restaurant_id == Restaurant.id).where(
        MenuItem.is_available == True,
        Restaurant.is_open == True,
    )

    all_items = db.execute(base_stmt).all()

    recommendations: List[RecommendedDishItem] = []

    # 1. Recommend dishes from customer's favourite categories that haven't been ordered yet
    for mi, rest in all_items:
        if mi.category in fav_cats and mi.id not in ordered_dish_ids:
            recommendations.append(
                RecommendedDishItem(
                    menu_item_id=mi.id,
                    dish_name=mi.name,
                    restaurant_id=rest.id,
                    restaurant_name=rest.name,
                    price=round(mi.price, 2),
                    category=mi.category,
                    image_url=mi.image_url,
                    reason=f"Recommended because you enjoy {mi.category} dishes",
                )
            )
            if len(recommendations) >= 4:
                break

    # 2. If fewer than 4 recommendations, add top available dishes from other categories
    if len(recommendations) < 4:
        for mi, rest in all_items:
            if not any(r.menu_item_id == mi.id for r in recommendations):
                recommendations.append(
                    RecommendedDishItem(
                        menu_item_id=mi.id,
                        dish_name=mi.name,
                        restaurant_id=rest.id,
                        restaurant_name=rest.name,
                        price=round(mi.price, 2),
                        category=mi.category,
                        image_url=mi.image_url,
                        reason=f"Popular campus favourite from {rest.name}",
                    )
                )
                if len(recommendations) >= 4:
                    break

    return RecommendationsResponse(
        recommendations=recommendations,
        favourite_categories=fav_cats,
    )


def generate_rule_based_narrative(
    user_name: str,
    spending: SpendingSummaryResponse,
    patterns: OrderingPatternsResponse,
) -> Tuple[str, List[str]]:
    """Builds an intelligent, factual natural language narrative based purely on verified database analytics."""
    highlights = []

    if spending.completed_orders == 0:
        narrative = (
            f"Welcome to Campus Byte, {user_name}! You have not completed any deliveries yet. "
            "Once you place your first order from our campus dining spots, your personalized spending analysis "
            "and food habit insights will appear here automatically."
        )
        highlights.append("No order history recorded yet")
        highlights.append("Explore campus eateries to unlock personalized insights")
        return narrative, highlights

    top_dish_str = patterns.top_dishes[0].dish_name if patterns.top_dishes else "campus food"
    top_cat_str = patterns.top_categories[0].category if patterns.top_categories else "diverse cuisines"
    fav_rest_str = patterns.favourite_restaurants[0].restaurant_name if patterns.favourite_restaurants else "campus dining"

    narrative = (
        f"Hi {user_name}, you have placed {spending.completed_orders} completed orders with a total spending of "
        f"₹{spending.total_spent:.2f} (averaging ₹{spending.average_order_value:.2f} per meal). "
        f"Your absolute favourite dish is {top_dish_str}, and your most visited dining spot is {fav_rest_str}. "
        f"You have a strong preference for {top_cat_str}, ordering approximately {patterns.order_frequency_per_month} "
        "times per month."
    )

    highlights.append(f"Total Dining Spend: ₹{spending.total_spent:.2f} across {spending.completed_orders} orders")
    highlights.append(f"Top Ordered Dish: {top_dish_str}")
    highlights.append(f"Preferred Campus Spot: {fav_rest_str}")
    highlights.append(f"Average Ticket Size: ₹{spending.average_order_value:.2f}")

    return narrative, highlights


def get_ai_insights_narrative(
    db: Session,
    customer_id: uuid.UUID,
    user_name: str,
) -> AiNarrativeResponse:
    """Generates AI insights using Gemini API if configured/reachable, with graceful rule-based fallback."""
    spending = get_spending_summary(db, customer_id)
    patterns = get_ordering_patterns(db, customer_id)

    # Default fallback
    rule_narrative, highlights = generate_rule_based_narrative(user_name, spending, patterns)

    if not settings.GEMINI_API_KEY or spending.completed_orders == 0:
        return AiNarrativeResponse(
            narrative=rule_narrative,
            source="rule_based",
            generated_at=datetime.now(timezone.utc).isoformat(),
            key_highlights=highlights,
        )

    # Attempt to invoke Gemini API with a strict 3.5s timeout
    try:
        top_dish = patterns.top_dishes[0].dish_name if patterns.top_dishes else "None"
        fav_rest = patterns.favourite_restaurants[0].restaurant_name if patterns.favourite_restaurants else "None"
        top_cat = patterns.top_categories[0].category if patterns.top_categories else "None"

        prompt = (
            f"You are a friendly dining assistant for the university campus food platform 'Campus Byte'. "
            f"Summarize this student's dining habits in 2 concise, energetic sentences. "
            f"Student Name: {user_name}. "
            f"Completed Orders: {spending.completed_orders}. "
            f"Total Spent: ₹{spending.total_spent}. "
            f"Average Order Value: ₹{spending.average_order_value}. "
            f"Top Dish: {top_dish}. "
            f"Favourite Restaurant: {fav_rest}. "
            f"Top Category: {top_cat}. "
            f"Do not invent facts. Address the student directly."
        )

        model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        resp = httpx.post(api_url, json=payload, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    ai_text = parts[0]["text"].strip()
                    return AiNarrativeResponse(
                        narrative=ai_text,
                        source="gemini",
                        generated_at=datetime.now(timezone.utc).isoformat(),
                        key_highlights=highlights,
                    )
        logger.warning("Gemini API non-200 response: %s %s. Falling back to rule-based.", resp.status_code, resp.text[:100])
    except Exception as e:
        logger.warning("Gemini API call failed (%s). Falling back to rule-based insights.", str(e))

    return AiNarrativeResponse(
        narrative=rule_narrative,
        source="rule_based",
        generated_at=datetime.now(timezone.utc).isoformat(),
        key_highlights=highlights,
    )

