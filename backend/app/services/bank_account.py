"""
Servicio de lógica de negocio para cuentas bancarias.
"""

from typing import List
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError
from app.models.bank_account import BankAccount
from app.repositories.bank_account import BankAccountRepository
from app.schemas.bank_account import (
    BankAccountListResponse,
    BankAccountResponse,
    CreateBankAccountRequest,
    UpdateBankAccountRequest,
)


class BankAccountService:
    """Servicio para operaciones de cuentas bancarias"""
    
    def __init__(self, bank_account_repo: BankAccountRepository):
        """
        Inicializa el servicio con el repositorio de cuentas bancarias.
        
        Args:
            bank_account_repo: Repositorio de cuentas bancarias
        """
        self.bank_account_repo = bank_account_repo
    
    async def create_bank_account(
        self,
        user_id: UUID,
        data: CreateBankAccountRequest
    ) -> BankAccountResponse:
        """
        Crea una nueva cuenta bancaria para el usuario.
        
        Args:
            user_id: UUID del usuario propietario
            data: Datos de la cuenta a crear
            
        Returns:
            Cuenta bancaria creada
            
        Raises:
            ValidationError: Si los datos son inválidos
        """
        # Validar que el nombre no esté vacío
        if not data.name or not data.name.strip():
            raise ValidationError(
                code="INVALID_ACCOUNT_NAME",
                message="El nombre de la cuenta no puede estar vacío"
            )
        
        # Si no se especifica saldo actual, usar el saldo inicial
        current_balance = data.current_balance if data.current_balance is not None else data.initial_balance
        
        # Crear la cuenta bancaria
        bank_account = BankAccount(
            user_id=user_id,
            name=data.name.strip(),
            color=data.color.upper(),
            initial_balance=data.initial_balance,
            current_balance=current_balance
        )
        
        created_account = await self.bank_account_repo.create(bank_account)
        
        return BankAccountResponse.model_validate(created_account)
    
    async def get_bank_accounts(
        self,
        user_id: UUID
    ) -> BankAccountListResponse:
        """
        Obtiene todas las cuentas bancarias de un usuario.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            Lista de cuentas bancarias con total
        """
        accounts = await self.bank_account_repo.list_by_user(user_id)
        
        return BankAccountListResponse(
            accounts=[BankAccountResponse.model_validate(acc) for acc in accounts],
            total=len(accounts)
        )
    
    async def get_bank_account(
        self,
        account_id: UUID,
        user_id: UUID
    ) -> BankAccountResponse:
        """
        Obtiene una cuenta bancaria específica del usuario.
        
        Args:
            account_id: UUID de la cuenta
            user_id: UUID del usuario
            
        Returns:
            Cuenta bancaria solicitada
            
        Raises:
            NotFoundError: Si la cuenta no existe o no pertenece al usuario
        """
        account = await self.bank_account_repo.get_by_id_for_user(
            account_id=account_id,
            user_id=user_id
        )
        
        if not account:
            raise NotFoundError(
                code="ACCOUNT_NOT_FOUND",
                message="Cuenta bancaria no encontrada"
            )
        
        return BankAccountResponse.model_validate(account)
    
    async def update_bank_account(
        self,
        account_id: UUID,
        user_id: UUID,
        data: UpdateBankAccountRequest
    ) -> BankAccountResponse:
        """
        Actualiza una cuenta bancaria existente.
        
        Args:
            account_id: UUID de la cuenta
            user_id: UUID del usuario
            data: Datos a actualizar
            
        Returns:
            Cuenta bancaria actualizada
            
        Raises:
            NotFoundError: Si la cuenta no existe o no pertenece al usuario
            ValidationError: Si los datos son inválidos
        """
        # Obtener la cuenta existente
        account = await self.bank_account_repo.get_by_id_for_user(
            account_id=account_id,
            user_id=user_id
        )
        
        if not account:
            raise NotFoundError(
                code="ACCOUNT_NOT_FOUND",
                message="Cuenta bancaria no encontrada"
            )
        
        # Actualizar campos si se proporcionan
        update_data = data.model_dump(exclude_unset=True)
        
        if "name" in update_data:
            if not update_data["name"] or not update_data["name"].strip():
                raise ValidationError(
                    code="INVALID_ACCOUNT_NAME",
                    message="El nombre de la cuenta no puede estar vacío"
                )
            account.name = update_data["name"].strip()
        
        if "color" in update_data:
            account.color = update_data["color"].upper()
        
        if "initial_balance" in update_data:
            account.initial_balance = update_data["initial_balance"]
        
        if "current_balance" in update_data:
            account.current_balance = update_data["current_balance"]
        
        # Guardar cambios
        await self.bank_account_repo.db.commit()
        await self.bank_account_repo.db.refresh(account)
        
        return BankAccountResponse.model_validate(account)
    
    async def delete_bank_account(
        self,
        account_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Elimina una cuenta bancaria del usuario.
        
        Args:
            account_id: UUID de la cuenta
            user_id: UUID del usuario
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundError: Si la cuenta no existe o no pertenece al usuario
        """
        # Verificar que la cuenta existe y pertenece al usuario
        account = await self.bank_account_repo.get_by_id_for_user(
            account_id=account_id,
            user_id=user_id
        )
        
        if not account:
            raise NotFoundError(
                code="ACCOUNT_NOT_FOUND",
                message="Cuenta bancaria no encontrada"
            )
        
        # Eliminar la cuenta
        success = await self.bank_account_repo.delete_for_user(
            account_id=account_id,
            user_id=user_id
        )
        
        return success
