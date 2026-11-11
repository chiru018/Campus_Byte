# Campus Byte – Engineering Standards
## Security, Architecture, Code Quality, Scalability, and Reliability

These engineering standards apply across all phases of the Campus Byte project. Every API, database model, service, and frontend component must adhere to these principles.

---

## 1. Security Requirements

### 1.1 Secret Management & Environment Variables
- Never hardcode passwords, JWT secrets, database credentials, or private keys.
- Store sensitive credentials in `.env` files and load them using Pydantic `BaseSettings`.
- Provide `.env.example` templates with non-sensitive placeholder values.
- Exclude `.env` and sensitive configurations from Git via `.gitignore`.
- Never expose backend secrets in API responses or frontend JavaScript bundles.

### 1.2 Authentication & Role-Based Access Control (RBAC)
- Enforce strict JWT authentication and backend RBAC on every sensitive endpoint.
- Never trust role information supplied by the client during registration or requests.
- Validate user identity, active account status (`is_active`), and permissions on every request.
- Enforce resource ownership (prevent Insecure Direct Object References - IDOR). A user cannot modify or delete entities belonging to another user.

### 1.3 Injection Prevention
- Use SQLAlchemy ORM with parameterized queries for all database operations.
- Avoid raw SQL string concatenation.
- Sanitize and validate all query parameters, filters, and pagination offsets/limits.

### 1.4 Cross-Site Scripting (XSS) & Data Validation
- Validate all incoming payloads using Pydantic v2 schemas with strict type constraints.
- Utilize React's built-in JSX escaping for safe HTML rendering.
- Validate external URLs (such as image links) to ensure safe protocols (`http://` or `https://`).

### 1.5 Secure Password Storage
- Use **Argon2id** (`argon2-cffi`) as the primary password hashing mechanism.
- Enforce password complexity: minimum 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special symbol.
- Never return plaintext passwords or password hashes in API responses or logs.

### 1.6 Session Management & Token Revocation
- Support dual-transport authentication: Bearer tokens in headers and secure `HttpOnly`, `SameSite=Lax` cookies.
- Implement server-side token revocation via database-backed denylist (`revoked_tokens` table) keyed by JWT ID (`jti`).
- Revoked tokens must be rejected immediately on all protected routes.

---

## 2. Architecture & System Design

### 2.1 Layered Separation of Concerns
1. **Presentation Layer (React 18):** Atomic components, pages, responsive layouts, React Context for state, declarative route guards (`ProtectedRoute`).
2. **API Layer (FastAPI Routers):** Route definitions, query/body parameter parsing, dependency injection (`Depends(get_db)`, `Depends(require_restaurant_owner)`).
3. **Business Logic Layer (Services):** Domain logic, transactional coordination, ownership checks, business rule enforcement.
4. **Data Access Layer (CRUD):** Parameterized SQLAlchemy database operations, filters, pagination, count queries.
5. **Persistence Layer (PostgreSQL 17):** Normalized schema, primary/foreign key constraints, check constraints, indexes, timestamps.

### 2.2 Stateless APIs & Scalability
- Keep FastAPI endpoints stateless to facilitate horizontal scaling.
- Offload user session states to verified JWTs and database denylists.
- Design database indexes on searchable and frequently filtered columns (`name`, `category`, `is_available`, `is_open`, `owner_id`, `restaurant_id`).

---

## 3. Database Engineering & Integrity

### 3.1 Relational Integrity & Schema Normalization
- Enforce 3rd Normal Form (3NF) across all database models.
- Use explicit foreign keys with defined `ondelete` actions (`CASCADE`, `RESTRICT`).
- Protect historical order data:
  - Do not hard delete restaurants or menu items that have associated historical orders.
  - Deactivate items (`is_available = False`, `is_open = False`) to maintain referential integrity.
  - Store item prices at the time of purchase in `order_items.price` so future menu price changes do not alter historic sales records.

### 3.2 Types & Constraints
- Primary Keys: UUID (`uuid.uuid4`).
- Currency / Money: `Numeric(10, 2)` or `Decimal`. Never store currency as floating-point.
- Check Constraints: `price > 0`, `quantity > 0`.
- Timestamps: UTC `DateTime(timezone=True)` with server defaults.

---

## 4. Code Quality & Maintainability

### 4.1 Clean Code Principles
- Keep functions small and focused on a single responsibility.
- Avoid code duplication (DRY).
- Write descriptive function, variable, and class names.
- Preserve docstrings and descriptive comments across all files.

### 4.2 Error Handling & Logging
- Use standard HTTP status codes:
  - `200 OK`: Successful retrieval / update
  - `201 Created`: Successful resource creation
  - `400 Bad Request`: Validation failure or business rule violation
  - `401 Unauthorized`: Unauthenticated / invalid or expired token
  - `403 Forbidden`: Authenticated user lacks permission / IDOR ownership failure
  - `404 Not Found`: Resource does not exist
  - `409 Conflict`: Duplicate unique key (e.g., email or owner already has restaurant)
  - `422 Unprocessable Entity`: Schema validation failure
- Never expose database connection strings, internal stack traces, or credentials in client error responses.

---

## 5. Testing & Quality Assurance

- Maintain an automated test suite using **Pytest**.
- Isolate test databases using in-memory SQLite with foreign key and constraint pragmas.
- Enforce automated testing for:
  - Unit logic (validation, hashing, token creation).
  - CRUD operations and database constraints.
  - Role-based access control and unauthorized/forbidden checks.
  - IDOR ownership validation (e.g. Owner A attempting to modify Owner B's restaurant or menu).
  - Regression testing across all completed phases.
- Ensure the frontend builds cleanly without TypeScript/JSX syntax errors (`npm run build`).
