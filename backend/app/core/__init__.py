"""
Módulo core con utilidades centrales de la aplicación.
"""

from app.core.exceptions import (
                                 CajaClaraException,
                                 DatabaseError,
                                 ForbiddenError,
                                 NotFoundError,
                                 OcrProcessingError,
                                 UnauthorizedError,
                                 ValidationError,
)

__all__ = [
    "CajaClaraException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "OcrProcessingError",
    "DatabaseError",
]