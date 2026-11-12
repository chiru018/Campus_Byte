from typing import Generator
import logging
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
pool_pre_ping = not is_sqlite

# SQLAlchemy Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=pool_pre_ping,
    echo=False,
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a scoped database session per request.
    Closes the session after the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Checks database connectivity by executing a lightweight query.
    Returns status dictionary with connection details.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar()
            return {
                "connected": True,
                "message": "Database connection successful",
            }
    except Exception as exc:
        logger.warning(f"Database connection check failed: {exc}")
        return {
            "connected": False,
            "message": f"Database connection failed: {str(exc)}",
        }

