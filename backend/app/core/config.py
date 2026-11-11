from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Campus Byte API"
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/campus_byte"

    # Security & JWT
    JWT_SECRET_KEY: str = "dev_super_secret_jwt_key_campus_byte_2026_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cookie Security Settings
    AUTH_COOKIE_NAME: str = "campus_byte_access_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_HTTPONLY: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

