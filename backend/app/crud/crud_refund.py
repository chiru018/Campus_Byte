import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.refund_request import RefundRequest
from app.models.enums import RefundStatus, RefundIssueCategory


def get_refund_by_id(db: Session, refund_id: uuid.UUID) -> Optional[RefundRequest]:
    return db.scalar(select(RefundRequest).where(RefundRequest.id == refund_id))


def get_active_refund_for_order(db: Session, order_id: uuid.UUID) -> Optional[RefundRequest]:
    """Finds an active refund request for an order that is not REJECTED."""
    stmt = (
        select(RefundRequest)
        .where(
            RefundRequest.order_id == order_id,
            RefundRequest.status.in_([
                RefundStatus.PENDING.value,
                RefundStatus.UNDER_REVIEW.value,
                RefundStatus.APPROVED.value,
                RefundStatus.RESOLVED.value,
            ]),
        )
    )
    return db.scalar(stmt)


def get_refunds_by_customer(
    db: Session,
    customer_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[RefundRequest], int]:
    stmt = (
        select(RefundRequest)
        .where(RefundRequest.customer_id == customer_id)
        .order_by(desc(RefundRequest.created_at))
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    count_stmt = select(func.count(RefundRequest.id)).where(RefundRequest.customer_id == customer_id)
    total = db.scalar(count_stmt) or 0
    return items, total


def get_refunds_by_restaurant(
    db: Session,
    restaurant_id: uuid.UUID,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[RefundRequest], int]:
    stmt = select(RefundRequest).where(RefundRequest.restaurant_id == restaurant_id)
    count_stmt = select(func.count(RefundRequest.id)).where(RefundRequest.restaurant_id == restaurant_id)

    if status:
        stmt = stmt.where(RefundRequest.status == status)
        count_stmt = count_stmt.where(RefundRequest.status == status)

    stmt = stmt.order_by(desc(RefundRequest.created_at)).offset(skip) .limit(limit)
    items = list(db.scalars(stmt).all())
    total = db.scalar(count_stmt) or 0
    return items, total


def create_refund_request(
    db: Session,
    order_id: uuid.UUID,
    customer_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    issue_category: str,
    description: str,
    requested_amount: Decimal,
) -> RefundRequest:
    refund = RefundRequest(
        id=uuid.uuid4(),
        order_id=order_id,
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        issue_category=issue_category,
        description=description,
        requested_amount=requested_amount,
        status=RefundStatus.PENDING.value,
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund


def update_refund_status(
    db: Session,
    refund: RefundRequest,
    status: str,
    approved_amount: Optional[Decimal] = None,
    owner_response: Optional[str] = None,
    resolution_notes: Optional[str] = None,
) -> RefundRequest:
    refund.status = status
    if approved_amount is not None:
        refund.approved_amount = approved_amount
    if owner_response is not None:
        refund.owner_response = owner_response
    if resolution_notes is not None:
        refund.resolution_notes = resolution_notes

    if status in (RefundStatus.APPROVED.value, RefundStatus.REJECTED.value, RefundStatus.RESOLVED.value):
        refund.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(refund)
    return refund

