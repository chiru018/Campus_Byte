import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_restaurant_owner
from app.schemas.menu_item import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemAvailabilityUpdate,
    MenuItemResponse,
    MenuItemListResponse,
    CategoryResponse,
)
from app.services.menu_service import (
    list_menu_items,
    get_item_details,
    add_item_to_menu,
    update_item,
    toggle_item_availability,
    remove_item,
    get_categories_list,
)

router = APIRouter(tags=["Menu Management"])


@router.get(
    "/menu/categories",
    response_model=List[CategoryResponse],
    summary="List Food Categories",
    description="Returns the standard list of food categories available in Campus Byte.",
)
def get_food_categories_endpoint():
    return get_categories_list()


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemListResponse,
    summary="List Restaurant Menu Items",
    description="Retrieves all menu items for a specific restaurant. Supports category filtering, availability filtering, and keyword search.",
)
def get_restaurant_menu_endpoint(
    restaurant_id: uuid.UUID,
    category: Optional[str] = Query(None, description="Filter items by category (e.g. BIRYANI, BEVERAGES)"),
    is_available: Optional[bool] = Query(None, description="Filter items by availability"),
    search: Optional[str] = Query(None, description="Search keyword for food name or description"),
    db: Session = Depends(get_db),
):
    items, total = list_menu_items(
        db=db,
        restaurant_id=restaurant_id,
        category=category,
        is_available=is_available,
        search=search,
    )
    return MenuItemListResponse(items=items, total=total)


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Menu Item",
    description="Adds a new menu item to the specified restaurant. Requires authentication and owner verification.",
)
def create_menu_item_endpoint(
    restaurant_id: uuid.UUID,
    item_in: MenuItemCreate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return add_item_to_menu(
        db=db,
        restaurant_id=restaurant_id,
        item_in=item_in,
        current_user_id=current_user.id,
    )


@router.get(
    "/menu/{item_id}",
    response_model=MenuItemResponse,
    summary="Get Menu Item Details",
    description="Retrieves details of an individual menu item by ID.",
)
def get_menu_item_endpoint(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return get_item_details(db=db, item_id=item_id)


@router.put(
    "/menu/{item_id}",
    response_model=MenuItemResponse,
    summary="Update Menu Item Details",
    description="Updates information, price, description, or category for a menu item. Requires owner verification.",
)
def update_menu_item_endpoint(
    item_id: uuid.UUID,
    update_in: MenuItemUpdate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return update_item(
        db=db,
        item_id=item_id,
        update_data=update_in,
        current_user_id=current_user.id,
    )


@router.patch(
    "/menu/{item_id}/availability",
    response_model=MenuItemResponse,
    summary="Change Menu Item Availability",
    description="Toggles or sets the availability flag for a menu item. Requires owner verification.",
)
def update_menu_item_availability_endpoint(
    item_id: uuid.UUID,
    availability_in: MenuItemAvailabilityUpdate,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return toggle_item_availability(
        db=db,
        item_id=item_id,
        is_available=availability_in.is_available,
        current_user_id=current_user.id,
    )


@router.delete(
    "/menu/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete or Deactivate Menu Item",
    description="Safely removes or deactivates a menu item. If historical order records reference it, deactivates (is_available=False).",
)
def delete_menu_item_endpoint(
    item_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    was_deactivated, message = remove_item(
        db=db, item_id=item_id, current_user_id=current_user.id
    )
    return {
        "item_id": item_id,
        "is_deactivated": was_deactivated,
        "message": message,
    }
