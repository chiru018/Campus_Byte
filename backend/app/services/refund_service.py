import uuid
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.enums import OrderStatus, RefundStatus
from app.models.refund_request import RefundRequest
from app.crud import crud_refund
from app.schemas.refund import (
    RefundRequestCreate,
    RefundApproveRequest,
    RefundRejectRequest,
    RefundResolveRequest,
    RefundRequestResponse,
    RefundListResponse,
)


def _to_response(db: Session, r: RefundRequest) -> RefundRequestResponse:
    cust = db.get(User, r.customer_id)
    rest = db.get(Restaurant, r.restaurant_id)
    return RefundRequestResponse(
        id=r.id,
        order_id=r.order_id,
        customer_id=r.customer_id,
        customer_name=cust.full_name if cust else "Campus Customer",
        restaurant_id=r.restaurant_id,
        restaurant_name=rest.name if rest else "Campus Restaurant",
        issue_category=r.issue_category,
        description=r.description,
        requested_amount=r.requested_amount,
        approved_amount=r.approved_amount,
        status=r.status,
        owner_response=r.owner_response,
        resolution_notes=r.resolution_notes,
        created_at=r.created_at,
        updated_at=r.updated_at,
        resolved_at=r.resolved_at,
    )


def create_customer_refund_request(
    db: Session,
    customer: User,
    data: RefundRequestCreate,
) -> RefundRequestResponse:
    # 1. Fetch order
    order = db.get(Order, data.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    # 2. Ownership verification
    if order.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only raise refund requests for your own orders.",
        )

    # 3. Only DELIVERED orders qualify
    if order.order_status != OrderStatus.DELIVERED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund requests can only be raised for DELIVERED orders.",
        )

    # 4. Requested amount cannot exceed order total
    if data.requested_amount > order.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested refund amount ({data.requested_amount}) cannot exceed the order total amount ({order.total_amount}).",
        )

    # 5. Check for active refund request for this order
    active_req = crud_refund.get_active_refund_for_order(db, data.order_id)
    if active_req:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An active refund request ({active_req.status}) already exists for this order.",
        )

    refund = crud_refund.create_refund_request(
        db=db,
        order_id=order.id,
        customer_id=customer.id,
        restaurant_id=order.restaurant_id,
        issue_category=data.issue_category.value,
        description=data.description.strip(),
        requested_amount=data.requested_amount,
    )

    return _to_response(db, refund)


def get_customer_refund_requests(
    db: Session,
    customer: User,
    page: int = 1,
    size: int = 20,
) -> RefundListResponse:
    skip = (page - 1) * size
    refunds, total = crud_refund.get_refunds_by_customer(db, customer.id, skip=skip, limit=size)
    items = [_to_response(db, r) for r in refunds]
    return RefundListResponse(requests=items, total=total)


def get_customer_refund_detail(
    db: Session,
    refund_id: uuid.UUID,
    customer: User,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    if refund.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return _to_response(db, refund)


def get_restaurant_refund_requests(
    db: Session,
    owner: User,
    status_filter: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> RefundListResponse:
    # 1. Fetch restaurant owned by this owner
    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant profile not found for this owner.",
        )

    skip = (page - 1) * size
    refunds, total = crud_refund.get_refunds_by_restaurant(
        db, restaurant.id, status=status_filter, skip=skip, limit=size
    )
    items = [_to_response(db, r) for r in refunds]
    return RefundListResponse(requests=items, total=total)


def get_restaurant_refund_detail(
    db: Session,
    refund_id: uuid.UUID,
    owner: User,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant or refund.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return _to_response(db, refund)


def set_refund_under_review(
    db: Session,
    refund_id: uuid.UUID,
    owner: User,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant or refund.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if refund.status != RefundStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move request from {refund.status} to UNDER_REVIEW.",
        )

    updated = crud_refund.update_refund_status(db, refund, RefundStatus.UNDER_REVIEW.value)
    return _to_response(db, updated)


def approve_refund_request(
    db: Session,
    refund_id: uuid.UUID,
    owner: User,
    data: RefundApproveRequest,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant or refund.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if refund.status not in (RefundStatus.PENDING.value, RefundStatus.UNDER_REVIEW.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status '{refund.status}'.",
        )

    if data.approved_amount > refund.requested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approved amount ({data.approved_amount}) cannot exceed requested amount ({refund.requested_amount}).",
        )

    updated = crud_refund.update_refund_status(
        db=db,
        refund=refund,
        status=RefundStatus.APPROVED.value,
        approved_amount=data.approved_amount,
        resolution_notes=data.resolution_notes,
    )
    return _to_response(db, updated)


def reject_refund_request(
    db: Session,
    refund_id: uuid.UUID,
    owner: User,
    data: RefundRejectRequest,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant or refund.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if refund.status not in (RefundStatus.PENDING.value, RefundStatus.UNDER_REVIEW.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject request with status '{refund.status}'.",
        )

    if not data.explanation or not data.explanation.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mandatory explanation is required to reject a refund request.",
        )

    updated = crud_refund.update_refund_status(
        db=db,
        refund=refund,
        status=RefundStatus.REJECTED.value,
        owner_response=data.explanation.strip(),
    )
    return _to_response(db, updated)


def resolve_refund_request(
    db: Session,
    refund_id: uuid.UUID,
    owner: User,
    data: RefundResolveRequest,
) -> RefundRequestResponse:
    refund = crud_refund.get_refund_by_id(db, refund_id)
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund request not found.")

    from app.crud.crud_restaurant import get_restaurant_by_owner_id
    restaurant = get_restaurant_by_owner_id(db, owner.id)
    if not restaurant or refund.restaurant_id != restaurant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if refund.status != RefundStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only APPROVED requests can be marked RESOLVED. Current status: '{refund.status}'.",
        )

    updated = crud_refund.update_refund_status(
        db=db,
        refund=refund,
        status=RefundStatus.RESOLVED.value,
        resolution_notes=data.resolution_notes,
    )
    return _to_response(db, updated)

