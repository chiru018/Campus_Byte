# Campus Byte – API Documentation

**Interactive Swagger UI:** `http://localhost:8000/docs`  
**Interactive ReDoc:** `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints (`/api/auth`)

### 1.1 Register Customer
- **Endpoint:** `POST /api/auth/register/customer`
- **Status:** `201 Created`
- **Request Body:**
  ```json
  {
    "full_name": "Alex Johnson",
    "email": "alex@campus.edu",
    "phone_number": "+1234567890",
    "password": "Password123!",
    "confirm_password": "Password123!"
  }
  ```
- **Response Body:** `UserResponse` (Does NOT expose password hash)

### 1.2 Register Restaurant Owner
- **Endpoint:** `POST /api/auth/register/restaurant-owner`
- **Status:** `201 Created`
- **Request Body:**
  ```json
  {
    "full_name": "Chef Mario",
    "email": "mario@campus.edu",
    "phone_number": "+1555123456",
    "password": "ChefPassword123!",
    "confirm_password": "ChefPassword123!",
    "restaurant_name": "Campus Trattoria",
    "restaurant_address": "Dining Hall West",
    "restaurant_description": "Italian pasta and pizza"
  }
  ```

### 1.3 Register Delivery Partner
- **Endpoint:** `POST /api/auth/register/delivery-partner`
- **Status:** `201 Created`
- **Request Body:**
  ```json
  {
    "full_name": "Sam Speed",
    "email": "sam@campus.edu",
    "phone_number": "+1555987654",
    "password": "SpeedPassword123!",
    "confirm_password": "SpeedPassword123!",
    "vehicle_type": "BICYCLE"
  }
  ```

### 1.4 User Login
- **Endpoint:** `POST /api/auth/login`
- **Status:** `200 OK`
- **Request Body:**
  ```json
  {
    "email": "alex@campus.edu",
    "password": "Password123!"
  }
  ```
- **Response Body:**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": { ... }
  }
  ```
- **Side Effect:** Sets `campus_byte_access_token` HttpOnly cookie.

### 1.5 Get Current User Profile
- **Endpoint:** `GET /api/auth/me`
- **Headers:** `Authorization: Bearer <token>` or HttpOnly Cookie
- **Status:** `200 OK`

### 1.6 Logout
- **Endpoint:** `POST /api/auth/logout`
- **Status:** `200 OK`
- **Side Effect:** Denylists JWT `jti` in PostgreSQL and deletes session cookie.

---

## 2. RBAC Protected Endpoints (`/api/protected`)

- `GET /api/protected/customer-only` – Restricted to `CUSTOMER` (403 for others).
- `GET /api/protected/restaurant-owner-only` – Restricted to `RESTAURANT_OWNER` (403 for others).
- `GET /api/protected/delivery-partner-only` – Restricted to `DELIVERY_PARTNER` (403 for others).

---

## 3. Restaurant Endpoints (`/api/restaurants`)

- `GET /api/restaurants` – List restaurants (`?page=1&size=20&search=...&is_open=...`).
- `GET /api/restaurants/{restaurant_id}` – Details by UUID.
- `POST /api/restaurants` – Create restaurant.
- `PUT /api/restaurants/{restaurant_id}` – Update restaurant.
- `PATCH /api/restaurants/{restaurant_id}/availability` – Toggle open/closed status.
- `DELETE /api/restaurants/{restaurant_id}` – Safe delete or deactivation.

---

## 4. Menu Endpoints (`/api/menu` & `/api/restaurants/{restaurant_id}/menu`)

- `GET /api/restaurants/{restaurant_id}/menu` – List items (`?category=...&is_available=...`).
- `POST /api/restaurants/{restaurant_id}/menu` – Add item (price must be `> 0`).
- `GET /api/menu/{item_id}` – Get item details.
- `PUT /api/menu/{item_id}` – Update dish details.
- `PATCH /api/menu/{item_id}/availability` – Toggle stock flag.
- `DELETE /api/menu/{item_id}` – Safe delete or deactivation.

---

## 5. Standard Error Format

All domain exceptions return uniform JSON structures:
```json
{
  "detail": "Description of the error condition.",
  "error_code": "RESOURCE_NOT_FOUND | DUPLICATE_RESOURCE | INVALID_CREDENTIALS | FORBIDDEN",
  "extra": null
}
```

