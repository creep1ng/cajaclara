# OCR Implementation - Reconocimiento de Facturas

## Descripción

Esta implementación permite a los usuarios registrar transacciones mediante el escaneo de fotografías de facturas o recibos. El sistema utiliza la API de OpenAI Vision para extraer automáticamente:

- **Monto**: Valor total de la transacción
- **Fecha**: Fecha de la transacción
- **Comerciante**: Nombre del negocio
- **Categoría sugerida**: Categoría automática basada en el tipo de comercio

## Arquitectura

### Componentes

1. **OCRService** (`app/services/ocr_service.py`)
   - Procesa imágenes usando OpenAI Vision API
   - Extrae datos estructurados con niveles de confianza
   - Valida formato y tamaño de imágenes

2. **TransactionService** (`app/services/transaction.py`)
   - Método `create_ocr_transaction()` para procesar datos OCR
   - Valida confianza mínima antes de crear transacción
   - Asigna categorías por defecto si la sugerencia no es válida

3. **Endpoint API** (`app/api/v1/endpoints/transactions.py`)
   - `POST /api/v1/transactions/ocr`
   - Recibe imagen y metadatos
   - Retorna transacción creada con detalles de OCR

4. **Schemas** (`app/schemas/transaction.py`)
   - `CreateOcrTransactionRequest`: Request para OCR
   - `OcrExtractedData`: Datos extraídos con confianza
   - `OcrTransactionResponse`: Response con detalles de OCR

## Flujo de Trabajo

```
Usuario sube imagen
       ↓
Validar imagen (formato, tamaño)
       ↓
OpenAI Vision API (extracción estructurada)
       ↓
Validar confianza mínima
       ↓
Asignar categoría (sugerida o por defecto)
       ↓
Crear transacción en BD
       ↓
Retornar transacción + detalles OCR
```

## Criterios de Aceptación

### ✅ Implementados

1. **Escaneo automático**
   - El sistema detecta monto, fecha y categoría sugerida
   - Niveles de confianza para cada campo extraído

2. **Manejo de fallos**
   - Si el OCR falla, retorna error descriptivo
   - Si la confianza es baja, solicita entrada manual
   - No se pierde el registro si el OCR falla parcialmente

3. **Validaciones**
   - Formato de imagen (JPEG, PNG, WebP)
   - Tamaño máximo de imagen (10 MB por defecto)
   - Confianza mínima del monto (0.7 por defecto)

## Configuración

Variables de entorno en `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-2024-08-06
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
OPENAI_TIMEOUT=30

# OCR Settings
OCR_MIN_CONFIDENCE=0.7
OCR_MAX_IMAGE_SIZE_MB=10
```

## Uso del API

### Request

```bash
curl -X POST http://localhost:8000/api/v1/transactions/ocr \
  -F "receipt_image=@recibo.jpg" \
  -F "transaction_type=expense" \
  -F "classification=business" \
  -F "description=Almuerzo con cliente"
```

### Response Exitoso (201)

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "amount": 45000.00,
  "currency": "COP",
  "category": {
    "id": "cat-cafe",
    "name": "Café/Restaurante",
    "icon": "☕"
  },
  "description": "Restaurante La Puerta Falsa - Almuerzo con cliente",
  "transaction_type": "expense",
  "classification": "business",
  "transaction_date": "2025-10-29T12:30:00",
  "metadata": {
    "source": "ocr",
    "ocr_confidence": 0.95,
    "vendor": "Restaurante La Puerta Falsa"
  },
  "ocr_details": {
    "amount": 45000.00,
    "amount_confidence": 0.95,
    "date": "2025-10-29T12:30:00",
    "date_confidence": 0.85,
    "vendor": "Restaurante La Puerta Falsa",
    "vendor_confidence": 0.90,
    "category_suggested": "cat-cafe",
    "category_confidence": 0.88,
    "extracted_text": "Restaurante La Puerta Falsa\nCalle 11 #6-50\n..."
  }
}
```

### Response Error OCR (422)

```json
{
  "code": "OCR_INSUFFICIENT_DATA",
  "message": "No se pudo extraer el monto con suficiente confianza. Por favor, ingrese los datos manualmente.",
  "details": {
    "amount": null,
    "confidence": 0.3,
    "min_required": 0.7
  }
}
```

### Response Imagen Inválida (400)

```json
{
  "code": "INVALID_IMAGE_FORMAT",
  "message": "Formato de imagen no permitido. Use: image/jpeg, image/png, image/jpg, image/webp",
  "details": {
    "content_type": "text/plain"
  }
}
```

## Categorías Soportadas

El OCR puede sugerir las siguientes categorías:

**Gastos:**
- `cat-food`: Supermercados, alimentos
- `cat-cafe`: Restaurantes, cafeterías
- `cat-transport`: Taxis, Uber, gasolina
- `cat-utilities`: Servicios públicos
- `cat-rent`: Arriendo
- `cat-entertainment`: Entretenimiento
- `cat-health`: Salud
- `cat-education`: Educación
- `cat-shopping`: Compras
- `cat-other-expense`: Otros gastos

**Ingresos:**
- `cat-salary`: Salario
- `cat-freelance`: Trabajo independiente
- `cat-sales`: Ventas
- `cat-other-income`: Otros ingresos

## Testing

Ejecutar tests:

```bash
# Todos los tests
uv run pytest tests/ -v

# Solo tests de OCR
uv run pytest tests/test_ocr_endpoint.py -v

# Con coverage
uv run pytest tests/test_ocr_endpoint.py -v --cov=app/services/ocr_service
```

## Limitaciones Conocidas

1. **Idioma**: Optimizado para recibos en español (Colombia)
2. **Calidad de imagen**: Requiere imágenes nítidas y bien iluminadas
3. **Formato de recibo**: Funciona mejor con recibos estándar impresos
4. **Costo**: Cada llamada a OpenAI Vision tiene un costo asociado

## Mejoras Futuras

- [ ] Cache de resultados para imágenes duplicadas
- [ ] Pre-procesamiento de imágenes (rotación, mejora de contraste)
- [ ] Soporte multi-moneda automático
- [ ] Extracción de ítems individuales del recibo
- [ ] Detección de recibos duplicados
- [ ] Modo offline con modelos locales

## Referencias

- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [OpenAPI Schema](../app/openapi.yaml)
