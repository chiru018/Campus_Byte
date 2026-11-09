import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.enums import UserRole
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.core.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    BusinessRuleException,
)
import app.crud.crud_restaurant as crud_restaurant
import app.crud.crud_user as crud_user


def list_restaurants(
    db: Session,
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    is_open: Optional[bool] = None,
) -> Tuple[List[Restaurant], int]:
    skip = (max(page, 1) - 1) * max(size, 1)
    return crud_restaurant.get_restaurants(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        is_open=is_open,
    )


def get_restaurant_details(db: Session, restaurant_id: uuid.UUID) -> Restaurant:
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant", restaurant_id)
    return restaurant


def create_new_restaurant(db: Session, restaurant_in: RestaurantCreate) -> Restaurant:
    # 1. Verify owner user exists
    owner = crud_user.get_user_by_id(db, restaurant_in.owner_id)
    if not owner:
        raise ResourceNotFoundException("User (Restaurant Owner)", restaurant_in.owner_id)

    # 2. Check owner role validation
    if owner.role != UserRole.RESTAURANT_OWNER:
        raise BusinessRuleException(
            f"User '{owner.email}' has role '{owner.role.value}', but must have role 'RESTAURANT_OWNER' to own a restaurant."
        )

    # 3. Check MVP 1:1 owner-to-restaurant constraint
    existing = crud_restaurant.get_restaurant_by_owner_id(db, restaurant_in.owner_id)
    if existing:
        raise DuplicateResourceException(
            "Restaurant", "owner_id", f"{restaurant_in.owner_id} (already owns '{existing.name}')"
        )

    return crud_restaurant.create_restaurant(db, restaurant_in)


def update_restaurant_info(
    db: Session, restaurant_id: uuid.UUID, update_data: RestaurantUpdate
) -> Restaurant:
    restaurant = get_restaurant_details(db, restaurant_id)
    return crud_restaurant.update_restaurant(db, restaurant, update_data)


def change_restaurant_availability(
    db: Session, restaurant_id: uuid.UUID, is_open: bool
) -> Restaurant:
    restaurant = get_restaurant_details(db, restaurant_id)
    return crud_restaurant.set_restaurant_availability(db, restaurant, is_open)


def remove_restaurant(db: Session, restaurant_id: uuid.UUID) -> Tuple[bool, str]:
    restaurant = get_restaurant_details(db, restaurant_id)
    return crud_restaurant.remove_or_deactivate_restaurant(db, restaurant)
