import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.enums import OrderStatus
from app.core.permissions import require_customer
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderCancelRequest,
)
from app.services.order_service import (
    place_order,
    get_my_orders,
    get_order_detail,
    cancel_customer_order,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place New Order",
    description="Validates items, calculates totals securely on backend, checks restaurant status, and creates an order with Cash on Delivery payment.",
)
def create_order_endpoint(
    order_in: OrderCreate,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    created_order = place_order(
        db=db,
        current_user=current_user,
        order_in=order_in,
    )
    return created_order


@router.get(
    "/my-orders",
    response_model=OrderListResponse,
    summary="Get Customer Orders",
    description="Returns the paginated order history of the currently authenticated customer.",
)
def get_my_orders_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    order_status: Optional[OrderStatus] = Query(None, alias="status", description="Filter by order status"),
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    orders, total = get_my_orders(
        db=db,
        current_user=current_user,
        order_status=order_status,
        page=page,
        size=size,
    )
    return OrderListResponse(
        orders=orders,
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get Order Detail",
    description="Retrieves full details of a specific order including snapshot items and status transition history. Enforces customer ownership.",
)
def get_order_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return get_order_detail(
        db=db,
        current_user=current_user,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel Pending Order",
    description="Allows a customer to cancel their order while it is still in PENDING status. Rejects cancellation once order is accepted or preparing.",
)
def cancel_order_endpoint(
    order_id: uuid.UUID,
    cancel_in: Optional[OrderCancelRequest] = None,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    reason = cancel_in.reason if cancel_in else None
    return cancel_customer_order(
        db=db,
        current_user=current_user,
        order_id=order_id,
        reason=reason,
    )

