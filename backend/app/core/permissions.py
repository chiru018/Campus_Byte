from typing import List, Callable
from fastapi import Depends

from app.models.user import User
from app.models.enums import UserRole
from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationException


class RoleChecker:
    """
    Reusable Role-Based Access Control dependency.
    Enforces that the authenticated user possesses one of the allowed roles.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            role_names = ", ".join([r.value for r in self.allowed_roles])
            raise AuthorizationException(
                detail=f"Operation requires one of the following roles: [{role_names}]. Current role: '{current_user.role.value}'."
            )
        return current_user


def require_roles(*roles: UserRole) -> Callable:
    """Factory creating a role-checking dependency for arbitrary role combinations."""
    return RoleChecker(allowed_roles=list(roles))


# Specific role dependencies
require_customer = RoleChecker([UserRole.CUSTOMER])
require_restaurant_owner = RoleChecker([UserRole.RESTAURANT_OWNER])
require_delivery_partner = RoleChecker([UserRole.DELIVERY_PARTNER])
