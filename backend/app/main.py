from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import system

# Application initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Campus Byte - Food Delivery Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modular API Routers
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
