"""
Endpoints para gestión de categorías.
"""

from typing import Optional

from app.api.deps import get_default_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.category import CategoryList
from app.services.category import create_category_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=CategoryList,
    status_code=status.HTTP_200_OK,
    summary="Listar categorías disponibles",
    description="Obtiene el catálogo de categorías predefinidas, con posibilidad de búsqueda",
)
async def list_categories(
    transaction_type: Optional[str] = Query(
        None,
        description="Filtrar por tipo de transacción",
        enum=["income", "expense"]
    ),
    search: Optional[str] = Query(
        None,
        description="Búsqueda por nombre o descripción"
    ),
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> CategoryList:
    """
    Lista categorías disponibles con filtros opcionales.
    
    Args:
        transaction_type: Tipo de transacción (income/expense)
        search: Búsqueda por nombre o descripción
        current_user: Usuario actual (default en MVP)
        db: Sesión de base de datos
        
    Returns:
        Lista de categorías que cumplen los criterios
        
    Raises:
        HTTPException: Error en la consulta a la base de datos (500)
    """
    try:
        # Crear servicio de categorías
        category_service = create_category_service(db)
        
        # Obtener categorías
        categories = await category_service.get_categories(
            transaction_type=transaction_type,
            search=search
        )
        
        # Devolver respuesta según OpenAPI
        return CategoryList(categories=categories)
        
    except Exception as e:
        # En caso de error de base de datos, devolver 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al consultar categorías de la base de datos"
        ) from e