from fastapi import APIRouter
from app.db.session import check_db_connection

router = APIRouter()


@router.get("/system-info", tags=["System"])
def get_system_info():
    """Returns system status and database connectivity details."""
    db_status = check_db_connection()
    return {
        "service": "Campus Byte API",
        "version": "v1",
        "database": db_status,
    }

