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
