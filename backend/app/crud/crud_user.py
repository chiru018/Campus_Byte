import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.scalar(select(User).where(User.id == user_id))


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return list(db.scalars(select(User).offset(skip).limit(limit)).all())


def count_users(db: Session) -> int:
    return db.scalar(select(func.count(User.id))) or 0


def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        full_name=user_in.full_name,
        email=user_in.email.lower(),
        phone_number=user_in.phone_number,
        password_hash=hashed_pwd,
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_obj: User, update_data: UserUpdate) -> User:
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user_obj, field, value)
    db.commit()
    db.refresh(user_obj)
    return user_obj
