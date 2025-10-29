"""
Rutas y endpoints para gestión de cuentas bancarias.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.bank_account import BankAccountRepository
from app.schemas.bank_account import (
    BankAccountListResponse,
    BankAccountResponse,
    CreateBankAccountRequest,
    UpdateBankAccountRequest,
)
from app.services.bank_account import BankAccountService

router = APIRouter()


@router.post(
    "",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cuenta bancaria",
    description="Registra una nueva cuenta bancaria con nombre, color y saldo inicial"
)
async def create_bank_account(
    data: CreateBankAccountRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BankAccountResponse:
    """
    Crea una nueva cuenta bancaria para el usuario autenticado.
    
    Args:
        data: Datos de la cuenta a crear
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Cuenta bancaria creada
    """
    repo = BankAccountRepository(db)
    service = BankAccountService(repo)
    
    return await service.create_bank_account(
        user_id=current_user.id,
        data=data
    )


@router.get(
    "",
    response_model=BankAccountListResponse,
    summary="Listar cuentas bancarias",
    description="Obtiene todas las cuentas bancarias registradas por el usuario"
)
async def list_bank_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BankAccountListResponse:
    """
    Lista todas las cuentas bancarias del usuario autenticado.
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Lista de cuentas bancarias con total
    """
    repo = BankAccountRepository(db)
    service = BankAccountService(repo)
    
    return await service.get_bank_accounts(user_id=current_user.id)


@router.get(
    "/{bank_account_id}",
    response_model=BankAccountResponse,
    summary="Obtener cuenta bancaria",
    description="Devuelve los detalles de una cuenta bancaria específica"
)
async def get_bank_account(
    bank_account_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BankAccountResponse:
    """
    Obtiene una cuenta bancaria específica del usuario.
    
    Args:
        bank_account_id: ID de la cuenta bancaria
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Cuenta bancaria solicitada
    """
    repo = BankAccountRepository(db)
    service = BankAccountService(repo)
    
    return await service.get_bank_account(
        account_id=bank_account_id,
        user_id=current_user.id
    )


@router.put(
    "/{bank_account_id}",
    response_model=BankAccountResponse,
    summary="Actualizar cuenta bancaria",
    description="Permite editar nombre, color y saldos de una cuenta bancaria"
)
async def update_bank_account(
    bank_account_id: UUID,
    data: UpdateBankAccountRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BankAccountResponse:
    """
    Actualiza una cuenta bancaria existente del usuario.
    
    Args:
        bank_account_id: ID de la cuenta bancaria
        data: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Cuenta bancaria actualizada
    """
    repo = BankAccountRepository(db)
    service = BankAccountService(repo)
    
    return await service.update_bank_account(
        account_id=bank_account_id,
        user_id=current_user.id,
        data=data
    )


@router.delete(
    "/{bank_account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cuenta bancaria",
    description="Elimina una cuenta bancaria del usuario"
)
async def delete_bank_account(
    bank_account_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> None:
    """
    Elimina una cuenta bancaria del usuario autenticado.
    
    Args:
        bank_account_id: ID de la cuenta bancaria
        current_user: Usuario autenticado
        db: Sesión de base de datos
    """
    repo = BankAccountRepository(db)
    service = BankAccountService(repo)
    
    await service.delete_bank_account(
        account_id=bank_account_id,
        user_id=current_user.id
    )
