# Campus Byte — Campus Food Ordering & Delivery Management Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-101%2F101%20passing-success)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%20|%203.12%20|%203.14-3776AB.svg?logo=python&logoColor=white)

> **B.Tech Final Year Engineering Capstone Project**  
> An enterprise-grade, secure, role-based food ordering and peer-to-peer campus delivery ecosystem connecting university students, campus kitchens, and student couriers.

---

## 1. Executive Overview

**Campus Byte** addresses the friction, long wait lines, and delivery inefficiencies inherent to university campus dining. Designed from the ground up under strict engineering standards, the platform unifies three primary campus stakeholders:

1. **Customers (Students & Faculty):** Discover campus eateries, customize meals, place idempotent orders with live status tracking, and receive delivery right to their campus residence.
2. **Restaurant Owners:** Manage food catalogs, categorize menus, toggle real-time kitchen availability, and drive orders through a streamlined preparation pipeline.
3. **Delivery Partners (Student Couriers):** Flexible on-campus peer delivery fleet that claims ready orders, executes pickup, verifies cash-on-delivery (COD) handoffs, and finalizes delivery.

---

## 2. System Architecture & Tech Stack

```
                                  [ Web Client (Browser) ]
                                             │
                       Port 80 (HTTP)        ▼
                        ┌──────────────────────────────────────┐
                        │   Frontend (Nginx + React 18 SPA)    │
                        │   - Vite 6.4 Build, Modular SCSS     │
                        │   - Reverse Proxy (/api, /health)    │
                        └──────────────────┬───────────────────┘
                                           │
                         Port 8000         ▼
                        ┌──────────────────────────────────────┐
                        │    Backend (FastAPI + Uvicorn)       │
                        │    - Pydantic v2 Validation          │
                        │    - Argon2id Password Hashing       │
                        │    - Dual-Transport JWT Auth + RBAC  │
                        │    - Row-level Concurrency Locks     │
                        └──────────────────┬───────────────────┘
                                           │
                         Port 5432         ▼
                        ┌──────────────────────────────────────┐
                        │    Database (PostgreSQL 17 / SQLite) │
                        │    - SQLAlchemy 2.0 ORM              │
                        │    - Alembic Schema Migrations       │
                        │    - Check & Foreign Key Constraints │
                        └──────────────────────────────────────┘
```

### Technology Breakdown

| Tier | Technologies | Highlights |
|---|---|---|
| **Frontend** | React 18, Vite 6, React Router v6, Axios, Lucide React, SCSS | Glassmorphism design, declarative protected route guards, resilient cart context |
| **Backend** | Python 3.11–3.14, FastAPI, Uvicorn, Pydantic v2 | High-throughput asynchronous routing, strict schema typing, OpenAPI documentation |
| **Database** | PostgreSQL 17 (Prod), SQLite (Dev), SQLAlchemy 2.0, Alembic | Declarative mapping, UUID primary keys, relational audit trails, atomic migrations |
| **Security** | Argon2id (`argon2-cffi`), PyJWT, HttpOnly Cookies | Memory-hard password hashing, server-side token denylist, IDOR isolation |
| **DevOps** | Docker, Docker Compose, Nginx Alpine, Multi-stage Builds | Production-ready zero-downtime containerization, unified bridge network |

---

## 3. Order Lifecycle State Machine

Orders transition through a deterministic lifecycle with strict validation rules and audit logging:

```
 [ PENDING ] ──────────────► [ CANCELLED ] (Customer-initiated only during PENDING)
      │
      ├────────────────────► [ REJECTED ]  (Restaurant-initiated with mandatory reason)
      ▼
 [ ACCEPTED ]
      │
      ▼
 [ PREPARING ]
      │
      ▼
 [ READY_FOR_PICKUP ] ────► Broadcasted to Available Delivery Fleet
      │
      ▼ (Atomic Claim via SELECT ... FOR UPDATE SKIP LOCKED)
 [ PICKED_UP ]
      │
      ▼
 [ OUT_FOR_DELIVERY ]
      │
      ▼ (COD Collection Verification)
 [ DELIVERED ] (Order completed; courier freed to AVAILABLE)
```

---

## 4. Key Security & Architectural Engineering Standards

1. **Role-Based Access Control (RBAC):**
   - Public registration endpoints explicitly enforce roles server-side (`/customer`, `/restaurant-owner`, `/delivery-partner`).
   - Role spoofing via client payloads is impossible.
2. **Insecure Direct Object Reference (IDOR) Protection:**
   - Every read, update, or deletion query filters on ownership (`owner_id`, `customer_id`, or `delivery_partner_id`).
   - Cross-tenant data leakage is strictly blocked with `403 Forbidden`.
3. **Financial & Pricing Integrity:**
   - Client-provided item prices are ignored. All order subtotals and totals are recalculated server-side using `Numeric(10, 2)` / `Decimal` directly from active database records.
   - Orders spanning items from multiple restaurants are rejected.
4. **Idempotency & Race Condition Prevention:**
   - Order submission accepts an optional `idempotency_key` to avoid double charges on network timeouts.
   - Delivery assignment claiming utilizes PostgreSQL row-level locks (`SELECT FOR UPDATE SKIP LOCKED`) to eliminate double-claiming conflicts.
5. **Server-Side Token Revocation:**
   - Every JWT carries a unique UUID `jti`. Logout records the `jti` in the PostgreSQL `revoked_tokens` table, immediately invalidating the token globally.

---

## 5. Development Phases Overview

| Phase | Description | Status | Verification |
|---|---|:---:|---|
| **Phase 1** | Project Scaffolding & Engineering Setup | **Done** | FastAPI, React Vite, Docker skeleton, SCSS architecture |
| **Phase 2** | Relational Database & Foundation Models | **Done** | 9 entities, UUID PKs, constraints, 26 tests |
| **Phase 3** | Authentication, JWT Security, & RBAC | **Done** | Argon2id, dual transport JWT, token denylist, 46 tests |
| **Phase 4** | Restaurant & Menu Management System | **Done** | Restaurant profiles, menu catalog CRUD, 54 tests |
| **Phase 5** | Customer Cart, Checkout & Order Placement | **Done** | Cart context, single-restaurant rule, checkout, 67 tests |
| **Phase 6** | Restaurant Order Processing & Kitchen Flow | **Done** | Kitchen order queue, accept/reject, prep states, 84 tests |
| **Phase 7** | Delivery Partner Dispatch & Tracking | **Done** | Courier onboarding, atomic claims, COD, 100 tests |
| **Phase 8** | Final Integration, Docker & Documentation | **Done** | Multi-container Docker, 21-step E2E test, 101/101 tests passing |

---

## 6. Quick Start Guide

### Option A: Running with Docker Compose (Recommended)

1. Clone the repository and configure the environment:
```bash
git clone https://github.com/chiru018/Campus_Byte.git
cd College_byte
cp .env.example .env
```

2. Launch all three containers:
```bash
docker compose up -d --build
```

3. Seed demo data:
```bash
docker compose exec backend python seed_data.py
```

4. Access the applications:
- **Web Application:** `http://localhost`
- **Backend API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost/health`

---

### Option B: Local Development (Fast Startup)

#### 1. Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1    # On Windows
# source .venv/bin/activate       # On Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations & seed data
cd backend
alembic upgrade head
python seed_data.py
cd ..

# Start backend server
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173` with automated proxying to the backend.

---

## 7. Demo Accounts & Credentials

The seed script creates ready-to-test accounts representing all three roles:

| Role | Email Address | Password | Profile Details |
|---|---|---|---|
| **Customer** | `student@campusbyte.com` | `Student123` | Active student with dorm address |
| **Restaurant Owner** | `owner@campusbyte.com` | `Owner123` | Manages **Campus Spice Kitchen** (6 dishes) |
| **Delivery Partner** | `courier@campusbyte.com` | `Courier123` | Active motorcycle fleet courier |

---

## 8. Verification & Quality Assurance

### Automated Backend Tests (101 Tests)
```bash
cmd /c "set PYTHONPATH=backend&& .venv\Scripts\pytest backend/tests -v"
```
```text
======================= 101 passed, 1 warning in 33.02s =======================
```

### Production Frontend Build
```bash
npm --prefix frontend run build
```
```text
✓ 1705 modules transformed.
dist/index.html                   0.76 kB │ gzip:   0.43 kB
dist/assets/index-BE4Zbpjd.css   65.22 kB │ gzip:   9.99 kB
dist/assets/index-D8Syms-l.js   438.51 kB │ gzip: 118.75 kB
✓ built in 11.87s
```

---

## 9. Comprehensive Documentation Index

For in-depth technical details, please refer to the dedicated manuals in `docs/`:

- [Local Environment Setup](docs/SETUP.md): Detailed installation and troubleshooting guide.
- [REST API Reference](docs/API.md): Full OpenAPI endpoint specifications and payload schemas.
- [Quality Assurance & Testing](docs/TESTING.md): Testing philosophy, test suite breakdowns, and security test scenarios.
- [Production Deployment Guide](docs/DEPLOYMENT.md): Containerization, Nginx proxying, backup, and production checklists.
- [Mandatory Engineering Standards](docs/ENGINEERING_STANDARDS.md): Security, architectural patterns, and database guidelines.

---

## 10. Repository & Academic Submission

- **Repository**: [https://github.com/chiru018/Campus_Byte](https://github.com/chiru018/Campus_Byte)
- **Branch**: `main`
- **License**: MIT
- **Submission**: B.Tech Final Year Capstone Project
