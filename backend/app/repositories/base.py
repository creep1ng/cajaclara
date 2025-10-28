"""
Repositorio base con operaciones CRUD genéricas.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from app.models.base import Base
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repositorio base con operaciones CRUD"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Inicializa el repositorio.
        
        Args:
            model: Clase del modelo SQLAlchemy
            db: Sesión de base de datos async
        """
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.
        
        Args:
            id: UUID del registro
            
        Returns:
            Instancia del modelo o None
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Obtiene todos los registros con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de instancias del modelo
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Crea un nuevo registro.
        
        Args:
            obj_in: Diccionario con datos del registro
            
        Returns:
            Instancia del modelo creada
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Actualiza un registro existente.
        
        Args:
            id: UUID del registro
            obj_in: Diccionario con datos a actualizar
            
        Returns:
            Instancia del modelo actualizada o None
        """
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: UUID) -> bool:
        """
        Elimina un registro (hard delete).
        
        Args:
            id: UUID del registro
            
        Returns:
            True si se eliminó, False si no existía
        """
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return False
        
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
    
    async def count(self) -> int:
        """
        Cuenta el total de registros.
        
        Returns:
            Número total de registros
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()