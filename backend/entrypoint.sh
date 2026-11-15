#!/bin/bash
set -e

echo "=========================================="
echo "  Campus Byte Backend Container Starting"
echo "=========================================="

echo "Waiting for PostgreSQL database to be ready..."
python -c "
import time, sys
from app.db.session import engine
from sqlalchemy import text

for i in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
            print('PostgreSQL is connected and accepting queries!')
            sys.exit(0)
    except Exception as e:
        print(f'Waiting for database connection... ({e})')
        time.sleep(2)
print('Error: Could not connect to database after 60 seconds.')
sys.exit(1)
"

echo "Applying Alembic database migrations..."
cd /app
alembic -c alembic.ini upgrade head

echo "Seeding initial demo data (if empty)..."
python seed_data.py || echo "Seed completed or skipped"

echo "Starting Uvicorn server on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
