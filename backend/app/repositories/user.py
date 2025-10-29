"""
Repositorio para usuarios.
"""

from typing import Optional
from uuid import UUID

from app.models.user import User
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[User]):
    """Repositorio para operaciones de usuarios"""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene usuario por email.

        Args:
            email: Email del usuario

        Returns:
            Usuario o None
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Obtiene usuario por ID.

        Args:
            user_id: UUID del usuario

        Returns:
            Usuario o None
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
