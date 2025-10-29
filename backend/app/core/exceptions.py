"""
Excepciones personalizadas para la aplicación.
"""

from typing import Any, Dict, Optional


class CajaClaraException(Exception):
    """Excepción base para todas las excepciones de la aplicación"""

    def __init__(
        self, code: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa la excepción.

        Args:
            code: Código de error único
            message: Mensaje de error legible
            details: Detalles adicionales del error
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CajaClaraException):
    """Error de validación de datos (422)"""

    pass


class NotFoundError(CajaClaraException):
    """Recurso no encontrado (404)"""

    pass


class UnauthorizedError(CajaClaraException):
    """Error de autenticación (401)"""

    pass


class ForbiddenError(CajaClaraException):
    """Error de autorización (403)"""

    pass


class OcrProcessingError(CajaClaraException):
    """Error en procesamiento OCR (422)"""

    pass


class DatabaseError(CajaClaraException):
    """Error de base de datos (500)"""

    pass
