import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate
from app.core.exceptions import ResourceNotFoundException
import app.crud.crud_menu as crud_menu
import app.crud.crud_restaurant as crud_restaurant


def list_menu_items(
    db: Session,
    restaurant_id: uuid.UUID,
    category: Optional[str] = None,
    is_available: Optional[bool] = None,
) -> Tuple[List[MenuItem], int]:
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant", restaurant_id)

    return crud_menu.get_menu_items_by_restaurant(
        db=db,
        restaurant_id=restaurant_id,
        category=category,
        is_available=is_available,
    )


def get_item_details(db: Session, item_id: uuid.UUID) -> MenuItem:
    item = crud_menu.get_menu_item_by_id(db, item_id)
    if not item:
        raise ResourceNotFoundException("MenuItem", item_id)
    return item


def add_item_to_menu(
    db: Session, restaurant_id: uuid.UUID, item_in: MenuItemCreate
) -> MenuItem:
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant", restaurant_id)

    return crud_menu.create_menu_item(
        db=db, restaurant_id=restaurant_id, item_in=item_in
    )


def update_item(
    db: Session, item_id: uuid.UUID, update_data: MenuItemUpdate
) -> MenuItem:
    item = get_item_details(db, item_id)
    return crud_menu.update_menu_item(db, item, update_data)


def toggle_item_availability(
    db: Session, item_id: uuid.UUID, is_available: bool
) -> MenuItem:
    item = get_item_details(db, item_id)
    return crud_menu.set_menu_item_availability(db, item, is_available)


def remove_item(db: Session, item_id: uuid.UUID) -> Tuple[bool, str]:
    item = get_item_details(db, item_id)
    return crud_menu.remove_or_deactivate_menu_item(db, item)
