"""
Tests para el endpoint de OCR de transacciones.
"""

import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status
from PIL import Image


@pytest.mark.asyncio
async def test_ocr_endpoint_success(client, mock_db_session):
    """Test exitoso de creación de transacción por OCR"""
    # Crear imagen de prueba
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Mock del OCR service
    with patch("app.services.ocr_service.OCRService") as MockOCRService:
        mock_ocr = MockOCRService.return_value
        mock_ocr.process_receipt = AsyncMock(
            return_value=Mock(
                amount=50000.00,
                amount_confidence=0.95,
                date=None,
                date_confidence=0.0,
                vendor="Restaurante La Puerta Falsa",
                vendor_confidence=0.9,
                category_suggested="cat-cafe",
                category_confidence=0.85,
                extracted_text="Restaurante La Puerta Falsa\nTotal: $50,000",
            )
        )

        # Mock de categoría
        with patch(
            "app.repositories.category.CategoryRepository.get_by_id"
        ) as mock_get_category:
            mock_get_category.return_value = Mock(
                id="cat-cafe",
                name="Café/Restaurante",
                transaction_type="expense",
            )

            # Mock de creación de transacción
            with patch(
                "app.repositories.transaction.TransactionRepository.create"
            ) as mock_create:
                mock_transaction = Mock(
                    id="test-uuid",
                    user_id="test-user",
                    amount=50000.00,
                    currency="COP",
                    category_id="cat-cafe",
                )
                mock_create.return_value = mock_transaction

                with patch(
                    "app.repositories.transaction.TransactionRepository.get_by_id_with_category"
                ) as mock_get:
                    mock_get.return_value = mock_transaction

                    response = await client.post(
                        "/api/v1/transactions/ocr",
                        files={
                            "receipt_image": ("receipt.jpg", img_bytes, "image/jpeg")
                        },
                        data={
                            "transaction_type": "expense",
                            "classification": "personal",
                        },
                    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["amount"] == 50000.00
    assert data["category"]["id"] == "cat-cafe"


@pytest.mark.asyncio
async def test_ocr_endpoint_invalid_file_type(client):
    """Test con archivo no válido"""
    # Crear archivo de texto
    text_file = io.BytesIO(b"This is not an image")

    response = await client.post(
        "/api/v1/transactions/ocr",
        files={"receipt_image": ("test.txt", text_file, "text/plain")},
        data={
            "transaction_type": "expense",
            "classification": "personal",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_ocr_endpoint_low_confidence(client, mock_db_session):
    """Test cuando el OCR tiene baja confianza"""
    # Crear imagen de prueba
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Mock del OCR service con baja confianza
    with patch("app.services.ocr_service.OCRService") as MockOCRService:
        mock_ocr = MockOCRService.return_value
        mock_ocr.process_receipt = AsyncMock(
            return_value=Mock(
                amount=None,
                amount_confidence=0.3,  # Baja confianza
                date=None,
                date_confidence=0.0,
                vendor=None,
                vendor_confidence=0.0,
                category_suggested=None,
                category_confidence=0.0,
                extracted_text="Texto ilegible",
            )
        )

        response = await client.post(
            "/api/v1/transactions/ocr",
            files={"receipt_image": ("receipt.jpg", img_bytes, "image/jpeg")},
            data={
                "transaction_type": "expense",
                "classification": "personal",
            },
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["code"] == "OCR_INSUFFICIENT_DATA"
