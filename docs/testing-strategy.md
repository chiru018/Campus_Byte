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
| **Database & Constraints** | `test_database.py` | Database connection, 8-table model creation, foreign key cascading, unique email constraint, positive price constraint, positive quantity constraint. | 6 |
| **Restaurants** | `test_restaurants.py` | CRUD operations, owner verification, 1:1 owner constraint, search keyword filtering, availability filtering, safe deactivation. | 10 |
| **Menu Management** | `test_menu.py` | Dish creation, invalid restaurant rejection, positive price validation, category filtering, stock toggling, historical order preservation. | 5 |
| **Users** | `test_users.py` | Public user profile retrieval, pagination, duplicate prevention, password hash suppression. | 4 |
| **Dashboards** | `test_dashboards.py` | Aggregate platform statistics across restaurants, menus, and users. | 1 |
| **Total** | | | **46 passing** |

---

## 3. Running the Test Suite

```powershell
# Run full test suite with verbose output
.\.venv\Scripts\pytest.exe -v

# Run only authentication and RBAC tests
.\.venv\Scripts\pytest.exe backend/tests/test_auth_and_rbac.py -v
```
