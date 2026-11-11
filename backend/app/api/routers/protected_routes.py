from fastapi import APIRouter, Depends

from app.models.user import User
from app.core.permissions import (
    require_customer,
    require_restaurant_owner,
    require_delivery_partner,
)

router = APIRouter(prefix="/protected", tags=["RBAC Protected Endpoints"])


@router.get(
    "/customer-only",
    summary="Customer-Only Resource",
    description="Accessible strictly by users with the CUSTOMER role.",
)
def customer_only_endpoint(
    current_user: User = Depends(require_customer),
):
    return {
        "status": "success",
        "message": f"Welcome, Customer {current_user.full_name}!",
        "role": current_user.role.value,
        "user_id": current_user.id,
    }


@router.get(
    "/restaurant-owner-only",
    summary="Restaurant-Owner-Only Resource",
    description="Accessible strictly by users with the RESTAURANT_OWNER role.",
)
def restaurant_owner_only_endpoint(
    current_user: User = Depends(require_restaurant_owner),
):
    return {
        "status": "success",
        "message": f"Welcome, Restaurant Owner {current_user.full_name}!",
        "role": current_user.role.value,
        "user_id": current_user.id,
    }


@router.get(
    "/delivery-partner-only",
    summary="Delivery-Partner-Only Resource",
    description="Accessible strictly by users with the DELIVERY_PARTNER role.",
)
def delivery_partner_only_endpoint(
    current_user: User = Depends(require_delivery_partner),
):
    return {
        "status": "success",
        "message": f"Welcome, Delivery Partner {current_user.full_name}!",
        "role": current_user.role.value,
        "user_id": current_user.id,
    }

