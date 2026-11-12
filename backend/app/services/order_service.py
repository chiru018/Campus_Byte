import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.schemas.order import OrderCreate, OrderResponse, OrderRejectRequest
from app.crud.crud_order import (
    get_order_by_id,
    get_order_by_idempotency,
    get_customer_orders,
    get_restaurant_orders,
    get_restaurant_order_by_id,
    get_restaurant_order_statistics,
    get_new_pending_orders_since,
    get_order_status_history,
    create_order_atomic,
    transition_order_status,
)
from app.crud.crud_restaurant import get_restaurant_by_id, get_restaurant_by_owner_id
from app.crud.crud_menu import get_menu_item_by_id
from app.core.exceptions import (
    ResourceNotFoundException,
    BusinessRuleException,
    AuthorizationException,
)

# Standard flat delivery fee for campus orders
STANDARD_DELIVERY_FEE = Decimal("2.00")


def _enrich_order_metadata(order: Order) -> Order:
    """Enriches order model instance with presentation metadata for serialization."""
    if order.restaurant:
        setattr(order, "restaurant_name", order.restaurant.name)
    if order.customer:
        setattr(order, "customer_name", order.customer.full_name)
        setattr(order, "customer_phone", order.customer.phone_number)
        setattr(order, "customer_email", order.customer.email)

    if order.delivery_partner:
        if hasattr(order.delivery_partner, "user") and order.delivery_partner.user:
            setattr(order, "delivery_partner_name", order.delivery_partner.user.full_name)
            setattr(order, "delivery_partner_phone", order.delivery_partner.user.phone_number)
        if hasattr(order.delivery_partner, "vehicle_type") and order.delivery_partner.vehicle_type:
            setattr(order, "delivery_partner_vehicle", getattr(order.delivery_partner.vehicle_type, "value", str(order.delivery_partner.vehicle_type)))

    # Attach dish image URLs if available from the underlying menu item
    if order.order_items:
        for item in order.order_items:
            if hasattr(item, "menu_item") and item.menu_item and item.menu_item.image_url:
                setattr(item, "image_url", item.menu_item.image_url)

    return order


def _get_owner_restaurant(db: Session, owner: User) -> Restaurant:
    """Retrieves the restaurant owned by the authenticated owner or raises 404/403."""
    restaurant = get_restaurant_by_owner_id(db=db, owner_id=owner.id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant profile for current owner", owner.id)
    return restaurant


# ==============================================================================
# CUSTOMER FACING SERVICES
# ==============================================================================

def place_order(
    db: Session,
    current_user: User,
    order_in: OrderCreate,
) -> Order:
    """
    Validate and place a new customer order with server-side pricing calculation.
    Protects against duplicate submission via idempotency key and prevents price tampering.
    """
    # 1. Idempotency Check
    if order_in.idempotency_key:
        existing_order = get_order_by_idempotency(
            db=db,
            customer_id=current_user.id,
            idempotency_key=order_in.idempotency_key,
        )
        if existing_order:
            return _enrich_order_metadata(existing_order)

    # 2. Restaurant Verification
    restaurant = get_restaurant_by_id(db=db, restaurant_id=order_in.restaurant_id)
    if not restaurant:
        raise ResourceNotFoundException("Restaurant", order_in.restaurant_id)

    if not restaurant.is_open:
        raise BusinessRuleException(
            f"'{restaurant.name}' is currently closed and not accepting food orders.",
            error_code="RESTAURANT_CLOSED",
        )

    # 3. Item Validations and Server-Side Pricing Calculation
    if not order_in.items:
        raise BusinessRuleException(
            "Order must contain at least one item.",
            error_code="EMPTY_ORDER",
        )

    subtotal = Decimal("0.00")
    items_data = []

    for item_input in order_in.items:
        if item_input.quantity <= 0:
            raise BusinessRuleException(
                "Quantity must be greater than zero.",
                error_code="INVALID_QUANTITY",
            )

        menu_item = get_menu_item_by_id(db=db, item_id=item_input.menu_item_id)
        if not menu_item:
            raise ResourceNotFoundException("MenuItem", item_input.menu_item_id)

        # Enforce that every item belongs strictly to the requested restaurant
        if menu_item.restaurant_id != restaurant.id:
            raise BusinessRuleException(
                f"Item '{menu_item.name}' does not belong to {restaurant.name}.",
                error_code="CROSS_RESTAURANT_ITEM",
            )

        # Enforce item availability
        if not menu_item.is_available:
            raise BusinessRuleException(
                f"'{menu_item.name}' is currently sold out / unavailable.",
                error_code="ITEM_UNAVAILABLE",
            )

        # Secure pricing calculation derived from DB model, ignoring any client claims
        unit_price = Decimal(str(menu_item.price))
        line_total = unit_price * item_input.quantity
        subtotal += line_total

        items_data.append({
            "menu_item_id": menu_item.id,
            "item_name": menu_item.name,
            "unit_price": unit_price,
            "quantity": item_input.quantity,
            "total_price": line_total,
        })

    delivery_fee = STANDARD_DELIVERY_FEE
    total_amount = subtotal + delivery_fee

    # 4. Atomic Database Transaction
    created_order = create_order_atomic(
        db=db,
        customer_id=current_user.id,
        restaurant_id=restaurant.id,
        delivery_address=order_in.delivery_address.strip(),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        items_data=items_data,
        payment_method=order_in.payment_method,
        idempotency_key=order_in.idempotency_key,
    )

    return _enrich_order_metadata(created_order)


def get_my_orders(
    db: Session,
    current_user: User,
    order_status: Optional[OrderStatus] = None,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[Order], int]:
    """Retrieve customer's order history."""
    skip = (page - 1) * size
    orders, total = get_customer_orders(
        db=db,
        customer_id=current_user.id,
        order_status=order_status,
        skip=skip,
        limit=size,
    )

    enriched_orders = [_enrich_order_metadata(o) for o in orders]
    return enriched_orders, total


def get_order_detail(
    db: Session,
    current_user: User,
    order_id: uuid.UUID,
) -> Order:
    """Retrieve single order with IDOR verification for customer."""
    order = get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check: Ensure customer owns this order
    if order.customer_id != current_user.id:
        raise AuthorizationException("You do not have permission to view this order.")

    return _enrich_order_metadata(order)


def cancel_customer_order(
    db: Session,
    current_user: User,
    order_id: uuid.UUID,
    reason: Optional[str] = None,
) -> Order:
    """
    Cancel an order if still in PENDING status.
    Protected against race conditions via database row locking.
    """
    order = get_order_by_id(db=db, order_id=order_id, for_update=True)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check
    if order.customer_id != current_user.id:
        raise AuthorizationException("You do not have permission to cancel this order.")

    # Status check: only pending can be cancelled by customer
    if order.order_status == OrderStatus.CANCELLED:
        raise BusinessRuleException(
            "This order has already been cancelled.",
            error_code="ORDER_ALREADY_CANCELLED",
        )

    if order.order_status != OrderStatus.PENDING:
        raise BusinessRuleException(
            f"Order cannot be cancelled because it is already {order.order_status.value}.",
            error_code="CANNOT_CANCEL_ACTIVE_ORDER",
        )

    updated_order = transition_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.CANCELLED,
        changed_by=current_user.id,
        changed_by_role="CUSTOMER",
        notes=reason or "Order cancelled by customer",
    )

    return _enrich_order_metadata(updated_order)


# ==============================================================================
# RESTAURANT OWNER FACING SERVICES (PHASE 6)
# ==============================================================================

def list_restaurant_orders(
    db: Session,
    owner: User,
    status: Optional[OrderStatus] = None,
    search: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[Order], int]:
    """Retrieve orders strictly belonging to the authenticated owner's restaurant."""
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    skip = (page - 1) * size

    orders, total = get_restaurant_orders(
        db=db,
        restaurant_id=restaurant.id,
        order_status=status,
        search=search,
        skip=skip,
        limit=size,
    )

    enriched = [_enrich_order_metadata(o) for o in orders]
    return enriched, total


def get_restaurant_order_detail(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
) -> Order:
    """Retrieve full details of an order belonging to the owner's restaurant."""
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    order = get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Protection: verify this order is from the owner's restaurant
    if order.restaurant_id != restaurant.id:
        raise AuthorizationException("You do not have permission to access orders from another restaurant.")

    return _enrich_order_metadata(order)


def get_restaurant_order_stats(
    db: Session,
    owner: User,
) -> Dict[str, int]:
    """Calculate aggregate order counts across all lifecycle states for this restaurant."""
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    return get_restaurant_order_statistics(db=db, restaurant_id=restaurant.id)


def get_restaurant_new_notifications(
    db: Session,
    owner: User,
    since: Optional[datetime] = None,
) -> Dict:
    """Retrieve pending order alerts since last cursor for the owner's restaurant."""
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    new_orders = get_new_pending_orders_since(db=db, restaurant_id=restaurant.id, since=since)
    enriched = [_enrich_order_metadata(o) for o in new_orders]

    latest_cursor = enriched[0].created_at if enriched else since
    return {
        "new_orders_count": len(enriched),
        "pending_orders": enriched,
        "latest_cursor": latest_cursor,
    }


def get_order_history_for_restaurant(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
):
    """Retrieve chronological status audit history for this restaurant's order."""
    # Enforce restaurant ownership check first
    get_restaurant_order_detail(db=db, owner=owner, order_id=order_id)
    return get_order_status_history(db=db, order_id=order_id)


def accept_restaurant_order(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
) -> Order:
    """
    Accept an incoming PENDING order.
    Transition: PENDING -> ACCEPTED
    Enforces concurrency row-level locking to prevent race conditions.
    """
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    order = get_order_by_id(db=db, order_id=order_id, for_update=True)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check
    if order.restaurant_id != restaurant.id:
        raise AuthorizationException("You do not have permission to accept orders from another restaurant.")

    # Concurrency and duplicate acceptance check
    if order.order_status == OrderStatus.ACCEPTED:
        raise BusinessRuleException(
            "This order has already been accepted.",
            error_code="ORDER_ALREADY_ACCEPTED",
        )

    if order.order_status == OrderStatus.REJECTED:
        raise BusinessRuleException(
            "Cannot accept an order that has already been rejected.",
            error_code="ORDER_ALREADY_REJECTED",
        )

    if order.order_status == OrderStatus.CANCELLED:
        raise BusinessRuleException(
            "Cannot accept an order that has been cancelled by the customer.",
            error_code="ORDER_CANCELLED",
        )

    if order.order_status != OrderStatus.PENDING:
        raise BusinessRuleException(
            f"Cannot accept order in status '{order.order_status.value}'. Only PENDING orders can be accepted.",
            error_code="INVALID_STATE_TRANSITION",
        )

    updated_order = transition_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.ACCEPTED,
        changed_by=owner.id,
        changed_by_role="RESTAURANT_OWNER",
        notes="Order accepted by kitchen",
    )

    return _enrich_order_metadata(updated_order)


def reject_restaurant_order(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
    reject_in: OrderRejectRequest,
) -> Order:
    """
    Reject an incoming PENDING order with mandatory reason.
    Transition: PENDING -> REJECTED
    Enforces concurrency row-level locking.
    """
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    reason = reject_in.reason.strip()

    if len(reason) < 5:
        raise BusinessRuleException(
            "Rejection reason must be at least 5 characters long.",
            error_code="INVALID_REJECTION_REASON",
        )

    order = get_order_by_id(db=db, order_id=order_id, for_update=True)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check
    if order.restaurant_id != restaurant.id:
        raise AuthorizationException("You do not have permission to reject orders from another restaurant.")

    if order.order_status == OrderStatus.REJECTED:
        raise BusinessRuleException(
            "This order has already been rejected.",
            error_code="ORDER_ALREADY_REJECTED",
        )

    if order.order_status == OrderStatus.CANCELLED:
        raise BusinessRuleException(
            "Cannot reject an order that has already been cancelled.",
            error_code="ORDER_ALREADY_CANCELLED",
        )

    if order.order_status != OrderStatus.PENDING:
        raise BusinessRuleException(
            f"Cannot reject order in status '{order.order_status.value}'. Orders that have been accepted or prepared cannot be rejected.",
            error_code="CANNOT_REJECT_ACCEPTED_ORDER",
        )

    updated_order = transition_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.REJECTED,
        changed_by=owner.id,
        changed_by_role="RESTAURANT_OWNER",
        notes=f"Order rejected by kitchen: {reason}",
        rejection_reason=reason,
    )

    return _enrich_order_metadata(updated_order)


def start_order_preparation(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
) -> Order:
    """
    Move an accepted order into kitchen preparation.
    Transition: ACCEPTED -> PREPARING
    """
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    order = get_order_by_id(db=db, order_id=order_id, for_update=True)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check
    if order.restaurant_id != restaurant.id:
        raise AuthorizationException("You do not have permission to manage orders from another restaurant.")

    if order.order_status == OrderStatus.PREPARING:
        raise BusinessRuleException(
            "Order preparation is already in progress.",
            error_code="ORDER_ALREADY_PREPARING",
        )

    if order.order_status == OrderStatus.PENDING:
        raise BusinessRuleException(
            "Order must be accepted by the kitchen before preparation can begin.",
            error_code="ORDER_NOT_ACCEPTED",
        )

    if order.order_status != OrderStatus.ACCEPTED:
        raise BusinessRuleException(
            f"Cannot start preparation for order in status '{order.order_status.value}'. Only ACCEPTED orders can enter preparation.",
            error_code="INVALID_STATE_TRANSITION",
        )

    updated_order = transition_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.PREPARING,
        changed_by=owner.id,
        changed_by_role="RESTAURANT_OWNER",
        notes="Kitchen started food preparation",
    )

    return _enrich_order_metadata(updated_order)


def mark_order_ready_for_pickup(
    db: Session,
    owner: User,
    order_id: uuid.UUID,
) -> Order:
    """
    Mark food preparation as complete and ready for delivery partner pickup.
    Transition: PREPARING -> READY_FOR_PICKUP
    """
    restaurant = _get_owner_restaurant(db=db, owner=owner)
    order = get_order_by_id(db=db, order_id=order_id, for_update=True)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check
    if order.restaurant_id != restaurant.id:
        raise AuthorizationException("You do not have permission to manage orders from another restaurant.")

    if order.order_status == OrderStatus.READY_FOR_PICKUP:
        raise BusinessRuleException(
            "Order is already marked as ready for pickup.",
            error_code="ORDER_ALREADY_READY",
        )

    if order.order_status in [OrderStatus.PENDING, OrderStatus.ACCEPTED]:
        raise BusinessRuleException(
            "Order must be in preparation before it can be marked ready for pickup.",
            error_code="ORDER_NOT_PREPARING",
        )

    if order.order_status != OrderStatus.PREPARING:
        raise BusinessRuleException(
            f"Cannot mark order in status '{order.order_status.value}' as ready for pickup. Only PREPARING orders can be marked ready.",
            error_code="INVALID_STATE_TRANSITION",
        )

    updated_order = transition_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.READY_FOR_PICKUP,
        changed_by=owner.id,
        changed_by_role="RESTAURANT_OWNER",
        notes="Kitchen completed food preparation; waiting for delivery partner pickup",
    )

    return _enrich_order_metadata(updated_order)
