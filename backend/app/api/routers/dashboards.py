from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get(
    "/stats",
    summary="Platform Dashboard Statistics",
    description="Returns aggregate counts of restaurants, active menus, and registered stakeholder roles across Campus Byte.",
)
def get_dashboard_stats_endpoint(
    db: Session = Depends(get_db),
):
    total_restaurants = db.scalar(select(func.count(Restaurant.id))) or 0
    open_restaurants = db.scalar(
        select(func.count(Restaurant.id)).where(Restaurant.is_open == True)  # noqa: E712
    ) or 0

    total_menu_items = db.scalar(select(func.count(MenuItem.id))) or 0
    available_menu_items = db.scalar(
        select(func.count(MenuItem.id)).where(MenuItem.is_available == True)  # noqa: E712
    ) or 0

    total_users = db.scalar(select(func.count(User.id))) or 0
    total_customers = db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    ) or 0
    total_owners = db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.RESTAURANT_OWNER)
    ) or 0
    total_couriers = db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.DELIVERY_PARTNER)
    ) or 0

    return {
        "restaurants": {
            "total": total_restaurants,
            "open": open_restaurants,
            "closed": total_restaurants - open_restaurants,
        },
        "menu_items": {
            "total": total_menu_items,
            "available": available_menu_items,
            "unavailable": total_menu_items - available_menu_items,
        },
        "users": {
            "total": total_users,
            "customers": total_customers,
            "restaurant_owners": total_owners,
            "delivery_partners": total_couriers,
        },
    }

