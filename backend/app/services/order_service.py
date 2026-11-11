import uuid
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.enums import OrderStatus, PaymentMethod, PaymentStatus
from app.schemas.order import OrderCreate, OrderResponse
from app.crud.crud_order import (
    get_order_by_id,
    get_order_by_idempotency,
    get_customer_orders,
    create_order_atomic,
    update_order_status,
)
from app.crud.crud_restaurant import get_restaurant_by_id
from app.crud.crud_menu import get_menu_item_by_id
from app.core.exceptions import (
    ResourceNotFoundException,
    BusinessRuleException,
    AuthorizationException,
)

# Standard flat delivery fee for campus orders
STANDARD_DELIVERY_FEE = Decimal("2.00")


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
            if existing_order.restaurant:
                setattr(existing_order, "restaurant_name", existing_order.restaurant.name)
            return existing_order

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

    setattr(created_order, "restaurant_name", restaurant.name)
    return created_order


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

    for order in orders:
        if order.restaurant:
            setattr(order, "restaurant_name", order.restaurant.name)

    return orders, total


def get_order_detail(
    db: Session,
    current_user: User,
    order_id: uuid.UUID,
) -> Order:
    """Retrieve single order with IDOR verification."""
    order = get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # IDOR Check: Ensure customer owns this order
    if order.customer_id != current_user.id:
        raise AuthorizationException("You do not have permission to view this order.")

    if order.restaurant:
        setattr(order, "restaurant_name", order.restaurant.name)

    return order


def cancel_customer_order(
    db: Session,
    current_user: User,
    order_id: uuid.UUID,
    reason: Optional[str] = None,
) -> Order:
    """
    Cancel an order if still in PENDING status.
    """
    order = get_order_by_id(db=db, order_id=order_id)
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

    updated_order = update_order_status(
        db=db,
        order=order,
        new_status=OrderStatus.CANCELLED,
        changed_by=current_user.id,
    )

    if updated_order.restaurant:
        setattr(updated_order, "restaurant_name", updated_order.restaurant.name)

    return updated_order
