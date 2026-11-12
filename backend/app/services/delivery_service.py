import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.delivery_partner import DeliveryPartner
from app.models.delivery_assignment import DeliveryAssignment
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.enums import (
    UserRole,
    PartnerAvailability,
    DeliveryStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)
from app.schemas.delivery import (
    DeliveryPartnerResponse,
    DeliveryPartnerProfileUpdate,
    AvailabilityUpdateRequest,
    DeliveryStatsResponse,
    AvailableDeliveryOrderResponse,
    ActiveDeliveryResponse,
    DeliveryCompleteRequest,
    CODConfirmRequest,
    CODStatusResponse,
    DeliveryHistoryItemResponse,
)
from app.schemas.order import OrderStatusHistoryResponse
from app.schemas.order_item import OrderItemResponse
from app.crud import crud_delivery, crud_order
from app.core.exceptions import (
    ResourceNotFoundException,
    BusinessRuleException,
    AuthorizationException,
    ConflictException,
)


def _get_partner_or_raise(db: Session, user: User) -> DeliveryPartner:
    """Helper to retrieve the DeliveryPartner profile for an authenticated user."""
    partner = crud_delivery.get_delivery_partner_by_user_id(db, user.id)
    if not partner:
        raise ResourceNotFoundException("Delivery partner profile for user", user.id)
    return partner


def _transform_active_delivery(assignment: DeliveryAssignment) -> ActiveDeliveryResponse:
    order = assignment.order
    items_list = []
    total_qty = 0
    if order.order_items:
        for it in order.order_items:
            total_qty += it.quantity
            items_list.append(OrderItemResponse.model_validate(it))

    history_list = []
    if order.status_history:
        for hist in sorted(order.status_history, key=lambda h: h.created_at):
            history_list.append(OrderStatusHistoryResponse.model_validate(hist))

    restaurant_name = order.restaurant.name if order.restaurant else "Campus Eatery"
    restaurant_address = order.restaurant.address if order.restaurant else ""
    restaurant_phone = order.restaurant.contact_number if order.restaurant else None

    customer_name = order.customer.full_name if order.customer else "Student Customer"
    customer_phone = order.customer.phone_number if order.customer else None

    return ActiveDeliveryResponse(
        order_id=order.id,
        assignment_id=assignment.id,
        order_status=order.order_status,
        delivery_status=assignment.delivery_status,
        restaurant_name=restaurant_name,
        restaurant_address=restaurant_address,
        restaurant_phone=restaurant_phone,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=order.delivery_address,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        cod_collected=order.cod_collected,
        items=items_list,
        item_count=total_qty,
        assigned_at=assignment.assigned_at,
        picked_up_at=assignment.picked_up_at,
        out_for_delivery_at=assignment.started_delivery_at,
        delivered_at=assignment.completed_at,
        status_history=history_list,
    )


# ==============================================================================
# PROFILE & AVAILABILITY SERVICES
# ==============================================================================

def get_delivery_partner_profile(db: Session, current_user: User) -> DeliveryPartnerResponse:
    partner = _get_partner_or_raise(db, current_user)
    resp = DeliveryPartnerResponse.model_validate(partner)
    resp.full_name = current_user.full_name
    resp.email = current_user.email
    resp.phone_number = current_user.phone_number
    return resp


def update_delivery_partner_profile(
    db: Session, current_user: User, profile_in: DeliveryPartnerProfileUpdate
) -> DeliveryPartnerResponse:
    partner = _get_partner_or_raise(db, current_user)
    updated = crud_delivery.update_delivery_partner_profile(
        db=db,
        partner=partner,
        vehicle_type=profile_in.vehicle_type,
        vehicle_registration_number=profile_in.vehicle_registration_number,
        phone_number=profile_in.phone_number,
    )
    resp = DeliveryPartnerResponse.model_validate(updated)
    resp.full_name = current_user.full_name
    resp.email = current_user.email
    resp.phone_number = current_user.phone_number
    return resp


def update_delivery_partner_availability(
    db: Session, current_user: User, req: AvailabilityUpdateRequest
) -> DeliveryPartnerResponse:
    partner = _get_partner_or_raise(db, current_user)

    # Check if partner currently has an active delivery
    active_assignment = crud_delivery.get_active_assignment_by_partner(db, partner.id)
    if active_assignment and req.availability_status in [
        PartnerAvailability.AVAILABLE,
        PartnerAvailability.OFFLINE,
    ]:
        raise BusinessRuleException(
            "Cannot change availability to AVAILABLE or OFFLINE while you have an active delivery in progress. "
            "Please complete the delivery first."
        )

    updated = crud_delivery.update_delivery_partner_availability(
        db=db, partner=partner, status=req.availability_status
    )
    resp = DeliveryPartnerResponse.model_validate(updated)
    resp.full_name = current_user.full_name
    resp.email = current_user.email
    resp.phone_number = current_user.phone_number
    return resp


# ==============================================================================
# ORDER DISCOVERY & ASSIGNMENT SERVICES
# ==============================================================================

def list_available_orders_for_delivery(
    db: Session, current_user: User, page: int = 1, size: int = 20
) -> Tuple[List[AvailableDeliveryOrderResponse], int]:
    partner = _get_partner_or_raise(db, current_user)

    # Partner must be set to AVAILABLE
    if partner.availability_status != PartnerAvailability.AVAILABLE:
        raise BusinessRuleException(
            "You must set your status to AVAILABLE to browse and accept delivery requests."
        )

    orders, total = crud_delivery.get_available_orders_for_delivery(db, page, size)

    results: List[AvailableDeliveryOrderResponse] = []
    for ord_obj in orders:
        summary_items = []
        item_count = 0
        if ord_obj.order_items:
            for it in ord_obj.order_items:
                summary_items.append(f"{it.quantity}x {it.item_name}")
                item_count += it.quantity
        items_summary = ", ".join(summary_items) if summary_items else "Food items"

        area = ord_obj.delivery_address.split(",")[0].strip() if ord_obj.delivery_address else "Campus Dorm"

        results.append(
            AvailableDeliveryOrderResponse(
                order_id=ord_obj.id,
                restaurant_name=ord_obj.restaurant.name if ord_obj.restaurant else "Campus Eatery",
                restaurant_address=ord_obj.restaurant.address if ord_obj.restaurant else "",
                restaurant_phone=ord_obj.restaurant.contact_number if ord_obj.restaurant else None,
                delivery_area=area,
                delivery_address=ord_obj.delivery_address,
                item_count=item_count,
                items_summary=items_summary,
                total_amount=ord_obj.total_amount,
                payment_method=ord_obj.payment_method,
                created_at=ord_obj.created_at,
                ready_for_pickup_at=ord_obj.ready_for_pickup_at,
            )
        )

    return results, total


def accept_delivery_request(
    db: Session, current_user: User, order_id: uuid.UUID
) -> ActiveDeliveryResponse:
    partner = _get_partner_or_raise(db, current_user)

    # 1. Partner availability check
    if partner.availability_status != PartnerAvailability.AVAILABLE:
        raise BusinessRuleException("You must be set to AVAILABLE to claim a delivery request.")

    # 2. Single active delivery per courier check
    active = crud_delivery.get_active_assignment_by_partner(db, partner.id)
    if active:
        raise BusinessRuleException("You already have an active delivery in progress.")

    # 3. Atomic claim with row locking & conflict detection
    order, assignment = crud_delivery.claim_order_for_delivery(
        db=db,
        order_id=order_id,
        partner_id=partner.id,
        user_id=current_user.id,
    )

    if not order or not assignment:
        # Check if order exists
        existing_order = crud_order.get_order_by_id(db, order_id)
        if not existing_order:
            raise ResourceNotFoundException("Order", order_id)
        raise ConflictException(
            "This delivery request has already been claimed by another delivery partner or is no longer eligible."
        )

    return _transform_active_delivery(assignment)


def get_current_active_delivery(
    db: Session, current_user: User
) -> Optional[ActiveDeliveryResponse]:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_active_assignment_by_partner(db, partner.id)
    if not assignment:
        return None
    return _transform_active_delivery(assignment)


def get_assignment_detail_by_order(
    db: Session, current_user: User, order_id: uuid.UUID
) -> ActiveDeliveryResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    # IDOR Check: Ensure current delivery partner owns this assignment
    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    return _transform_active_delivery(assignment)


# ==============================================================================
# DELIVERY LIFECYCLE TRANSITIONS
# ==============================================================================

def confirm_restaurant_pickup(
    db: Session, current_user: User, order_id: uuid.UUID
) -> ActiveDeliveryResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    # IDOR Check
    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    order = assignment.order
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    # Validate state
    if order.order_status == OrderStatus.PICKED_UP:
        raise BusinessRuleException("Order has already been picked up from the restaurant.")
    if order.order_status != OrderStatus.READY_FOR_PICKUP:
        raise BusinessRuleException(
            f"Cannot pick up order in '{order.order_status.value}' status. Order must be READY_FOR_PICKUP."
        )

    now_ts = datetime.now(timezone.utc)
    order.order_status = OrderStatus.PICKED_UP
    order.picked_up_at = now_ts
    assignment.delivery_status = DeliveryStatus.PICKED_UP
    assignment.picked_up_at = now_ts

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=OrderStatus.READY_FOR_PICKUP.value,
        new_status=OrderStatus.PICKED_UP.value,
        changed_by=current_user.id,
        changed_by_role=UserRole.DELIVERY_PARTNER.value,
        notes="Courier collected order package from restaurant kitchen.",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    db.refresh(assignment)

    return _transform_active_delivery(assignment)


def start_out_for_delivery(
    db: Session, current_user: User, order_id: uuid.UUID
) -> ActiveDeliveryResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    # IDOR Check
    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    order = assignment.order
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    if order.order_status == OrderStatus.OUT_FOR_DELIVERY:
        raise BusinessRuleException("Order is already out for delivery.")
    if order.order_status != OrderStatus.PICKED_UP:
        raise BusinessRuleException(
            f"Cannot start delivery for order in '{order.order_status.value}' status. Order must be PICKED_UP."
        )

    now_ts = datetime.now(timezone.utc)
    order.order_status = OrderStatus.OUT_FOR_DELIVERY
    order.out_for_delivery_at = now_ts
    assignment.delivery_status = DeliveryStatus.OUT_FOR_DELIVERY
    assignment.started_delivery_at = now_ts

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=OrderStatus.PICKED_UP.value,
        new_status=OrderStatus.OUT_FOR_DELIVERY.value,
        changed_by=current_user.id,
        changed_by_role=UserRole.DELIVERY_PARTNER.value,
        notes="Courier has departed restaurant and is on the way to dorm.",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    db.refresh(assignment)

    return _transform_active_delivery(assignment)


def confirm_cod_collection(
    db: Session, current_user: User, order_id: uuid.UUID, req: CODConfirmRequest
) -> CODStatusResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    order = assignment.order
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    if order.payment_method != PaymentMethod.CASH_ON_DELIVERY:
        raise BusinessRuleException("This order does not use Cash on Delivery.")

    if order.order_status not in [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.PICKED_UP]:
        raise BusinessRuleException(
            f"Cannot collect COD for order in '{order.order_status.value}' status. Must be active out for delivery."
        )

    # Validate exact collection amount (within 0.01 tolerance)
    if abs(req.collected_amount - order.total_amount) > Decimal("0.01"):
        raise BusinessRuleException(
            f"Submitted cash amount (${req.collected_amount}) does not match order payable total (${order.total_amount})."
        )

    now_ts = datetime.now(timezone.utc)
    order.payment_status = PaymentStatus.PAID
    order.cod_collected = True
    order.cod_collected_at = now_ts
    order.cod_collected_by = current_user.id

    db.commit()
    db.refresh(order)

    return CODStatusResponse(
        order_id=order.id,
        is_cod=True,
        total_amount=order.total_amount,
        payment_status=order.payment_status,
        cod_collected=order.cod_collected,
        cod_collected_at=order.cod_collected_at,
        cod_collected_by_name=current_user.full_name,
    )


def get_cod_status(
    db: Session, current_user: User, order_id: uuid.UUID
) -> CODStatusResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    order = assignment.order
    is_cod = (order.payment_method == PaymentMethod.CASH_ON_DELIVERY)
    return CODStatusResponse(
        order_id=order.id,
        is_cod=is_cod,
        total_amount=order.total_amount,
        payment_status=order.payment_status,
        cod_collected=order.cod_collected,
        cod_collected_at=order.cod_collected_at,
        cod_collected_by_name=current_user.full_name if order.cod_collected else None,
    )


def complete_delivery(
    db: Session, current_user: User, order_id: uuid.UUID, req: DeliveryCompleteRequest
) -> ActiveDeliveryResponse:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    order = assignment.order
    if not order:
        raise ResourceNotFoundException("Order", order_id)

    if order.order_status != OrderStatus.OUT_FOR_DELIVERY:
        raise BusinessRuleException(
            f"Cannot complete delivery for order in '{order.order_status.value}' status. Order must be OUT_FOR_DELIVERY."
        )

    now_ts = datetime.now(timezone.utc)

    # Cash on Delivery validation
    if order.payment_method == PaymentMethod.CASH_ON_DELIVERY:
        if not order.cod_collected:
            if req.confirm_cash_collected:
                if req.collected_amount is not None:
                    if abs(req.collected_amount - order.total_amount) > Decimal("0.01"):
                        raise BusinessRuleException(
                            f"Collected cash amount (${req.collected_amount}) does not match order total (${order.total_amount})."
                        )
                order.payment_status = PaymentStatus.PAID
                order.cod_collected = True
                order.cod_collected_at = now_ts
                order.cod_collected_by = current_user.id
            else:
                raise BusinessRuleException(
                    "Cash on Delivery payment must be confirmed before marking order as delivered."
                )

    # Complete order & assignment
    order.order_status = OrderStatus.DELIVERED
    order.delivered_at = now_ts
    assignment.delivery_status = DeliveryStatus.DELIVERED
    assignment.delivered_at = now_ts
    assignment.completed_at = now_ts

    # Reset partner availability to AVAILABLE
    partner.availability_status = PartnerAvailability.AVAILABLE
    partner.is_available = True

    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=OrderStatus.OUT_FOR_DELIVERY.value,
        new_status=OrderStatus.DELIVERED.value,
        changed_by=current_user.id,
        changed_by_role=UserRole.DELIVERY_PARTNER.value,
        notes="Courier confirmed order delivery to customer. Transaction complete.",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    db.refresh(assignment)

    return _transform_active_delivery(assignment)


# ==============================================================================
# HISTORY & STATISTICS SERVICES
# ==============================================================================

def get_delivery_history_list(
    db: Session,
    current_user: User,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[DeliveryHistoryItemResponse], int]:
    partner = _get_partner_or_raise(db, current_user)
    assignments, total = crud_delivery.get_delivery_history(
        db=db,
        partner_id=partner.id,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size,
    )

    items: List[DeliveryHistoryItemResponse] = []
    for a in assignments:
        ord_obj = a.order
        items.append(
            DeliveryHistoryItemResponse(
                order_id=ord_obj.id,
                assignment_id=a.id,
                restaurant_name=ord_obj.restaurant.name if ord_obj.restaurant else "Campus Eatery",
                delivery_address=ord_obj.delivery_address,
                total_amount=ord_obj.total_amount,
                payment_method=ord_obj.payment_method,
                payment_status=ord_obj.payment_status,
                order_status=ord_obj.order_status,
                delivery_status=a.delivery_status,
                cod_collected=ord_obj.cod_collected,
                assigned_at=a.assigned_at,
                picked_up_at=a.picked_up_at,
                completed_at=a.completed_at,
            )
        )
    return items, total


def get_delivery_dashboard_stats(
    db: Session, current_user: User
) -> DeliveryStatsResponse:
    partner = _get_partner_or_raise(db, current_user)
    stats_dict = crud_delivery.get_delivery_partner_statistics(
        db, partner.id, current_user.id
    )
    return DeliveryStatsResponse(
        available_requests_count=stats_dict["available_requests_count"],
        active_delivery_count=stats_dict["active_delivery_count"],
        completed_deliveries_count=stats_dict["completed_deliveries_count"],
        total_deliveries_count=stats_dict["total_deliveries_count"],
        total_cod_collected=stats_dict["total_cod_collected"],
        availability_status=partner.availability_status,
    )


def get_order_status_history_for_delivery(
    db: Session, current_user: User, order_id: uuid.UUID
) -> List[OrderStatusHistoryResponse]:
    partner = _get_partner_or_raise(db, current_user)
    assignment = crud_delivery.get_assignment_by_order_id(db, order_id)
    if not assignment:
        raise ResourceNotFoundException("Delivery assignment for order", order_id)

    if assignment.delivery_partner_id != partner.id:
        raise AuthorizationException("You are not the assigned delivery partner for this order.")

    history_records = crud_order.get_order_status_history(db, order_id)
    return [OrderStatusHistoryResponse.model_validate(h) for h in history_records]

