"""
Schemas para transacciones.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse
from app.schemas.common import PaginationInfo


class TransactionBase(BaseModel):
    """Base schema para transacción"""

    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="COP", pattern="^(COP|USD|EUR)$")
    description: Optional[str] = Field(None, max_length=500)
    transaction_type: str = Field(pattern="^(income|expense)$")
    classification: str = Field(pattern="^(personal|business)$")
    transaction_date: datetime
    tags: Optional[List[str]] = None


class CreateManualTransactionRequest(TransactionBase):
    """Schema para crear transacción manual"""

    category_id: str = Field(max_length=50)
    entrepreneurship_id: Optional[UUID] = None


class UpdateTransactionRequest(BaseModel):
    """Schema para actualizar transacción"""

    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: Optional[datetime] = None
    classification: Optional[str] = Field(None, pattern="^(personal|business)$")
    tags: Optional[List[str]] = None
    entrepreneurship_id: Optional[UUID] = None


class TransactionMetadata(BaseModel):
    """Metadata de transacción"""

    source: str = Field(pattern="^(manual|ocr|api_import)$")
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class TransactionResponse(BaseModel):
    """Schema de respuesta de transacción"""

    id: UUID
    user_id: UUID
    entrepreneurship_id: Optional[UUID]
    amount: Decimal
    currency: str
    category: Optional[CategoryResponse]
    description: Optional[str]
    transaction_type: str
    classification: str
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
    sync_status: str
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = Field(None, alias="extra_data")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionFilters(BaseModel):
    """Filtros para listar transacciones"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_type: Optional[str] = Field(None, pattern="^(income|expense)$")
    classification: Optional[str] = Field(None, pattern="^(personal|business)$")
    category_id: Optional[str] = None
    entrepreneurship_id: Optional[UUID] = None


class ClassificationSummary(BaseModel):
    """Resumen por clasificación"""

    income: Decimal = Decimal("0.00")
    expense: Decimal = Decimal("0.00")


class TransactionSummary(BaseModel):
    """Resumen de transacciones"""

    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_balance: Decimal = Decimal("0.00")
    by_classification: Dict[str, ClassificationSummary] = Field(
        default_factory=lambda: {
            "personal": ClassificationSummary(),
            "business": ClassificationSummary(),
        }
    )


class TransactionListResponse(BaseModel):
    """Lista paginada de transacciones"""

    transactions: List[TransactionResponse]
    pagination: PaginationInfo
    summary: TransactionSummary


class CreateOcrTransactionRequest(BaseModel):
    """Schema para crear transacción desde OCR"""

    transaction_type: str = Field(pattern="^(income|expense)$")
    classification: str = Field(pattern="^(personal|business)$")
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    entrepreneurship_id: Optional[UUID] = None


class OcrExtractedData(BaseModel):
    """Datos extraídos del OCR"""

    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    amount_confidence: float = Field(ge=0.0, le=1.0)
    date: Optional[datetime] = None
    date_confidence: float = Field(ge=0.0, le=1.0)
    vendor: Optional[str] = Field(None, max_length=200)
    vendor_confidence: float = Field(ge=0.0, le=1.0)
    category_suggested: Optional[str] = Field(None, max_length=50)
    category_confidence: float = Field(ge=0.0, le=1.0)
    extracted_text: str = Field(max_length=5000)


class OcrTransactionResponse(TransactionResponse):
    """Schema de respuesta para transacción OCR con detalles adicionales"""

    ocr_details: Optional[OcrExtractedData] = None
