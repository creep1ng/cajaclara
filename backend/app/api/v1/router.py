"""
Router principal de la API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import transactions

api_router = APIRouter()

# Include routers
api_router.include_router(transactions.router)