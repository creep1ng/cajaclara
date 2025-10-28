"""
Aplicación FastAPI principal (versión MVP).
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    CajaClaraException,
    DatabaseError,
    ForbiddenError,
    NotFoundError,
    OcrProcessingError,
    UnauthorizedError,
    ValidationError,
)
from app.db.database import get_db
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 MVP Mode: {settings.MVP_MODE}")
    
    # Initialize database
    async for db in get_db():
        await init_db(db)
        break
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para gestión de transacciones financieras (MVP)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS - Permisivo para MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
def get_status_code_for_exception(exc: CajaClaraException) -> int:
    """Map exception types to HTTP status codes"""
    if isinstance(exc, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UnauthorizedError):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ForbiddenError):
        return status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValidationError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, OcrProcessingError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, DatabaseError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return status.HTTP_400_BAD_REQUEST


@app.exception_handler(CajaClaraException)
async def cajaclara_exception_handler(request: Request, exc: CajaClaraException):
    """Handle custom exceptions"""
    status_code = get_status_code_for_exception(exc)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    print(f"❌ Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if settings.DEBUG else {},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include routers
app.include_router(api_router, prefix="/api/v1")


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "mode": "MVP" if settings.MVP_MODE else "Production"
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
