# Campus Byte – Automated Testing Strategy

This document outlines the testing architecture, fixture isolation, and validation procedures implemented across the application.

---

## 1. Test Architecture & Database Isolation

To prevent destructive modification to development and production PostgreSQL data, automated tests utilize an **isolated, transactional in-memory test database**:
- Engine: SQLite with `StaticPool` (`check_same_thread=False`).
- Integrity Enforcement: `PRAGMA foreign_keys=ON;` enabled on every test connection to mirror PostgreSQL foreign key and check constraint semantics.
- Fixture Scope: Each test runs with a freshly created schema via `Base.metadata.create_all(bind=test_engine)` and clean teardown via `Base.metadata.drop_all(bind=test_engine)`.

---

## 2. Test Suite Categories

| Module | Test File | Scope Covered | Tests Count |
| :--- | :--- | :--- | :--- |
| **Authentication & RBAC** | `test_auth_and_rbac.py` | Registration per role, password policy, login, invalid credentials, inactive accounts, token expiration, signature validation, token revocation, RBAC role restrictions. | 20 |
| **Database & Constraints** | `test_database.py` | Database connection, model creation, foreign key cascading, unique email constraint, positive price constraint, positive quantity constraint. | 5 |
| **Restaurants** | `test_restaurants.py` | CRUD operations, owner verification, 1:1 owner constraint, search keyword filtering, availability filtering, safe deactivation. | 13 |
| **Menu Management** | `test_menu.py` | Dish creation, invalid restaurant rejection, positive price validation, category filtering, stock toggling, historical order preservation. | 10 |
| **Customer Orders & Checkout** | `test_orders.py` | Order placement, server-side price computation, delivery fee calculation, duplicate submit idempotency, customer IDOR protection, pending order cancellation. | 13 |
| **Restaurant Order Processing** | `test_restaurant_orders.py` | Incoming order list, status filtering, customer search, order statistics, live polling notifications, accept/reject workflows, mandatory rejection reason, kitchen preparation lifecycle (`PREPARING` -> `READY_FOR_PICKUP`), owner IDOR protection, concurrency race resolution, audit history timeline. | 17 |
| **Delivery Management & Tracking** | `test_delivery.py` | Courier registration, vehicle profiles, availability toggle (`AVAILABLE` / `OFFLINE` / `BUSY`), available orders query, atomic order claim & 409 conflict, lifecycle transitions (`PICKED_UP` -> `OUT_FOR_DELIVERY` -> `DELIVERED`), COD confirmation, courier IDOR protection, and customer/restaurant status synchronization. | 16 |
| **Users** | `test_users.py` | Public user profile retrieval, pagination, duplicate prevention, password hash suppression. | 5 |
| **Dashboards** | `test_dashboards.py` | Aggregate platform statistics across restaurants, menus, and users. | 1 |
| **Total** | | | **100 passing** |

---

## 3. Running the Test Suite

```powershell
# Run full test suite with verbose output
.\.venv\Scripts\pytest.exe -v

# Run only authentication and RBAC tests
.\.venv\Scripts\pytest.exe backend/tests/test_auth_and_rbac.py -v
```

