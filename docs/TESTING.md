# Campus Byte — Quality Assurance & Testing Guide

This document details the testing architecture, methodology, coverage areas, and procedures for validating the **Campus Byte** platform.

---

## 1. Test Suite Overview

Campus Byte features a comprehensive automated test suite consisting of **101 tests** spanning unit testing, functional verification, role-based authorization guards, IDOR security barriers, race-condition resilience, and end-to-end multi-party order lifecycle validation.

| Test Module | Test Count | Focus Area |
|---|---|---|
| `test_auth_and_rbac.py` | 20 | Registration, Argon2id hashing, token expiration, revocation denylist, RBAC checks |
| `test_database.py` | 5 | DB engine, entity relationships, unique email, price/quantity check constraints |
| `test_dashboards.py` | 1 | Aggregate metrics, administrative dashboards |
| `test_restaurants.py` | 13 | Restaurant registration, profile queries, availability toggling, update IDOR protection |
| `test_menu.py` | 10 | Category listing, menu item CRUD, price positive checks, historical order deactivation |
| `test_orders.py` | 13 | Server-side pricing recalculation, multi-restaurant rejection, idempotency key deduplication |
| `test_restaurant_orders.py` | 17 | Kitchen state machine (PENDING → ACCEPTED → PREPARING → READY), IDOR isolation |
| `test_delivery.py` | 16 | Fleet onboarding, status toggles, concurrency row-locks, COD collection enforcement |
| `test_users.py` | 5 | CRUD user operations, email uniqueness |
| `test_e2e_lifecycle.py` | 1 | Complete 21-step multi-party lifecycle from customer order to kitchen preparation and delivery |
| **Total** | **101** | **100% Pass Rate Across All Suites** |

---

## 2. Running Backend Tests

Ensure your virtual environment is active, then execute:

```bash
# Windows
cmd /c "set PYTHONPATH=backend&& .venv\Scripts\pytest backend/tests -v"

# Linux / macOS
PYTHONPATH=backend pytest backend/tests -v
```

### Running Specific Suites
To run only the End-to-End integration test:
```bash
cmd /c "set PYTHONPATH=backend&& .venv\Scripts\pytest backend/tests/test_e2e_lifecycle.py -v"
```

To run security and authorization tests:
```bash
cmd /c "set PYTHONPATH=backend&& .venv\Scripts\pytest backend/tests/test_auth_and_rbac.py -v"
```

---

## 3. Test Architecture & Fixtures

The test infrastructure in `backend/tests/conftest.py` executes against an isolated in-memory SQLite database:
- `StaticPool` ensures single-process test isolation with zero side-effects on persistent data.
- Foreign Key enforcement is activated via `PRAGMA foreign_keys=ON` on every SQLite connection.
- Each test function receives a freshly populated database schema (`Base.metadata.create_all`) which is systematically torn down (`Base.metadata.drop_all`) upon test completion.
- FastAPI's `app.dependency_overrides[get_db]` ensures test client calls hit the isolated test database session.

---

## 4. Key Security & Functional Test Scenarios

### 4.1 Insecure Direct Object Reference (IDOR)
- **Restaurants**: Verified that a restaurant owner cannot update or delete menus belonging to other owners (`test_reject_update_by_different_owner_idor`).
- **Orders**: Verified that customers cannot read or cancel orders belonging to other students (`test_get_order_detail_and_idor`, `test_cancel_order_idor_protection`).
- **Kitchen**: Verified that an owner cannot accept or modify orders belonging to competing campus kitchens (`test_accept_order_by_other_owner_idor`).
- **Delivery**: Verified that delivery partners cannot inspect or modify deliveries assigned to fellow fleet members (`test_delivery_idor_protection`).

### 4.2 Idempotency & Financial Integrity
- Orders require server-side pricing recalculation directly from MenuItem database records. Client-provided prices are ignored to prevent price-tampering attacks.
- Duplicate submission with the same `idempotency_key` returns the existing order rather than creating duplicate database entries.
- Orders spanning multiple restaurants are strictly rejected with `400 Bad Request`.

### 4.3 Concurrent Delivery Claiming
- When two delivery partners attempt to claim the same order simultaneously, row-level locking ensures that exactly one succeeds with `201 Created` while the second receives `409 Conflict`.

---

## 5. Frontend Build Verification

To verify that the frontend bundles cleanly with zero TypeScript/JavaScript compilation errors:

```bash
cd frontend
npm run build
```

The production output will be generated in `frontend/dist/`.
