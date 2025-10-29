"""
Endpoints para procesamiento OCR
"""

import logging
from uuid import UUID

from app.api.deps import get_default_user
from app.core.exceptions import OcrProcessingError
from app.db.database import get_db
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import TransactionResponse
from app.services.category import CategoryService
from app.services.ocr_service import OCRService
from app.services.transaction import TransactionService
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Procesar recibo con OCR",
    description="Extrae información de una imagen de recibo y crea una transacción",
)
async def process_receipt_ocr(
    receipt_image: UploadFile = File(..., description="Imagen del recibo"),
    transaction_type: str = Form(..., description="Tipo de transacción"),
    classification: str = Form(..., description="Clasificación"),
    description: str = Form(None, description="Descripción adicional"),
    tags: str = Form(None, description="Etiquetas separadas por coma"),
    current_user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """
    Procesa imagen de recibo con OCR y crea transacción
    
    Args:
        receipt_image: Archivo de imagen del recibo
        transaction_type: Tipo de transacción (income/expense)
        classification: Clasificación (personal/business)
        description: Descripción adicional
        tags: Etiquetas separadas por coma
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        Transacción creada con datos OCR
        
    Raises:
        OcrProcessingError: Si hay error en el procesamiento
    """
    try:
        # Validar tipo de transacción
        if transaction_type not in ["income", "expense"]:
            raise OcrProcessingError(
                code="INVALID_TRANSACTION_TYPE",
                message="Tipo de transacción inválido. Debe ser 'income' o 'expense'"
            )
        
        # Validar clasificación
        if classification not in ["personal", "business"]:
            raise OcrProcessingError(
                code="INVALID_CLASSIFICATION",
                message="Clasificación inválida. Debe ser 'personal' o 'business'"
            )
        
        # Validar tipo de archivo
        if not receipt_image or not receipt_image.content_type or not receipt_image.content_type.startswith("image/"):
            raise OcrProcessingError(
                code="INVALID_FILE_TYPE",
                message="El archivo debe ser una imagen (JPG, PNG, WebP)"
            )
        
        # Validar tamaño (10MB máximo)
        max_size = 10 * 1024 * 1024  # 10MB
        if receipt_image and receipt_image.size and receipt_image.size > max_size:
            raise OcrProcessingError(
                code="FILE_TOO_LARGE",
                message=f"El archivo es demasiado grande. Máximo permitido: {max_size // (1024*1024)}MB"
            )
        
        # Leer imagen
        image_data = await receipt_image.read()
        
        # Procesar con OCR
        async with OCRService() as ocr_service:
            ocr_result = await ocr_service.process_receipt_image(
                image_data=image_data,
                transaction_type=transaction_type,
                classification=classification
            )
        
        # Extraer datos procesados
        parsed_data = ocr_result["parsed_data"]
        confidence = ocr_result["confidence"]
        
        # Validar confianza mínima
        if confidence < 0.3:
            raise OcrProcessingError(
                code="LOW_CONFIDENCE",
                message="La confianza del OCR es muy baja. Intenta con una imagen más clara."
            )
        
        # Inicializar servicios
        transaction_repo = TransactionRepository(db)
        category_repo = CategoryRepository(db)
        category_service = CategoryService(category_repo)
        transaction_service = TransactionService(
            transaction_repo=transaction_repo, 
            category_repo=category_repo
        )
        
        # Determinar categoría
        category_id = None
        if parsed_data.get("category_suggested"):
            # Buscar categoría sugerida
            categories = await category_service.get_categories(transaction_type=transaction_type)
            category = next(
                (cat for cat in categories if cat.name.lower() == parsed_data["category_suggested"].lower()),
                None
            )
            if category:
                category_id = category.id
        
        # Extraer datos estructurados si están disponibles
        structured_data = parsed_data.get("structured_data", {})
        merchant_data = structured_data.get("merchant", {})
        transaction_data_ocr = structured_data.get("transaction", {})
        
        # Preparar datos de transacción con prioridad a datos estructurados
        transaction_data = {
            "amount": parsed_data.get("amount") or transaction_data_ocr.get("total"),
            "currency": transaction_data_ocr.get("currency", "COP"),
            "category_id": category_id,
            "description": description or parsed_data.get("vendor") or merchant_data.get("name"),
            "transaction_type": transaction_type,
            "classification": classification,
            "transaction_date": parsed_data.get("transaction_date") or transaction_data_ocr.get("date"),
            "tags": [tag.strip() for tag in tags.split(",")] if tags else None,
        }
        
        # Crear transacción
        from app.schemas.transaction import CreateManualTransactionRequest
        transaction_request = CreateManualTransactionRequest(**transaction_data)
        transaction = await transaction_service.create_manual_transaction(
            user_id=current_user.id,
            data=transaction_request
        )
        
        # Agregar metadatos OCR enriquecidos
        transaction.metadata = {
            "source": "ocr",
            "ocr_confidence": confidence,
            "extracted_text": ocr_result["extracted_text"],
            "vendor_detected": parsed_data.get("vendor") or merchant_data.get("name"),
            "vendor_address": merchant_data.get("address"),
            "vendor_phone": merchant_data.get("phone"),
            "vendor_nit": merchant_data.get("nit"),
            "amount_confidence": parsed_data.get("amount_confidence"),
            "date_confidence": parsed_data.get("date_confidence"),
            "category_confidence": parsed_data.get("category_confidence"),
            "vendor_confidence": parsed_data.get("vendor_confidence"),
            "invoice_number": transaction_data_ocr.get("invoice_number"),
            "subtotal": transaction_data_ocr.get("subtotal"),
            "tax": transaction_data_ocr.get("tax"),
            "payment_method": structured_data.get("payment_method"),
            "items": structured_data.get("items", []),
            "structured_confidence": structured_data.get("confidence", {}),
        }
        
        # Guardar metadatos
        await transaction_repo.update(transaction.id, {"metadata": transaction.metadata})
        
        logger.info(
            f"OCR transaction created: user={current_user.id}, "
            f"amount={transaction.amount}, confidence={confidence:.2f}"
        )
        
        return TransactionResponse.model_validate(transaction)
        
    except OcrProcessingError:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise OcrProcessingError(
            code="OCR_PROCESSING_ERROR",
            message=f"Error procesando imagen: {str(e)}"
        )


@router.post(
    "/analyze",
    summary="Analizar imagen con OCR",
    description="Extrae información de una imagen sin crear transacción",
)
async def analyze_image_ocr(
    receipt_image: UploadFile = File(..., description="Imagen a analizar"),
    transaction_type: str = Form("expense", description="Tipo de transacción esperado"),
    classification: str = Form("personal", description="Clasificación esperada"),
    current_user: User = Depends(get_default_user),
) -> dict:
    """
    Analiza imagen con OCR sin crear transacción
    
    Args:
        receipt_image: Archivo de imagen a analizar
        transaction_type: Tipo de transacción esperado
        classification: Clasificación esperada
        current_user: Usuario actual
        
    Returns:
        Resultados del análisis OCR
        
    Raises:
        OcrProcessingError: Si hay error en el procesamiento
    """
    try:
        # Validaciones básicas
        if not receipt_image or not receipt_image.content_type or not receipt_image.content_type.startswith("image/"):
            raise OcrProcessingError(
                code="INVALID_FILE_TYPE",
                message="El archivo debe ser una imagen"
            )
        
        # Leer imagen
        image_data = await receipt_image.read()
        
        # Procesar con OCR
        async with OCRService() as ocr_service:
            ocr_result = await ocr_service.process_receipt_image(
                image_data=image_data,
                transaction_type=transaction_type,
                classification=classification
            )
        
        return {
            "success": True,
            "extracted_text": ocr_result["extracted_text"],
            "parsed_data": ocr_result["parsed_data"],
            "confidence": ocr_result["confidence"],
            "message": "Análisis completado exitosamente"
        }
        
    except OcrProcessingError:
        raise
    except Exception as e:
        logger.error(f"Error analyzing OCR: {str(e)}")
        raise OcrProcessingError(
            code="OCR_ANALYSIS_ERROR",
            message=f"Error analizando imagen: {str(e)}"
        )