"""
Router principal de la API v1.
"""

from app.api.v1.endpoints import categories, transactions
from app.routes import auth
from fastapi import APIRouter

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(transactions.router)
api_router.include_router(categories.router)