# Campus Byte – System Architecture Documentation

Campus Byte is engineered as a decoupled, multi-stakeholder campus food ordering and delivery management system.

---

## 1. High-Level Architecture Overview

```mermaid
flowchart TD
    Client["React 18 + Vite Frontend"]
    
    subgraph WebServer ["FastAPI Application (ASGI)"]
        CORS["CORS Middleware"]
        AuthMiddleware["JWT & Cookie Extraction"]
        RBAC["Role-Based Access Control (RBAC)"]
        
        subgraph APILayer ["API Routers (/api)"]
            AuthRouter["/auth"]
            RestRouter["/restaurants"]
            MenuRouter["/menu"]
            UserRouter["/users"]
            DashRouter["/dashboards"]
            ProtectedRouter["/protected"]
        end
        
        subgraph ServiceLayer ["Service Layer"]
            AuthService["auth_service"]
            RestService["restaurant_service"]
            MenuService["menu_service"]
            UserService["user_service"]
        end
        
        subgraph CRUDLayer ["CRUD & Data Access"]
            CRUDAuth["crud_token"]
            CRUDRest["crud_restaurant"]
            CRUDMenu["crud_menu"]
            CRUDUser["crud_user"]
            CRUDDelivery["crud_delivery"]
        end
    end

    subgraph DataStore ["Persistence Layer"]
        PG[("PostgreSQL 17 Database")]
    end

    Client -->|HTTPS / JSON + HttpOnly Cookies| CORS
    CORS --> AuthMiddleware
    AuthMiddleware --> RBAC
    RBAC --> APILayer
    APILayer --> ServiceLayer
    ServiceLayer --> CRUDLayer
    CRUDLayer -->|SQLAlchemy 2.0 ORM| PG
```

---

## 2. Multi-Stakeholder Roles & Permission Matrix

The platform strictly differentiates three participant types:

| Role | Permitted Actions & Boundaries | Prohibited Actions |
| :--- | :--- | :--- |
| **`CUSTOMER`** | Register, login, view public restaurants/menus, view and place own orders, access `/customer/dashboard`. | Cannot create restaurants, manage menus, accept deliveries, or view other customers' orders. |
| **`RESTAURANT_OWNER`** | Register with automatic restaurant provisioning, manage own restaurant profile & menu, view kitchen orders, access `/restaurant/dashboard`. | Cannot place delivery runs, mark orders delivered, or access other restaurants' analytics. |
| **`DELIVERY_PARTNER`** | Register with vehicle mode, toggle on-duty availability, view and accept eligible campus drops, access `/delivery/dashboard`. | Cannot alter restaurant items, modify menu prices, or access customer billing records. |

---

## 3. Authentication & Security Design

1. **Password Security:**
   - Hashing: `Argon2id` (via `argon2-cffi`), memory-hard, highly resistant to GPU cracking.
   - Policy: Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number, and 1 special symbol.
   - Plaintext passwords and hashes are never exposed in logs or API responses.
2. **Stateless JWT with Server-Side Revocation:**
   - Tokens signed with HMAC-SHA256 (`HS256`) using environment secret `JWT_SECRET_KEY`.
   - Claims: `sub` (User UUID), `role` (Role string), `iat`, `exp` (30 min lifetime), `jti` (Token UUID).
   - Revocation: When a user logs out, the token's `jti` is stored in the `revoked_tokens` table. On every request, `get_current_user` verifies the token has not been revoked.
3. **Transport Security:**
   - Dual-mode support: Authorization Bearer header + secure HttpOnly cookies (`SameSite=Lax`, `HttpOnly=True`).
4. **Backend-Enforced RBAC:**
   - Reusable `RoleChecker` dependency enforces required roles at the FastAPI routing layer.

---

## 4. Frontend Architecture

1. **State Management:**
   - `AuthContext`: Centralized provider tracking `user`, `role`, `loading`, `isAuthenticated`.
   - On app load: Restores session by calling `GET /api/auth/me`.
2. **Routing & Guards:**
   - `ProtectedRoute`: Evaluates role membership; redirects unauthenticated visitors to `/login` with target path preserved, and unauthorized roles to `/unauthorized`.
3. **Decoupled API Client:**
   - Axios instance with interceptors attaching Bearer tokens and managing 401 unauthenticated purges.

---

## 5. Delivery Partner Subsystem & Order State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: Customer Checkout
    PENDING --> ACCEPTED: Restaurant Accepts
    PENDING --> REJECTED: Restaurant Declines (w/ reason)
    PENDING --> CANCELLED: Customer Cancels
    ACCEPTED --> PREPARING: Kitchen Starts Cooking
    PREPARING --> READY_FOR_PICKUP: Kitchen Marks Food Ready
    READY_FOR_PICKUP --> PICKED_UP: Courier Claims & Picks Up
    PICKED_UP --> OUT_FOR_DELIVERY: Courier En Route to Dorm
    OUT_FOR_DELIVERY --> DELIVERED: Handover Complete & COD Verified
    DELIVERED --> [*]
```

### 5.1 Courier Availability & Assignment Rules
1. **Three-State Lifecycle:** `OFFLINE` (idle/shift off), `AVAILABLE` (polling & accepting runs), `BUSY` (in-flight delivery run).
2. **Locking & Single Run Invariance:** A courier may only claim one active run at a time. While `BUSY`, attempts to transition to `AVAILABLE` or `OFFLINE` are blocked by the backend until the active delivery is fulfilled.
3. **Atomic Claiming:** Simultaneous claims on a `READY_FOR_PICKUP` order utilize row-level locking (`with_for_update`) to ensure exactly one winner (201) and subsequent 409 Conflict rejection.
4. **COD Verification:** Deliveries using Cash on Delivery require verification that the collected physical cash matches the authoritative order total amount before `DELIVERED` state transition is persisted.


