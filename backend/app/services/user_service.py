import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException
import app.crud.crud_user as crud_user


def register_user(db: Session, user_in: UserCreate) -> User:
    existing = crud_user.get_user_by_email(db, user_in.email)
    if existing:
        raise DuplicateResourceException("User", "email", user_in.email)
    return crud_user.create_user(db, user_in)


def fetch_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundException("User", user_id)
    return user


def fetch_users(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
    users = crud_user.get_users(db, skip=skip, limit=limit)
    total = crud_user.count_users(db)
    return users, total


def modify_user(db: Session, user_id: uuid.UUID, update_data: UserUpdate) -> User:
    user = fetch_user_by_id(db, user_id)
    return crud_user.update_user(db, user, update_data)
