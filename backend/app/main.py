from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import CampusByteException
from app.api.routers import (
    auth,
    restaurants,
    menu,
    orders,
    restaurant_orders,
    delivery,
    users,
    dashboards,
    system,
    protected_routes,
)

# Application initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Campus Byte - Food Delivery Platform API (Phase 7 Delivery Partner Management & Delivery Tracking)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handler for domain exceptions
@app.exception_handler(CampusByteException)
async def campus_byte_exception_handler(request: Request, exc: CampusByteException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "extra": exc.extra,
        },
    )

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to ensure tables exist
@app.on_event("startup")
def startup_event():
    import app.models  # noqa: F401
    from app.db.base import Base
    from app.db.session import engine
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(f"Database table initialization notice: {exc}")

# Modular API Routers mounted under /api
app.include_router(auth.router, prefix="/api")
app.include_router(protected_routes.router, prefix="/api")
app.include_router(restaurants.router, prefix="/api")
app.include_router(menu.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(restaurant_orders.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(dashboards.router, prefix="/api")
app.include_router(system.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint for Campus Byte API."""
    return {
        "message": "Welcome to Campus Byte API",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
    }
