"""
Endpoints para gestión de transacciones.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_default_user
from app.db.database import get_db
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import (
    CreateManualTransactionRequest,
    TransactionFilters,
    TransactionListResponse,
    TransactionResponse,
    UpdateTransactionRequest,
)
from app.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/manual",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar transacción manual",
    description="Crea una nueva transacción registrada manualmente en 3 toques (monto, categoría, fecha)",
)
async def create_manual_transaction(
    data: CreateManualTransactionRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Crea una transacción manual.

    Args:
        data: Datos de la transacción
        current_user: Usuario actual (default en MVP)
        db: Sesión de base de datos

    Returns:
        Transacción creada con todos sus detalles

    Raises:
        ValidationError: Si la categoría no existe o no coincide con el tipo
    """
    # Inicializar repositorios
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)

    # Inicializar servicio
    transaction_service = TransactionService(
        transaction_repo=transaction_repo, category_repo=category_repo
    )

    # Crear transacción
    return await transaction_service.create_manual_transaction(
        user_id=current_user.id, data=data
    )


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="Listar transacciones con filtros",
    description="Obtiene lista paginada de transacciones del usuario con soporte para filtros",
)
async def list_transactions(
    start_date: datetime | None = Query(None, description="Fecha inicial (ISO 8601)"),
    end_date: datetime | None = Query(None, description="Fecha final (ISO 8601)"),
    transaction_type: str | None = Query(
        None, description="Filtrar por tipo (income, expense)"
    ),
    classification: str | None = Query(
        None, description="Filtrar por clasificación (personal, business)"
    ),
    category_id: str | None = Query(None, description="Filtrar por categoría"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Registros por página"),
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    """
    Lista transacciones con filtros y paginación.

    Args:
        start_date: Fecha inicial
        end_date: Fecha final
        transaction_type: Tipo de transacción (income/expense)
        classification: Clasificación (personal/business)
        category_id: ID de categoría
        page: Número de página
        limit: Registros por página
        current_user: Usuario actual
        db: Sesión de base de datos

    Returns:
        Lista de transacciones con paginación y resumen
    """
    # Crear filtros
    filters = TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        classification=classification,
        category_id=category_id,
    )

    # Inicializar repositorios y servicio
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo, category_repo=category_repo
    )

    # Listar transacciones
    result = await transaction_service.list_transactions(
        user_id=current_user.id, filters=filters, page=page, limit=limit
    )

    return TransactionListResponse(
        transactions=result["transactions"],
        pagination=result["pagination"],
        summary=result["summary"],
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Obtener detalle de transacción",
    description="Devuelve los detalles completos de una transacción específica",
)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Obtiene una transacción específica.

    Args:
        transaction_id: UUID de la transacción
        current_user: Usuario actual
        db: Sesión de base de datos

    Returns:
        Transacción encontrada

    Raises:
        NotFoundError: Si la transacción no existe
    """
    # Inicializar repositorios y servicio
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo, category_repo=category_repo
    )

    # Obtener transacción
    return await transaction_service.get_transaction(
        transaction_id=transaction_id, user_id=current_user.id
    )


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Actualizar transacción",
    description="Permite corregir datos de una transacción registrada",
)
async def update_transaction(
    transaction_id: UUID,
    data: UpdateTransactionRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Actualiza una transacción.

    Args:
        transaction_id: UUID de la transacción
        data: Datos a actualizar
        current_user: Usuario actual
        db: Sesión de base de datos

    Returns:
        Transacción actualizada

    Raises:
        NotFoundError: Si la transacción no existe
        ValidationError: Si los datos son inválidos
    """
    # Inicializar repositorios y servicio
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo, category_repo=category_repo
    )

    # Actualizar transacción
    return await transaction_service.update_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
        data=data.model_dump(exclude_unset=True),
    )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar transacción",
    description="Marca una transacción como eliminada (soft delete para auditoría)",
)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Elimina una transacción (soft delete).

    Args:
        transaction_id: UUID de la transacción
        current_user: Usuario actual
        db: Sesión de base de datos

    Raises:
        NotFoundError: Si la transacción no existe
    """
    # Inicializar repositorios y servicio
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo, category_repo=category_repo
    )

    # Eliminar transacción
    await transaction_service.delete_transaction(
        transaction_id=transaction_id, user_id=current_user.id
    )
