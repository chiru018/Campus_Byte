import uuid
from datetime import timedelta
import pytest
import jwt
from sqlalchemy import select

from app.models import User, Restaurant, DeliveryPartner, UserRole
from app.core.config import settings
from app.core.security import create_access_token


# =====================================================================
# 1. REGISTRATION TESTS
# =====================================================================

def test_register_customer_success(client, db_session):
    """Test customer registration with valid credentials and password confirmation."""
    payload = {
        "full_name": "Charlie Student",
        "email": "charlie@campus.edu",
        "phone_number": "+1234567890",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    response = client.post("/api/auth/register/customer", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "charlie@campus.edu"
    assert data["role"] == "CUSTOMER"
    assert "password_hash" not in data
    assert "password" not in data

    # Verify user saved in DB with Argon2 hash
    user = db_session.scalar(select(User).where(User.email == "charlie@campus.edu"))
    assert user is not None
    assert user.password_hash.startswith("$argon2")


def test_register_restaurant_owner_success(client, db_session):
    """Test restaurant owner registration creates User and Restaurant profile atomically."""
    payload = {
        "full_name": "Chef Mario",
        "email": "mario@campus.edu",
        "phone_number": "+1555123999",
        "password": "SuperChef2026!",
        "confirm_password": "SuperChef2026!",
        "restaurant_name": "Mario's Campus Trattoria",
        "restaurant_address": "Dining Hall West, Station 3",
        "restaurant_description": "Handmade pasta and fresh paninis",
    }
    response = client.post("/api/auth/register/restaurant-owner", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "mario@campus.edu"
    assert data["role"] == "RESTAURANT_OWNER"
    assert "password_hash" not in data

    # Verify restaurant profile exists and links to owner
    restaurant = db_session.scalar(select(Restaurant).where(Restaurant.name == "Mario's Campus Trattoria"))
    assert restaurant is not None
    assert str(restaurant.owner_id) == data["id"]


def test_register_delivery_partner_success(client, db_session):
    """Test delivery partner registration creates User and Delivery fleet profile atomically."""
    payload = {
        "full_name": "Sam Speed",
        "email": "sam.speed@campus.edu",
        "phone_number": "+1555987654",
        "password": "FastCourier2026!",
        "confirm_password": "FastCourier2026!",
        "vehicle_type": "SCOOTER",
    }
    response = client.post("/api/auth/register/delivery-partner", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "sam.speed@campus.edu"
    assert data["role"] == "DELIVERY_PARTNER"

    # Verify delivery partner record exists
    courier = db_session.scalar(select(DeliveryPartner).where(DeliveryPartner.user_id == uuid.UUID(data["id"])))
    assert courier is not None
    assert courier.vehicle_type == "SCOOTER"


def test_registration_duplicate_email_rejected(client):
    """Test that duplicate email registration returns 409 Conflict."""
    payload = {
        "full_name": "Duplicate User",
        "email": "duplicate.test@campus.edu",
        "password": "ValidPassword123!",
        "confirm_password": "ValidPassword123!",
    }
    res1 = client.post("/api/auth/register/customer", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register/customer", json=payload)
    assert res2.status_code == 409


def test_registration_invalid_email_format(client):
    """Test rejection of malformed email address."""
    payload = {
        "full_name": "Invalid Email",
        "email": "not-an-email",
        "password": "ValidPassword123!",
        "confirm_password": "ValidPassword123!",
    }
    response = client.post("/api/auth/register/customer", json=payload)
    assert response.status_code == 422


def test_registration_password_mismatch(client):
    """Test rejection when password and confirm_password differ."""
    payload = {
        "full_name": "Mismatch Test",
        "email": "mismatch@campus.edu",
        "password": "ValidPassword123!",
        "confirm_password": "DifferentPassword123!",
    }
    response = client.post("/api/auth/register/customer", json=payload)
    assert response.status_code == 422


def test_registration_weak_password_rejected(client):
    """Test rejection of passwords violating the security policy."""
    weak_passwords = [
        "short1!",        # < 8 chars
        "alllowercase1!", # missing uppercase
        "ALLUPPERCASE1!", # missing lowercase
        "NoDigitsHere!",  # missing digit
        "NoSpecialChar1", # missing special char
    ]
    for weak in weak_passwords:
        payload = {
            "full_name": "Weak Pass User",
            "email": f"weak_{weak[:5]}@campus.edu",
            "password": weak,
            "confirm_password": weak,
        }
        response = client.post("/api/auth/register/customer", json=payload)
        assert response.status_code == 422


# =====================================================================
# 2. LOGIN AND AUTHENTICATION TESTS
# =====================================================================

def test_login_success(client):
    """Test successful login returns valid JWT token and sets HttpOnly cookie."""
    # Register customer first
    reg_payload = {
        "full_name": "Login User",
        "email": "login.test@campus.edu",
        "password": "SecureLogin123!",
        "confirm_password": "SecureLogin123!",
    }
    client.post("/api/auth/register/customer", json=reg_payload)

    # Login
    login_payload = {
        "email": "login.test@campus.edu",
        "password": "SecureLogin123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert data["user"]["email"] == "login.test@campus.edu"
    assert "password_hash" not in data["user"]

    # Verify HttpOnly cookie was set
    assert settings.AUTH_COOKIE_NAME in response.cookies


def test_login_invalid_password(client):
    """Test login with wrong password returns 401 without revealing user existence."""
    login_payload = {
        "email": "login.test@campus.edu",
        "password": "WrongPassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_nonexistent_email(client):
    """Test login with non-existent email returns 401 with identical generic message."""
    login_payload = {
        "email": "nobody@campus.edu",
        "password": "AnyPassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_inactive_account(client, db_session):
    """Test deactivated account is denied login."""
    reg_payload = {
        "full_name": "Suspended Student",
        "email": "suspended@campus.edu",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    client.post("/api/auth/register/customer", json=reg_payload)

    # Deactivate account in DB
    user = db_session.scalar(select(User).where(User.email == "suspended@campus.edu"))
    user.is_active = False
    db_session.commit()

    # Attempt login
    response = client.post("/api/auth/login", json={
        "email": "suspended@campus.edu",
        "password": "Password123!",
    })
    assert response.status_code == 401
    assert "inactive or suspended" in response.json()["detail"]


# =====================================================================
# 3. JWT SECURITY & TOKEN REVOCATION TESTS
# =====================================================================

def test_get_current_user_me(client):
    """Test /api/auth/me resolves authenticated user profile."""
    reg_payload = {
        "full_name": "Profile Student",
        "email": "profile@campus.edu",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    client.post("/api/auth/register/customer", json=reg_payload)
    login_res = client.post("/api/auth/login", json={
        "email": "profile@campus.edu",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@campus.edu"
    assert data["role"] == "CUSTOMER"
    assert "password_hash" not in data


def test_logout_and_token_revocation(client):
    """Test that logout revokes token and revoked token is rejected on subsequent calls."""
    reg_payload = {
        "full_name": "Logout Student",
        "email": "logout@campus.edu",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    client.post("/api/auth/register/customer", json=reg_payload)
    login_res = client.post("/api/auth/login", json={
        "email": "logout@campus.edu",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]

    # 1. Verify token works before logout
    check_before = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert check_before.status_code == 200

    # 2. Perform logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    # 3. Verify token is now REVOKED on subsequent calls
    check_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert check_after.status_code == 401
    assert "revoked" in check_after.json()["detail"]


def test_jwt_expired_token(client, db_session):
    """Test expired token is rejected with 401 TokenExpiredException."""
    reg_payload = {
        "full_name": "Expired User",
        "email": "expired@campus.edu",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    client.post("/api/auth/register/customer", json=reg_payload)
    user = db_session.scalar(select(User).where(User.email == "expired@campus.edu"))

    # Generate token expired 5 minutes ago
    expired_token, _, _ = create_access_token(
        user_id=user.id,
        role=user.role.value,
        expires_delta=timedelta(minutes=-5),
    )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"]


def test_jwt_invalid_signature(client, sample_customer):
    """Test token signed with wrong secret key is rejected."""
    tampered_token = jwt.encode(
        {"sub": str(sample_customer.id), "role": "CUSTOMER", "exp": 9999999999, "iat": 1000000000, "jti": "fake-jti"},
        "wrong-unauthorized-secret-key-that-is-at-least-32-bytes-long!",
        algorithm="HS256",
    )
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert response.status_code == 401


def test_jwt_missing_and_malformed_token(client):
    """Test unauthenticated request and malformed string."""
    # Missing token
    res1 = client.get("/api/auth/me")
    assert res1.status_code == 401

    # Malformed token
    res2 = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt-token"})
    assert res2.status_code == 401


# =====================================================================
# 4. ROLE-BASED ACCESS CONTROL (RBAC) TESTS
# =====================================================================

def test_rbac_customer_access(client):
    """Customer can access customer endpoints, but is denied owner and delivery endpoints."""
    # Register customer
    client.post("/api/auth/register/customer", json={
        "full_name": "Role Customer",
        "email": "role.customer@campus.edu",
        "password": "Password123!",
        "confirm_password": "Password123!",
    })
    token = client.post("/api/auth/login", json={
        "email": "role.customer@campus.edu",
        "password": "Password123!",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Customer route -> ALLOW (200)
    res_cust = client.get("/api/protected/customer-only", headers=headers)
    assert res_cust.status_code == 200

    # 2. Restaurant owner route -> FORBIDDEN (403)
    res_owner = client.get("/api/protected/restaurant-owner-only", headers=headers)
    assert res_owner.status_code == 403

    # 3. Delivery partner route -> FORBIDDEN (403)
    res_courier = client.get("/api/protected/delivery-partner-only", headers=headers)
    assert res_courier.status_code == 403


def test_rbac_restaurant_owner_access(client):
    """Restaurant owner can access owner endpoints, but is denied customer and delivery endpoints."""
    # Register owner
    client.post("/api/auth/register/restaurant-owner", json={
        "full_name": "Role Owner",
        "email": "role.owner@campus.edu",
        "phone_number": "+1555000222",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "restaurant_name": "Campus Bagels",
        "restaurant_address": "Hall C",
    })
    token = client.post("/api/auth/login", json={
        "email": "role.owner@campus.edu",
        "password": "Password123!",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Restaurant owner route -> ALLOW (200)
    res_owner = client.get("/api/protected/restaurant-owner-only", headers=headers)
    assert res_owner.status_code == 200

    # 2. Customer route -> FORBIDDEN (403)
    res_cust = client.get("/api/protected/customer-only", headers=headers)
    assert res_cust.status_code == 403

    # 3. Delivery partner route -> FORBIDDEN (403)
    res_courier = client.get("/api/protected/delivery-partner-only", headers=headers)
    assert res_courier.status_code == 403


def test_rbac_delivery_partner_access(client):
    """Delivery partner can access courier endpoints, but is denied customer and owner endpoints."""
    # Register courier
    client.post("/api/auth/register/delivery-partner", json={
        "full_name": "Role Courier",
        "email": "role.courier@campus.edu",
        "phone_number": "+1555000333",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "vehicle_type": "BICYCLE",
    })
    token = client.post("/api/auth/login", json={
        "email": "role.courier@campus.edu",
        "password": "Password123!",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Delivery partner route -> ALLOW (200)
    res_courier = client.get("/api/protected/delivery-partner-only", headers=headers)
    assert res_courier.status_code == 200

    # 2. Customer route -> FORBIDDEN (403)
    res_cust = client.get("/api/protected/customer-only", headers=headers)
    assert res_cust.status_code == 403

    # 3. Restaurant owner route -> FORBIDDEN (403)
    res_owner = client.get("/api/protected/restaurant-owner-only", headers=headers)
    assert res_owner.status_code == 403


def test_unauthenticated_protected_access(client):
    """Unauthenticated access to any protected route returns 401."""
    assert client.get("/api/protected/customer-only").status_code == 401
    assert client.get("/api/protected/restaurant-owner-only").status_code == 401
    assert client.get("/api/protected/delivery-partner-only").status_code == 401
