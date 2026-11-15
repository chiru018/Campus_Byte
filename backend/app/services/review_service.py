import uuid
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.enums import OrderStatus
from app.crud import crud_review
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    RestaurantReviewSummary,
)


def submit_customer_review(
    db: Session,
    customer: User,
    data: ReviewCreate,
) -> ReviewResponse:
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
            detail="You can only review your own orders.",
        )

    # 3. Only DELIVERED orders qualify
    if order.order_status != OrderStatus.DELIVERED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be submitted for completed (DELIVERED) orders.",
        )

    # 4. Check for duplicate review on this order
    existing = crud_review.get_review_by_order_id(db, data.order_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A review has already been submitted for this order.",
        )

    # 5. Rating validation
    if not (1 <= data.rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rating must be an integer between 1 and 5.",
        )

    review = crud_review.create_review(
        db=db,
        customer_id=customer.id,
        restaurant_id=order.restaurant_id,
        order_id=order.id,
        rating=data.rating,
        comment=data.comment.strip() if data.comment else None,
    )

    rest = db.get(Restaurant, review.restaurant_id)
    return ReviewResponse(
        id=review.id,
        customer_id=review.customer_id,
        customer_name=customer.full_name,
        restaurant_id=review.restaurant_id,
        restaurant_name=rest.name if rest else "Campus Restaurant",
        order_id=review.order_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def update_customer_review(
    db: Session,
    review_id: uuid.UUID,
    customer: User,
    data: ReviewUpdate,
) -> ReviewResponse:
    review = crud_review.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    if review.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews.",
        )

    if not (1 <= data.rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rating must be an integer between 1 and 5.",
        )

    updated = crud_review.update_review(
        db=db,
        review=review,
        rating=data.rating,
        comment=data.comment.strip() if data.comment else None,
    )

    rest = db.get(Restaurant, updated.restaurant_id)
    return ReviewResponse(
        id=updated.id,
        customer_id=updated.customer_id,
        customer_name=customer.full_name,
        restaurant_id=updated.restaurant_id,
        restaurant_name=rest.name if rest else "Campus Restaurant",
        order_id=updated.order_id,
        rating=updated.rating,
        comment=updated.comment,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


def delete_customer_review(
    db: Session,
    review_id: uuid.UUID,
    customer: User,
) -> None:
    review = crud_review.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    if review.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews.",
        )

    crud_review.delete_review(db, review)


def get_restaurant_reviews_summary(
    db: Session,
    restaurant_id: uuid.UUID,
    page: int = 1,
    size: int = 20,
) -> RestaurantReviewSummary:
    restaurant = db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found.",
        )

    skip = (page - 1) * size
    reviews, total = crud_review.get_reviews_by_restaurant(db, restaurant_id, skip=skip, limit=size)
    avg_rating, total_count, distribution = crud_review.get_restaurant_rating_stats(db, restaurant_id)

    items = []
    for r in reviews:
        c_user = db.get(User, r.customer_id)
        items.append(
            ReviewResponse(
                id=r.id,
                customer_id=r.customer_id,
                customer_name=c_user.full_name if c_user else "Campus Student",
                restaurant_id=r.restaurant_id,
                restaurant_name=restaurant.name,
                order_id=r.order_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return RestaurantReviewSummary(
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        average_rating=avg_rating,
        total_reviews=total_count,
        rating_distribution=distribution,
        reviews=items,
    )


def get_customer_reviews(
    db: Session,
    customer: User,
    page: int = 1,
    size: int = 20,
) -> List[ReviewResponse]:
    skip = (page - 1) * size
    reviews, _ = crud_review.get_reviews_by_customer(db, customer.id, skip=skip, limit=size)
    results = []
    for r in reviews:
        rest = db.get(Restaurant, r.restaurant_id)
        results.append(
            ReviewResponse(
                id=r.id,
                customer_id=r.customer_id,
                customer_name=customer.full_name,
                restaurant_id=r.restaurant_id,
                restaurant_name=rest.name if rest else "Campus Restaurant",
                order_id=r.order_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return results

