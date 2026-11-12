import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.enums import OrderStatus
from app.core.permissions import require_restaurant_owner
from app.schemas.order import (
    OrderResponse,
    OrderListResponse,
    OrderRejectRequest,
    OrderStatusHistoryResponse,
    RestaurantOrderStatsResponse,
    NewOrdersNotificationResponse,
)
from app.services.order_service import (
    list_restaurant_orders,
    get_restaurant_order_detail,
    get_restaurant_order_stats,
    get_restaurant_new_notifications,
    get_order_history_for_restaurant,
    accept_restaurant_order,
    reject_restaurant_order,
    start_order_preparation,
    mark_order_ready_for_pickup,
)

router = APIRouter(prefix="/restaurant/orders", tags=["Restaurant Orders"])


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List Restaurant Orders",
    description="Retrieve paginated incoming and past orders belonging to the authenticated owner's restaurant.",
)
def list_orders_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    order_status: Optional[OrderStatus] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by Order ID, delivery address, or customer name"),
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    orders, total = list_restaurant_orders(
        db=db,
        owner=current_user,
        status=order_status,
        search=search,
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
    "/statistics",
    response_model=RestaurantOrderStatsResponse,
    summary="Get Order Statistics",
    description="Retrieve real aggregated counts of orders across all lifecycle states for the owner's restaurant.",
)
def get_order_stats_endpoint(
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    stats = get_restaurant_order_stats(db=db, owner=current_user)
    return RestaurantOrderStatsResponse(**stats)


@router.get(
    "/notifications",
    response_model=NewOrdersNotificationResponse,
    summary="Incoming Order Notifications",
    description="Poll for newly received pending orders since a provided cursor timestamp.",
)
def get_notifications_endpoint(
    since: Optional[datetime] = Query(None, description="ISO timestamp cursor for incremental polling"),
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    data = get_restaurant_new_notifications(db=db, owner=current_user, since=since)
    return NewOrdersNotificationResponse(**data)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get Restaurant Order Detail",
    description="Retrieve comprehensive details of a specific order including customer contact information, line items, and timestamps.",
)
def get_order_detail_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return get_restaurant_order_detail(
        db=db,
        owner=current_user,
        order_id=order_id,
    )


@router.get(
    "/{order_id}/history",
    response_model=List[OrderStatusHistoryResponse],
    summary="Get Order Audit History",
    description="Retrieve chronological status transition history for an order belonging to the owner's restaurant.",
)
def get_order_history_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    history = get_order_history_for_restaurant(
        db=db,
        owner=current_user,
        order_id=order_id,
    )
    return history


@router.patch(
    "/{order_id}/accept",
    response_model=OrderResponse,
    summary="Accept Pending Order",
    description="Acknowledge and accept an incoming order in PENDING status. Transitions order to ACCEPTED.",
)
def accept_order_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return accept_restaurant_order(
        db=db,
        owner=current_user,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/reject",
    response_model=OrderResponse,
    summary="Reject Pending Order",
    description="Reject an incoming order in PENDING status with a required reason. Transitions order to REJECTED.",
)
def reject_order_endpoint(
    order_id: uuid.UUID,
    reject_in: OrderRejectRequest,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return reject_restaurant_order(
        db=db,
        owner=current_user,
        order_id=order_id,
        reject_in=reject_in,
    )


@router.patch(
    "/{order_id}/start-preparation",
    response_model=OrderResponse,
    summary="Start Food Preparation",
    description="Start cooking the food for an order in ACCEPTED status. Transitions order to PREPARING.",
)
def start_preparation_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return start_order_preparation(
        db=db,
        owner=current_user,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/ready-for-pickup",
    response_model=OrderResponse,
    summary="Mark Order Ready for Pickup",
    description="Complete cooking and package the food. Transitions order from PREPARING to READY_FOR_PICKUP.",
)
def ready_for_pickup_endpoint(
    order_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return mark_order_ready_for_pickup(
        db=db,
        owner=current_user,
        order_id=order_id,
    )
