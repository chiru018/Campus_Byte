# Campus Byte – Application Security Checklist & Verification

This document audits the security controls implemented in **Campus Byte** against OWASP Top 10 guidelines and strict project engineering standards.

---

| Security Area | Control Implemented | Verification Method | Status |
| :--- | :--- | :--- | :--- |
| **Password Hashing** | Argon2id (`time_cost=2`, `memory_cost=65536`, `parallelism=2`). Salted per user. | Verified via `test_register_customer_success` inspecting `$argon2` prefix. | ✅ PASS |
| **Password Policy** | Enforced 8+ characters, uppercase, lowercase, numeric digit, and special symbol. | Verified via `test_registration_weak_password_rejected`. | ✅ PASS |
| **Plaintext Leakage** | `password_hash` excluded from all Pydantic response models and loggers. | Verified via tests checking `password_hash not in response.json()`. | ✅ PASS |
| **User Enumeration** | `POST /api/auth/login` returns identical `Invalid email or password.` for non-existent users and wrong passwords. | Verified via `test_login_invalid_password` and `test_login_nonexistent_email`. | ✅ PASS |
| **Token Invalidation** | Server-side denylist table `revoked_tokens`. When user logs out, token `jti` is stored and blocked on subsequent calls. | Verified via `test_logout_and_token_revocation`. | ✅ PASS |
| **Expired Tokens** | JWT expiration enforced on every call (`exp` claim verified by PyJWT). | Verified via `test_jwt_expired_token`. | ✅ PASS |
| **Tampered Signatures** | Signature verification with `HS256` rejects tokens signed with arbitrary keys. | Verified via `test_jwt_invalid_signature`. | ✅ PASS |
| **Server-Side RBAC** | Role enforcement executed at FastAPI routing layer via `RoleChecker`. Frontend roles never trusted. | Verified via `test_rbac_customer_access`, `test_rbac_restaurant_owner_access`, etc. | ✅ PASS |
| **Cookie Security** | HttpOnly, SameSite=Lax session cookies prevent JavaScript XSS theft. | Verified in login response headers. | ✅ PASS |
| **SQL Injection** | Exclusively parameterized SQLAlchemy 2.0 ORM queries; zero string concatenation in queries. | Verified across all repository CRUD implementations. | ✅ PASS |
| **CORS Configuration** | Restricted to explicit development and production origins (`http://localhost:5173`, `http://127.0.0.1:5173`). Wildcard `*` rejected. | Configured in `app.core.config.Settings.BACKEND_CORS_ORIGINS`. | ✅ PASS |
| **Transaction Safety** | Multi-table registration (Owner + Restaurant, Courier + DeliveryPartner) wrapped in database transactions with rollback on failure. | Verified via `test_register_restaurant_owner_success`. | ✅ PASS |
| **Secret Management** | All credentials (`JWT_SECRET_KEY`, `DATABASE_URL`) loaded from environment variables. `.env` strictly ignored by Git. | Verified in `.gitignore`. | ✅ PASS |
| **Restaurant Ownership (IDOR)** | Owner A cannot modify, update availability, or delete Owner B's restaurant. Enforced in FastAPI service layer with 403 Forbidden. | Verified via `test_reject_update_by_different_owner_idor`. | ✅ PASS |
| **Menu Item Ownership (IDOR)** | Owner A cannot create, update, toggle availability, or delete dishes on Owner B's restaurant. | Verified via `test_reject_add_menu_item_by_other_owner_idor` and `test_get_update_and_delete_menu_item`. | ✅ PASS |
| **Role Privilege Enforcement** | Customers and delivery partners cannot create or modify restaurants or food items. | Verified via `test_reject_restaurant_creation_by_customer` and `test_reject_add_menu_item_by_customer`. | ✅ PASS |
| **Price Integrity** | Menu item creation and update enforce strictly positive prices (`price > 0`). Zero and negative prices rejected. | Verified via `test_reject_menu_item_invalid_price` (HTTP 422). | ✅ PASS |
| **Category Whitelisting** | Standardized 10 food categories with input normalization and rejection of invalid values. | Verified via `test_reject_menu_item_invalid_category` (HTTP 422). | ✅ PASS |
| **Historical Data Integrity** | Deleting a menu item referenced in historical orders sets `is_available = False` rather than breaking references or foreign keys. | Verified via `test_delete_menu_item_with_historical_orders_deactivates`. | ✅ PASS |
| **Image URL Sanitation** | Validates that image URLs begin with safe protocols (`http://`, `https://`, or `/`). | Verified via Pydantic validator on `RestaurantBase` and `MenuItemBase`. | ✅ PASS |
| **Price Tampering Prevention** | Client prices, subtotals, and delivery fees are strictly ignored. All line prices, subtotal, and total amount derived on backend using `Decimal`. | Verified via `test_place_order_success`. | ✅ PASS |
| **Double Submit / Idempotency** | Orders accept unique `idempotency_key`. Duplicate requests within 24 hours safely return existing order without duplicate charging or creation. | Verified via `test_place_order_idempotency_duplicate_submission`. | ✅ PASS |
| **Customer Order Ownership (IDOR)** | Customer B cannot inspect or cancel Customer A's order details. Enforced in service layer with HTTP 403 Forbidden. | Verified via `test_get_order_detail_and_idor` and `test_cancel_order_idor_protection`. | ✅ PASS |
| **Order Cancellation Enforcement** | Cancellation is restricted strictly to `PENDING` orders. Transitions beyond pending (`ACCEPTED`, `PREPARING`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`) reject cancellation with HTTP 400. | Verified via `test_cancel_pending_order_success` and `test_cancel_already_cancelled_order`. | ✅ PASS |
| **Single-Restaurant Cart Rule** | Frontend CartContext enforces single-restaurant cart restriction with confirmation modal. Backend verifies all ordered items belong to target restaurant. | Verified via `test_place_order_cross_restaurant_item`. | ✅ PASS |
