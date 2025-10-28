"""
Configuración centralizada de la aplicación usando Pydantic Settings.
Todas las variables de entorno se cargan desde .env
"""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación"""
    
    # Application
    APP_NAME: str = "CajaClara API"
    APP_VERSION: str = "1.0.0-mvp"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # MVP Settings
    MVP_MODE: bool = True
    DEFAULT_USER_ID: str = "00000000-0000-0000-0000-000000000001"
    DEFAULT_USER_EMAIL: str = "demo@cajaclara.com"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/cajaclara",
        description="URL de conexión a PostgreSQL"
    )
    DB_ECHO: bool = Field(default=False, description="Log SQL queries")
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=10)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=300)
    
    # CORS
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Orígenes permitidos para CORS (separados por coma)"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string"""
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_MODEL: str = Field(
        default="gpt-4-vision-preview",
        description="Modelo de OpenAI para OCR"
    )
    OPENAI_MAX_TOKENS: int = Field(default=1000, ge=100, le=4000)
    OPENAI_TEMPERATURE: float = Field(default=0.1, ge=0.0, le=1.0)
    OPENAI_TIMEOUT: int = Field(default=30, ge=10, le=120)
    
    # OCR Settings
    OCR_MIN_CONFIDENCE: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confianza mínima para aceptar extracción OCR"
    )
    OCR_MAX_IMAGE_SIZE_MB: int = Field(default=10, ge=1, le=20)
    OCR_ALLOWED_FORMATS: List[str] = Field(
        default=["image/jpeg", "image/png", "image/jpg", "image/webp"]
    )
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100)
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=500)
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL debe ser una URL de PostgreSQL")
        return v
    
    def get_database_url_sync(self) -> str:
        """Retorna URL síncrona para Alembic"""
        return self.DATABASE_URL.replace("+asyncpg", "")


# Singleton instance
settings = Settings()


# Helper functions
def get_settings() -> Settings:
    """Dependency para FastAPI"""
    return settings


def is_production() -> bool:
    """Check if running in production"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.ENVIRONMENT == "development"
