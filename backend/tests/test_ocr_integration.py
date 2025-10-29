"""
Pruebas de integración para el servicio OCR
"""

import io
from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from app.services.ocr_service import OCRService
from fastapi.testclient import TestClient
from PIL import Image


class TestOCRIntegration:
    """Pruebas de integración para OCR"""

    @pytest.fixture
    def client(self):
        """Cliente de prueba FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def sample_image(self):
        """Imagen de prueba para OCR"""
        # Crear una imagen de prueba simple
        img = Image.new('RGB', (200, 100), color='white')
        
        # Agregar texto simple
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            
        draw.text((10, 10), "TOTAL: $45.000", fill='black', font=font)
        draw.text((10, 30), "RESTAURANTE EJEMPLO", fill='black', font=font)
        draw.text((10, 50), "27/10/2025", fill='black', font=font)
        
        # Convertir a bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes

    @pytest.fixture
    def ocr_service(self):
        """Instancia del servicio OCR"""
        return OCRService()

    @pytest.mark.asyncio
    async def test_process_receipt_image_success(self, ocr_service, sample_image):
        """Prueba procesamiento exitoso de imagen"""
        with patch('app.services.ocr_service.httpx.AsyncClient') as mock_client:
            # Mock de respuesta OpenAI
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "TOTAL: $45.000\nRESTAURANTE EJEMPLO\n27/10/2025"
                    }
                }]
            }
            mock_client.return_value.post.return_value = mock_response
            
            result = await ocr_service.process_receipt_image(
                sample_image,
                transaction_type="expense",
                classification="personal"
            )
            
            assert "extracted_text" in result
            assert "parsed_data" in result
            assert "confidence" in result
            assert result["confidence"] > 0

    @pytest.mark.asyncio
    async def test_process_receipt_image_invalid_size(self, ocr_service):
        """Prueba manejo de imagen demasiado grande"""
        # Crear imagen grande (simulando más de 10MB)
        large_image = b'x' * (11 * 1024 * 1024)  # 11MB
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.process_receipt_image(large_image)
        
        assert "demasiado grande" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_process_receipt_image_invalid_format(self, ocr_service):
        """Prueba manejo de formato inválido"""
        # Archivo que no es imagen
        invalid_file = b"esto no es una imagen"
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.process_receipt_image(invalid_file)
        
        assert "inválida" in str(exc_info.value).lower() or "corrupta" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_extract_amount_success(self, ocr_service):
        """Prueba extracción correcta de monto"""
        text = "TOTAL: $45.000\nSUBTOTAL: $40.000\nIVA: $5.000"
        amount, confidence = ocr_service._extract_amount(text)
        
        assert amount == 45000
        assert confidence >= 0.6

    @pytest.mark.asyncio
    async def test_extract_date_success(self, ocr_service):
        """Prueba extracción correcta de fecha"""
        text = "Fecha: 27/10/2025\nTOTAL: $45.000"
        date, confidence = ocr_service._extract_date(text)
        
        assert date == "2025-10-27"
        assert confidence >= 0.6

    @pytest.mark.asyncio
    async def test_extract_vendor_success(self, ocr_service):
        """Prueba extracción correcta de vendedor"""
        text = "RESTAURANTE EJEMPLO\nTOTAL: $45.000\nFecha: 27/10/2025"
        vendor, confidence = ocr_service._extract_vendor(text)
        
        assert vendor == "RESTAURANTE EJEMPLO"
        assert confidence >= 0.6

    @pytest.mark.asyncio
    async def test_suggest_category_success(self, ocr_service):
        """Prueba sugerencia correcta de categoría"""
        text = "RESTAURANTE EJEMPLO\nCOMIDA PARA LLEVAR\nTOTAL: $45.000"
        vendor = "RESTAURANTE EJEMPLO"
        
        category, confidence = ocr_service._suggest_category(text, vendor, "expense")
        
        assert category == "food"
        assert confidence >= 0.3

    def test_validate_image_success(self, ocr_service, sample_image):
        """Prueba validación exitosa de imagen"""
        # No debe lanzar excepción
        import asyncio
        asyncio.run(ocr_service._validate_image(sample_image))

    def test_validate_image_too_large(self, ocr_service):
        """Prueba validación de imagen demasiado grande"""
        large_image = b'x' * (11 * 1024 * 1024)  # 11MB
        
        with pytest.raises(Exception):
            import asyncio
            asyncio.run(ocr_service._validate_image(large_image))

    def test_validate_image_invalid_format(self, ocr_service):
        """Prueba validación de formato inválido"""
        invalid_image = b"esto no es una imagen"
        
        with pytest.raises(Exception):
            import asyncio
            asyncio.run(ocr_service._validate_image(invalid_image))

    @pytest.mark.asyncio
    async def test_parse_receipt_text_comprehensive(self, ocr_service):
        """Prueba parsing completo de texto de recibo"""
        text = """
        RESTAURANTE EJEMPLO
        Nit: 123.456.789-0
        Dirección: Calle 123 #45-67
        Tel: 3001234567
        
        FACTURA No: 001234
        Fecha: 27/10/2025
        Hora: 14:30
        
        DESCRIPCIÓN CANTIDAD VALOR
        Hamburguesa 1 $25.000
        Bebida 1 $10.000
        Propina 1 $5.000
        
        SUBTOTAL $40.000
        IVA (19%) $7.600
        TOTAL $47.600
        """
        
        result = await ocr_service._parse_receipt_text(
            text, 
            transaction_type="expense", 
            classification="personal"
        )
        
        assert "amount" in result
        assert "transaction_date" in result
        assert "vendor" in result
        assert "category_suggested" in result
        assert "confidence" in result
        
        # Verificar valores extraídos
        assert result["amount"] == 47600  # $47.600
        assert result["transaction_date"] == "2025-10-27"
        assert "RESTAURANTE" in result["vendor"]
        assert result["category_suggested"] == "food"
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_parse_receipt_text_low_confidence(self, ocr_service):
        """Prueba parsing con baja confianza"""
        text = "texto sin información clara de recibo"
        
        result = await ocr_service._parse_receipt_text(
            text, 
            transaction_type="expense", 
            classification="personal"
        )
        
        assert result["confidence"] < 0.5
        assert result["amount"] is None
        assert result["transaction_date"] is None
        assert result["vendor"] is None
        assert result["category_suggested"] is None

    @pytest.mark.asyncio
    async def test_context_manager(self, ocr_service):
        """Prueba que el servicio funciona como context manager"""
        with patch.object(ocr_service, 'client') as mock_client:
            mock_client.aclose = AsyncMock()
            
            async with ocr_service:
                pass
            
            mock_client.aclose.assert_called_once()


class TestOCREndpoint:
    """Pruebas de integración para el endpoint OCR"""

    @pytest.fixture
    def client(self):
        """Cliente de prueba FastAPI"""
        return TestClient(app)

    @pytest.fixture
    def sample_image_file(self):
        """Archivo de imagen de prueba"""
        img = Image.new('RGB', (200, 100), color='white')
        
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            
        draw.text((10, 10), "TOTAL: $45.000", fill='black', font=font)
        draw.text((10, 30), "RESTAURANTE", fill='black', font=font)
        draw.text((10, 50), "27/10/2025", fill='black', font=font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes

    def test_ocr_endpoint_success(self, client, sample_image_file):
        """Prueba endpoint OCR exitoso"""
        with patch('app.services.ocr_service.httpx.AsyncClient') as mock_client:
            # Mock de respuesta OpenAI
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "TOTAL: $45.000\nRESTAURANTE\n27/10/2025"
                    }
                }]
            }
            mock_client.return_value.post.return_value = mock_response
            
            response = client.post(
                "/api/v1/transactions/ocr",
                files={
                    "receipt_image": ("test.jpg", sample_image_file, "image/jpeg"),
                    "transaction_type": (None, "expense"),
                    "classification": (None, "personal")
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "amount" in data
            assert "ocr_details" in data
            assert data["amount"] == 45000

    def test_ocr_endpoint_missing_image(self, client):
        """Prueba endpoint OCR sin imagen"""
        response = client.post(
            "/api/v1/transactions/ocr",
            data={
                "transaction_type": "expense",
                "classification": "personal"
            }
        )
        
        assert response.status_code == 422

    def test_ocr_endpoint_invalid_file_type(self, client):
        """Prueba endpoint OCR con tipo de archivo inválido"""
        response = client.post(
            "/api/v1/transactions/ocr",
            files={
                "receipt_image": ("test.txt", b"texto plano", "text/plain"),
                "transaction_type": (None, "expense"),
                "classification": (None, "personal")
            }
        )
        
        assert response.status_code == 400

    def test_ocr_endpoint_missing_fields(self, client, sample_image_file):
        """Prueba endpoint OCR sin campos requeridos"""
        response = client.post(
            "/api/v1/transactions/ocr",
            files={
                "receipt_image": ("test.jpg", sample_image_file, "image/jpeg")
            }
        )
        
        assert response.status_code == 422

    def test_ocr_endpoint_openai_error(self, client, sample_image_file):
        """Prueba manejo de error de OpenAI"""
        with patch('app.services.ocr_service.httpx.AsyncClient') as mock_client:
            # Mock de error de OpenAI
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_client.return_value.post.return_value = mock_response
            
            response = client.post(
                "/api/v1/transactions/ocr",
                files={
                    "receipt_image": ("test.jpg", sample_image_file, "image/jpeg"),
                    "transaction_type": (None, "expense"),
                    "classification": (None, "personal")
                }
            )
            
            assert response.status_code == 422
            data = response.json()
            assert "message" in data