# Campus Byte — Developer Environment & Local Setup Guide

This guide walks you through setting up the complete **Campus Byte** restaurant food ordering and delivery management system on your local machine for development, testing, and evaluation.

---

## 1. Prerequisites

Ensure your system meets the following software requirements:

| Tool | Recommended Version | Verification Command |
|---|---|---|
| **Python** | 3.11+ (Tested on Python 3.11 - 3.14) | `python --version` |
| **Node.js** | 20 LTS or higher | `node --version` |
| **npm** | 9+ or 10+ | `npm --version` |
| **PostgreSQL** (Optional for dev, recommended for prod) | 16+ or 17+ | `psql --version` |
| **Docker & Docker Compose** (Optional) | 24+ | `docker --version` |
| **Git** | 2.40+ | `git --version` |

---

## 2. Repository Cloning & Structure

```bash
git clone https://github.com/chiru018/Campus_Byte.git
cd College_byte
```

Project workspace structure:
```text
College_byte/
├── backend/               # FastAPI backend with SQLAlchemy & Alembic
│   ├── app/               # Core application source code
│   ├── tests/             # 101 pytest automated tests
│   ├── alembic/           # Database migration scripts
│   ├── Dockerfile         # Backend production container specification
│   ├── entrypoint.sh      # Migration runner and container startup
│   ├── requirements.txt   # Python backend dependencies
│   └── seed_data.py       # Idempotent demo database seeder
├── frontend/              # React 18 single-page application with Vite
│   ├── src/               # React components, pages, routes, and services
│   ├── Dockerfile         # Multi-stage production build (Node + Nginx)
│   ├── nginx.conf         # Production Nginx reverse proxy configuration
│   ├── package.json       # Frontend dependencies and build scripts
│   └── vite.config.js     # Dev server configuration with backend proxy
├── docs/                  # System engineering documentation
│   ├── SETUP.md           # This setup guide
│   ├── API.md             # REST API reference documentation
│   ├── TESTING.md         # QA and testing guide (101 tests)
│   └── DEPLOYMENT.md      # Docker and production deployment guide
├── docker-compose.yml     # Multi-container orchestration (DB, API, Web)
├── .env.example           # Example environment variable template
└── README.md              # Project overview and architecture report
```

---

## 3. Backend Setup

### Step 3.1: Python Virtual Environment

From the project root:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3.2: Configure Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
cp .env.example backend/.env
```

For **Zero-Config Local Development**, SQLite is supported out of the box:
```env
DATABASE_URL=sqlite:///./campus_byte.db
JWT_SECRET_KEY=dev-campus-byte-super-secret-jwt-key-2026-min32chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000","http://localhost"]
```

For **PostgreSQL Development**:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=campus_byte
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/campus_byte
```

### Step 3.3: Database Migrations & Initial Seeding

Run database migrations to initialize the schema:
```bash
cd backend
alembic upgrade head
cd ..
```

Populate the database with pre-configured demo users and restaurants:
```bash
python backend/seed_data.py
```

This seeds:
- **Customer**: `student@campusbyte.com` / `Student123`
- **Restaurant Owner**: `owner@campusbyte.com` / `Owner123` (Manages **Campus Spice Kitchen**)
- **Delivery Partner**: `courier@campusbyte.com` / `Courier123` (Active motorcycle fleet profile)
- **6 Signature Menu Items** across Biryani, North Indian, and Beverages

### Step 3.4: Launch the Backend Server

```bash
# From project root
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger documentation is available at:
`http://127.0.0.1:8000/docs`

---

## 4. Frontend Setup

### Step 4.1: Install Node Dependencies

Open a new terminal window:
```bash
cd frontend
npm install
```

### Step 4.2: Start Vite Development Server

```bash
npm run dev
```

The frontend will run on `http://localhost:5173`.
All requests to `/api/*` and `/health` are automatically forwarded to `http://localhost:8000` via the Vite proxy configured in `vite.config.js`.

---

## 5. Verification Checklist

1. Open `http://localhost:5173` in your browser.
2. Log in with `student@campusbyte.com` / `Student123`.
3. Explore the restaurant **Campus Spice Kitchen** and add items to your cart.
4. Place an order with Cash on Delivery.
5. In a separate tab/incognito window, log in with `owner@campusbyte.com` / `Owner123` to accept and prepare the order.
6. In a third window, log in with `courier@campusbyte.com` / `Courier123` to accept delivery and complete the lifecycle.

---

## 6. Running Automated Tests

To verify backend integrity at any time:
```bash
# Windows
cmd /c "set PYTHONPATH=backend&& .venv\Scripts\pytest backend/tests -v"

# Linux / macOS
PYTHONPATH=backend pytest backend/tests -v
```
All **101 tests** must pass.
