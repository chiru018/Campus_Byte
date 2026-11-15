#!/bin/bash
set -e

echo "Running Alembic migrations..."
cd /app
alembic -c alembic.ini upgrade head

echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
