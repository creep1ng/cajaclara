"""
Servicio para gestión de cuentas bancarias.
"""

import re
from decimal import Decimal
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.bank_account import BankAccountRepository
from app.schemas.bank_account import (BankAccountListResponse,
                                      BankAccountResponse,
                                      CreateBankAccountRequest,
                                      UpdateBankAccountRequest)

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class BankAccountService:
    """Servicio con reglas de negocio para cuentas bancarias."""

    def __init__(self, repository: BankAccountRepository):
        """Inicializa el servicio con su repositorio asociado."""
        self.repository = repository

    async def list_accounts(self, user_id: UUID) -> BankAccountListResponse:
        """Devuelve todas las cuentas de un usuario."""
        accounts = await self.repository.list_by_user(user_id)
        return BankAccountListResponse(
            accounts=[BankAccountResponse.model_validate(acc) for acc in accounts],
            total=len(accounts),
        )

    async def get_account(self, account_id: UUID, user_id: UUID) -> BankAccountResponse:
        """Obtiene una cuenta específica del usuario."""
        account = await self.repository.get_by_id_for_user(account_id, user_id)
        if account is None:
            raise NotFoundError(
                code="BANK_ACCOUNT_NOT_FOUND",
                message="La cuenta bancaria solicitada no existe",
                details={"account_id": str(account_id)},
            )
        return BankAccountResponse.model_validate(account)

    async def create_account(
        self,
        user_id: UUID,
        data: CreateBankAccountRequest,
    ) -> BankAccountResponse:
        """Crea una nueva cuenta bancaria validando reglas de negocio."""
        await self._validate_color(data.color)
        await self._ensure_unique_name(user_id, data.name)

        account_data = data.model_dump(exclude_none=True)
        account_data["user_id"] = user_id
        account_data["current_balance"] = account_data.get(
            "current_balance", account_data["initial_balance"]
        )

        self._validate_non_negative(account_data["initial_balance"], "initial_balance")
        self._validate_non_negative(account_data["current_balance"], "current_balance")

        account = await self.repository.create(account_data)
        return BankAccountResponse.model_validate(account)

    async def update_account(
        self,
        account_id: UUID,
        user_id: UUID,
        data: UpdateBankAccountRequest,
    ) -> BankAccountResponse:
        """Actualiza datos de una cuenta bancaria."""
        account = await self.repository.get_by_id_for_user(account_id, user_id)
        if account is None:
            raise NotFoundError(
                code="BANK_ACCOUNT_NOT_FOUND",
                message="La cuenta bancaria solicitada no existe",
                details={"account_id": str(account_id)},
            )

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != account.name:
            await self._ensure_unique_name(user_id, update_data["name"])

        if "color" in update_data:
            await self._validate_color(update_data["color"])

        if "initial_balance" in update_data:
            self._validate_non_negative(update_data["initial_balance"], "initial_balance")

        if "current_balance" in update_data:
            self._validate_non_negative(update_data["current_balance"], "current_balance")

        updated_account = await self.repository.update(account_id, update_data)
        return BankAccountResponse.model_validate(updated_account)

    async def delete_account(self, account_id: UUID, user_id: UUID) -> None:
        """Elimina definitivamente una cuenta del usuario."""
        deleted = await self.repository.delete_for_user(account_id, user_id)
        if not deleted:
            raise NotFoundError(
                code="BANK_ACCOUNT_NOT_FOUND",
                message="La cuenta bancaria solicitada no existe",
                details={"account_id": str(account_id)},
            )

    async def _ensure_unique_name(self, user_id: UUID, name: str) -> None:
        """Valida que el usuario no tenga otra cuenta con el mismo nombre."""
        existing = await self.repository.get_by_name_for_user(name, user_id)
        if existing:
            raise ValidationError(
                code="BANK_ACCOUNT_DUPLICATED_NAME",
                message="Ya tienes una cuenta bancaria con ese nombre",
                details={"name": name},
            )

    async def _validate_color(self, color: str) -> None:
        """Valida formato de color hexadecimal."""
        if not HEX_COLOR_PATTERN.match(color):
            raise ValidationError(
                code="BANK_ACCOUNT_INVALID_COLOR",
                message="El color debe tener formato hexadecimal (#RRGGBB)",
                details={"color": color},
            )

    def _validate_non_negative(self, value: Decimal, field: str) -> None:
        """Garantiza que los montos no sean negativos."""
        if value < 0:
            raise ValidationError(
                code="BANK_ACCOUNT_NEGATIVE_VALUE",
                message="Los montos deben ser mayores o iguales a cero",
                details={"field": field, "value": float(value)},
            )
