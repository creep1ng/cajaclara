"""
Servicio de OCR usando OpenAI Vision API para extraer datos de facturas.
"""

import base64
import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional

from openai import AsyncOpenAI
from PIL import Image
from pydantic import BaseModel, Field

from app.config import settings
from app.core.exceptions import ValidationError
from app.schemas.transaction import OcrExtractedData

logger = logging.getLogger(__name__)


class OpenAIVisionResponse(BaseModel):
    """Respuesta estructurada de OpenAI Vision API"""

    amount: Optional[float] = Field(None, description="Monto de la transacción")
    amount_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confianza en el monto detectado"
    )
    date_str: Optional[str] = Field(
        None, description="Fecha en formato ISO 8601 o legible"
    )
    date_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confianza en la fecha detectada"
    )
    vendor: Optional[str] = Field(None, description="Nombre del comerciante")
    vendor_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confianza en el vendedor"
    )
    category_suggested: Optional[str] = Field(
        None, description="Categoría sugerida (id de categoría)"
    )
    category_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confianza en la categoría"
    )
    extracted_text: str = Field(
        default="", description="Texto completo extraído del recibo"
    )


class OCRService:
    """Servicio para procesar imágenes de facturas con OCR"""

    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT
        )
        self.model = settings.OPENAI_MODEL
        self.min_confidence = settings.OCR_MIN_CONFIDENCE

    async def process_receipt(
        self, image_data: bytes, content_type: str
    ) -> OcrExtractedData:
        """
        Procesa una imagen de recibo y extrae información estructurada.

        Args:
            image_data: Datos binarios de la imagen
            content_type: Tipo MIME de la imagen

        Returns:
            Datos extraídos con niveles de confianza

        Raises:
            ValidationError: Si la imagen es inválida o el OCR falla
        """
        # Validar imagen
        self._validate_image(image_data, content_type)

        # Procesar con OpenAI Vision
        try:
            vision_response = await self._call_openai_vision(image_data, content_type)
            logger.info(
                f"OCR completado - Monto: {vision_response.amount}, "
                f"Confianza: {vision_response.amount_confidence}"
            )
        except Exception as e:
            logger.error(f"Error en OpenAI Vision API: {str(e)}")
            raise ValidationError(
                code="OCR_FAILED",
                message="No se pudo procesar la imagen. Por favor, intente con otra foto o ingrese los datos manualmente.",
                details={"error": str(e)},
            )

        # Convertir a OcrExtractedData
        return self._convert_to_extracted_data(vision_response)

    def _validate_image(self, image_data: bytes, content_type: str) -> None:
        """
        Valida el formato y tamaño de la imagen.

        Args:
            image_data: Datos binarios de la imagen
            content_type: Tipo MIME

        Raises:
            ValidationError: Si la imagen no es válida
        """
        # Validar tipo de contenido
        if content_type not in settings.OCR_ALLOWED_FORMATS:
            raise ValidationError(
                code="INVALID_IMAGE_FORMAT",
                message=f"Formato de imagen no permitido. Use: {', '.join(settings.OCR_ALLOWED_FORMATS)}",
                details={"content_type": content_type},
            )

        # Validar tamaño
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > settings.OCR_MAX_IMAGE_SIZE_MB:
            raise ValidationError(
                code="IMAGE_TOO_LARGE",
                message=f"La imagen es demasiado grande. Máximo {settings.OCR_MAX_IMAGE_SIZE_MB} MB",
                details={"size_mb": round(size_mb, 2)},
            )

        # Validar que sea una imagen válida
        try:
            img = Image.open(BytesIO(image_data))
            img.verify()
        except Exception as e:
            raise ValidationError(
                code="INVALID_IMAGE",
                message="La imagen está corrupta o no es válida",
                details={"error": str(e)},
            )

    async def _call_openai_vision(
        self, image_data: bytes, content_type: str
    ) -> OpenAIVisionResponse:
        """
        Llama a OpenAI Vision API con salida estructurada.

        Args:
            image_data: Datos binarios de la imagen
            content_type: Tipo MIME

        Returns:
            Respuesta estructurada de OpenAI
        """
        # Codificar imagen en base64
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_url = f"data:{content_type};base64,{base64_image}"

        # Construir prompt para extracción estructurada
        prompt = """Analiza esta imagen de recibo o factura y extrae la siguiente información:

1. **Monto total** (amount): El valor total de la transacción. Solo el número, sin símbolos de moneda.
2. **Confianza del monto** (amount_confidence): Qué tan seguro estás del monto (0.0 a 1.0).
3. **Fecha** (date_str): La fecha de la transacción en formato ISO 8601 (YYYY-MM-DD) si es posible.
4. **Confianza de la fecha** (date_confidence): Qué tan seguro estás de la fecha (0.0 a 1.0).
5. **Vendedor** (vendor): El nombre del comerciante o negocio.
6. **Confianza del vendedor** (vendor_confidence): Qué tan seguro estás del nombre (0.0 a 1.0).
7. **Categoría sugerida** (category_suggested): Sugiere una de estas categorías basándote en el tipo de negocio:
   - "cat-food" (supermercados, alimentos)
   - "cat-cafe" (restaurantes, cafeterías, comida fuera)
   - "cat-transport" (taxis, uber, gasolina, parqueaderos)
   - "cat-utilities" (luz, agua, internet, telefonía)
   - "cat-rent" (alquiler, arrendamiento)
   - "cat-entertainment" (cine, eventos, recreación, streaming)
   - "cat-health" (médico, farmacia, hospital)
   - "cat-education" (colegios, cursos, libros)
   - "cat-shopping" (ropa, tecnología, compras personales)
   - "cat-salary" (para ingresos por salario)
   - "cat-freelance" (para ingresos por trabajos independientes)
   - "cat-sales" (para ingresos por ventas)
   - "cat-other-expense" (cualquier otro gasto)
   - "cat-other-income" (cualquier otro ingreso)
8. **Confianza de categoría** (category_confidence): Qué tan seguro estás de la categoría (0.0 a 1.0).
9. **Texto extraído** (extracted_text): Todo el texto visible en la imagen.

Si algún campo no está visible o no estás seguro, usa null para el valor y 0.0 para la confianza."""

        # Llamar a la API con structured outputs
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                response_format=OpenAIVisionResponse,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            # Parsear respuesta estructurada
            if response.choices[0].message.parsed:
                return response.choices[0].message.parsed
            else:
                raise ValueError("No se recibió respuesta estructurada de OpenAI")

        except Exception as e:
            logger.error(f"Error llamando a OpenAI Vision: {str(e)}")
            raise

    def _convert_to_extracted_data(
        self, vision_response: OpenAIVisionResponse
    ) -> OcrExtractedData:
        """
        Convierte la respuesta de OpenAI a OcrExtractedData.

        Args:
            vision_response: Respuesta de OpenAI Vision

        Returns:
            Datos extraídos formateados
        """
        # Convertir fecha
        transaction_date = None
        if vision_response.date_str:
            try:
                # Intentar parsear como ISO 8601
                transaction_date = datetime.fromisoformat(
                    vision_response.date_str.replace("Z", "+00:00")
                )
            except ValueError:
                # Intentar otros formatos comunes
                for fmt in [
                    "%Y-%m-%d",
                    "%d/%m/%Y",
                    "%m/%d/%Y",
                    "%d-%m-%Y",
                    "%Y/%m/%d",
                ]:
                    try:
                        transaction_date = datetime.strptime(
                            vision_response.date_str, fmt
                        )
                        break
                    except ValueError:
                        continue

        # Convertir monto a Decimal
        amount = None
        if vision_response.amount is not None:
            try:
                amount = Decimal(str(vision_response.amount)).quantize(Decimal("0.01"))
            except Exception as e:
                logger.warning(
                    f"No se pudo convertir monto {vision_response.amount}: {e}"
                )

        return OcrExtractedData(
            amount=amount,
            amount_confidence=vision_response.amount_confidence,
            date=transaction_date,
            date_confidence=vision_response.date_confidence,
            vendor=vision_response.vendor,
            vendor_confidence=vision_response.vendor_confidence,
            category_suggested=vision_response.category_suggested,
            category_confidence=vision_response.category_confidence,
            extracted_text=vision_response.extracted_text or "",
        )
