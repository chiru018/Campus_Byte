import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.permissions import require_customer
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    RestaurantReviewSummary,
)
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Customer Review",
    description="Allows a customer to review a restaurant for a qualifying completed (DELIVERED) order.",
)
def submit_review_endpoint(
    data: ReviewCreate,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return review_service.submit_customer_review(db=db, customer=current_user, data=data)


@router.get(
    "/my-reviews",
    response_model=List[ReviewResponse],
    summary="Get My Submitted Reviews",
    description="Returns all restaurant reviews submitted by the authenticated customer.",
)
def get_my_reviews_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return review_service.get_customer_reviews(db=db, customer=current_user, page=page, size=size)


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Edit Customer Review",
    description="Allows a customer to edit their own submitted review.",
)
def update_review_endpoint(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    return review_service.update_customer_review(
        db=db, review_id=review_id, customer=current_user, data=data
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Customer Review",
    description="Allows a customer to delete their own submitted review.",
)
def delete_review_endpoint(
    review_id: uuid.UUID,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    review_service.delete_customer_review(
        db=db, review_id=review_id, customer=current_user
    )
    return None


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=RestaurantReviewSummary,
    summary="Get Restaurant Reviews & Rating Summary",
    description="Public endpoint to retrieve review list, average rating, and 1-5 star distribution for a restaurant.",
)
def get_restaurant_reviews_endpoint(
    restaurant_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return review_service.get_restaurant_reviews_summary(
        db=db, restaurant_id=restaurant_id, page=page, size=size
    )

