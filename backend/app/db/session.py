from typing import Generator
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

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
