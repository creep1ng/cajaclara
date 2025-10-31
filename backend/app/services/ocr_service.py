"""
Servicio OpenAI Vision para OCR
Procesa imágenes de recibos y extrae información de transacciones
"""

import base64
import io
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional, Tuple

import httpx
from app.config import settings
from app.core.exceptions import OcrProcessingError
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """Servicio para procesamiento OCR con OpenAI Vision"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.max_image_size = settings.OCR_MAX_IMAGE_SIZE_MB * 1024 * 1024

    async def process_receipt_image(
        self,
        image_data: bytes,
        transaction_type: str = "expense",
        classification: str = "personal"
    ) -> Dict:
        """
        Procesa imagen de recibo y extrae información de transacción

        Args:
            image_data: Bytes de la imagen
            transaction_type: Tipo de transacción esperado
            classification: Clasificación (personal/business)

        Returns:
            Dict con información extraída

        Raises:
            OcrProcessingError: Si hay error en el procesamiento
        """
        try:
            # Validar imagen
            await self._validate_image(image_data)

            # Preparar imagen para OpenAI
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Extraer texto con OpenAI Vision
            extracted_text = await self._extract_text_with_openai(base64_image)

            # Procesar texto extraído
            parsed_data = await self._parse_receipt_text(
                extracted_text,
                transaction_type,
                classification
            )

            return {
                "extracted_text": extracted_text,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error(f"Error procesando imagen OCR: {str(e)}")
            raise OcrProcessingError(
                code="OCR_PROCESSING_ERROR", message=f"Error procesando imagen: {str(e)}")

    async def _validate_image(self, image_data: bytes) -> None:
        """Valida que la imagen cumpla con los requisitos"""
        if len(image_data) > self.max_image_size:
            raise OcrProcessingError(
                code="IMAGE_SIZE_ERROR",
                message=f"Imagen demasiado grande. Máximo permitido: {settings.OCR_MAX_IMAGE_SIZE_MB}MB"
            )

        try:
            # Validar que sea una imagen válida
            with Image.open(io.BytesIO(image_data)) as img:
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Optimizar imagen si es muy grande
                if img.size[0] > 2000 or img.size[1] > 2000:
                    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)

        except Exception as e:
            raise OcrProcessingError(
                code="INVALID_IMAGE_ERROR", message=f"Imagen inválida o corrupta: {str(e)}")

    async def _extract_text_with_openai(self, base64_image: str) -> str:
        """Extrae texto de la imagen usando OpenAI Vision API"""

        prompt = """
        Analiza esta imagen de un recibo o factura y extrae la información en formato JSON estructurado.
        
        Devuelve ÚNICAMENTE un objeto JSON con las siguientes claves:
        {
            "extracted_text": "texto completo extraído",
            "merchant": {
                "name": "nombre del comerciante",
                "address": "dirección si es visible",
                "phone": "teléfono si es visible",
                "nit": "NIT si es visible"
            },
            "transaction": {
                "total": 12345.67,
                "subtotal": 11000.00,
                "tax": 1345.67,
                "currency": "COP",
                "date": "2025-10-27",
                "time": "14:30",
                "invoice_number": "001234"
            },
            "items": [
                {
                    "description": "descripción del producto",
                    "quantity": 1,
                    "unit_price": 25000.00,
                    "total": 25000.00
                }
            ],
            "payment_method": "efectivo/tarjeta/transferencia",
            "confidence": {
                "overall": 0.85,
                "merchant": 0.9,
                "amount": 0.95,
                "date": 0.8,
                "items": 0.7
            }
        }
        
        Si no puedes extraer algún campo, usa null. Si hay múltiples montos, prioriza el total.
        Responde ÚNICAMENTE con el JSON, sin texto adicional.
        """

        try:
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
            )

            if response.status_code != 200:
                logger.error(
                    f"OpenAI API error: {response.status_code} - {response.text}")
                raise OcrProcessingError(
                    code="OCR_SERVICE_ERROR", message="Error en el servicio de OCR")

            result = response.json()
            extracted_text = result["choices"][0]["message"]["content"].strip()

            if not extracted_text:
                raise OcrProcessingError(
                    code="NO_TEXT_EXTRACTED", message="No se pudo extraer texto de la imagen")

            return extracted_text

        except httpx.RequestError as e:
            logger.error(f"Error llamando OpenAI API: {str(e)}")
            raise OcrProcessingError(
                code="OCR_CONNECTION_ERROR", message="Error de conexión con el servicio OCR")
        except Exception as e:
            logger.error(f"Error inesperado en OCR: {str(e)}")
            raise OcrProcessingError(
                code="OCR_UNKNOWN_ERROR", message=f"Error procesando OCR: {str(e)}")

    async def _parse_receipt_text(
        self,
        text: str,
        transaction_type: str,
        classification: str
    ) -> Dict:
        """
        Analiza el texto extraído y estructura la información

        Args:
            text: Texto extraído de la imagen (puede ser JSON estructurado o texto plano)
            transaction_type: Tipo de transacción esperado
            classification: Clasificación personal/business

        Returns:
            Dict con datos estructurados de la transacción
        """

        # Intentar parsear como JSON estructurado primero
        try:
            import json
            parsed_json = json.loads(text)

            if isinstance(parsed_json, dict):
                return self._parse_structured_json(parsed_json, transaction_type, classification)
        except (json.JSONDecodeError, ValueError):
            # Fallback a parsing de texto plano
            pass

        # Extraer monto
        amount, amount_confidence = self._extract_amount(text)

        # Extraer fecha
        date, date_confidence = self._extract_date(text)

        # Extraer vendedor
        vendor, vendor_confidence = self._extract_vendor(text)

        # Sugerir categoría basada en vendedor y contenido
        category, category_confidence = self._suggest_category(
            text, vendor, transaction_type
        )

        # Calcular confianza general
        overall_confidence = (
            amount_confidence * 0.4 +
            date_confidence * 0.3 +
            category_confidence * 0.2 +
            vendor_confidence * 0.1
        )

        return {
            "amount": amount,
            "amount_confidence": amount_confidence,
            "transaction_date": date,
            "date_confidence": date_confidence,
            "vendor": vendor,
            "vendor_confidence": vendor_confidence,
            "category_suggested": category,
            "category_confidence": category_confidence,
            "confidence": overall_confidence,
            "transaction_type": transaction_type,
            "classification": classification
        }

    def _parse_structured_json(self, json_data: Dict, transaction_type: str, classification: str) -> Dict:
        """
        Parsea datos JSON estructurados de OpenAI Vision

        Args:
            json_data: Datos estructurados del OCR
            transaction_type: Tipo de transacción esperado
            classification: Clasificación personal/business

        Returns:
            Dict con datos estructurados de la transacción
        """

        # Extraer datos del JSON estructurado
        transaction = json_data.get("transaction", {})
        merchant = json_data.get("merchant", {})
        confidence = json_data.get("confidence", {})

        # Extraer monto con validación
        amount = transaction.get("total")
        if amount is None:
            # Fallback a otros montos
            amount = transaction.get("subtotal")

        amount_confidence = confidence.get("amount", 0.8)

        # Extraer fecha
        date = transaction.get("date")
        date_confidence = confidence.get("date", 0.7)

        # Extraer vendedor
        vendor = merchant.get("name")
        vendor_confidence = confidence.get("merchant", 0.8)

        # Sugerir categoría basada en vendedor y contenido
        extracted_text = json_data.get("extracted_text", "")
        category, category_confidence = self._suggest_category(
            extracted_text, vendor, transaction_type
        )

        # Usar confianza del JSON si está disponible
        overall_confidence = confidence.get("overall", 0.8)
        if overall_confidence == 0:
            # Calcular confianza general si no está en el JSON
            overall_confidence = (
                amount_confidence * 0.4 +
                date_confidence * 0.3 +
                category_confidence * 0.2 +
                vendor_confidence * 0.1
            )

        # Intent: Convertir el monto extraído a Decimal y registrar el valor crudo y procesado.
        # Esto permite detectar si el valor ya viene dividido (ej. 383.93) o si la división ocurre
        # en otra parte del flujo (frontend / serialización).
        processed_amount = None
        raw_amount = amount
        try:
            if raw_amount is not None:
                # Normalizar tipos: si viene como str/float/int, convertir de forma segura.
                # Si viene como número con separadores (ej. "38,393.00") se intentará limpiar.
                if isinstance(raw_amount, str):
                    amt = raw_amount.replace(',', '').strip()
                    processed_amount = Decimal(amt)
                else:
                    # Usar str() para evitar pérdida al pasar float directamente a Decimal
                    processed_amount = Decimal(str(raw_amount))
        except (InvalidOperation, ValueError) as e:
            logger.error(
                "OCRService:_parse_structured_json - error convirtiendo 'total' a Decimal "
                f"(raw_amount={raw_amount!r}, type={type(raw_amount)}): {e}"
            )
            processed_amount = None

        logger.debug(
            "OCRService:_parse_structured_json - monto crudo -> procesado | "
            f"raw_amount={raw_amount!r} processed_amount={processed_amount!r} "
            f"amount_confidence={amount_confidence!r} overall_confidence={overall_confidence!r}"
        )

        return {
            "amount": processed_amount,
            "amount_confidence": amount_confidence,
            "transaction_date": date,
            "date_confidence": date_confidence,
            "vendor": vendor,
            "vendor_confidence": vendor_confidence,
            "category_suggested": category,
            "category_confidence": category_confidence,
            "confidence": overall_confidence,
            "transaction_type": transaction_type,
            "classification": classification,
            "structured_data": {
                "merchant": merchant,
                "items": json_data.get("items", []),
                "payment_method": json_data.get("payment_method"),
                "invoice_number": transaction.get("invoice_number"),
                "subtotal": transaction.get("subtotal"),
                "tax": transaction.get("tax"),
                "currency": transaction.get("currency", "COP")
            }
        }

    def _extract_amount(self, text: str) -> Tuple[Optional[Decimal], float]:
        """Extrae monto del texto"""

        # Patrones comunes para montos en Colombia
        patterns = [
            r'\$\s*([\d,]+\.?\d*)',  # $ 45.000
            r'([\d,]+\.?\d*)\s*$',   # 45.000 $
            r'Total[:\s]*\$?\s*([\d,]+\.?\d*)',  # Total: $45.000
            r'VALOR[:\s]*\$?\s*([\d,]+\.?\d*)',  # VALOR $45.000
            r'Importe[:\s]*\$?\s*([\d,]+\.?\d*)',  # Importe $45.000
        ]

        best_amount = None
        best_confidence = 0.0

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Limpiar y convertir monto
                    raw = match.strip()
                    # Caso 1: contiene punto decimal con 1-2 decimales -> '.' es separador decimal
                    if '.' in raw and re.match(r'.*\.\d{1,2}$', raw):
                        # Eliminar separadores de miles (comas) y conservar el punto decimal
                        amount_str = raw.replace(',', '')
                    # Caso 2: contiene coma decimal (ej. '123,45') y no contiene punto -> tratar la coma como separador decimal
                    elif ',' in raw and re.match(r'.*,\d{1,2}$', raw) and '.' not in raw:
                        amount_str = raw.replace('.', '').replace(',', '.')
                    else:
                        # Sin parte decimal explícita: eliminar separadores de miles (puntos/comas)
                        # y tratar el número como valor entero (ej. "38,393" -> "38393" -> 38393)
                        amount_str = raw.replace(',', '').replace('.', '')

                    amount = Decimal(amount_str)

                    # Validar rango razonable
                    if 100 <= amount <= 10000000:  # $1 a $10M
                        confidence = 0.8 if "total" in pattern.lower() else 0.6
                        if best_amount is None or amount > best_amount:
                            best_amount = amount
                            best_confidence = confidence

                except (ValueError, InvalidOperation):
                    continue

        return best_amount, best_confidence

    def _extract_date(self, text: str) -> Tuple[Optional[str], float]:
        """Extrae fecha del texto"""

        # Patrones de fecha comunes en Colombia
        patterns = [
            r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',  # 27/10/2025
            r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',  # 2025-10-27
            # Fecha: 27/10/2025
            r'Fecha[:\s]*(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',
        ]

        best_date = None
        best_confidence = 0.0

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 3:
                        day, month, year = match
                        if len(year) == 2:
                            year = f"20{year}"

                        # Validar fecha
                        if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            confidence = 0.8 if "fecha" in pattern.lower() else 0.6

                            if best_date is None or confidence > best_confidence:
                                best_date = date_str
                                best_confidence = confidence

                except (ValueError, IndexError):
                    continue

        return best_date, best_confidence

    def _extract_vendor(self, text: str) -> Tuple[Optional[str], float]:
        """Extrae nombre del vendedor/comerciante"""

        # Buscar en las primeras líneas (usualmente el nombre del comercio)
        lines = text.split('\n')[:5]

        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                # Excluir líneas que parecen totales o fechas
                if not any(char.isdigit() for char in line) and '$' not in line:
                    return line, 0.7

        return None, 0.0

    def _suggest_category(
        self,
        text: str,
        vendor: Optional[str],
        transaction_type: str
    ) -> Tuple[Optional[str], float]:
        """Sugiere categoría basada en el contenido"""

        # Mapeo de palabras clave a categorías
        category_keywords = {
            "food": ["restaurante", "café", "comida", "alimentos", "restaurant", "cafe"],
            "transport": ["taxi", "uber", "transporte", "gasolina", "parking"],
            "shopping": ["tienda", "compra", "mall", "ropa", "zapatos"],
            "health": ["farmacia", "médico", "salud", "medicinas"],
            "entertainment": ["cine", "teatro", "concierto", "entretenimiento"],
            "utilities": ["servicios", "luz", "agua", "gas", "teléfono"],
            "education": ["libros", "curso", "educación", "colegio"],
        }

        text_lower = text.lower()
        vendor_lower = vendor.lower() if vendor else ""

        best_category = None
        best_score = 0.0

        for category, keywords in category_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 0.3
                if keyword in vendor_lower:
                    score += 0.5

            if score > best_score:
                best_score = score
                best_category = category

        confidence = min(best_score, 0.9)  # Máximo 90% de confianza

        return best_category, confidence

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
