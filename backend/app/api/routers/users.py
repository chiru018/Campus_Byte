import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserListResponse
from app.services.user_service import register_user, fetch_user_by_id, fetch_users

router = APIRouter(prefix="/users", tags=["Users (Development)"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User (Development)",
    description="Registers a new user record with role and salted password hash. Intended for development seeding prior to Phase 3 JWT authentication.",
)
def create_user_endpoint(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(db=db, user_in=user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User By ID (Development)",
    description="Retrieves public profile details for a user. Sensitive security credentials (password hashes) are never exposed.",
)
def get_user_endpoint(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return fetch_user_by_id(db=db, user_id=user_id)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List Users (Development)",
    description="Lists registered users with pagination. Restricted development utility endpoint.",
)
def list_users_endpoint(
    skip: int = Query(0, ge=0, description="Offset record count"),
    limit: int = Query(100, ge=1, le=100, description="Page limit"),
    db: Session = Depends(get_db),
):
    users, total = fetch_users(db=db, skip=skip, limit=limit)
    return UserListResponse(users=users, total=total)
