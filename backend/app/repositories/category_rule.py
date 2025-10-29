"""
Repositorio para reglas de categorización.
"""

from typing import List
from uuid import UUID

from app.models.category_rule import CategoryRule
from app.repositories.base import BaseRepository
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRuleRepository(BaseRepository[CategoryRule]):
    """Repositorio para operaciones de reglas de categorización"""

    def __init__(self, db: AsyncSession):
        super().__init__(CategoryRule, db)

    async def get_active_rules_for_user(self, user_id: UUID) -> List[CategoryRule]:
        """
        Obtiene reglas activas de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de reglas activas
        """
        result = await self.db.execute(
            select(CategoryRule)
            .where(and_(CategoryRule.user_id == user_id, CategoryRule.enabled == True))
            .order_by(CategoryRule.created_at.desc())
        )
        return list(result.scalars().all())
