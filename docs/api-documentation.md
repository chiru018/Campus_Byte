# Campus Byte – API Documentation

**Interactive Swagger UI:** `http://localhost:8000/docs`  
**Interactive ReDoc:** `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints (`/api/auth`)

### 1.1 Register Customer
- **Endpoint:** `POST /api/auth/register/customer`
- **Access:** Public
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
- **Access:** Public
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
- **Access:** Public
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
- **Access:** Public
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
- **Access:** Authenticated
- **Status:** `200 OK`
- **Side Effect:** Denylists JWT `jti` in PostgreSQL `revoked_tokens` table and deletes session cookie.

---

## 2. Restaurant Management Endpoints (`/api/restaurants`)

### 2.1 List Restaurants
- **Endpoint:** `GET /api/restaurants`
- **Access:** Public / Customer
- **Query Parameters:**
  - `page` (int, default: 1)
  - `size` (int, default: 20)
  - `search` (string, optional)
  - `is_open` (boolean, optional)
- **Status:** `200 OK`
- **Response:** `RestaurantListResponse` containing `restaurants`, `total`, `page`, `size`.

### 2.2 Get My Restaurant Profile
- **Endpoint:** `GET /api/restaurants/my-restaurant`
- **Access:** `RESTAURANT_OWNER`
- **Status:** `200 OK` / `404 Not Found`
- **Response:** `RestaurantResponse`

### 2.3 Get Restaurant Details
- **Endpoint:** `GET /api/restaurants/{restaurant_id}`
- **Access:** Public
- **Status:** `200 OK` / `404 Not Found`
- **Response:** `RestaurantResponse`

### 2.4 Get Restaurant Statistics
- **Endpoint:** `GET /api/restaurants/{restaurant_id}/stats`
- **Access:** `RESTAURANT_OWNER` (Enforces ownership IDOR check)
- **Status:** `200 OK` / `403 Forbidden` / `404 Not Found`
- **Response:**
  ```json
  {
    "restaurant_id": "...",
    "restaurant_name": "Campus Grill & Cafe",
    "is_open": true,
    "total_menu_items": 12,
    "available_menu_items": 10,
    "unavailable_menu_items": 2,
    "profile_completion_percentage": 100
  }
  ```

### 2.5 Create Restaurant
- **Endpoint:** `POST /api/restaurants`
- **Access:** `RESTAURANT_OWNER` (Links automatically to `current_user.id`)
- **Status:** `201 Created` / `409 Conflict` (if owner already has a restaurant)
- **Request Body:**
  ```json
  {
    "name": "Pizza Corner",
    "description": "Authentic woodfired pizzas",
    "address": "Campus Center, Booth 4",
    "contact_number": "+1234567800",
    "image_url": "https://example.com/pizza.jpg",
    "is_open": true
  }
  ```

### 2.6 Update Restaurant
- **Endpoint:** `PUT /api/restaurants/{restaurant_id}`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Status:** `200 OK` / `403 Forbidden` / `404 Not Found`

### 2.7 Update Restaurant Availability
- **Endpoint:** `PATCH /api/restaurants/{restaurant_id}/availability`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Request Body:** `{"is_open": false}`
- **Status:** `200 OK` / `403 Forbidden`

### 2.8 Delete or Deactivate Restaurant
- **Endpoint:** `DELETE /api/restaurants/{restaurant_id}`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Status:** `200 OK` (Deactivates if historical orders exist, otherwise deletes)

---

## 3. Menu Management Endpoints (`/api/menu` & `/api/restaurants/.../menu`)

### 3.1 List Food Categories
- **Endpoint:** `GET /api/menu/categories`
- **Access:** Public
- **Status:** `200 OK`
- **Response:** Array of category items: `[{"key": "BIRYANI", "label": "Biryani"}, ...]`

### 3.2 List Restaurant Menu Items
- **Endpoint:** `GET /api/restaurants/{restaurant_id}/menu`
- **Access:** Public
- **Query Parameters:**
  - `category` (string, optional: e.g. `BIRYANI`, `BURGERS`, `BEVERAGES`)
  - `is_available` (boolean, optional)
  - `search` (string, optional)
- **Status:** `200 OK`
- **Response:** `MenuItemListResponse` containing `items` and `total`.

### 3.3 Add Menu Item
- **Endpoint:** `POST /api/restaurants/{restaurant_id}/menu`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Status:** `201 Created` / `422 Unprocessable Entity`
- **Request Body:**
  ```json
  {
    "name": "Classic Cheeseburger",
    "description": "Beef patty, cheddar cheese, brioche bun",
    "price": "8.50",
    "category": "BURGERS",
    "image_url": "https://example.com/burger.jpg",
    "is_available": true
  }
  ```

### 3.4 Get Menu Item Details
- **Endpoint:** `GET /api/menu/{item_id}`
- **Access:** Public
- **Status:** `200 OK` / `404 Not Found`

### 3.5 Update Menu Item
- **Endpoint:** `PUT /api/menu/{item_id}`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Status:** `200 OK` / `403 Forbidden` / `422 Unprocessable Entity`

### 3.6 Change Item Availability
- **Endpoint:** `PATCH /api/menu/{item_id}/availability`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Request Body:** `{"is_available": false}`
- **Status:** `200 OK` / `403 Forbidden`

### 3.7 Delete or Deactivate Menu Item
- **Endpoint:** `DELETE /api/menu/{item_id}`
- **Access:** `RESTAURANT_OWNER` (Owner-verified; 403 for other owners)
- **Behavior:**
  - If item appears in historical orders (`order_items`), sets `is_available = False` to protect historical audit trails.
  - If no historical orders reference it, deletes record from database.
- **Status:** `200 OK` / `403 Forbidden`

---

## 4. Order & Checkout Endpoints (`/api/orders`)

### 4.1 Place Food Order
- **Endpoint:** `POST /api/orders`
- **Access:** `CUSTOMER` role only
- **Status:** `201 Created`
- **Security & Integrity Controls:**
  - **Server-Side Price Computation:** Client prices are strictly ignored. The server looks up live prices from `menu_items`, verifies `is_available=True` and restaurant `is_open=True`, and sums `unit_price * quantity`.
  - **Delivery Fee:** Flat \$2.00 fee automatically applied by backend.
  - **Idempotency Protection:** If `idempotency_key` is supplied, duplicate submissions within 24 hours safely return the existing order without creating duplicate orders.
  - **Single Restaurant Verification:** Validates that all items belong to the requested restaurant.
- **Request Body:**
  ```json
  {
    "restaurant_id": "8f8b6567-0c79-4a0d-b4f0-4a8b7c7b2a1a",
    "delivery_address": "Hostel B, Room 304, Campus North (Landmark: Near elevator) | Recipient: Alex (+1555123456)",
    "payment_method": "CASH_ON_DELIVERY",
    "items": [
      {
        "menu_item_id": "3c9d74e2-6d27-4bf3-a09c-2f9b8c9a1d2e",
        "quantity": 2
      }
    ],
    "idempotency_key": "cb-order-1699999999-a1b2c3d4"
  }
  ```
- **Response Body:** `OrderResponse` including calculated `subtotal`, `delivery_fee`, `total_amount`, `order_status` (`PENDING`), `payment_status` (`PENDING`), snapshot line items, and initial status history.

### 4.2 Get Customer Order History
- **Endpoint:** `GET /api/orders/my-orders`
- **Access:** `CUSTOMER` role only
- **Query Parameters:**
  - `page`: Page number (default: 1)
  - `size`: Page size (default: 20)
  - `status`: Optional filter by `OrderStatus` (`PENDING`, `ACCEPTED`, `PREPARING`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`)
- **Status:** `200 OK`
- **Response Body:** `OrderListResponse` with list of user's orders and total count.

### 4.3 Get Order Detail & Tracking
- **Endpoint:** `GET /api/orders/{order_id}`
- **Access:** `CUSTOMER` role only (Owner check: customer must own this order)
- **Status:** `200 OK` / `403 Forbidden` / `404 Not Found`
- **Response Body:** `OrderResponse` with items snapshot, restaurant name, and full `status_history` timeline.

### 4.4 Cancel Pending Order
- **Endpoint:** `PATCH /api/orders/{order_id}/cancel`
- **Access:** `CUSTOMER` role only (Owner check: customer must own this order)
- **Status:** `200 OK` / `400 Bad Request` / `403 Forbidden`
- **Business Rule:** Only orders in `PENDING` status may be cancelled. Orders that have transitioned to `ACCEPTED`, `PREPARING`, `OUT_FOR_DELIVERY`, or `DELIVERED` cannot be cancelled.
- **Request Body (Optional):**
  ```json
  {
    "reason": "Placed by mistake"
  }
  ```
- **Response Body:** Updated `OrderResponse` with `order_status: "CANCELLED"` and appended history transition.

---

## 5. Restaurant Order Processing Endpoints (`/api/restaurant/orders`)

All endpoints in this section require `RESTAURANT_OWNER` role authentication and enforce restaurant ownership verification (an owner cannot access or transition another restaurant's orders).

### 5.1 List Restaurant Orders
- **Endpoint:** `GET /api/restaurant/orders`
- **Access:** `RESTAURANT_OWNER`
- **Query Parameters:**
  - `status`: Optional filter by `OrderStatus` (`PENDING`, `ACCEPTED`, `PREPARING`, `READY_FOR_PICKUP`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`, `REJECTED`)
  - `search`: Case-insensitive substring match on order UUID, customer name, email, or dorm address
  - `date`: Filter orders by calendar date (`YYYY-MM-DD`)
  - `page`: Page number (default: 1)
  - `size`: Page size (default: 20, max: 100)
- **Status:** `200 OK`
- **Response Body:** `OrderListResponse` with total count, pagination metadata, and list of orders with customer contact and order items.

### 5.2 Get Restaurant Order Statistics
- **Endpoint:** `GET /api/restaurant/orders/statistics`
- **Access:** `RESTAURANT_OWNER`
- **Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "total_orders": 45,
    "pending_orders": 3,
    "accepted_orders": 2,
    "preparing_orders": 4,
    "ready_for_pickup_orders": 1,
    "delivered_orders": 32,
    "cancelled_orders": 2,
    "rejected_orders": 1,
    "today_orders": 12,
    "today_revenue": "184.50"
  }
  ```

### 5.3 Live Incoming Order Notifications (Polling)
- **Endpoint:** `GET /api/restaurant/orders/notifications`
- **Access:** `RESTAURANT_OWNER`
- **Query Parameters:**
  - `since`: ISO timestamp (e.g. `2026-11-12T10:00:00Z`). If omitted, checks for new pending orders created in the last 60 seconds.
- **Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "new_pending_count": 2,
    "has_new_orders": true,
    "latest_orders": [ ... ],
    "server_timestamp": "2026-11-12T10:05:00.123456Z"
  }
  ```

### 5.4 Get Order Detail
- **Endpoint:** `GET /api/restaurant/orders/{order_id}`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Status:** `200 OK` / `403 Forbidden` / `404 Not Found`
- **Response Body:** Full `OrderResponse` including customer phone/email, dorm room delivery location, snapshot items, pricing breakdown, timestamps (`accepted_at`, `preparing_at`, `ready_for_pickup_at`, `rejected_at`), and status history timeline.

### 5.5 Get Order Status History Timeline
- **Endpoint:** `GET /api/restaurant/orders/{order_id}/history`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Status:** `200 OK` / `403 Forbidden` / `404 Not Found`
- **Response Body:** List of `OrderStatusHistoryResponse` entries chronologically sorted, detailing `previous_status`, `new_status`, `changed_by_role`, `notes`, and `created_at`.

### 5.6 Accept Order
- **Endpoint:** `PATCH /api/restaurant/orders/{order_id}/accept`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Business Rule:** Order must be in `PENDING` status. Atomic state locking prevents concurrency collisions with customer cancellations.
- **Status:** `200 OK` / `400 Bad Request` / `403 Forbidden` / `404 Not Found`
- **State Transition:** `PENDING` -> `ACCEPTED` (sets `accepted_at` timestamp).

### 5.7 Reject Order
- **Endpoint:** `PATCH /api/restaurant/orders/{order_id}/reject`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Business Rule:** Order must be in `PENDING` status. Requires explicit `reason` of 5+ characters.
- **Request Body:**
  ```json
  {
    "reason": "Kitchen at peak capacity, out of burger buns."
  }
  ```
- **Status:** `200 OK` / `400 Bad Request` / `422 Unprocessable Entity` / `403 Forbidden` / `404 Not Found`
- **State Transition:** `PENDING` -> `REJECTED` (sets `rejected_at` timestamp and records reason).

### 5.8 Start Food Preparation
- **Endpoint:** `PATCH /api/restaurant/orders/{order_id}/start-preparation`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Business Rule:** Order must be in `ACCEPTED` status.
- **Status:** `200 OK` / `400 Bad Request` / `403 Forbidden` / `404 Not Found`
- **State Transition:** `ACCEPTED` -> `PREPARING` (sets `preparing_at` timestamp).

### 5.9 Mark Order Ready for Courier Pickup
- **Endpoint:** `PATCH /api/restaurant/orders/{order_id}/ready-for-pickup`
- **Access:** `RESTAURANT_OWNER` (Ownership verified)
- **Business Rule:** Order must be in `PREPARING` status.
- **Status:** `200 OK` / `400 Bad Request` / `403 Forbidden` / `404 Not Found`
- **State Transition:** `PREPARING` -> `READY_FOR_PICKUP` (sets `ready_for_pickup_at` timestamp). Ready for delivery partner dispatch in Phase 7.

