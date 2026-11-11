import uuid
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus


def get_order_by_id(db: Session, order_id: uuid.UUID) -> Optional[Order]:
    """Retrieve an order by ID with items, history, and restaurant eager-loaded."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
        )
        .where(Order.id == order_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_order_by_idempotency(
    db: Session, customer_id: uuid.UUID, idempotency_key: str
) -> Optional[Order]:
    """Check for an existing order by customer and idempotency key."""
    if not idempotency_key:
        return None
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
        )
        .where(
            Order.customer_id == customer_id,
            Order.idempotency_key == idempotency_key,
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_customer_orders(
    db: Session,
    customer_id: uuid.UUID,
    order_status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Order], int]:
    """Retrieve paginated orders for a specific customer."""
    count_stmt = select(func.count(Order.id)).where(Order.customer_id == customer_id)
    query_stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
        )
        .where(Order.customer_id == customer_id)
    )

    if order_status is not None:
        count_stmt = count_stmt.where(Order.order_status == order_status)
        query_stmt = query_stmt.where(Order.order_status == order_status)

    total = db.execute(count_stmt).scalar() or 0
    orders = (
        db.execute(
            query_stmt.order_by(desc(Order.created_at)).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )
    return list(orders), total


def create_order_atomic(
    db: Session,
    customer_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    delivery_address: str,
    subtotal: Decimal,
    delivery_fee: Decimal,
    total_amount: Decimal,
    items_data: List[dict],
    payment_method: PaymentMethod = PaymentMethod.CASH_ON_DELIVERY,
    idempotency_key: Optional[str] = None,
) -> Order:
    """
    Atomically insert Order, OrderItem line items, and initial OrderStatusHistory.
    """
    new_order = Order(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        delivery_address=delivery_address,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        idempotency_key=idempotency_key,
    )
    db.add(new_order)
    db.flush()  # generates new_order.id

    # Create line items
    for item in items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item["menu_item_id"],
            item_name=item["item_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            total_price=item["total_price"],
        )
        db.add(order_item)

    # Record initial status in history
    history = OrderStatusHistory(
        order_id=new_order.id,
        previous_status=None,
        new_status=OrderStatus.PENDING.value,
        changed_by=customer_id,
    )
    db.add(history)

    db.commit()
    db.refresh(new_order)
    return get_order_by_id(db, new_order.id) or new_order


def update_order_status(
    db: Session,
    order: Order,
    new_status: OrderStatus,
    changed_by: Optional[uuid.UUID] = None,
) -> Order:
    """Transition order status and append to status history."""
    prev_status = order.order_status.value if order.order_status else None
    order.order_status = new_status

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=prev_status,
        new_status=new_status.value,
        changed_by=changed_by,
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return get_order_by_id(db, order.id) or order
