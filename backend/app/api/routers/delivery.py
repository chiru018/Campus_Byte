import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_delivery_partner
from app.schemas.delivery import (
    DeliveryPartnerResponse,
    DeliveryPartnerProfileUpdate,
    AvailabilityUpdateRequest,
    DeliveryStatsResponse,
    AvailableDeliveryOrderListResponse,
    ActiveDeliveryResponse,
    DeliveryCompleteRequest,
    CODConfirmRequest,
    CODStatusResponse,
    DeliveryHistoryListResponse,
)
from app.schemas.order import OrderStatusHistoryResponse
from app.services import delivery_service

router = APIRouter(prefix="/delivery", tags=["Delivery Partner Management"])


# ==============================================================================
# PROFILE & AVAILABILITY ENDPOINTS
# ==============================================================================

@router.get(
    "/profile",
    response_model=DeliveryPartnerResponse,
    summary="Get delivery partner profile",
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Retrieve operational courier profile for the authenticated delivery partner."""
    return delivery_service.get_delivery_partner_profile(db=db, current_user=current_user)


@router.patch(
    "/profile",
    response_model=DeliveryPartnerResponse,
    summary="Update delivery partner profile",
)
def update_profile(
    profile_in: DeliveryPartnerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Update courier vehicle configuration and contact phone number."""
    return delivery_service.update_delivery_partner_profile(
        db=db, current_user=current_user, profile_in=profile_in
    )


@router.patch(
    "/availability",
    response_model=DeliveryPartnerResponse,
    summary="Toggle operational availability",
)
def update_availability(
    req: AvailabilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """
    Update courier availability state: OFFLINE, AVAILABLE, or BUSY.
    Blocked if an active delivery assignment is currently in progress.
    """
    return delivery_service.update_delivery_partner_availability(
        db=db, current_user=current_user, req=req
    )


@router.get(
    "/dashboard/statistics",
    response_model=DeliveryStatsResponse,
    summary="Get delivery partner performance KPIs",
)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Calculates active assignments, completed orders, and cash collection totals."""
    return delivery_service.get_delivery_dashboard_stats(
        db=db, current_user=current_user
    )


# ==============================================================================
# AVAILABLE ORDERS & ASSIGNMENT ENDPOINTS
# ==============================================================================

@router.get(
    "/available-orders",
    response_model=AvailableDeliveryOrderListResponse,
    summary="List available delivery orders ready for pickup",
)
def get_available_orders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """
    Retrieves orders in READY_FOR_PICKUP state without an assigned courier.
    Partner must currently be AVAILABLE.
    """
    orders, total = delivery_service.list_available_orders_for_delivery(
        db=db, current_user=current_user, page=page, size=size
    )
    return AvailableDeliveryOrderListResponse(
        orders=orders,
        total=total,
        page=page,
        size=size,
    )


@router.post(
    "/assignments/{order_id}/accept",
    response_model=ActiveDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept / claim a delivery request",
)
def accept_delivery(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """
    Claims an eligible READY_FOR_PICKUP order atomically.
    Transitions partner state to BUSY and prevents double-claiming via concurrency locks.
    """
    return delivery_service.accept_delivery_request(
        db=db, current_user=current_user, order_id=order_id
    )


@router.get(
    "/active-delivery",
    response_model=Optional[ActiveDeliveryResponse],
    summary="Get current active delivery for partner",
)
def get_active_delivery(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Returns the ongoing active delivery task assigned to the courier, or null."""
    return delivery_service.get_current_active_delivery(
        db=db, current_user=current_user
    )


@router.get(
    "/assignments/{order_id}",
    response_model=ActiveDeliveryResponse,
    summary="Get delivery assignment details by order ID",
)
def get_assignment_detail(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Retrieves full restaurant and customer handover details (ownership enforced)."""
    return delivery_service.get_assignment_detail_by_order(
        db=db, current_user=current_user, order_id=order_id
    )


# ==============================================================================
# LIFECYCLE TRANSITIONS: PICKUP, OUT FOR DELIVERY, COMPLETION
# ==============================================================================

@router.patch(
    "/assignments/{order_id}/pickup",
    response_model=ActiveDeliveryResponse,
    summary="Confirm order package pickup from restaurant",
)
def confirm_pickup(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Transitions order from READY_FOR_PICKUP to PICKED_UP."""
    return delivery_service.confirm_restaurant_pickup(
        db=db, current_user=current_user, order_id=order_id
    )


@router.patch(
    "/assignments/{order_id}/start-delivery",
    response_model=ActiveDeliveryResponse,
    summary="Start campus delivery run to customer dorm",
)
def start_delivery(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Transitions order from PICKED_UP to OUT_FOR_DELIVERY."""
    return delivery_service.start_out_for_delivery(
        db=db, current_user=current_user, order_id=order_id
    )


@router.post(
    "/assignments/{order_id}/confirm-cod",
    response_model=CODStatusResponse,
    summary="Explicitly confirm Cash on Delivery collection",
)
def confirm_cod(
    order_id: uuid.UUID,
    req: CODConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Validates cash amount collected against order total and marks payment PAID."""
    return delivery_service.confirm_cod_collection(
        db=db, current_user=current_user, order_id=order_id, req=req
    )


@router.get(
    "/assignments/{order_id}/cod-status",
    response_model=CODStatusResponse,
    summary="Inspect Cash on Delivery payment status",
)
def get_cod_status(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Returns cash collection status, amount, and recipient courier details."""
    return delivery_service.get_cod_status(
        db=db, current_user=current_user, order_id=order_id
    )


@router.patch(
    "/assignments/{order_id}/complete",
    response_model=ActiveDeliveryResponse,
    summary="Complete order delivery to customer",
)
def complete_delivery(
    order_id: uuid.UUID,
    req: DeliveryCompleteRequest = DeliveryCompleteRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """
    Transitions order from OUT_FOR_DELIVERY to DELIVERED.
    Enforces COD payment confirmation and automatically resets courier to AVAILABLE.
    """
    return delivery_service.complete_delivery(
        db=db, current_user=current_user, order_id=order_id, req=req
    )


# ==============================================================================
# AUDIT & HISTORY ENDPOINTS
# ==============================================================================

@router.get(
    "/history",
    response_model=DeliveryHistoryListResponse,
    summary="Get delivery partner delivery history",
)
def get_delivery_history(
    status: Optional[str] = Query(None, description="Status filter: ALL, DELIVERED, CANCELLED"),
    date_from: Optional[datetime] = Query(None, description="Filter start timestamp"),
    date_to: Optional[datetime] = Query(None, description="Filter end timestamp"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Returns paginated delivery history of assigned and completed orders."""
    items, total = delivery_service.get_delivery_history_list(
        db=db,
        current_user=current_user,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size,
    )
    return DeliveryHistoryListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/assignments/{order_id}/history",
    response_model=list[OrderStatusHistoryResponse],
    summary="Get order status history for delivery assignment",
)
def get_assignment_history(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_partner),
):
    """Retrieves chronological lifecycle transition records for the assigned order."""
    return delivery_service.get_order_status_history_for_delivery(
        db=db, current_user=current_user, order_id=order_id
    )
