import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantAvailabilityUpdate,
    RestaurantResponse,
    RestaurantListResponse,
)
from app.services.restaurant_service import (
    list_restaurants,
    get_restaurant_details,
    create_new_restaurant,
    update_restaurant_info,
    change_restaurant_availability,
    remove_restaurant,
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


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Restaurant",
    description="Registers a new restaurant. Note: `owner_id` manual selection is a Phase 2 development-only mechanism and will be replaced by authenticated JWT identity in Phase 3.",
)
def create_restaurant_endpoint(
    restaurant_in: RestaurantCreate,
    db: Session = Depends(get_db),
):
    return create_new_restaurant(db=db, restaurant_in=restaurant_in)


@router.put(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Update Restaurant Information",
    description="Updates metadata, address, contact, and information for an existing restaurant.",
)
def update_restaurant_endpoint(
    restaurant_id: uuid.UUID,
    update_in: RestaurantUpdate,
    db: Session = Depends(get_db),
):
    return update_restaurant_info(
        db=db, restaurant_id=restaurant_id, update_data=update_in
    )


@router.patch(
    "/{restaurant_id}/availability",
    response_model=RestaurantResponse,
    summary="Update Restaurant Availability",
    description="Toggles or sets the open/closed availability state of the restaurant.",
)
def update_restaurant_availability_endpoint(
    restaurant_id: uuid.UUID,
    availability_in: RestaurantAvailabilityUpdate,
    db: Session = Depends(get_db),
):
    return change_restaurant_availability(
        db=db, restaurant_id=restaurant_id, is_open=availability_in.is_open
    )


@router.delete(
    "/{restaurant_id}",
    summary="Delete or Deactivate Restaurant",
    description="Safely removes a restaurant if it has no orders. If historical orders exist, automatically deactivates (is_open=False) to preserve referential integrity.",
)
def delete_restaurant_endpoint(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    deactivated, message = remove_restaurant(db=db, restaurant_id=restaurant_id)
    return {
        "restaurant_id": restaurant_id,
        "deactivated": deactivated,
        "message": message,
    }
