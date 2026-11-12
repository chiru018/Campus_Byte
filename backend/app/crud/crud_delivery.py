import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models.delivery_partner import DeliveryPartner
from app.models.delivery_assignment import DeliveryAssignment
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.restaurant import Restaurant
from app.models.user import User
from app.models.enums import (
    UserRole,
    VehicleType,
    PartnerAvailability,
    DeliveryStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)


def get_delivery_partner_by_user_id(
    db: Session, user_id: uuid.UUID
) -> Optional[DeliveryPartner]:
    return db.scalar(
        select(DeliveryPartner)
        .options(joinedload(DeliveryPartner.user))
        .where(DeliveryPartner.user_id == user_id)
    )


def get_delivery_partner_by_id(
    db: Session, partner_id: uuid.UUID
) -> Optional[DeliveryPartner]:
    return db.scalar(
        select(DeliveryPartner)
        .options(joinedload(DeliveryPartner.user))
        .where(DeliveryPartner.id == partner_id)
    )


def create_delivery_partner_profile(
    db: Session,
    user_id: uuid.UUID,
    vehicle_type: VehicleType = VehicleType.BICYCLE,
    vehicle_registration_number: Optional[str] = None,
) -> DeliveryPartner:
    partner = DeliveryPartner(
        user_id=user_id,
        vehicle_type=vehicle_type,
        vehicle_registration_number=vehicle_registration_number,
        availability_status=PartnerAvailability.AVAILABLE,
        is_available=True,
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)
    return partner


def update_delivery_partner_profile(
    db: Session,
    partner: DeliveryPartner,
    vehicle_type: Optional[VehicleType] = None,
    vehicle_registration_number: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> DeliveryPartner:
    if vehicle_type is not None:
        partner.vehicle_type = vehicle_type
    if vehicle_registration_number is not None:
        partner.vehicle_registration_number = vehicle_registration_number
    if phone_number is not None and partner.user:
        partner.user.phone_number = phone_number

    db.commit()
    db.refresh(partner)
    return partner


def update_delivery_partner_availability(
    db: Session,
    partner: DeliveryPartner,
    status: PartnerAvailability,
) -> DeliveryPartner:
    partner.availability_status = status
    partner.is_available = (status == PartnerAvailability.AVAILABLE)
    db.commit()
    db.refresh(partner)
    return partner


def get_active_assignment_by_partner(
    db: Session, partner_id: uuid.UUID
) -> Optional[DeliveryAssignment]:
    active_statuses = [
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.OUT_FOR_DELIVERY,
    ]
    return db.scalar(
        select(DeliveryAssignment)
        .options(
            joinedload(DeliveryAssignment.order).joinedload(Order.restaurant),
            joinedload(DeliveryAssignment.order).joinedload(Order.customer),
            joinedload(DeliveryAssignment.order).joinedload(Order.order_items),
            joinedload(DeliveryAssignment.order).joinedload(Order.status_history),
        )
        .where(
            DeliveryAssignment.delivery_partner_id == partner_id,
            DeliveryAssignment.delivery_status.in_(active_statuses),
        )
        .order_by(DeliveryAssignment.assigned_at.desc())
    )


def get_active_assignment_by_order(
    db: Session, order_id: uuid.UUID
) -> Optional[DeliveryAssignment]:
    active_statuses = [
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.OUT_FOR_DELIVERY,
    ]
    return db.scalar(
        select(DeliveryAssignment).where(
            DeliveryAssignment.order_id == order_id,
            DeliveryAssignment.delivery_status.in_(active_statuses),
        )
    )


def get_assignment_by_order_id(
    db: Session, order_id: uuid.UUID
) -> Optional[DeliveryAssignment]:
    return db.scalar(
        select(DeliveryAssignment)
        .options(
            joinedload(DeliveryAssignment.delivery_partner).joinedload(DeliveryPartner.user),
            joinedload(DeliveryAssignment.order).joinedload(Order.restaurant),
            joinedload(DeliveryAssignment.order).joinedload(Order.customer),
        )
        .where(DeliveryAssignment.order_id == order_id)
        .order_by(DeliveryAssignment.assigned_at.desc())
    )


def get_available_orders_for_delivery(
    db: Session, page: int = 1, size: int = 20
) -> Tuple[List[Order], int]:
    base_query = (
        select(Order)
        .join(Restaurant, Order.restaurant_id == Restaurant.id)
        .where(
            Order.order_status == OrderStatus.READY_FOR_PICKUP,
            Order.delivery_partner_id.is_(None),
            Restaurant.is_open.is_(True),
        )
    )

    count_stmt = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(count_stmt) or 0

    orders_stmt = (
        base_query
        .options(
            joinedload(Order.restaurant),
            joinedload(Order.customer),
            joinedload(Order.order_items),
        )
        .order_by(
            func.coalesce(Order.ready_for_pickup_at, Order.created_at).desc()
        )
        .offset((page - 1) * size)
        .limit(size)
    )
    orders = list(db.scalars(orders_stmt).unique().all())
    return orders, total


def claim_order_for_delivery(
    db: Session,
    order_id: uuid.UUID,
    partner_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Tuple[Optional[Order], Optional[DeliveryAssignment]]:
    """
    Atomically claims an unassigned READY_FOR_PICKUP order for the given delivery partner.
    Uses row-level locking on PostgreSQL or conditional concurrency checks.
    """
    stmt = select(Order).where(Order.id == order_id)
    if db.bind and db.bind.dialect.name != "sqlite":
        stmt = stmt.with_for_update()

    order = db.scalar(stmt)
    if not order:
        return None, None

    # Check eligibility
    if order.order_status != OrderStatus.READY_FOR_PICKUP or order.delivery_partner_id is not None:
        return None, None

    # Assign order
    order.delivery_partner_id = partner_id

    # Create delivery assignment
    assignment = DeliveryAssignment(
        order_id=order.id,
        delivery_partner_id=partner_id,
        delivery_status=DeliveryStatus.ASSIGNED,
    )
    db.add(assignment)

    # Record history
    history = OrderStatusHistory(
        order_id=order.id,
        previous_status=OrderStatus.READY_FOR_PICKUP.value,
        new_status=OrderStatus.READY_FOR_PICKUP.value,
        changed_by=user_id,
        changed_by_role=UserRole.DELIVERY_PARTNER.value,
        notes="Delivery partner accepted assignment. Ready for restaurant pickup.",
    )
    db.add(history)

    # Set partner availability to BUSY
    partner = db.get(DeliveryPartner, partner_id)
    if partner:
        partner.availability_status = PartnerAvailability.BUSY
        partner.is_available = False

    db.commit()
    db.refresh(order)
    db.refresh(assignment)
    return order, assignment


def get_delivery_history(
    db: Session,
    partner_id: uuid.UUID,
    status_filter: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[DeliveryAssignment], int]:
    base_query = (
        select(DeliveryAssignment)
        .join(Order, DeliveryAssignment.order_id == Order.id)
        .where(DeliveryAssignment.delivery_partner_id == partner_id)
    )

    if status_filter and status_filter.upper() != "ALL":
        target = status_filter.upper()
        if target in [s.value for s in DeliveryStatus]:
            base_query = base_query.where(DeliveryAssignment.delivery_status == DeliveryStatus(target))
        elif target in [s.value for s in OrderStatus]:
            base_query = base_query.where(Order.order_status == OrderStatus(target))

    if date_from:
        base_query = base_query.where(DeliveryAssignment.assigned_at >= date_from)
    if date_to:
        base_query = base_query.where(DeliveryAssignment.assigned_at <= date_to)

    count_stmt = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(count_stmt) or 0

    assignments_stmt = (
        base_query
        .options(
            joinedload(DeliveryAssignment.order).joinedload(Order.restaurant),
            joinedload(DeliveryAssignment.order).joinedload(Order.customer),
        )
        .order_by(DeliveryAssignment.assigned_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    assignments = list(db.scalars(assignments_stmt).unique().all())
    return assignments, total


def get_delivery_partner_statistics(
    db: Session, partner_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    # 1. Available requests count (platform-wide unassigned READY_FOR_PICKUP)
    available_stmt = (
        select(func.count())
        .select_from(Order)
        .join(Restaurant, Order.restaurant_id == Restaurant.id)
        .where(
            Order.order_status == OrderStatus.READY_FOR_PICKUP,
            Order.delivery_partner_id.is_(None),
            Restaurant.is_open.is_(True),
        )
    )
    available_count = db.scalar(available_stmt) or 0

    # 2. Active delivery count for this partner
    active_statuses = [
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.OUT_FOR_DELIVERY,
    ]
    active_stmt = (
        select(func.count())
        .select_from(DeliveryAssignment)
        .where(
            DeliveryAssignment.delivery_partner_id == partner_id,
            DeliveryAssignment.delivery_status.in_(active_statuses),
        )
    )
    active_count = db.scalar(active_stmt) or 0

    # 3. Completed deliveries count for this partner
    completed_stmt = (
        select(func.count())
        .select_from(DeliveryAssignment)
        .where(
            DeliveryAssignment.delivery_partner_id == partner_id,
            DeliveryAssignment.delivery_status == DeliveryStatus.DELIVERED,
        )
    )
    completed_count = db.scalar(completed_stmt) or 0

    # 4. Total deliveries count for this partner
    total_stmt = (
        select(func.count())
        .select_from(DeliveryAssignment)
        .where(DeliveryAssignment.delivery_partner_id == partner_id)
    )
    total_count = db.scalar(total_stmt) or 0

    # 5. Total COD collected by this partner
    cod_stmt = (
        select(func.coalesce(func.sum(Order.total_amount), Decimal("0.00")))
        .where(
            Order.cod_collected.is_(True),
            Order.cod_collected_by == user_id,
        )
    )
    cod_total = db.scalar(cod_stmt) or Decimal("0.00")

    return {
        "available_requests_count": available_count,
        "active_delivery_count": active_count,
        "completed_deliveries_count": completed_count,
        "total_deliveries_count": total_count,
        "total_cod_collected": cod_total,
    }
