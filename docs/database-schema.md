# Campus Byte – Relational Database Schema Documentation

This document describes the 3NF-normalized relational schema for **Campus Byte**, implemented via SQLAlchemy 2.0 ORM and managed by Alembic.

---

## 1. Primary Key Strategy

All entities consistently utilize **128-bit UUIDs (v4)** as primary keys (`uuid.UUID`).
- In PostgreSQL: Maps to native `UUID`.
- In SQLite (Unit Testing): Maps to `CHAR(32)` / `CHAR(36)`.
- Security Benefit: Prevents enumeration attacks across user IDs, orders, and restaurants.

---

## 2. Table Specifications

### Table 1: `users`
Core user identity storage supporting multiple roles across the campus delivery lifecycle.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Unique user identifier |
| `full_name` | `VARCHAR(100)` | No | - | Full name of the user |
| `email` | `VARCHAR(255)` | No | `UNIQUE`, `INDEX` | Login and notification email |
| `phone_number` | `VARCHAR(20)` | Yes | - | Contact phone number |
| `password_hash` | `VARCHAR(255)` | No | - | PBKDF2-HMAC-SHA256 salted hash |
| `role` | `VARCHAR(30)` | No | `INDEX`, `default='CUSTOMER'` | Enum: `CUSTOMER`, `RESTAURANT_OWNER`, `DELIVERY_PARTNER` |
| `is_active` | `BOOLEAN` | No | `default=TRUE` | Soft deactivation flag |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Registration timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `server_default=NOW()`, `onupdate=NOW()` | Last modification timestamp |

**Indexes & Constraints:**
- `pk_users`: Primary key on `id`.
- `ix_users_email`: Unique B-Tree index on `email`.
- `ix_users_role`: Index on `role` for role-filtered queries.

---

### Table 2: `restaurants`
Campus dining outlets and external restaurant partner profiles.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Unique restaurant identifier |
| `owner_id` | `UUID` | No | `FOREIGN KEY(users.id)`, `UNIQUE`, `INDEX` | Owning restaurant owner user |
| `name` | `VARCHAR(120)` | No | `INDEX` | Commercial name of the outlet |
| `description` | `TEXT` | Yes | - | Detailed description and cuisine types |
| `address` | `VARCHAR(255)` | No | - | Campus building or street address |
| `contact_number` | `VARCHAR(20)` | No | - | Kitchen/manager phone number |
| `image_url` | `VARCHAR(500)` | Yes | - | Storefront logo or cover image URL |
| `is_open` | `BOOLEAN` | No | `INDEX`, `default=TRUE` | Availability flag for taking orders |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `server_default=NOW()`, `onupdate=NOW()` | Last update timestamp |

**Indexes & Constraints:**
- `fk_restaurants_owner_id`: References `users(id)` ON DELETE CASCADE.
- `uq_restaurants_owner_id`: Enforces 1:1 owner-to-restaurant relationship in MVP.
- `ix_restaurants_name`: Index for keyword search.
- `ix_restaurants_is_open`: Index for filtering open restaurants.

---

### Table 3: `menu_items`
Dishes, food items, snacks, and beverages offered by restaurants.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Unique item identifier |
| `restaurant_id` | `UUID` | No | `FOREIGN KEY(restaurants.id)`, `INDEX` | Parent restaurant |
| `name` | `VARCHAR(120)` | No | `INDEX` | Dish/item name |
| `description` | `TEXT` | Yes | - | Dietary info, ingredients, description |
| `price` | `NUMERIC(10,2)` | No | `CHECK (price > 0)` | Price per unit in currency |
| `category` | `VARCHAR(50)` | No | `INDEX` | Category (e.g. Beverages, Mains, Snacks) |
| `image_url` | `VARCHAR(500)` | Yes | - | Dish presentation photo |
| `is_available` | `BOOLEAN` | No | `INDEX`, `default=TRUE` | Stock availability toggle |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Timestamp created |
| `updated_at` | `TIMESTAMPTZ` | No | `server_default=NOW()`, `onupdate=NOW()` | Timestamp updated |

**Indexes & Constraints:**
- `check_menu_item_price_positive`: `CHECK (price > 0)`.
- `fk_menu_items_restaurant_id`: References `restaurants(id)` ON DELETE CASCADE.
- `ix_menu_items_restaurant_id`: B-Tree index for loading restaurant menus.
- `ix_menu_items_category`: Index for category filtering.

---

### Table 4: `delivery_partners`
Student courier and delivery partner operational profiles.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Partner identifier |
| `user_id` | `UUID` | No | `FOREIGN KEY(users.id)`, `UNIQUE`, `INDEX` | Associated user account |
| `vehicle_type` | `VARCHAR(20)` | No | `default='BICYCLE'` | Enum: `BICYCLE`, `SCOOTER`, `WALKING`, `MOTORCYCLE`, `CAR` |
| `is_available` | `BOOLEAN` | No | `INDEX`, `default=TRUE` | On-duty availability status |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Registration timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `server_default=NOW()`, `onupdate=NOW()` | Update timestamp |

**Indexes & Constraints:**
- `fk_delivery_partners_user_id`: References `users(id)` ON DELETE CASCADE.
- `uq_delivery_partners_user_id`: Guarantees one profile per user.

---

### Table 5: `orders`
Core transaction entity linking customer orders with restaurants and couriers.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Order identifier |
| `customer_id` | `UUID` | No | `FOREIGN KEY(users.id)`, `INDEX` | Ordering customer |
| `restaurant_id` | `UUID` | No | `FOREIGN KEY(restaurants.id)`, `INDEX` | Target kitchen |
| `delivery_partner_id` | `UUID` | Yes | `FOREIGN KEY(delivery_partners.id)`, `INDEX` | Assigned courier |
| `delivery_address` | `VARCHAR(255)` | No | - | Campus dorm/room delivery location |
| `subtotal` | `NUMERIC(10,2)` | No | `CHECK (subtotal >= 0)` | Sum of item totals |
| `delivery_fee` | `NUMERIC(10,2)` | No | `CHECK (delivery_fee >= 0)`, `default=0.00` | Campus delivery surcharge |
| `total_amount` | `NUMERIC(10,2)` | No | `CHECK (total_amount >= 0)` | Grand payable total |
| `payment_method` | `VARCHAR(30)` | No | `default='CASH_ON_DELIVERY'` | Enum: `CASH_ON_DELIVERY` |
| `payment_status` | `VARCHAR(20)` | No | `INDEX`, `default='PENDING'` | Enum: `PENDING`, `PAID`, `FAILED` |
| `order_status` | `VARCHAR(30)` | No | `INDEX`, `default='PENDING'` | Full order state machine |
| `rejection_reason` | `VARCHAR(500)` | Yes | - | Reason provided by restaurant if order is rejected |
| `accepted_at` | `TIMESTAMPTZ` | Yes | - | Timestamp when restaurant accepted order |
| `rejected_at` | `TIMESTAMPTZ` | Yes | - | Timestamp when restaurant rejected order |
| `preparing_at` | `TIMESTAMPTZ` | Yes | - | Timestamp when food preparation began |
| `ready_for_pickup_at` | `TIMESTAMPTZ` | Yes | - | Timestamp when kitchen marked food ready for courier pickup |
| `idempotency_key` | `VARCHAR(64)` | Yes | `INDEX` | Client-generated duplicate submit token |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Timestamp order placed |
| `updated_at` | `TIMESTAMPTZ` | No | `server_default=NOW()`, `onupdate=NOW()` | Timestamp state updated |

**Check Constraints:**
- `check_order_subtotal_non_negative`: `subtotal >= 0`
- `check_order_delivery_fee_non_negative`: `delivery_fee >= 0`
- `check_order_total_non_negative`: `total_amount >= 0`

---

### Table 6: `order_items`
Individual line items inside an order, preserving historical prices and item names.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Line item identifier |
| `order_id` | `UUID` | No | `FOREIGN KEY(orders.id)`, `INDEX` | Parent order |
| `menu_item_id` | `UUID` | No | `FOREIGN KEY(menu_items.id)`, `INDEX` | Original menu item |
| `item_name` | `VARCHAR(120)` | No | - | Historical item name snapshot |
| `unit_price` | `NUMERIC(10,2)` | No | `CHECK (unit_price > 0)` | Historical unit price snapshot |
| `quantity` | `INTEGER` | No | `CHECK (quantity > 0)` | Ordered quantity |
| `total_price` | `NUMERIC(10,2)` | No | `CHECK (total_price > 0)` | `quantity * unit_price` |

**Check Constraints:**
- `check_order_item_quantity_positive`: `quantity > 0`
- `check_order_item_unit_price_positive`: `unit_price > 0`
- `check_order_item_total_price_positive`: `total_price > 0`

---

### Table 7: `delivery_assignments`
Audit log of courier assignment dispatches per order.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Assignment identifier |
| `order_id` | `UUID` | No | `FOREIGN KEY(orders.id)`, `INDEX` | Target order |
| `delivery_partner_id` | `UUID` | No | `FOREIGN KEY(delivery_partners.id)`, `INDEX` | Assigned courier |
| `assigned_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Dispatch timestamp |
| `picked_up_at` | `TIMESTAMPTZ` | Yes | - | Food pickup timestamp |
| `delivered_at` | `TIMESTAMPTZ` | Yes | - | Customer drop timestamp |
| `delivery_status` | `VARCHAR(20)` | No | `INDEX`, `default='ASSIGNED'` | Enum: `ASSIGNED`, `PICKED_UP`, `DELIVERED`, `CANCELLED` |

---

### Table 8: `order_status_history`
Immutable audit log tracking every order state transition.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | History entry identifier |
| `order_id` | `UUID` | No | `FOREIGN KEY(orders.id)`, `INDEX` | Order reference |
| `previous_status` | `VARCHAR(30)` | Yes | - | State prior to change |
| `new_status` | `VARCHAR(30)` | No | - | New state |
| `changed_by` | `UUID` | Yes | `FOREIGN KEY(users.id)`, `INDEX` | User triggering transition |
| `changed_by_role` | `VARCHAR(30)` | Yes | - | Role of user triggering change (e.g. CUSTOMER, RESTAURANT_OWNER, DELIVERY_PARTNER) |
| `notes` | `VARCHAR(500)` | Yes | - | Descriptive audit details or reasons (e.g. rejection explanation) |
| `created_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Audit log timestamp |

---

### Table 9: `revoked_tokens`
Server-side token denylist tracking revoked JWT identifiers (jti) upon explicit user logout.

| Column | Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | `PRIMARY KEY`, `default=uuid4` | Revocation identifier |
| `jti` | `VARCHAR(64)` | No | `UNIQUE`, `INDEX` | JWT unique token identifier |
| `user_id` | `UUID` | No | `FOREIGN KEY(users.id)`, `INDEX` | User owning the revoked token |
| `revoked_at` | `TIMESTAMPTZ` | No | `server_default=NOW()` | Exact revocation timestamp |
| `expires_at` | `TIMESTAMPTZ` | No | `INDEX` | Token expiration timestamp for cleanup |

---

## 3. Alembic Migration History

1. **`20261111_0001_initial_schema.py`**: Initial schema defining core 9 relational tables, foreign key constraints, indexes, and positive amount checks.
2. **`20261111_0002_add_revoked_tokens_table.py`**: Added `revoked_tokens` table for server-side JWT session invalidation on logout.
3. **`20261111_0003_add_order_idempotency_key.py`**: Added `idempotency_key` column with indexing on `orders` table to prevent duplicate checkout submissions.
4. **`20261112_0004_add_restaurant_order_processing_fields.py`**: Added `rejection_reason`, `accepted_at`, `rejected_at`, `preparing_at`, `ready_for_pickup_at` to `orders`, and added `changed_by_role`, `notes` to `order_status_history`.


