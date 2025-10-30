"""
Endpoints para gestión de cuentas bancarias.
"""

from uuid import UUID

from app.api.deps import get_default_user
from app.db.database import get_db
from app.models.user import User
from app.repositories.bank_account import BankAccountRepository
from app.schemas.bank_account import (BankAccountListResponse,
                                      BankAccountResponse,
                                      CreateBankAccountRequest,
                                      UpdateBankAccountRequest)
from app.services.bank_account_service import BankAccountService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/bank-accounts", tags=["Bank Accounts"])


def get_service(db: AsyncSession) -> BankAccountService:
    """Crea una instancia del servicio de cuentas bancarias."""
    repository = BankAccountRepository(db)
    return BankAccountService(repository)


@router.get(
    "",
    response_model=BankAccountListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar cuentas bancarias",
    description="Obtiene todas las cuentas bancarias registradas por el usuario",
)
async def list_bank_accounts(
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> BankAccountListResponse:
    """Devuelve la lista de cuentas bancarias del usuario autenticado."""
    service = get_service(db)
    return await service.list_accounts(UUID(str(current_user.id)))


@router.post(
    "",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cuenta bancaria",
    description="Registra una nueva cuenta bancaria con nombre, color y saldo inicial",
)
async def create_bank_account(
    payload: CreateBankAccountRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    """Crea una cuenta bancaria para el usuario."""
    service = get_service(db)
    return await service.create_account(UUID(str(current_user.id)), payload)


@router.get(
    "/{account_id}",
    response_model=BankAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener cuenta bancaria",
    description="Devuelve los detalles de una cuenta bancaria específica",
)
async def get_bank_account(
    account_id: UUID,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    """Obtiene información detallada de una cuenta bancaria."""
    service = get_service(db)
    return await service.get_account(account_id, UUID(str(current_user.id)))


@router.put(
    "/{account_id}",
    response_model=BankAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar cuenta bancaria",
    description="Permite editar nombre, color y saldos de una cuenta bancaria",
)
async def update_bank_account(
    account_id: UUID,
    payload: UpdateBankAccountRequest,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    """Actualiza los datos de una cuenta bancaria existente."""
    service = get_service(db)
    return await service.update_account(
        account_id=account_id,
        user_id=UUID(str(current_user.id)),
        data=payload,
    )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cuenta bancaria",
    description="Elimina una cuenta bancaria del usuario",
)
async def delete_bank_account(
    account_id: UUID,
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Elimina definitivamente una cuenta bancaria."""
    service = get_service(db)
    await service.delete_account(account_id, UUID(str(current_user.id)))
