"""
Servicio de categorías para la lógica de negocio.
"""

from typing import List, Optional

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import Category
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryService:
    """Servicio para operaciones de categorías"""
    
    def __init__(self, category_repo: CategoryRepository):
        """
        Inicializa el servicio con el repositorio de categorías.
        
        Args:
            category_repo: Repositorio de categorías
        """
        self.category_repo = category_repo
    
    async def get_categories(
        self,
        transaction_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Category]:
        """
        Obtiene lista de categorías con filtros opcionales.
        
        Args:
            transaction_type: Tipo de transacción (income/expense)
            search: Búsqueda por nombre o descripción
            
        Returns:
            Lista de categorías que cumplen los criterios
            
        Raises:
            Exception: Error en la consulta a la base de datos
        """
        try:
            # Obtener categorías desde el repositorio
            categories = await self.category_repo.list_by_type(
                transaction_type=transaction_type,
                search=search
            )
            
            # Convertir a schemas de respuesta
            return [Category.model_validate(category) for category in categories]
            
        except Exception as e:
            # Log del error (en producción se usaría logging)
            print(f"Error en CategoryService.get_categories: {str(e)}")
            raise Exception("Error al consultar categorías de la base de datos")


def create_category_service(db: AsyncSession) -> CategoryService:
    """
    Crea una instancia del servicio de categorías.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Instancia de CategoryService
    """
    category_repo = CategoryRepository(db)
    return CategoryService(category_repo)