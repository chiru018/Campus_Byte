import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import require_customer, require_restaurant_owner
from app.schemas.refund import (
    RefundRequestCreate,
    RefundApproveRequest,
    RefundRejectRequest,
    RefundResolveRequest,
    RefundRequestResponse,
    RefundListResponse,
)
from app.services import refund_service

router = APIRouter(tags=["Refund & Issue Management"])


# ==============================================================================
# CUSTOMER REFUND ENDPOINTS
# ==============================================================================

@router.post(
    "/refunds",
    response_model=RefundRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Raise Refund / Issue Request",
    description="Customer raises an issue or refund request for a completed (DELIVERED) order.",
)
def create_refund_endpoint(
    data: RefundRequestCreate,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return refund_service.create_customer_refund_request(
        db=db, customer=current_user, data=data
    )


@router.get(
    "/refunds/my-requests",
    response_model=RefundListResponse,
    summary="Get Customer Refund Requests",
    description="Returns all refund and issue requests submitted by the authenticated customer.",
)
def get_my_refunds_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return refund_service.get_customer_refund_requests(
        db=db, customer=current_user, page=page, size=size
    )


@router.get(
    "/refunds/{refund_id}",
    response_model=RefundRequestResponse,
    summary="Get Customer Refund Details",
    description="Retrieves status and resolution details for a specific refund request.",
)
def get_customer_refund_detail_endpoint(
    refund_id: uuid.UUID,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return refund_service.get_customer_refund_detail(
        db=db, refund_id=refund_id, customer=current_user
    )


# ==============================================================================
# RESTAURANT OWNER REFUND ENDPOINTS
# ==============================================================================

@router.get(
    "/restaurant/refunds",
    response_model=RefundListResponse,
    summary="Get Restaurant Refund Requests",
    description="Restaurant owner retrieves issue and refund requests submitted for their outlet.",
)
def get_restaurant_refunds_endpoint(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, UNDER_REVIEW, APPROVED, REJECTED, RESOLVED)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.get_restaurant_refund_requests(
        db=db, owner=current_user, status_filter=status, page=page, size=size
    )


@router.get(
    "/restaurant/refunds/{refund_id}",
    response_model=RefundRequestResponse,
    summary="Get Restaurant Refund Details",
    description="Restaurant owner views details of a specific refund request.",
)
def get_restaurant_refund_detail_endpoint(
    refund_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.get_restaurant_refund_detail(
        db=db, refund_id=refund_id, owner=current_user
    )


@router.patch(
    "/restaurant/refunds/{refund_id}/under-review",
    response_model=RefundRequestResponse,
    summary="Mark Refund Under Review",
    description="Restaurant owner moves request from PENDING to UNDER_REVIEW.",
)
def set_under_review_endpoint(
    refund_id: uuid.UUID,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.set_refund_under_review(
        db=db, refund_id=refund_id, owner=current_user
    )


@router.patch(
    "/restaurant/refunds/{refund_id}/approve",
    response_model=RefundRequestResponse,
    summary="Approve Refund Request",
    description="Restaurant owner approves refund request with validated refund amount.",
)
def approve_refund_endpoint(
    refund_id: uuid.UUID,
    data: RefundApproveRequest,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.approve_refund_request(
        db=db, refund_id=refund_id, owner=current_user, data=data
    )


@router.patch(
    "/restaurant/refunds/{refund_id}/reject",
    response_model=RefundRequestResponse,
    summary="Reject Refund Request",
    description="Restaurant owner rejects refund request with mandatory explanation.",
)
def reject_refund_endpoint(
    refund_id: uuid.UUID,
    data: RefundRejectRequest,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.reject_refund_request(
        db=db, refund_id=refund_id, owner=current_user, data=data
    )


@router.patch(
    "/restaurant/refunds/{refund_id}/resolve",
    response_model=RefundRequestResponse,
    summary="Mark Refund Resolved",
    description="Restaurant owner marks approved refund as settled/resolved.",
)
def resolve_refund_endpoint(
    refund_id: uuid.UUID,
    data: RefundResolveRequest,
    current_user: User = Depends(require_restaurant_owner),
    db: Session = Depends(get_db),
):
    return refund_service.resolve_refund_request(
        db=db, refund_id=refund_id, owner=current_user, data=data
    )

