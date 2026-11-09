# Campus Byte – Campus Food Delivery Platform

Campus Byte is a modern, full-stack campus food delivery platform designed to streamline ordering and delivery workflows for three primary stakeholders:

1. **Customers (Students & Faculty):** Browse campus canteens and local restaurants, place orders directly to campus dorms and academic buildings, and track order state in real time.
2. **Restaurant Owners:** Manage food items, menus, and incoming kitchen orders with instant status dispatch and sales reporting.
3. **Delivery Partners (Student Couriers):** Peer-to-peer campus delivery fleet operating between lectures with flexible schedules and smart campus routing.

---

## 1. Project Objectives

- **Campus-Centric Logistics:** Eliminate delivery bottlenecks by optimizing for dorm entrances, campus quads, and academic halls.
- **Micro-Economy for Students:** Enable flexible peer couriering for students between classes.
- **Robust Architecture:** Clean decoupling between React frontend and FastAPI backend, backed by PostgreSQL 17 and SQLAlchemy ORM.
- **Maintainable Standards:** Modular routing, typed schemas (Pydantic v2), migration versioning (Alembic), and containerized portability (Docker Compose).

---

## 2. Technology Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Language:** JavaScript (JSX)
- **Routing:** React Router DOM (v6)
- **Styling:** SCSS with modern modular design tokens
- **HTTP Client:** Axios with centralized interceptors
- **Icons:** Lucide React
- **State Management:** React Context API

### Backend
- **Framework:** Python FastAPI
- **Web Server:** Uvicorn (ASGI)
- **Database ORM:** SQLAlchemy 2.0 (Declarative Base)
- **Database Driver:** `psycopg` (v3 with binary wheels)
- **Data Validation & Settings:** Pydantic v2 & Pydantic-Settings
- **Database Migrations:** Alembic
- **Environment Management:** Python-Dotenv

### Database & Infrastructure
- **Relational Database:** PostgreSQL 17
- **Containers:** Docker & Docker Compose
- **Version Control:** Git & GitHub

---

## 3. Project Architecture & Folder Structure

```
campus-byte/
│
├── frontend/                     # React + Vite Single Page Application
│   ├── public/                   # Static public assets
│   ├── src/
│   │   ├── assets/               # Media and graphic assets
│   │   ├── components/           # UI Components
│   │   │   ├── common/           # Reusable atomic UI (Button, Card, etc.)
│   │   │   ├── navigation/       # Navbar and navigation links
│   │   │   └── layout/           # Page wrappers and Footer
│   │   ├── pages/                # Page views
│   │   │   ├── public/           # LandingPage, Login, Register
│   │   │   ├── customer/         # Customer ordering views (Phase 2+)
│   │   │   ├── restaurant/       # Restaurant management views (Phase 2+)
│   │   │   └── delivery/         # Courier delivery views (Phase 2+)
│   │   ├── layouts/              # Main layout shells
│   │   ├── routes/               # AppRoutes with React Router DOM
│   │   ├── services/             # Axios API client and endpoints
│   │   ├── context/              # AuthContext and global state
│   │   ├── hooks/                # Custom React hooks
│   │   ├── styles/               # SCSS variables and global design system
│   │   ├── App.jsx               # Application entry wrapper
│   │   └── main.jsx              # DOM root mount
│   ├── package.json              # Frontend scripts & dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── .env.example              # Frontend environment template
│   └── .env                      # Local frontend environment config
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/          # Modular API endpoint routers
│   │   ├── core/                 # App configuration & settings
│   │   ├── db/                   # Database session, engine, & Base
│   │   ├── models/               # SQLAlchemy ORM models (Phase 2+)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── services/             # Core business services
│   │   ├── crud/                 # Database CRUD operations
│   │   └── main.py               # FastAPI entry point & CORS
│   ├── alembic/                  # Alembic database migration scripts
│   ├── alembic.ini               # Alembic configuration
│   ├── check_db.py               # Database connectivity verification script
│   ├── requirements.txt          # Python backend dependencies
│   ├── Dockerfile                # Backend container definition
│   ├── .dockerignore             # Docker build ignores
│   └── .env.example              # Backend environment template
│
├── docker-compose.yml            # Multi-container orchestration (FastAPI + Postgres)
├── .gitignore                    # Git exclusions
├── .dockerignore                 # Root container exclusions
├── README.md                     # Project documentation
└── .env.example                  # Root environment template
```

---

## 4. Environment Configuration

### Root Environment (`.env.example`)
Template for containerized or shared environment variables:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=campus_byte
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://postgres:your_secure_password@localhost:5432/campus_byte
PROJECT_NAME="Campus Byte API"
API_VERSION="v1"
DEBUG=True
VITE_API_BASE_URL=http://localhost:8000
```

### Backend Configuration (`backend/.env`)
Copy `backend/.env.example` to `backend/.env` and update credentials:
```bash
DATABASE_URL=postgresql+psycopg://<USERNAME>:<PASSWORD>@localhost:5432/campus_byte
PROJECT_NAME="Campus Byte API"
API_VERSION="v1"
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000"]
```

### Frontend Configuration (`frontend/.env`)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## 5. PostgreSQL Local Setup Guide

PostgreSQL is installed locally on Windows (service: `postgresql-x64-17`).

### Step 1: Open PostgreSQL Interactive Terminal
You can use `psql` directly from PowerShell or Command Prompt:
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```
*(Enter your PostgreSQL master password when prompted)*

### Step 2: Create the Database
Inside the `psql` prompt, execute:
```sql
CREATE DATABASE campus_byte;
```
Verify the database list:
```sql
\l
```
Exit `psql`:
```sql
\q
```

### Step 3: Configure Database Credentials
Create `backend/.env` with your actual PostgreSQL password:
```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD_HERE@localhost:5432/campus_byte
```

### Step 4: Test Database Connectivity
Run the connectivity check script:
```powershell
.\.venv\Scripts\python.exe backend/check_db.py
```

---

## 6. Development Commands

### Backend

1. **Activate virtual environment:**
   ```powershell
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```
2. **Install dependencies:**
   ```powershell
   pip install -r backend/requirements.txt
   ```
3. **Start FastAPI backend:**
   ```powershell
   cd backend
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. **Access Endpoints:**
   - Root: `http://localhost:8000/`
   - Health: `http://localhost:8000/health`
   - Swagger Interactive Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend

1. **Install dependencies:**
   ```powershell
   cd frontend
   npm install
   ```
2. **Start Vite development server:**
   ```powershell
   npm run dev
   ```
3. **Build / compile production bundle:**
   ```powershell
   npm run build
   ```
4. **Access Frontend:**
   - Landing Page: `http://localhost:5173`

---

## 7. Docker & Docker Compose Setup

> **Note:** Docker Desktop is currently not installed on this system. The Docker specifications and compose manifests are fully configured and ready for execution once Docker Desktop is installed.

When Docker Desktop is installed:

1. **Build and start all services:**
   ```bash
   docker compose up --build
   ```
2. **Start in detached mode:**
   ```bash
   docker compose up -d
   ```
3. **Stop all services:**
   ```bash
   docker compose down
   ```
4. **Stop and wipe persistent volume:**
   ```bash
   docker compose down -v
   ```

---

## 8. Git & Version Control

- `.gitignore` is pre-configured to exclude all virtual environments (`.venv/`), Node modules (`node_modules/`), build outputs (`dist/`), environment secrets (`.env`), and temporary caches.
- Changes should be committed on modular feature branches following Phase 1 completion.
