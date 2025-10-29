"""
Schemas comunes reutilizables.
"""

from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field

# Generic type for paginated responses
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parámetros de paginación"""

    page: int = Field(default=1, ge=1, description="Número de página")
    limit: int = Field(default=20, ge=1, le=100, description="Registros por página")

    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.limit


class PaginationInfo(BaseModel):
    """Información de paginación en respuestas"""

    page: int = Field(description="Página actual")
    limit: int = Field(description="Registros por página")
    total: int = Field(description="Total de registros")
    total_pages: int = Field(description="Total de páginas")

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationInfo":
        """Factory method para crear PaginationInfo"""
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(page=page, limit=limit, total=total, total_pages=total_pages)


class ErrorDetail(BaseModel):
    """Detalle de error"""

    field: str = Field(description="Campo con error")
    constraint: str = Field(description="Restricción violada")
    message: str = Field(description="Mensaje de error")


class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""

    code: str = Field(description="Código de error")
    message: str = Field(description="Mensaje de error legible")
    details: dict = Field(default_factory=dict, description="Detalles adicionales")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Respuesta de éxito genérica"""

    message: str = Field(description="Mensaje de éxito")
    data: dict = Field(default_factory=dict)
