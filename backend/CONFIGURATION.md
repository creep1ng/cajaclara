# Configuración y Variables de Entorno - CajaClara Backend

Esta guía documenta todas las variables de entorno y opciones de configuración disponibles en el backend de CajaClara.

## 📋 Tabla de Contenidos

- [Sistema de Configuración](#sistema-de-configuración)
- [Variables de Entorno](#variables-de-entorno)
- [Configuración por Ambiente](#configuración-por-ambiente)
- [Ejemplos de Configuración](#ejemplos-de-configuración)

## Sistema de Configuración

CajaClara utiliza **Pydantic Settings** para gestionar la configuración, lo que proporciona:

- ✅ Validación automática de tipos
- ✅ Valores por defecto
- ✅ Carga desde archivo `.env`
- ✅ Conversión automática de tipos
- ✅ Documentación integrada

### Archivo de Configuración

La configuración se define en [`backend/app/config.py`](app/config.py):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración aquí

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
```

## Variables de Entorno

### 🔧 Aplicación

| Variable      | Tipo   | Default           | Descripción                                       |
| ------------- | ------ | ----------------- | ------------------------------------------------- |
| `APP_NAME`    | `str`  | `"CajaClara API"` | Nombre de la aplicación                           |
| `APP_VERSION` | `str`  | `"1.0.0-mvp"`     | Versión de la API                                 |
| `ENVIRONMENT` | `str`  | `"development"`   | Ambiente (`development`, `staging`, `production`) |
| `DEBUG`       | `bool` | `False`           | Modo debug (solo desarrollo)                      |
| `MVP_MODE`    | `bool` | `True`            | Modo MVP (simplificaciones activas)               |

**Ejemplo:**

```bash
APP_NAME=CajaClara API
APP_VERSION=1.0.0-mvp
ENVIRONMENT=development
DEBUG=true
MVP_MODE=true
```

### 🗄️ Base de Datos

| Variable          | Tipo   | Default | Descripción                       | Requerido |
| ----------------- | ------ | ------- | --------------------------------- | --------- |
| `DATABASE_URL`    | `str`  | -       | URL de conexión PostgreSQL        | ✅        |
| `DB_ECHO`         | `bool` | `False` | Mostrar queries SQL en logs       | ❌        |
| `DB_POOL_SIZE`    | `int`  | `5`     | Tamaño del pool de conexiones     | ❌        |
| `DB_MAX_OVERFLOW` | `int`  | `10`    | Conexiones adicionales permitidas | ❌        |

**Formato de DATABASE_URL:**

```bash
# Async (runtime)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Sync (migraciones Alembic)
DATABASE_URL=postgresql://user:password@host:port/database
```

**Ejemplos:**

```bash
# Desarrollo local
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cajaclara

# Docker Compose
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/cajaclara

# Producción (con SSL)
DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/cajaclara?ssl=require
```

**Configuración avanzada:**

```bash
DB_ECHO=true              # Ver queries en desarrollo
DB_POOL_SIZE=10           # Más conexiones para producción
DB_MAX_OVERFLOW=20        # Permitir picos de tráfico
```

### 🔐 Seguridad y Autenticación

| Variable                      | Tipo  | Default   | Descripción                | Requerido |
| ----------------------------- | ----- | --------- | -------------------------- | --------- |
| `SECRET_KEY`                  | `str` | -         | Clave secreta para JWT     | ✅        |
| `ALGORITHM`                   | `str` | `"HS256"` | Algoritmo de firma JWT     | ❌        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `1440`    | Expiración del token (24h) | ❌        |

**Generar SECRET_KEY segura:**

```bash
# Opción 1: OpenSSL
openssl rand -hex 32

# Opción 2: Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Ejemplo:**

```bash
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

⚠️ **IMPORTANTE:** Nunca uses la misma `SECRET_KEY` en desarrollo y producción.

### 🌐 CORS (Cross-Origin Resource Sharing)

| Variable               | Tipo  | Default                   | Descripción                              |
| ---------------------- | ----- | ------------------------- | ---------------------------------------- |
| `BACKEND_CORS_ORIGINS` | `str` | `"http://localhost:3000"` | Orígenes permitidos (separados por coma) |

**Formato:**

```bash
# Un solo origen
BACKEND_CORS_ORIGINS=http://localhost:3000

# Múltiples orígenes (separados por coma)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://app.cajaclara.com

# Desarrollo (permitir todos - NO usar en producción)
BACKEND_CORS_ORIGINS=*
```

**Ejemplos por ambiente:**

```bash
# Desarrollo
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Staging
BACKEND_CORS_ORIGINS=https://staging.cajaclara.com

# Producción
BACKEND_CORS_ORIGINS=https://app.cajaclara.com,https://www.cajaclara.com
```

### 🤖 OpenAI (OCR)

| Variable             | Tipo    | Default                  | Descripción                  | Requerido     |
| -------------------- | ------- | ------------------------ | ---------------------------- | ------------- |
| `OPENAI_API_KEY`     | `str`   | -                        | API key de OpenAI            | ✅ (para OCR) |
| `OPENAI_MODEL`       | `str`   | `"gpt-4-vision-preview"` | Modelo de visión a usar      | ❌            |
| `OPENAI_MAX_TOKENS`  | `int`   | `1000`                   | Tokens máximos por request   | ❌            |
| `OPENAI_TEMPERATURE` | `float` | `0.1`                    | Temperatura del modelo (0-1) | ❌            |

**Ejemplo:**

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-vision-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
```

**Modelos disponibles:**

- `gpt-4-vision-preview` - Mejor calidad, más costoso
- `gpt-4-turbo` - Balance calidad/costo
- `gpt-4o` - Más rápido y económico

### 📸 OCR (Procesamiento de Imágenes)

| Variable                | Tipo    | Default | Descripción                                    |
| ----------------------- | ------- | ------- | ---------------------------------------------- |
| `OCR_MIN_CONFIDENCE`    | `float` | `0.7`   | Confianza mínima para aceptar extracción (0-1) |
| `OCR_MAX_IMAGE_SIZE_MB` | `int`   | `10`    | Tamaño máximo de imagen en MB                  |

**Ejemplo:**

```bash
OCR_MIN_CONFIDENCE=0.7        # 70% de confianza mínima
OCR_MAX_IMAGE_SIZE_MB=10      # Máximo 10 MB por imagen
```

### 📄 Paginación

| Variable            | Tipo  | Default | Descripción                      |
| ------------------- | ----- | ------- | -------------------------------- |
| `DEFAULT_PAGE_SIZE` | `int` | `20`    | Registros por página por defecto |
| `MAX_PAGE_SIZE`     | `int` | `100`   | Máximo de registros por página   |

**Ejemplo:**

```bash
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### 📝 Logging

| Variable     | Tipo  | Default  | Descripción                                            |
| ------------ | ----- | -------- | ------------------------------------------------------ |
| `LOG_LEVEL`  | `str` | `"INFO"` | Nivel de logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FORMAT` | `str` | `"json"` | Formato de logs (`json`, `text`)                       |

**Ejemplo:**

```bash
# Desarrollo
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Producción
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 👤 Usuario Default (MVP)

| Variable             | Tipo  | Default                                  | Descripción                |
| -------------------- | ----- | ---------------------------------------- | -------------------------- |
| `DEFAULT_USER_ID`    | `str` | `"00000000-0000-0000-0000-000000000001"` | UUID del usuario default   |
| `DEFAULT_USER_EMAIL` | `str` | `"demo@cajaclara.com"`                   | Email del usuario default  |
| `DEFAULT_USER_NAME`  | `str` | `"Usuario Demo"`                         | Nombre del usuario default |

**Ejemplo:**

```bash
DEFAULT_USER_ID=00000000-0000-0000-0000-000000000001
DEFAULT_USER_EMAIL=demo@cajaclara.com
DEFAULT_USER_NAME=Usuario Demo
```

⚠️ **Nota:** Estas variables solo se usan en modo MVP. En producción, se debe implementar autenticación completa.

## Configuración por Ambiente

### 🛠️ Desarrollo Local

Archivo `.env` para desarrollo:

```bash
# Aplicación
APP_NAME=CajaClara API
ENVIRONMENT=development
DEBUG=true
MVP_MODE=true

# Base de Datos
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cajaclara
DB_ECHO=true

# Seguridad
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# OpenAI (opcional en desarrollo)
OPENAI_API_KEY=sk-your-dev-key
OPENAI_MODEL=gpt-4-vision-preview

# OCR
OCR_MIN_CONFIDENCE=0.7
OCR_MAX_IMAGE_SIZE_MB=10

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Usuario Default
DEFAULT_USER_EMAIL=demo@cajaclara.com
```

### 🧪 Staging

```bash
# Aplicación
APP_NAME=CajaClara API
ENVIRONMENT=staging
DEBUG=false
MVP_MODE=false

# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:pass@staging-db:5432/cajaclara
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Seguridad
SECRET_KEY=staging-secret-key-different-from-prod
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=https://staging.cajaclara.com

# OpenAI
OPENAI_API_KEY=sk-staging-key
OPENAI_MODEL=gpt-4-vision-preview

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 🚀 Producción

```bash
# Aplicación
APP_NAME=CajaClara API
ENVIRONMENT=production
DEBUG=false
MVP_MODE=false

# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:secure-pass@prod-db:5432/cajaclara?ssl=require
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Seguridad
SECRET_KEY=production-secret-key-very-secure-and-long
ACCESS_TOKEN_EXPIRE_MINUTES=720  # 12 horas en producción

# CORS
BACKEND_CORS_ORIGINS=https://app.cajaclara.com,https://www.cajaclara.com

# OpenAI
OPENAI_API_KEY=sk-production-key
OPENAI_MODEL=gpt-4-vision-preview
OPENAI_MAX_TOKENS=1000

# OCR
OCR_MIN_CONFIDENCE=0.8  # Mayor confianza en producción
OCR_MAX_IMAGE_SIZE_MB=5  # Límite más estricto

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json

# Paginación
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=50  # Límite más bajo en producción
```

## Ejemplos de Configuración

### Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/cajaclara
      - SECRET_KEY=${SECRET_KEY}
      - BACKEND_CORS_ORIGINS=http://localhost:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cajaclara-config
data:
  APP_NAME: "CajaClara API"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  BACKEND_CORS_ORIGINS: "https://app.cajaclara.com"
```

### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cajaclara-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql+asyncpg://user:pass@db:5432/cajaclara"
  SECRET_KEY: "your-secret-key"
  OPENAI_API_KEY: "sk-your-key"
```

## Validación de Configuración

### Verificar Configuración Actual

```python
# En Python shell o script
from app.config import settings

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Database: {settings.DATABASE_URL}")
print(f"Debug: {settings.DEBUG}")
print(f"CORS Origins: {settings.cors_origins_list}")
```

### Health Check

El endpoint `/health` muestra información básica de configuración:

```bash
curl http://localhost:8000/health
```

Respuesta:

```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0-mvp",
  "database": "connected"
}
```

## Troubleshooting

### Problema: Base de datos no conecta

**Síntomas:**

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Soluciones:**

1. Verificar que PostgreSQL esté corriendo
2. Verificar `DATABASE_URL` en `.env`
3. Verificar que el host sea accesible
4. Para Docker: usar nombre del servicio (`db`) en lugar de `localhost`

### Problema: CORS errors en frontend

**Síntomas:**

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solución:**

```bash
# Agregar origen del frontend a BACKEND_CORS_ORIGINS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Problema: JWT inválido

**Síntomas:**

```
401 Unauthorized: Invalid authentication token
```

**Soluciones:**

1. Verificar que `SECRET_KEY` sea la misma que generó el token
2. Verificar que el token no haya expirado
3. Verificar formato del header: `Authorization: Bearer <token>`

## Mejores Prácticas

### ✅ DO

- ✅ Usar diferentes `SECRET_KEY` por ambiente
- ✅ Usar variables de entorno para secretos
- ✅ Validar configuración al inicio
- ✅ Documentar variables personalizadas
- ✅ Usar valores por defecto seguros
- ✅ Rotar `SECRET_KEY` periódicamente en producción

### ❌ DON'T

- ❌ Commitear archivos `.env` al repositorio
- ❌ Usar la misma `SECRET_KEY` en todos los ambientes
- ❌ Hardcodear secretos en el código
- ❌ Usar `DEBUG=true` en producción
- ❌ Permitir CORS `*` en producción
- ❌ Exponer información sensible en logs

## Referencias

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Configuration](https://fastapi.tiangolo.com/advanced/settings/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

---

**Última actualización:** 2025-10-28  
**Versión:** 1.0.0
