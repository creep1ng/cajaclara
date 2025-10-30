"""
Servicio de lógica de negocio para transacciones.
"""

from decimal import Decimal
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.bank_account import BankAccountRepository
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import (
    CreateManualTransactionRequest,
    TransactionFilters,
    TransactionResponse,
)


class TransactionService:
    """Servicio para gestión de transacciones"""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
        bank_account_repo: BankAccountRepository,
    ):
        """
        Inicializa el servicio de transacciones.

        Args:
            transaction_repo: Repositorio de transacciones
            category_repo: Repositorio de categorías
            bank_account_repo: Repositorio de cuentas bancarias
        """
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.bank_account_repo = bank_account_repo

    async def _update_account_balance(
        self,
        account_id: UUID,
        user_id: UUID,
        amount: Decimal,
        transaction_type: str,
    ) -> None:
        """
        Actualiza el saldo de una cuenta bancaria según la transacción.

        Args:
            account_id: UUID de la cuenta bancaria
            user_id: UUID del usuario propietario
            amount: Monto de la transacción
            transaction_type: Tipo de transacción (income, expense, transfer)
        """
        account = await self.bank_account_repo.get_by_id_for_user(account_id, user_id)
        if account is None:
            raise NotFoundError(
                code="BANK_ACCOUNT_NOT_FOUND",
                message=f"Bank account '{account_id}' not found",
                details={"account_id": str(account_id)},
            )

        # Calcular nuevo saldo
        if transaction_type == "income":
            new_balance = account.current_balance + amount
        elif transaction_type == "expense":
            new_balance = account.current_balance - amount
        else:  # transfer - se maneja en el método de transferencia
            return

        # Actualizar saldo
        await self.bank_account_repo.update(
            account_id, {"current_balance": new_balance}
        )

    async def create_manual_transaction(
        self, user_id: UUID, data: CreateManualTransactionRequest
    ) -> TransactionResponse:
        """
        Crea transacción manual.

        Args:
            user_id: UUID del usuario
            data: Datos de la transacción

        Returns:
            Transacción creada

        Raises:
            ValidationError: Si categoría no existe o datos inválidos
        """
        # Validar según tipo de transacción
        if data.transaction_type == "transfer":
            # Para transferencias, validar cuentas
            if not data.from_account or not data.to_account:
                raise ValidationError(
                    code="INVALID_TRANSFER",
                    message="Transfer requires both from_account and to_account",
                    details={"from_account": data.from_account, "to_account": data.to_account},
                )
            if data.from_account == data.to_account:
                raise ValidationError(
                    code="INVALID_TRANSFER",
                    message="from_account and to_account cannot be the same",
                    details={"from_account": data.from_account, "to_account": data.to_account},
                )
        else:
            # Para ingresos y gastos, validar categoría
            if not data.category_id:
                raise ValidationError(
                    code="INVALID_CATEGORY",
                    message="category_id is required for income and expense transactions",
                    details={"field": "category_id"},
                )
            
            category = await self.category_repo.get_by_id(data.category_id)
            if category is None:
                raise ValidationError(
                    code="INVALID_CATEGORY",
                    message=f"Category '{data.category_id}' not found",
                    details={"field": "category_id", "value": data.category_id},
                )

            # Validar que el tipo de categoría coincida con el tipo de transacción
            if category.transaction_type != data.transaction_type:
                raise ValidationError(
                    code="CATEGORY_TYPE_MISMATCH",
                    message=f"Category '{category.name}' is for {category.transaction_type}, but transaction is {data.transaction_type}",
                    details={
                        "category_type": category.transaction_type,
                        "transaction_type": data.transaction_type,
                    },
                )

        # Crear transacción
        transaction_data = {
            "user_id": user_id,
            "amount": data.amount,
            "currency": data.currency,
            "category_id": data.category_id,
            "description": data.description,
            "transaction_type": data.transaction_type,
            "classification": data.classification,
            "transaction_date": data.transaction_date,
            "entrepreneurship_id": data.entrepreneurship_id,
            "bank_account_id": data.bank_account_id,
            "from_account": data.from_account,
            "to_account": data.to_account,
            "tags": data.tags or [],
            "metadata": {"source": "manual"},
            "sync_status": "synced",
            "created_by": user_id,
        }

        transaction = await self.transaction_repo.create(transaction_data)

        # Actualizar saldo de cuenta bancaria si se proporcionó
        if data.bank_account_id:
            await self._update_account_balance(
                account_id=data.bank_account_id,
                user_id=user_id,
                amount=data.amount,
                transaction_type=data.transaction_type,
            )

        # Cargar con categoría para la respuesta
        transaction_with_category = (
            await self.transaction_repo.get_by_id_with_category(
                transaction.id, user_id
            )
        )

        return TransactionResponse.model_validate(transaction_with_category)

    async def get_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> TransactionResponse:
        """
        Obtiene una transacción específica.

        Args:
            transaction_id: UUID de la transacción
            user_id: UUID del usuario propietario

        Returns:
            Transacción encontrada

        Raises:
            NotFoundError: Si la transacción no existe
        """
        transaction = await self.transaction_repo.get_by_id_with_category(
            transaction_id, user_id
        )

        if transaction is None:
            raise NotFoundError(
                code="TRANSACTION_NOT_FOUND",
                message=f"Transaction '{transaction_id}' not found",
                details={"transaction_id": str(transaction_id)},
            )

        return TransactionResponse.model_validate(transaction)

    async def list_transactions(
        self,
        user_id: UUID,
        filters: TransactionFilters,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """
        Lista transacciones con filtros y paginación.

        Args:
            user_id: UUID del usuario
            filters: TransactionFilters con filtros
            page: Número de página
            limit: Registros por página

        Returns:
            Diccionario con transacciones, paginación y resumen
        """
        skip = (page - 1) * limit
        transactions, total = await self.transaction_repo.list_with_filters(
            user_id=user_id, filters=filters, skip=skip, limit=limit
        )

        # Calcular resumen
        summary = await self.transaction_repo.calculate_summary(user_id, filters)

        total_pages = (total + limit - 1) // limit

        return {
            "transactions": [
                TransactionResponse.model_validate(tx) for tx in transactions
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
            },
            "summary": summary.model_dump(),
        }

    async def update_transaction(
        self, transaction_id: UUID, user_id: UUID, data: dict
    ) -> TransactionResponse:
        """
        Actualiza una transacción.

        Args:
            transaction_id: UUID de la transacción
            user_id: UUID del usuario propietario
            data: Datos a actualizar

        Returns:
            Transacción actualizada

        Raises:
            NotFoundError: Si la transacción no existe
            ValidationError: Si los datos son inválidos
        """
        # Verificar que la transacción existe
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if transaction is None or transaction.user_id != user_id:
            raise NotFoundError(
                code="TRANSACTION_NOT_FOUND",
                message=f"Transaction '{transaction_id}' not found",
                details={"transaction_id": str(transaction_id)},
            )

        # Validar categoría si se proporciona
        if "category_id" in data and data["category_id"]:
            category = await self.category_repo.get_by_id(data["category_id"])
            if category is None:
                raise ValidationError(
                    code="INVALID_CATEGORY",
                    message=f"Category '{data['category_id']}' not found",
                    details={"field": "category_id", "value": data["category_id"]},
                )

            # Validar que el tipo de categoría coincida
            transaction_type = data.get("transaction_type", transaction.transaction_type)
            if category.transaction_type != transaction_type:
                raise ValidationError(
                    code="CATEGORY_TYPE_MISMATCH",
                    message=f"Category '{category.name}' is for {category.transaction_type}, but transaction is {transaction_type}",
                    details={
                        "category_type": category.transaction_type,
                        "transaction_type": transaction_type,
                    },
                )

        # Actualizar
        updated_transaction = await self.transaction_repo.update(
            transaction_id, data
        )

        # Cargar con categoría
        transaction_with_category = (
            await self.transaction_repo.get_by_id_with_category(
                updated_transaction.id, user_id
            )
        )

        return TransactionResponse.model_validate(transaction_with_category)

    async def delete_transaction(
        self, transaction_id: UUID, user_id: UUID
    ) -> None:
        """
        Elimina una transacción (soft delete).

        Args:
            transaction_id: UUID de la transacción
            user_id: UUID del usuario propietario

        Raises:
            NotFoundError: Si la transacción no existe
        """
        transaction = await self.transaction_repo.get_by_id_with_category(
            transaction_id, user_id
        )
        if transaction is None:
            raise NotFoundError(
                code="TRANSACTION_NOT_FOUND",
                message=f"Transaction '{transaction_id}' not found",
                details={"transaction_id": str(transaction_id)},
            )

        await self.transaction_repo.soft_delete(transaction_id, user_id)
