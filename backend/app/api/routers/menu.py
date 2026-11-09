import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.menu_item import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemAvailabilityUpdate,
    MenuItemResponse,
    MenuItemListResponse,
)
from app.services.menu_service import (
    list_menu_items,
    get_item_details,
    add_item_to_menu,
    update_item,
    toggle_item_availability,
    remove_item,
)

router = APIRouter(tags=["Menu Management"])


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemListResponse,
    summary="List Restaurant Menu Items",
    description="Retrieves all menu items for a specific restaurant. Supports category filtering and availability filtering.",
)
def get_restaurant_menu_endpoint(
    restaurant_id: uuid.UUID,
    category: Optional[str] = Query(None, description="Filter items by category (e.g. Beverages, Mains)"),
    is_available: Optional[bool] = Query(None, description="Filter items by availability"),
    db: Session = Depends(get_db),
):
    items, total = list_menu_items(
        db=db,
        restaurant_id=restaurant_id,
        category=category,
        is_available=is_available,
    )
    return MenuItemListResponse(items=items, total=total)


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Menu Item",
    description="Adds a new menu item to the specified restaurant. Enforces strictly positive price (> 0).",
)
def create_menu_item_endpoint(
    restaurant_id: uuid.UUID,
    item_in: MenuItemCreate,
    db: Session = Depends(get_db),
):
    return add_item_to_menu(
        db=db, restaurant_id=restaurant_id, item_in=item_in
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
    description="Updates information, price, description, or category for a menu item.",
)
def update_menu_item_endpoint(
    item_id: uuid.UUID,
    update_in: MenuItemUpdate,
    db: Session = Depends(get_db),
):
    return update_item(db=db, item_id=item_id, update_data=update_in)


@router.patch(
    "/menu/{item_id}/availability",
    response_model=MenuItemResponse,
    summary="Change Menu Item Availability",
    description="Toggles or sets the availability flag for a menu item.",
)
def update_menu_item_availability_endpoint(
    item_id: uuid.UUID,
    availability_in: MenuItemAvailabilityUpdate,
    db: Session = Depends(get_db),
):
    return toggle_item_availability(
        db=db, item_id=item_id, is_available=availability_in.is_available
    )


@router.delete(
    "/menu/{item_id}",
    summary="Delete or Deactivate Menu Item",
    description="Removes a menu item. If the item exists in order history, marks unavailable rather than breaking references.",
)
def delete_menu_item_endpoint(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    deactivated, message = remove_item(db=db, item_id=item_id)
    return {
        "item_id": item_id,
        "deactivated": deactivated,
        "message": message,
    }
