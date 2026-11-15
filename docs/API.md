# Campus Byte — REST API Reference Manual

The **Campus Byte API** is built using **FastAPI**, featuring automatic OpenAPI schema generation, strict Pydantic v2 data validation, Argon2id password hashing, and role-based access control.

Base URL (Local): `http://localhost:8000/api`  
Interactive OpenAPI Explorer: `http://localhost:8000/docs`  
ReDoc Reference: `http://localhost:8000/redoc`

---

## 1. Authentication & Role-Based Access Control

All protected endpoints expect a standard JWT Bearer token:
`Authorization: Bearer <jwt_access_token>`

Alternatively, the API supports automatic **HttpOnly cookie authentication** (`access_token` cookie) for browser security.

### 1.1 Register Customer
- **Endpoint**: `POST /api/auth/register/customer`
- **Access**: Public
- **Request Body**:
```json
{
  "full_name": "John Doe",
  "email": "john.doe@campus.edu",
  "phone_number": "+1234567890",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```
- **Response**: `201 Created`

### 1.2 Register Restaurant Owner
- **Endpoint**: `POST /api/auth/register/restaurant-owner`
- **Access**: Public
- **Description**: Atomically registers a user with role `RESTAURANT_OWNER` and creates their initial restaurant profile.
- **Request Body**:
```json
{
  "full_name": "Chef Mario",
  "email": "mario@campus.edu",
  "phone_number": "+1555123999",
  "password": "SuperChef2026!",
  "confirm_password": "SuperChef2026!",
  "restaurant_name": "Mario's Campus Trattoria",
  "restaurant_address": "Dining Hall West, Station 3",
  "restaurant_description": "Handmade pasta and fresh paninis"
}
```
- **Response**: `201 Created`

### 1.3 Register Delivery Partner
- **Endpoint**: `POST /api/auth/register/delivery-partner`
- **Access**: Public
- **Description**: Atomically registers a user with role `DELIVERY_PARTNER` and sets up their delivery fleet profile.
- **Request Body**:
```json
{
  "full_name": "Sam Speed",
  "email": "sam.speed@campus.edu",
  "phone_number": "+1555987654",
  "password": "FastCourier2026!",
  "confirm_password": "FastCourier2026!",
  "vehicle_type": "MOTORCYCLE"
}
```
- **Response**: `201 Created`

### 1.4 User Login
- **Endpoint**: `POST /api/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "student@campusbyte.com",
  "password": "Student123"
}
```
- **Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "full_name": "Demo Student",
    "email": "student@campusbyte.com",
    "role": "CUSTOMER"
  }
}
```

### 1.5 User Logout
- **Endpoint**: `POST /api/auth/logout`
- **Access**: Authenticated (`CUSTOMER`, `RESTAURANT_OWNER`, `DELIVERY_PARTNER`)
- **Description**: Immediately invalidates the token by writing its unique JTI identifier to the database revocation table.
- **Response**: `200 OK`

---

## 2. Restaurant & Menu Management

### 2.1 Discover Restaurants
- **Endpoint**: `GET /api/restaurants/`
- **Access**: Public
- **Query Params**: `page` (int), `size` (int), `search` (str), `is_open` (bool)
- **Response**: `200 OK` with paginated restaurant list.

### 2.2 Get Restaurant Details
- **Endpoint**: `GET /api/restaurants/{restaurant_id}`
- **Access**: Public
- **Response**: `200 OK`

### 2.3 Get My Restaurant Profile
- **Endpoint**: `GET /api/restaurants/my-restaurant`
- **Access**: Role `RESTAURANT_OWNER`
- **Response**: `200 OK`

### 2.4 Update Restaurant
- **Endpoint**: `PUT /api/restaurants/{restaurant_id}`
- **Access**: Role `RESTAURANT_OWNER` (Protected by IDOR checks)

### 2.5 Toggle Restaurant Availability
- **Endpoint**: `PATCH /api/restaurants/{restaurant_id}/availability`
- **Access**: Role `RESTAURANT_OWNER`
- **Request Body**: `{"is_open": true}`

### 2.6 List Menu Items for Restaurant
- **Endpoint**: `GET /api/restaurants/{restaurant_id}/menu`
- **Access**: Public
- **Query Params**: `category`, `is_available`, `search`, `page`, `size`
- **Response**: `200 OK`

### 2.7 Add Menu Item
- **Endpoint**: `POST /api/restaurants/{restaurant_id}/menu`
- **Access**: Role `RESTAURANT_OWNER`
- **Request Body**:
```json
{
  "name": "Chicken Tikka Biryani",
  "description": "Fragrant basmati rice cooked with marinated chicken",
  "price": 220.00,
  "category": "BIRYANI",
  "image_url": "https://images.unsplash.com/photo-...",
  "is_available": true
}
```

---

## 3. Customer Orders & Checkout

### 3.1 Place New Order
- **Endpoint**: `POST /api/orders`
- **Access**: Role `CUSTOMER`
- **Description**: Validates server-side pricing directly against the database, rejects items from multiple restaurants, verifies restaurant open status, and supports idempotent retries via `idempotency_key`.
- **Request Body**:
```json
{
  "restaurant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "delivery_address": "Hostel 4, Room 302",
  "payment_method": "CASH_ON_DELIVERY",
  "special_instructions": "Contactless dropoff please",
  "idempotency_key": "unique-client-uuid-or-hash",
  "items": [
    {
      "menu_item_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "quantity": 2
    }
  ]
}
```
- **Response**: `201 Created`

### 3.2 List Customer's Orders
- **Endpoint**: `GET /api/orders`
- **Access**: Role `CUSTOMER`
- **Response**: `200 OK`

### 3.3 Get Customer Order Details
- **Endpoint**: `GET /api/orders/{order_id}`
- **Access**: Role `CUSTOMER` (Protected against IDOR)

### 3.4 Cancel Pending Order
- **Endpoint**: `PATCH /api/orders/{order_id}/cancel`
- **Access**: Role `CUSTOMER` (Only permitted when order is in `PENDING` state)

---

## 4. Restaurant Order Processing

### 4.1 List Orders for Restaurant
- **Endpoint**: `GET /api/restaurant/orders`
- **Access**: Role `RESTAURANT_OWNER`
- **Query Params**: `status`, `page`, `size`

### 4.2 Accept Order
- **Endpoint**: `PATCH /api/restaurant/orders/{order_id}/accept`
- **Access**: Role `RESTAURANT_OWNER`
- **Resulting Status**: `ACCEPTED`

### 4.3 Reject Order
- **Endpoint**: `PATCH /api/restaurant/orders/{order_id}/reject`
- **Access**: Role `RESTAURANT_OWNER`
- **Request Body**: `{"reason": "Kitchen at capacity"}`
- **Resulting Status**: `REJECTED`

### 4.4 Start Preparation
- **Endpoint**: `PATCH /api/restaurant/orders/{order_id}/start-preparation`
- **Access**: Role `RESTAURANT_OWNER`
- **Resulting Status**: `PREPARING`

### 4.5 Mark Ready for Pickup
- **Endpoint**: `PATCH /api/restaurant/orders/{order_id}/ready-for-pickup`
- **Access**: Role `RESTAURANT_OWNER`
- **Resulting Status**: `READY_FOR_PICKUP`

### 4.6 Audit Transition History
- **Endpoint**: `GET /api/restaurant/orders/{order_id}/history`
- **Access**: Role `RESTAURANT_OWNER`
- **Response**: `200 OK` with full chronological status transition logs.

---

## 5. Delivery Fleet & Tracking

### 5.1 Get Delivery Partner Profile
- **Endpoint**: `GET /api/delivery/profile`
- **Access**: Role `DELIVERY_PARTNER`

### 5.2 Toggle Availability Status
- **Endpoint**: `PATCH /api/delivery/availability`
- **Access**: Role `DELIVERY_PARTNER`
- **Request Body**: `{"availability_status": "AVAILABLE"}`

### 5.3 Discover Available Ready Orders
- **Endpoint**: `GET /api/delivery/available-orders`
- **Access**: Role `DELIVERY_PARTNER` (Must be in `AVAILABLE` status)

### 5.4 Claim/Accept Delivery Assignment
- **Endpoint**: `POST /api/delivery/assignments/{order_id}/accept`
- **Access**: Role `DELIVERY_PARTNER`
- **Description**: Uses PostgreSQL row-level locks (`SELECT ... FOR UPDATE SKIP LOCKED`) to prevent race conditions and double-claims across multiple simultaneous drivers.
- **Response**: `201 Created`

### 5.5 Confirm Pickup from Restaurant
- **Endpoint**: `PATCH /api/delivery/assignments/{order_id}/pickup`
- **Access**: Assigned `DELIVERY_PARTNER`
- **Resulting Status**: `PICKED_UP`

### 5.6 Start Transit
- **Endpoint**: `PATCH /api/delivery/assignments/{order_id}/start-delivery`
- **Access**: Assigned `DELIVERY_PARTNER`
- **Resulting Status**: `OUT_FOR_DELIVERY`

### 5.7 Cash on Delivery Verification
- **Endpoint**: `POST /api/delivery/assignments/{order_id}/confirm-cod`
- **Access**: Assigned `DELIVERY_PARTNER`
- **Request Body**: `{"confirm_cash_collected": true, "collected_amount": 502.00}`

### 5.8 Complete Delivery
- **Endpoint**: `PATCH /api/delivery/assignments/{order_id}/complete`
- **Access**: Assigned `DELIVERY_PARTNER`
- **Request Body**: `{"confirm_delivered": true}`
- **Resulting Status**: `DELIVERED` (Automatically marks courier `AVAILABLE`)

---

## 6. System Health

### 6.1 Liveness Probe
- **Endpoint**: `GET /health`
- **Access**: Public
- **Response**: `{"status": "healthy", "service": "Campus Byte API"}`
