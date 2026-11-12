import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict
from sqlalchemy import select, func, desc, or_, cast, String
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.restaurant import Restaurant
from app.models.user import User
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus


def get_order_by_id(db: Session, order_id: uuid.UUID, for_update: bool = False) -> Optional[Order]:
    """Retrieve an order by ID with items, history, customer, and restaurant eager-loaded."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
            joinedload(Order.customer),
        )
        .where(Order.id == order_id)
    )
    if for_update and db.bind and db.bind.dialect.name != "sqlite":
        stmt = stmt.with_for_update()

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
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
            joinedload(Order.customer),
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
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
            joinedload(Order.customer),
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


def get_restaurant_orders(
    db: Session,
    restaurant_id: uuid.UUID,
    order_status: Optional[OrderStatus] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Order], int]:
    """
    Retrieve paginated orders for a specific restaurant with status filter and search.
    """
    count_stmt = select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)
    query_stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
            joinedload(Order.customer),
        )
        .where(Order.restaurant_id == restaurant_id)
    )

    if order_status is not None:
        count_stmt = count_stmt.where(Order.order_status == order_status)
        query_stmt = query_stmt.where(Order.order_status == order_status)

    if search and search.strip():
        term = f"%{search.strip()}%"
        # Search by order ID string, delivery address, or customer name
        search_filter = or_(
            cast(Order.id, String).ilike(term),
            Order.delivery_address.ilike(term),
            Order.customer.has(User.full_name.ilike(term)),
        )
        count_stmt = count_stmt.where(search_filter)
        query_stmt = query_stmt.where(search_filter)

    total = db.execute(count_stmt).scalar() or 0
    orders = (
        db.execute(
            query_stmt.order_by(desc(Order.created_at)).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )
    return list(orders), total


def get_restaurant_order_by_id(
    db: Session,
    restaurant_id: uuid.UUID,
    order_id: uuid.UUID,
    for_update: bool = False,
) -> Optional[Order]:
    """Retrieve an order strictly belonging to the specified restaurant."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            selectinload(Order.status_history),
            joinedload(Order.restaurant),
            joinedload(Order.customer),
        )
        .where(
            Order.id == order_id,
            Order.restaurant_id == restaurant_id,
        )
    )
    if for_update and db.bind and db.bind.dialect.name != "sqlite":
        stmt = stmt.with_for_update()

    return db.execute(stmt).scalar_one_or_none()


def get_restaurant_order_statistics(
    db: Session,
    restaurant_id: uuid.UUID,
) -> Dict[str, int]:
    """
    Aggregate counts of orders across different lifecycle states for an authenticated restaurant.
    """
    stmt = select(
        func.count(Order.id).label("total_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.PENDING).label("pending_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.ACCEPTED).label("accepted_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.PREPARING).label("preparing_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.READY_FOR_PICKUP).label("ready_for_pickup_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.REJECTED).label("rejected_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.CANCELLED).label("cancelled_orders"),
        func.count(Order.id).filter(Order.order_status == OrderStatus.DELIVERED).label("delivered_orders"),
    ).where(Order.restaurant_id == restaurant_id)

    row = db.execute(stmt).one()
    return {
        "total_orders": row.total_orders or 0,
        "pending_orders": row.pending_orders or 0,
        "accepted_orders": row.accepted_orders or 0,
        "preparing_orders": row.preparing_orders or 0,
        "ready_for_pickup_orders": row.ready_for_pickup_orders or 0,
        "rejected_orders": row.rejected_orders or 0,
        "cancelled_orders": row.cancelled_orders or 0,
        "delivered_orders": row.delivered_orders or 0,
    }


def get_new_pending_orders_since(
    db: Session,
    restaurant_id: uuid.UUID,
    since: Optional[datetime] = None,
) -> List[Order]:
    """Retrieve new pending orders for in-app alert notifications."""
    stmt = (
        select(Order)
        .options(
            selectinload(Order.order_items).joinedload(OrderItem.menu_item),
            joinedload(Order.customer),
        )
        .where(
            Order.restaurant_id == restaurant_id,
            Order.order_status == OrderStatus.PENDING,
        )
    )
    if since is not None:
        stmt = stmt.where(Order.created_at > since)

    return list(db.execute(stmt.order_by(desc(Order.created_at))).scalars().all())


def get_order_status_history(
    db: Session,
    order_id: uuid.UUID,
) -> List[OrderStatusHistory]:
    """Retrieve chronological status audit history for an order."""
    stmt = (
        select(OrderStatusHistory)
        .where(OrderStatusHistory.order_id == order_id)
        .order_by(OrderStatusHistory.created_at.asc())
    )
    return list(db.execute(stmt).scalars().all())


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
        changed_by_role="CUSTOMER",
        notes="Order placed by customer",
    )
    db.add(history)

    db.commit()
    db.refresh(new_order)
    return get_order_by_id(db, new_order.id) or new_order


def transition_order_status(
    db: Session,
    order: Order,
    new_status: OrderStatus,
    changed_by: Optional[uuid.UUID] = None,
    changed_by_role: Optional[str] = None,
    notes: Optional[str] = None,
    rejection_reason: Optional[str] = None,
) -> Order:
    """
    Safely transition order status, set respective lifecycle timestamp,
    record audit history, and commit atomically.
    """
    prev_status = order.order_status.value if order.order_status else None
    order.order_status = new_status
    now = datetime.now(timezone.utc)

    if new_status == OrderStatus.ACCEPTED:
        order.accepted_at = now
    elif new_status == OrderStatus.REJECTED:
        order.rejected_at = now
        order.rejection_reason = rejection_reason
    elif new_status == OrderStatus.PREPARING:
        order.preparing_at = now
    elif new_status == OrderStatus.READY_FOR_PICKUP:
        order.ready_for_pickup_at = now

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=prev_status,
        new_status=new_status.value,
        changed_by=changed_by,
        changed_by_role=changed_by_role,
        notes=notes or rejection_reason,
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return get_order_by_id(db, order.id) or order


def update_order_status(
    db: Session,
    order: Order,
    new_status: OrderStatus,
    changed_by: Optional[uuid.UUID] = None,
) -> Order:
    """Transition order status and append to status history (generic fallback)."""
    return transition_order_status(
        db=db,
        order=order,
        new_status=new_status,
        changed_by=changed_by,
        changed_by_role=None,
        notes=None,
    )
