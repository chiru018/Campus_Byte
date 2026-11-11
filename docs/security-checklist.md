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
