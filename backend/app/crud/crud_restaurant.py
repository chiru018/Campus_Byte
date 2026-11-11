import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.order import Order
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def get_restaurant_by_id(db: Session, restaurant_id: uuid.UUID) -> Optional[Restaurant]:
    return db.scalar(select(Restaurant).where(Restaurant.id == restaurant_id))


def get_restaurant_by_owner_id(db: Session, owner_id: uuid.UUID) -> Optional[Restaurant]:
    return db.scalar(select(Restaurant).where(Restaurant.owner_id == owner_id))


def get_restaurants(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    is_open: Optional[bool] = None,
) -> Tuple[List[Restaurant], int]:
    query = select(Restaurant)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            or_(
                Restaurant.name.ilike(search_filter),
                Restaurant.description.ilike(search_filter),
                Restaurant.address.ilike(search_filter),
            )
        )

    if is_open is not None:
        query = query.where(Restaurant.is_open == is_open)

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Paginate and order by created_at descending
    query = query.order_by(Restaurant.created_at.desc()).offset(skip).limit(limit)
    items = list(db.scalars(query).all())

    return items, total


def create_restaurant(db: Session, restaurant_in: RestaurantCreate) -> Restaurant:
    restaurant = Restaurant(
        owner_id=restaurant_in.owner_id,
        name=restaurant_in.name,
        description=restaurant_in.description,
        address=restaurant_in.address,
        contact_number=restaurant_in.contact_number,
        image_url=restaurant_in.image_url,
        is_open=restaurant_in.is_open,
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def update_restaurant(
    db: Session, restaurant_obj: Restaurant, update_data: RestaurantUpdate
) -> Restaurant:
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(restaurant_obj, field, value)
    db.commit()
    db.refresh(restaurant_obj)
    return restaurant_obj


def set_restaurant_availability(
    db: Session, restaurant_obj: Restaurant, is_open: bool
) -> Restaurant:
    restaurant_obj.is_open = is_open
    db.commit()
    db.refresh(restaurant_obj)
    return restaurant_obj


def remove_or_deactivate_restaurant(
    db: Session, restaurant_obj: Restaurant
) -> Tuple[bool, str]:
    """
    Safely handles restaurant removal.
    If the restaurant has associated orders, it deactivates (is_open=False) to preserve historical data.
    If no orders exist, performs safe deletion.
    """
    orders_count = db.scalar(
        select(func.count(Order.id)).where(Order.restaurant_id == restaurant_obj.id)
    ) or 0

    if orders_count > 0:
        restaurant_obj.is_open = False
        db.commit()
        return True, "Restaurant has existing order history; it was successfully deactivated rather than deleted."
    else:
        db.delete(restaurant_obj)
        db.commit()
        return False, "Restaurant was successfully removed."

