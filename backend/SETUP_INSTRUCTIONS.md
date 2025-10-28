# Instrucciones de Configuración - CajaClara Backend

## Problema Actual

El contenedor de PostgreSQL necesita ser recreado para usar PostgreSQL 17 en lugar de la versión 18 (latest).

## Solución

### Paso 1: Detener y Eliminar Contenedores Actuales

```bash
# Desde la raíz del proyecto
docker-compose -f .devcontainer/docker-compose.yml down -v
```

El flag `-v` eliminará también los volúmenes, lo que limpiará los datos incompatibles de PostgreSQL 18.

### Paso 2: Reconstruir Contenedores

```bash
# Reconstruir con la nueva configuración
docker-compose -f .devcontainer/docker-compose.yml up -d
```

### Paso 3: Verificar que PostgreSQL está Corriendo

```bash
# Verificar logs de PostgreSQL
docker-compose -f .devcontainer/docker-compose.yml logs db

# Deberías ver algo como:
# PostgreSQL 17.x ready to accept connections
```

### Paso 4: Crear Migración Inicial

```bash
cd backend
uv run alembic revision --autogenerate -m "Initial migration with all models"
```

### Paso 5: Aplicar Migraciones

```bash
uv run alembic upgrade head
```

### Paso 6: Iniciar Servidor de Desarrollo

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verificación

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "healthy",
  "version": "1.0.0-mvp",
  "environment": "development",
  "mode": "MVP"
}
```

### 2. Documentación API

Abrir en navegador: http://localhost:8000/docs

### 3. Crear Transacción Manual (Test)

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

## Estructura de Base de Datos

Después de aplicar las migraciones, tendrás las siguientes tablas:

- `users` - Usuarios del sistema
- `entrepreneurships` - Emprendimientos de usuarios
- `categories` - Categorías predefinidas (15 categorías)
- `transactions` - Transacciones financieras
- `category_rules` - Reglas de categorización automática

## Datos Iniciales

Al iniciar la aplicación por primera vez, se crearán automáticamente:

1. **Usuario Default:**

   - ID: `00000000-0000-0000-0000-000000000001`
   - Email: `demo@cajaclara.com`

2. **15 Categorías Predefinidas:**
   - 10 categorías de gastos
   - 5 categorías de ingresos

## Troubleshooting

### Error: "Name or service not known"

La base de datos no está corriendo. Ejecuta:

```bash
docker-compose -f .devcontainer/docker-compose.yml up -d db
```

### Error: "relation does not exist"

Las migraciones no se han aplicado. Ejecuta:

```bash
cd backend && uv run alembic upgrade head
```

### Error: "Default user not found"

La aplicación no pudo inicializar la base de datos. Verifica que:

1. PostgreSQL esté corriendo
2. Las migraciones estén aplicadas
3. Reinicia el servidor

---

**Última actualización:** 2025-10-28
