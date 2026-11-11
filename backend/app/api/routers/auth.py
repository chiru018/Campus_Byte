from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.auth import (
    CustomerRegisterRequest,
    RestaurantOwnerRegisterRequest,
    DeliveryPartnerRegisterRequest,
    LoginRequest,
    TokenResponse,
    AuthMeResponse,
)
from app.core.config import settings
from app.core.dependencies import get_current_user, extract_raw_token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post(
    "/register/customer",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Customer",
    description="Registers a new customer account with verified email uniqueness and password strength.",
)
def register_customer_endpoint(
    req: CustomerRegisterRequest,
    db: Session = Depends(get_db),
):
    return auth_service.register_customer(db=db, req=req)


@router.post(
    "/register/restaurant-owner",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Restaurant Owner",
    description="Registers a restaurant owner and creates their dining establishment profile atomically.",
)
def register_restaurant_owner_endpoint(
    req: RestaurantOwnerRegisterRequest,
    db: Session = Depends(get_db),
):
    return auth_service.register_restaurant_owner(db=db, req=req)


@router.post(
    "/register/delivery-partner",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Delivery Partner",
    description="Registers a student courier and creates their delivery fleet profile.",
)
def register_delivery_partner_endpoint(
    req: DeliveryPartnerRegisterRequest,
    db: Session = Depends(get_db),
):
    return auth_service.register_delivery_partner(db=db, req=req)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates credentials and returns a signed JWT access token. Also sets a secure HttpOnly session cookie.",
)
def login_endpoint(
    req: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user, token, expires_in = auth_service.authenticate_user(db=db, req=req)

    # Set secure HttpOnly cookie for browser protection
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        max_age=expires_in,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=user,
    )


@router.get(
    "/me",
    response_model=AuthMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Resolves and returns the full profile of the authenticated user from the verified JWT.",
)
def get_current_user_profile_endpoint(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout User",
    description="Invalidates the current JWT by recording its jti in the database revocation denylist and clears session cookies.",
)
def logout_endpoint(
    response: Response,
    token: str = Depends(extract_raw_token),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service.logout_user(db=db, token=token)

    # Clear HttpOnly session cookie
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path="/",
        httponly=settings.COOKIE_HTTPONLY,
        samesite=settings.COOKIE_SAMESITE,
    )

    return {
        "message": "Successfully logged out. Session has been revoked.",
        "user_id": current_user.id,
    }
