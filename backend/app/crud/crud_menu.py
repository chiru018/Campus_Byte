import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.models.order_item import OrderItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate


def get_menu_item_by_id(db: Session, item_id: uuid.UUID) -> Optional[MenuItem]:
    return db.scalar(select(MenuItem).where(MenuItem.id == item_id))


def get_menu_items_by_restaurant(
    db: Session,
    restaurant_id: uuid.UUID,
    category: Optional[str] = None,
    is_available: Optional[bool] = None,
) -> Tuple[List[MenuItem], int]:
    query = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)

    if category:
        query = query.where(MenuItem.category.ilike(category.strip()))

    if is_available is not None:
        query = query.where(MenuItem.is_available == is_available)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    items = list(db.scalars(query.order_by(MenuItem.category, MenuItem.name)).all())
    return items, total


def create_menu_item(
    db: Session, restaurant_id: uuid.UUID, item_in: MenuItemCreate
) -> MenuItem:
    menu_item = MenuItem(
        restaurant_id=restaurant_id,
        name=item_in.name,
        description=item_in.description,
        price=item_in.price,
        category=item_in.category,
        image_url=item_in.image_url,
        is_available=item_in.is_available,
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


def update_menu_item(
    db: Session, item_obj: MenuItem, update_data: MenuItemUpdate
) -> MenuItem:
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(item_obj, field, value)
    db.commit()
    db.refresh(item_obj)
    return item_obj


def set_menu_item_availability(
    db: Session, item_obj: MenuItem, is_available: bool
) -> MenuItem:
    item_obj.is_available = is_available
    db.commit()
    db.refresh(item_obj)
    return item_obj


def remove_or_deactivate_menu_item(
    db: Session, item_obj: MenuItem
) -> Tuple[bool, str]:
    """
    Safely removes menu item.
    If the item appears in historical order items, marks unavailable rather than breaking references.
    Otherwise, deletes the record.
    """
    order_items_count = db.scalar(
        select(func.count(OrderItem.id)).where(OrderItem.menu_item_id == item_obj.id)
    ) or 0

    if order_items_count > 0:
        item_obj.is_available = False
        db.commit()
        return True, "Menu item has historical order occurrences; it was deactivated (is_available=False)."
    else:
        db.delete(item_obj)
        db.commit()
        return False, "Menu item was successfully deleted."
