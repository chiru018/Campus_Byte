# Campus Byte — Production Deployment & Docker Guide

This guide details how to build, configure, deploy, and monitor **Campus Byte** in a containerized production environment using **Docker** and **Docker Compose**.

---

## 1. Production Architecture Overview

In production, Campus Byte runs as three orchestrated container services connected via an internal bridge network:

```
[ Web Browser ]
      │ (HTTP Port 80)
      ▼
┌──────────────────────────────────────────────┐
│  campus_byte_frontend (Nginx Alpine)         │
│  - Serves compiled React 18 SPA              │
│  - Proxies /api/* to backend:8000            │
│  - Proxies /health to backend:8000           │
└──────────────────────┬───────────────────────┘
                       │ (Internal Network: campus_byte_network)
                       ▼
┌──────────────────────────────────────────────┐
│  campus_byte_backend (FastAPI / Uvicorn)     │
│  - entrypoint.sh runs Alembic migrations     │
│  - Uvicorn ASGI server on port 8000          │
└──────────────────────┬───────────────────────┘
                       │ (Port 5432)
                       ▼
┌──────────────────────────────────────────────┐
│  campus_byte_postgres (PostgreSQL 17 Alpine) │
│  - Persistent data volume                    │
│  - Healthcheck with pg_isready               │
└──────────────────────────────────────────────┘
```

---

## 2. Environment Configuration

Create a production `.env` file in the root directory:

```env
# Database Credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_strong_production_password_here
POSTGRES_DB=campus_byte
POSTGRES_PORT=5432

# Production Database Connection String
DATABASE_URL=postgresql+psycopg://postgres:your_strong_production_password_here@postgres:5432/campus_byte

# Security & Tokens
JWT_SECRET_KEY=generate_a_cryptographically_secure_random_key_64_chars_min
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false

# Allowed Origins
BACKEND_CORS_ORIGINS=["http://localhost","http://localhost:80","https://yourdomain.edu"]
```

> [!CAUTION]
> Never commit your production `.env` file to source control. Ensure it is included in `.gitignore`.

---

## 3. Deployment with Docker Compose

### Step 3.1: Build and Launch Containers

Run the following command from the project root:

```bash
docker compose up -d --build
```

### Step 3.2: Verify Service Status

Inspect running containers and health checks:
```bash
docker compose ps
```

Expected output:
```text
NAME                   IMAGE                    COMMAND                  SERVICE    STATUS
campus_byte_postgres   postgres:17-alpine       "docker-entrypoint.s…"   postgres   Up (healthy)
campus_byte_backend    college_byte-backend     "./entrypoint.sh"        backend    Up
campus_byte_frontend   college_byte-frontend    "/docker-entrypoint.…"   frontend   Up
```

### Step 3.3: Verify Container Logs

```bash
# Check Alembic migrations and Uvicorn startup
docker compose logs backend

# Check Nginx access and error logs
docker compose logs frontend
```

---

## 4. Production Database Seeding

To seed production demonstration accounts and initial menus:

```bash
docker compose exec backend python seed_data.py
```

This sets up:
- Student user: `student@campusbyte.com` / `Student123`
- Restaurant owner: `owner@campusbyte.com` / `Owner123`
- Delivery courier: `courier@campusbyte.com` / `Courier123`
- Campus Spice Kitchen restaurant and 6 signature items.

---

## 5. Health Monitoring & Maintenance

### Liveness Probe
```bash
curl http://localhost/health
# Response: {"status":"healthy","service":"Campus Byte API"}
```

### Database Backup
```bash
docker compose exec postgres pg_dump -U postgres campus_byte > backup_$(date +%Y%m%d).sql
```

### Database Restoration
```bash
cat backup_20261115.sql | docker compose exec -T postgres psql -U postgres campus_byte
```

### Shutting Down
To gracefully stop all services:
```bash
docker compose down
```
To stop and remove data volumes:
```bash
docker compose down -v
```
