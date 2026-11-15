import uuid
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.review import Review
from app.models.user import User


def get_review_by_id(db: Session, review_id: uuid.UUID) -> Optional[Review]:
    return db.scalar(select(Review).where(Review.id == review_id))


def get_review_by_order_id(db: Session, order_id: uuid.UUID) -> Optional[Review]:
    return db.scalar(select(Review).where(Review.order_id == order_id))


def get_reviews_by_restaurant(
    db: Session,
    restaurant_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[Review], int]:
    stmt = (
        select(Review)
        .where(Review.restaurant_id == restaurant_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    count_stmt = select(func.count(Review.id)).where(Review.restaurant_id == restaurant_id)
    total = db.scalar(count_stmt) or 0
    return items, total


def get_restaurant_rating_stats(db: Session, restaurant_id: uuid.UUID) -> Tuple[float, int, Dict[int, int]]:
    avg_rating_stmt = select(func.avg(Review.rating), func.count(Review.id)).where(
        Review.restaurant_id == restaurant_id
    )
    row = db.execute(avg_rating_stmt).one_or_none()
    avg_val = float(row[0]) if row and row[0] is not None else 0.0
    total_count = int(row[1]) if row and row[1] is not None else 0

    # Rating distribution 1..5
    dist_stmt = (
        select(Review.rating, func.count(Review.id))
        .where(Review.restaurant_id == restaurant_id)
        .group_by(Review.rating)
    )
    dist_rows = db.execute(dist_stmt).all()
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r, c in dist_rows:
        if r in distribution:
            distribution[r] = int(c)

    return round(avg_val, 2), total_count, distribution


def get_reviews_by_customer(
    db: Session,
    customer_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[Review], int]:
    stmt = (
        select(Review)
        .where(Review.customer_id == customer_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    count_stmt = select(func.count(Review.id)).where(Review.customer_id == customer_id)
    total = db.scalar(count_stmt) or 0
    return items, total


def create_review(
    db: Session,
    customer_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    order_id: uuid.UUID,
    rating: int,
    comment: Optional[str] = None,
) -> Review:
    review = Review(
        id=uuid.uuid4(),
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        order_id=order_id,
        rating=rating,
        comment=comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_review(
    db: Session,
    review: Review,
    rating: int,
    comment: Optional[str] = None,
) -> Review:
    review.rating = rating
    review.comment = comment
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()

