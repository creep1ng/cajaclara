"""
Servicio de lógica de negocio para transacciones.
"""

from datetime import datetime
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import (
    CreateManualTransactionRequest,
    CreateOcrTransactionRequest,
    OcrExtractedData,
    OcrTransactionResponse,
    TransactionFilters,
    TransactionResponse,
)


class TransactionService:
    """Servicio para gestión de transacciones"""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ):
        """
        Inicializa el servicio de transacciones.

        Args:
            transaction_repo: Repositorio de transacciones
            category_repo: Repositorio de categorías
        """
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

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
            ValidationError: Si categoría no existe
        """
        # Validar categoría
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
            "tags": data.tags or [],
            "metadata": {"source": "manual"},
            "sync_status": "synced",
            "created_by": user_id,
        }

        transaction = await self.transaction_repo.create(transaction_data)

        # Cargar con categoría para la respuesta
        transaction_with_category = await self.transaction_repo.get_by_id_with_category(
            transaction.id, user_id
        )

        return TransactionResponse.model_validate(transaction_with_category)

    async def create_ocr_transaction(
        self,
        user_id: UUID,
        ocr_data: OcrExtractedData,
        request_data: CreateOcrTransactionRequest,
    ) -> OcrTransactionResponse:
        """
        Crea transacción desde datos extraídos por OCR.

        Args:
            user_id: UUID del usuario
            ocr_data: Datos extraídos por OCR
            request_data: Datos adicionales de la petición

        Returns:
            Transacción creada con detalles de OCR

        Raises:
            ValidationError: Si los datos son inválidos
        """
        # Determinar categoría a usar
        category_id = None
        if (
            ocr_data.category_suggested
            and ocr_data.category_confidence >= self._get_min_confidence()
        ):
            # Verificar que la categoría sugerida existe
            category = await self.category_repo.get_by_id(ocr_data.category_suggested)
            if category and category.transaction_type == request_data.transaction_type:
                category_id = ocr_data.category_suggested

        # Si no hay categoría válida, usar categoría por defecto
        if not category_id:
            # Usar categoría "otros" según el tipo de transacción
            category_id = (
                "cat-other-income"
                if request_data.transaction_type == "income"
                else "cat-other-expense"
            )

        # Validar que tengamos al menos el monto
        if (
            not ocr_data.amount
            or ocr_data.amount_confidence < self._get_min_confidence()
        ):
            raise ValidationError(
                code="OCR_INSUFFICIENT_DATA",
                message="No se pudo extraer el monto con suficiente confianza. Por favor, ingrese los datos manualmente.",
                details={
                    "amount": str(ocr_data.amount) if ocr_data.amount else None,
                    "confidence": ocr_data.amount_confidence,
                    "min_required": self._get_min_confidence(),
                },
            )

        # Usar fecha extraída o fecha actual
        transaction_date = ocr_data.date
        if not transaction_date or ocr_data.date_confidence < 0.5:
            transaction_date = datetime.now()

        # Construir descripción
        description = request_data.description or ""
        if ocr_data.vendor:
            description = f"{ocr_data.vendor} - {description}".strip(" - ")

        # Crear transacción
        transaction_data = {
            "user_id": user_id,
            "amount": ocr_data.amount,
            "currency": "COP",  # Por defecto COP
            "category_id": category_id,
            "description": description,
            "transaction_type": request_data.transaction_type,
            "classification": request_data.classification,
            "transaction_date": transaction_date,
            "entrepreneurship_id": request_data.entrepreneurship_id,
            "tags": request_data.tags or [],
            "metadata": {
                "source": "ocr",
                "ocr_confidence": ocr_data.amount_confidence,
                "vendor": ocr_data.vendor,
                "extracted_text": ocr_data.extracted_text[:500],  # Limitar tamaño
            },
            "sync_status": "synced",
            "created_by": user_id,
        }

        transaction = await self.transaction_repo.create(transaction_data)

        # Cargar con categoría para la respuesta
        transaction_with_category = await self.transaction_repo.get_by_id_with_category(
            transaction.id, user_id
        )

        # Crear respuesta con detalles de OCR
        response = OcrTransactionResponse.model_validate(transaction_with_category)
        response.ocr_details = ocr_data

        return response

    def _get_min_confidence(self) -> float:
        """Obtiene el umbral mínimo de confianza desde config"""
        from app.config import settings

        return settings.OCR_MIN_CONFIDENCE

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
            transaction_type = data.get(
                "transaction_type", transaction.transaction_type
            )
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
        updated_transaction = await self.transaction_repo.update(transaction_id, data)

        # Cargar con categoría
        transaction_with_category = await self.transaction_repo.get_by_id_with_category(
            updated_transaction.id, user_id
        )

        return TransactionResponse.model_validate(transaction_with_category)

    async def delete_transaction(self, transaction_id: UUID, user_id: UUID) -> None:
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
