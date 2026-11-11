import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.enums import UserRole
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantStatsResponse,
)
from app.core.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    BusinessRuleException,
    AuthorizationException,
)
import app.crud.crud_restaurant as crud_restaurant
import app.crud.crud_user as crud_user
import app.crud.crud_menu as crud_menu


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


def get_my_restaurant(db: Session, owner_id: uuid.UUID) -> Restaurant:
    restaurant = crud_restaurant.get_restaurant_by_owner_id(db, owner_id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant", f"for owner {owner_id}")
    return restaurant


def create_new_restaurant(
    db: Session,
    restaurant_in: RestaurantCreate,
    owner_id: uuid.UUID,
) -> Restaurant:
    # 1. Verify owner user exists
    owner = crud_user.get_user_by_id(db, owner_id)
    if not owner:
        raise ResourceNotFoundException("User (Restaurant Owner)", owner_id)

    # 2. Check owner role validation
    if owner.role != UserRole.RESTAURANT_OWNER:
        raise BusinessRuleException(
            f"User '{owner.email}' has role '{owner.role.value}', but must have role 'RESTAURANT_OWNER' to own a restaurant."
        )

    # 3. Check MVP 1:1 owner-to-restaurant constraint
    existing = crud_restaurant.get_restaurant_by_owner_id(db, owner_id)
    if existing:
        raise DuplicateResourceException(
            "Restaurant", "owner_id", f"{owner_id} (already owns '{existing.name}')"
        )

    # Force owner_id from authenticated user session
    restaurant_in.owner_id = owner_id
    return crud_restaurant.create_restaurant(db, restaurant_in)


def update_restaurant_info(
    db: Session,
    restaurant_id: uuid.UUID,
    update_data: RestaurantUpdate,
    current_user_id: uuid.UUID,
) -> Restaurant:
    restaurant = get_restaurant_details(db, restaurant_id)
    if restaurant.owner_id != current_user_id:
        raise AuthorizationException("You do not have permission to modify this restaurant.")

    return crud_restaurant.update_restaurant(db, restaurant, update_data)


def change_restaurant_availability(
    db: Session,
    restaurant_id: uuid.UUID,
    is_open: bool,
    current_user_id: uuid.UUID,
) -> Restaurant:
    restaurant = get_restaurant_details(db, restaurant_id)
    if restaurant.owner_id != current_user_id:
        raise AuthorizationException("You do not have permission to modify this restaurant's availability.")

    return crud_restaurant.set_restaurant_availability(db, restaurant, is_open)


def remove_restaurant(
    db: Session,
    restaurant_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> Tuple[bool, str]:
    restaurant = get_restaurant_details(db, restaurant_id)
    if restaurant.owner_id != current_user_id:
        raise AuthorizationException("You do not have permission to delete this restaurant.")

    return crud_restaurant.remove_or_deactivate_restaurant(db, restaurant)


def get_restaurant_stats(
    db: Session,
    restaurant_id: uuid.UUID,
    current_user_id: uuid.UUID,
) -> RestaurantStatsResponse:
    restaurant = get_restaurant_details(db, restaurant_id)
    if restaurant.owner_id != current_user_id:
        raise AuthorizationException("You do not have permission to view statistics for this restaurant.")

    stats = crud_menu.get_menu_stats_by_restaurant(db, restaurant_id)

    # Calculate profile completion percentage based on 5 core fields
    fields = [
        bool(restaurant.name),
        bool(restaurant.description),
        bool(restaurant.address),
        bool(restaurant.contact_number),
        bool(restaurant.image_url),
    ]
    completion = int((sum(fields) / len(fields)) * 100)

    return RestaurantStatsResponse(
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        is_open=restaurant.is_open,
        total_menu_items=stats["total"],
        available_menu_items=stats["available"],
        unavailable_menu_items=stats["unavailable"],
        profile_completion_percentage=completion,
    )
