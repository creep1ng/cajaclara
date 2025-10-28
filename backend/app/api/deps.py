"""
Dependencias comunes para endpoints (versión MVP simplificada).
"""

from uuid import UUID

from app.config import settings
from app.db.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_default_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Obtiene usuario default para MVP.
    
    En MVP no hay autenticación, se usa un usuario default.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Usuario default
        
    Raises:
        RuntimeError: Si el usuario default no existe
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(settings.DEFAULT_USER_ID))
    
    if user is None:
        raise RuntimeError(
            f"Default user not found. Please run database initialization. "
            f"Expected user ID: {settings.DEFAULT_USER_ID}"
        )
    
    return user