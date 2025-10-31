"""
Endpoints para gestión de transacciones.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_default_user
from app.core.exceptions import ValidationError
from app.db.database import get_db
from app.models.user import User
from app.repositories.bank_account import BankAccountRepository
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import (
    CreateManualTransactionRequest,
    CreateOcrTransactionRequest,
    OcrDetailsResponse,
    OcrTransactionResponse,
    TransactionFilters,
    TransactionListResponse,
    TransactionResponse,
    UpdateTransactionRequest,
)
from app.services.ocr_service import OCRService
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
    bank_account_repo = BankAccountRepository(db)

    # Inicializar servicio
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Crear transacción
    return await transaction_service.create_manual_transaction(
        user_id=UUID(str(current_user.id)), data=data
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
    bank_account_repo = BankAccountRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Listar transacciones
    result = await transaction_service.list_transactions(
        user_id=UUID(str(current_user.id)), filters=filters, page=page, limit=limit
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
    bank_account_repo = BankAccountRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Obtener transacción
    return await transaction_service.get_transaction(
        transaction_id=transaction_id, user_id=UUID(str(current_user.id))
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
    bank_account_repo = BankAccountRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Actualizar transacción
    return await transaction_service.update_transaction(
        transaction_id=transaction_id,
        user_id=UUID(str(current_user.id)),
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
    bank_account_repo = BankAccountRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Eliminar transacción
    await transaction_service.delete_transaction(
        transaction_id=transaction_id, user_id=UUID(str(current_user.id))
    )


@router.post(
    "/ocr",
    response_model=OcrTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar transacción por OCR (foto)",
    description="Captura una foto de recibo y extrae monto, fecha y categoría sugerida automáticamente",
)
async def create_ocr_transaction(
    receipt_image: UploadFile = File(..., description="Foto del recibo (JPG, PNG, máx. 10 MB)"),
    transaction_type: str = Form(..., regex="^(income|expense)$"),
    classification: str = Form(..., regex="^(personal|business)$"),
    description: str = Form(None, max_length=500),
    tags: str = Form(None),
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> OcrTransactionResponse:
    """
    Crea una transacción usando OCR para extraer datos de una imagen.

    Args:
        receipt_image: Archivo de imagen del recibo
        transaction_type: Tipo de transacción (income/expense)
        classification: Clasificación (personal/business)
        description: Descripción opcional
        tags: Etiquetas opcionales (separadas por comas)
        current_user: Usuario actual
        db: Sesión de base de datos

    Returns:
        Transacción creada con detalles del procesamiento OCR

    Raises:
        ValidationError: Si la imagen es inválida o no se pueden extraer datos
        OcrProcessingError: Si hay error en el procesamiento OCR
    """
    # Validar archivo
    if receipt_image.content_type and not receipt_image.content_type.startswith('image/'):
        raise ValidationError(
            code="INVALID_FILE_TYPE",
            message="El archivo debe ser una imagen (JPG, PNG, WebP)"
        )
    
    if receipt_image.size and receipt_image.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError(
            code="FILE_TOO_LARGE",
            message="La imagen no puede superar los 10 MB"
        )

    # Inicializar servicios
    transaction_repo = TransactionRepository(db)
    category_repo = CategoryRepository(db)
    bank_account_repo = BankAccountRepository(db)
    transaction_service = TransactionService(
        transaction_repo=transaction_repo,
        category_repo=category_repo,
        bank_account_repo=bank_account_repo,
    )

    # Procesar imagen con OCR
    async with OCRService() as ocr_service:
        image_data = await receipt_image.read()
        ocr_result = await ocr_service.process_receipt_image(
            image_data=image_data,
            transaction_type=transaction_type,
            classification=classification
        )

    # Preparar datos para la transacción
    parsed_data = ocr_result["parsed_data"]
    
    # Buscar categoría sugerida si existe
    category_id: Optional[str] = None
    if parsed_data.get("category_suggested"):
        # Buscar categoría por nombre o ID
        categories = await category_repo.list_by_type(
            transaction_type=transaction_type
        )
        for cat in categories:
            if cat.name.lower() == parsed_data["category_suggested"].lower():
                category_id = str(cat.id)
                break
    
    # Si no se encontró categoría, usar una por defecto según el tipo
    if not category_id:
        if transaction_type == "expense":
            category_id = "cat-other-expense"  # Categoría por defecto para gastos
        else:
            category_id = "cat-other-income"   # Categoría por defecto para ingresos

    # Crear transacción con datos extraídos
    transaction_data = {
        "amount": parsed_data.get("amount"),
        "currency": "COP",
        "category_id": category_id,
        "description": description or parsed_data.get("vendor"),
        "transaction_type": transaction_type,
        "classification": classification,
        "transaction_date": (
            datetime.fromisoformat(parsed_data["transaction_date"])
            if parsed_data.get("transaction_date")
            else datetime.now()
        ),
        "tags": tags.split(',') if tags else None,
        "metadata": {
            "source": "ocr",
            "ocr_confidence": parsed_data.get("confidence", 0.0),
            "extracted_text": ocr_result["extracted_text"],
            "vendor_detected": parsed_data.get("vendor"),
            "amount_confidence": parsed_data.get("amount_confidence", 0.0),
            "date_confidence": parsed_data.get("date_confidence", 0.0),
            "category_confidence": parsed_data.get("category_confidence", 0.0)
        }
    }

    # Crear transacción
    transaction = await transaction_service.create_manual_transaction(
        user_id=UUID(str(current_user.id)),
        data=CreateManualTransactionRequest(**transaction_data)
    )

    # Construir respuesta con detalles OCR
    ocr_details = OcrDetailsResponse(
        extracted_text=ocr_result["extracted_text"],
        amount_extracted=parsed_data.get("amount"),
        amount_confidence=parsed_data.get("amount_confidence", 0.0),
        fecha_extracted=parsed_data.get("transaction_date"),
        fecha_confidence=parsed_data.get("date_confidence", 0.0),
        category_suggested=parsed_data.get("category_suggested"),
        category_confidence=parsed_data.get("category_confidence", 0.0),
        vendor_detected=parsed_data.get("vendor"),
        vendor_confidence=parsed_data.get("vendor_confidence", 0.0)
    )

    # Crear respuesta combinando transacción y detalles OCR
    response_data = transaction.dict()
    response_data["ocr_details"] = ocr_details.dict()
    
    return OcrTransactionResponse(**response_data)
    
    return OcrTransactionResponse(**response_data)
