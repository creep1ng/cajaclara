# CajaClara Backend API

Sistema backend FastAPI para gestión de transacciones financieras personales y de microempresas, con soporte para registro manual, OCR de recibos, categorización automática y exportación de datos.

## 🎯 Alcance del MVP

El MVP actual incluye:

### ✅ Funcionalidades Implementadas

- **Gestión de Transacciones (CRUD Completo)**

  - Registro manual de ingresos y gastos
  - Listado con filtros avanzados (fechas, tipo, clasificación, categoría)
  - Actualización de transacciones
  - Eliminación lógica (soft delete) para auditoría
  - Resúmenes automáticos (totales, balance neto, desglose por clasificación)

- **Sistema de Categorías**

  - 15 categorías predefinidas (10 gastos, 5 ingresos)
  - Categorización por tipo de transacción
  - Iconos y colores para UI

- **Gestión de Emprendimientos**

  - Asociación de transacciones con negocios específicos
  - Seguimiento financiero separado por emprendimiento

- **Base de Datos**

  - PostgreSQL 17 con migraciones Alembic
  - Soft deletes para auditoría
  - Índices optimizados para búsquedas rápidas
  - Soporte para JSONB (metadatos flexibles)

- **Seguridad y Configuración**
  - Autenticación JWT (estructura base)
  - CORS configurado
  - Variables de entorno con Pydantic
  - Manejo de errores robusto

### 🚧 Pendientes para Versión Completa

- Procesamiento OCR de recibos (OpenAI Vision API)
- Reglas de categorización automática
- Exportación a Excel/CSV
- Tests unitarios e integración
- Autenticación completa (login, registro)

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- PostgreSQL 17
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes Python)

### Instalación

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd cajaclara/backend
```

2. **Instalar dependencias**

```bash
uv sync
```

3. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Iniciar base de datos (Docker)**

```bash
# Desde la raíz del proyecto
docker-compose -f .devcontainer/docker-compose.yml up -d db
```

5. **Ejecutar migraciones**

```bash
uv run alembic upgrade head
```

6. **Iniciar servidor de desarrollo**

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:

- **API:** http://localhost:8000
- **Documentación Swagger:** http://localhost:8000/docs
- **Documentación ReDoc:** http://localhost:8000/redoc

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/              # Endpoints y routers
│   │   ├── deps.py       # Dependencias (auth, db)
│   │   └── v1/           # API versión 1
│   │       ├── router.py
│   │       └── endpoints/
│   ├── core/             # Utilidades core
│   │   ├── exceptions.py # Excepciones personalizadas
│   │   └── security.py   # JWT y seguridad
│   ├── db/               # Configuración de base de datos
│   │   ├── database.py   # Sesión async
│   │   └── init_db.py    # Inicialización y seed
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   ├── repositories/     # Capa de acceso a datos
│   ├── services/         # Lógica de negocio
│   ├── config.py         # Configuración y settings
│   └── main.py           # Aplicación FastAPI
├── migrations/           # Migraciones Alembic
├── tests/                # Tests
├── .env                  # Variables de entorno
├── alembic.ini          # Configuración Alembic
└── pyproject.toml       # Dependencias
```

## 🛠️ Comandos Útiles

### Desarrollo

```bash
# Iniciar servidor con recarga automática
uv run uvicorn app.main:app --reload

# Ejecutar en modo debug
uv run uvicorn app.main:app --reload --log-level debug

# Formatear código
uv run ruff format .

# Linter
uv run ruff check --fix .
```

### Base de Datos

```bash
# Crear nueva migración
uv run alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
uv run alembic upgrade head

# Revertir última migración
uv run alembic downgrade -1

# Ver historial de migraciones
uv run alembic history

# Ver estado actual
uv run alembic current
```

### Tests

```bash
# Ejecutar todos los tests
uv run pytest

# Tests con cobertura
uv run pytest --cov=app tests/

# Tests específicos
uv run pytest tests/unit/test_services.py -v
```

## 📚 Documentación Adicional

- **[Configuración y Variables de Entorno](./CONFIGURATION.md)** - Guía completa de configuración
- **[Arquitectura Técnica](./TECHNICAL_ARCHITECTURE.md)** - Diseño del sistema y base de datos
- **[Modelo de Emprendimientos](./ENTREPRENEURSHIP_MODEL.md)** - Documentación del modelo de negocios

## 🔌 API Endpoints

### Transacciones

| Método | Endpoint                      | Descripción                        |
| ------ | ----------------------------- | ---------------------------------- |
| POST   | `/api/v1/transactions/manual` | Crear transacción manual           |
| GET    | `/api/v1/transactions`        | Listar transacciones con filtros   |
| GET    | `/api/v1/transactions/{id}`   | Obtener detalle de transacción     |
| PUT    | `/api/v1/transactions/{id}`   | Actualizar transacción             |
| DELETE | `/api/v1/transactions/{id}`   | Eliminar transacción (soft delete) |

### Categorías (Pendiente)

| Método | Endpoint                   | Descripción                   |
| ------ | -------------------------- | ----------------------------- |
| GET    | `/api/v1/categories`       | Listar categorías             |
| POST   | `/api/v1/categories/rules` | Crear regla de categorización |

### Exportación (Pendiente)

| Método | Endpoint                      | Descripción            |
| ------ | ----------------------------- | ---------------------- |
| GET    | `/api/v1/transactions/export` | Exportar transacciones |

## 🧪 Ejemplos de Uso

### Crear Transacción

```bash
curl -X POST http://localhost:8000/api/v1/transactions/manual \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45000,
    "currency": "COP",
    "category_id": "cat-cafe",
    "description": "Café para oficina",
    "transaction_type": "expense",
    "classification": "business",
    "transaction_date": "2025-10-28T14:30:00Z"
  }'
```

### Listar Transacciones

```bash
curl "http://localhost:8000/api/v1/transactions?page=1&limit=20&classification=business"
```

### Actualizar Transacción

```bash
curl -X PUT http://localhost:8000/api/v1/transactions/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50000,
    "description": "Café actualizado"
  }'
```

## 🏗️ Stack Tecnológico

- **Framework:** FastAPI 0.120+
- **Base de Datos:** PostgreSQL 17
- **ORM:** SQLAlchemy 2.0+ (async)
- **Migraciones:** Alembic 1.17+
- **Validación:** Pydantic 2.12+
- **Driver DB:** asyncpg (async), psycopg2-binary (migraciones)
- **Servidor:** Uvicorn

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Convenciones de Código

- **Nombres:** Inglés para código, español para comentarios/docs
- **Formato:** Usar `ruff format` antes de commit
- **Type Hints:** Obligatorios en funciones públicas
- **Docstrings:** Google style en español
- **Tests:** Cobertura mínima 80%

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

## 👥 Equipo

CajaClara Team - Medellín, Colombia

---

**Versión:** 1.0.0-mvp  
**Última actualización:** 2025-10-28
