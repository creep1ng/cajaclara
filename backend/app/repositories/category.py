"""
Repositorio para categorías.
"""

from typing import List, Optional

from app.models.category import Category
from app.repositories.base import BaseRepository
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRepository(BaseRepository[Category]):
    """Repositorio para operaciones de categorías"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)
    
    async def get_by_id(self, category_id: str) -> Optional[Category]:
        """
        Obtiene categoría por ID.
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            Categoría o None
        """
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_type(
        self,
        transaction_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Category]:
        """
        Lista categorías con filtros.
        
        Args:
            transaction_type: Tipo de transacción (income/expense)
            search: Búsqueda por nombre o descripción
            
        Returns:
            Lista de categorías
        """
        conditions = []
        
        if transaction_type:
            conditions.append(Category.transaction_type == transaction_type)
        
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Category.name.ilike(search_pattern),
                    Category.description.ilike(search_pattern)
                )
            )
        
        query = select(Category)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Category.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())