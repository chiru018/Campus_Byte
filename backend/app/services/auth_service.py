import uuid
from datetime import datetime, timezone
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt

from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.enums import UserRole
from app.schemas.auth import (
    CustomerRegisterRequest,
    RestaurantOwnerRegisterRequest,
    DeliveryPartnerRegisterRequest,
    LoginRequest,
    AuthMeResponse,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.exceptions import (
    DuplicateResourceException,
    InvalidCredentialsException,
    InactiveAccountException,
    BusinessRuleException,
    AuthenticationException,
)
from app.core.config import settings
import app.crud.crud_user as crud_user
import app.crud.crud_token as crud_token
import app.crud.crud_delivery as crud_delivery


def register_customer(db: Session, req: CustomerRegisterRequest) -> User:
    """Registers a customer user account."""
    existing = crud_user.get_user_by_email(db, req.email)
    if existing:
        raise DuplicateResourceException("User", "email", req.email)

    user = User(
        full_name=req.full_name,
        email=req.email.lower(),
        phone_number=req.phone_number,
        password_hash=get_password_hash(req.password),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_restaurant_owner(
    db: Session, req: RestaurantOwnerRegisterRequest
) -> User:
    """
    Registers a restaurant owner and automatically provisions their restaurant profile.
    Uses atomic transaction to prevent orphan users or restaurants.
    """
    existing = crud_user.get_user_by_email(db, req.email)
    if existing:
        raise DuplicateResourceException("User", "email", req.email)

    try:
        user = User(
            full_name=req.full_name,
            email=req.email.lower(),
            phone_number=req.phone_number,
            password_hash=get_password_hash(req.password),
            role=UserRole.RESTAURANT_OWNER,
            is_active=True,
        )
        db.add(user)
        db.flush()  # Obtain user.id without closing transaction

        restaurant = Restaurant(
            owner_id=user.id,
            name=req.restaurant_name,
            description=req.restaurant_description,
            address=req.restaurant_address,
            contact_number=req.phone_number,
            is_open=True,
        )
        db.add(restaurant)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise BusinessRuleException(
            f"Failed to create restaurant owner profile: {str(exc)}"
        )


def register_delivery_partner(
    db: Session, req: DeliveryPartnerRegisterRequest
) -> User:
    """
    Registers a student courier and provisions their delivery fleet profile.
    Uses atomic transaction to ensure consistent state.
    """
    existing = crud_user.get_user_by_email(db, req.email)
    if existing:
        raise DuplicateResourceException("User", "email", req.email)

    try:
        user = User(
            full_name=req.full_name,
            email=req.email.lower(),
            phone_number=req.phone_number,
            password_hash=get_password_hash(req.password),
            role=UserRole.DELIVERY_PARTNER,
            is_active=True,
        )
        db.add(user)
        db.flush()

        crud_delivery.create_delivery_partner_profile(
            db=db,
            user_id=user.id,
            vehicle_type=req.vehicle_type,
            vehicle_registration_number=req.vehicle_registration_number,
        )
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise BusinessRuleException(
            f"Failed to create delivery partner profile: {str(exc)}"
        )


def authenticate_user(
    db: Session, req: LoginRequest
) -> Tuple[User, str, int]:
    """
    Authenticates user credentials.
    Security: Returns generic InvalidCredentialsException to prevent email enumeration.
    """
    user = crud_user.get_user_by_email(db, req.email)
    if not user:
        raise InvalidCredentialsException()

    if not verify_password(req.password, user.password_hash):
        raise InvalidCredentialsException()

    if not user.is_active:
        raise InactiveAccountException()

    token, jti, expire = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )
    expires_in = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return user, token, expires_in


def logout_user(db: Session, token: str) -> None:
    """
    Revokes the current JWT access token by adding its jti to the database denylist.
    Ensures revoked tokens can never access protected endpoints.
    """
    try:
        payload = decode_access_token(token)
        jti = payload["jti"]
        user_id = uuid.UUID(payload["sub"])
        exp_timestamp = payload["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        if not crud_token.is_token_revoked(db, jti):
            crud_token.revoke_token(
                db=db,
                jti=jti,
                user_id=user_id,
                expires_at=expires_at,
            )
    except jwt.ExpiredSignatureError:
        # Token is already expired naturally, no need to denylist
        pass
    except jwt.InvalidTokenError:
        raise AuthenticationException("Invalid token provided for logout.")

