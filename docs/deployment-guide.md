# Campus Byte – Deployment & Operations Guide

This guide details environment configuration, database migrations, and operational commands for running Campus Byte.

---

## 1. Prerequisites

- **Python:** 3.12+ (Python 3.14.2 verified)
- **Node.js:** v20+ (Node v24.12.0 verified) & npm 11+
- **Database:** PostgreSQL 17 (Service `postgresql-x64-17`)
- **Containers:** Docker Desktop & Docker Compose (Optional for local development)

---

## 2. Environment Configuration

### Root Environment (`.env`)
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=campus_byte
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://postgres:your_secure_password@localhost:5432/campus_byte
PROJECT_NAME="Campus Byte API"
API_VERSION="v1"
DEBUG=True
JWT_SECRET_KEY="generate_a_strong_64_char_secret_key_here"
VITE_API_BASE_URL=http://localhost:8000
```

### Backend Environment (`backend/.env`)
```bash
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/campus_byte
PROJECT_NAME="Campus Byte API"
API_VERSION="v1"
DEBUG=True
JWT_SECRET_KEY="generate_a_strong_64_char_secret_key_here"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000"]
AUTH_COOKIE_NAME="campus_byte_access_token"
COOKIE_SECURE=False
COOKIE_SAMESITE="lax"
COOKIE_HTTPONLY=True
```

---

## 3. Database Migrations

Apply Alembic migrations to synchronize the PostgreSQL schema:
```powershell
cd backend
..\.venv\Scripts\alembic.exe upgrade head
```

Verify migration status:
```powershell
..\.venv\Scripts\alembic.exe current
```

---

## 4. Starting the Services

### Backend Service (FastAPI)
```powershell
cd backend
..\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### Frontend Application (React + Vite)
```powershell
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 5. Docker Deployment

When Docker Desktop is installed, spin up all services with one command:
```bash
docker compose up --build -d
```
Stop containers:
```bash
docker compose down
```
