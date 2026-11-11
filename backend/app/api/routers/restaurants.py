import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_restaurant_owner
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantAvailabilityUpdate,
    RestaurantResponse,
    RestaurantListResponse,
    RestaurantStatsResponse,
)
from app.services.restaurant_service import (
    list_restaurants,
    get_restaurant_details,
    get_my_restaurant,
    create_new_restaurant,
    update_restaurant_info,
    change_restaurant_availability,
    remove_restaurant,
    get_restaurant_stats,
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get(
    "",
    response_model=RestaurantListResponse,
    summary="List Restaurants",
    description="Retrieves a paginated list of campus food outlets, with optional search filtering by name/address and filter by availability.",
)
def get_restaurants_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search keyword for restaurant name or description"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    db: Session = Depends(get_db),
):
    items, total = list_restaurants(
        db=db, page=page, size=size, search=search, is_open=is_open
    )
    return RestaurantListResponse(
        restaurants=items, total=total, page=page, size=size
    )


@router.get(
    "/my-restaurant",
    response_model=RestaurantResponse,
    summary="Get My Restaurant Profile",
    description="Retrieves the restaurant profile owned by the currently authenticated restaurant owner.",
)
def get_my_restaurant_endpoint(
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return get_my_restaurant(db=db, owner_id=current_user.id)


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Get Restaurant Details",
    description="Retrieves full profile details for a specific campus food outlet by ID.",
)
def get_restaurant_by_id_endpoint(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return get_restaurant_details(db=db, restaurant_id=restaurant_id)


@router.get(
    "/{restaurant_id}/stats",
    response_model=RestaurantStatsResponse,
    summary="Get Restaurant Statistics",
    description="Retrieves menu item metrics and profile completion for the authenticated restaurant owner.",
)
def get_restaurant_stats_endpoint(
    restaurant_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return get_restaurant_stats(
        db=db, restaurant_id=restaurant_id, current_user_id=current_user.id
    )


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Restaurant",
    description="Registers a new restaurant for the authenticated owner. Automatically links the restaurant to the owner's identity.",
)
def create_restaurant_endpoint(
    restaurant_in: RestaurantCreate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return create_new_restaurant(
        db=db, restaurant_in=restaurant_in, owner_id=current_user.id
    )


@router.put(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Update Restaurant Information",
    description="Updates metadata, address, contact, and information for an existing restaurant. Enforces owner authorization.",
)
def update_restaurant_endpoint(
    restaurant_id: uuid.UUID,
    update_in: RestaurantUpdate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return update_restaurant_info(
        db=db,
        restaurant_id=restaurant_id,
        update_data=update_in,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{restaurant_id}/availability",
    response_model=RestaurantResponse,
    summary="Update Restaurant Availability",
    description="Toggles or sets the open/closed availability state of the restaurant. Enforces owner authorization.",
)
def update_restaurant_availability_endpoint(
    restaurant_id: uuid.UUID,
    availability_in: RestaurantAvailabilityUpdate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return change_restaurant_availability(
        db=db,
        restaurant_id=restaurant_id,
        is_open=availability_in.is_open,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete or Deactivate Restaurant",
    description="Safely removes or deactivates a restaurant. If historical orders exist, preserves data integrity by deactivating (is_open=False).",
)
def delete_restaurant_endpoint(
    restaurant_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    was_deactivated, message = remove_restaurant(
        db=db, restaurant_id=restaurant_id, current_user_id=current_user.id
    )
    return {
        "restaurant_id": restaurant_id,
        "is_deactivated": was_deactivated,
        "message": message,
    }
