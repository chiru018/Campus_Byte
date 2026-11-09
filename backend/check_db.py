"""
Database Connectivity Verification Script for Campus Byte.

Usage:
    python check_db.py
"""

import sys
import os

# Ensure backend root is in python search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.session import check_db_connection


def main():
    print("=" * 60)
    print("  Campus Byte - Database Connectivity Check")
    print("=" * 60)
    print(f"Connecting using DATABASE_URL: {settings.DATABASE_URL.split('@')[-1]}")
    
    result = check_db_connection()
    if result["connected"]:
        print("\n [SUCCESS] Successfully connected to PostgreSQL database!")
        print(f"Details: {result['message']}")
        sys.exit(0)
    else:
        print("\n [FAILURE] Could not connect to PostgreSQL database.")
        print(f"Details: {result['message']}")
        print("\nTroubleshooting tips:")
        print("1. Ensure PostgreSQL service ('postgresql-x64-17') is running.")
        print("2. Ensure database 'campus_byte' has been created.")
        print("3. Check your credentials in backend/.env (or set DATABASE_URL).")
        sys.exit(1)


if __name__ == "__main__":
    main()
