# CajaClara Frontend - React + Vite

Frontend completo integrado con el backend FastAPI, manteniendo toda la funcionalidad del MVP original en HTML.

## 🎯 Estado del Proyecto

### ✅ Infraestructura Completada (100%)

#### 1. Servicio API Completo
**Archivo:** [`src/services/api.js`](src/services/api.js)

- ✅ **Transacciones**
  - `createManualTransaction()` - Crear transacción manual
  - `createOcrTransaction()` - Crear por OCR con imagen
  - `listTransactions()` - Listar con filtros y paginación
  - `getTransaction()` - Obtener detalle
  - `updateTransaction()` - Actualizar
  - `deleteTransaction()` - Eliminar (soft delete)
  - `exportTransactions()` - Exportar CSV/PDF

- ✅ **Categorías**
  - `listCategories()` - Listar categorías
  - `createCategoryRule()` - Crear regla de categorización

- ✅ **Cuentas**
  - `createAccount()` - Crear cuenta
  - `listAccounts()` - Listar cuentas
  - `updateAccount()` - Actualizar
  - `deleteAccount()` - Eliminar

- ✅ **Autenticación**
  - `login()` - Login con email/password
  - `logout()` - Cerrar sesión
  - `isAuthenticated()` - Verificar autenticación
  - `getCurrentUser()` - Obtener usuario actual

- ✅ **Utilidades**
  - `formatCurrency()` - Formatear montos en COP
  - `formatDate()` - Formatear fechas
  - `formatDateTime()` - Formatear fecha/hora
  - `downloadBlob()` - Descargar archivos
  - `ApiError` - Clase para manejo de errores

#### 2. Context API para Estado Global
**Archivo:** [`src/context/AppContext.jsx`](src/context/AppContext.jsx)

- ✅ **Estado de Autenticación**
  - `user` - Usuario actual
  - `isAuthenticated` - Estado de autenticación
  - `login()` - Iniciar sesión
  - `loginAsGuest()` - Entrar como invitado (MVP)
  - `logout()` - Cerrar sesión

- ✅ **Gestión de Categorías**
  - `categories` - Lista de categorías (cache)
  - `loadCategories()` - Cargar categorías
  - `getCategoriesByType()` - Filtrar por tipo

- ✅ **Gestión de Transacciones**
  - `transactions` - Lista de transacciones
  - `transactionsSummary` - Resumen (totales, balance)
  - `createTransaction()` - Crear transacción
  - `updateTransaction()` - Actualizar
  - `deleteTransaction()` - Eliminar
  - `loadTransactions()` - Cargar con filtros
  - `refreshDashboard()` - Refrescar datos

- ✅ **Sistema de Notificaciones**
  - `notifications` - Array de notificaciones activas
  - `showNotification()` - Mostrar notificación
  - `removeNotification()` - Remover notificación

- ✅ **Estados de Carga**
  - `globalLoading` - Carga global
  - `authLoading` - Carga de autenticación
  - `categoriesLoading` - Carga de categorías

#### 3. Estilos Globales
**Archivo:** [`src/styles/globals.css`](src/styles/globals.css)

- ✅ Todos los estilos del MVP original (1423 líneas)
- ✅ Variables CSS para colores y dimensiones
- ✅ Estilos para todos los componentes:
  - Login page
  - Dashboard
  - Formularios
  - Botones
  - Cards
  - Modales
  - Notificaciones
  - Gauges
  - Tablas/Listas
  - Responsive design
- ✅ Animaciones y transiciones

#### 4. Configuración
- ✅ `.env` - Variables de entorno
- ✅ `.env.example` - Template de variables
- ✅ `ARCHITECTURE.md` - Arquitectura completa
- ✅ `IMPLEMENTATION_GUIDE.md` - Guía de implementación

### 📋 Componentes Pendientes

Los siguientes componentes React necesitan ser implementados siguiendo la guía en [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md):

#### Fase 1: Componentes Base
- [ ] `src/components/common/NotificationContainer.jsx`
- [ ] `src/components/common/Loading.jsx`
- [ ] `src/components/common/Modal.jsx`
- [ ] `src/components/common/Button.jsx`
- [ ] `src/components/common/Input.jsx`

#### Fase 2: Autenticación
- [ ] `src/components/auth/LoginPage.jsx`
- [ ] `src/components/auth/GuestLogin.jsx`

#### Fase 3: Dashboard
- [ ] `src/components/dashboard/Dashboard.jsx`
- [ ] `src/components/layout/Header.jsx`
- [ ] `src/components/dashboard/WorkflowInfo.jsx`
- [ ] `src/components/dashboard/ApiStatus.jsx`
- [ ] `src/components/dashboard/CashCard.jsx`
- [ ] `src/components/dashboard/GaugesCard.jsx`
- [ ] `src/components/dashboard/DateSelector.jsx`
- [ ] `src/components/dashboard/AccountsCard.jsx`

#### Fase 4: Transacciones
- [ ] `src/components/transactions/ManualRecordModal.jsx`
- [ ] `src/components/transactions/VisualRecordModal.jsx`
- [ ] `src/components/transactions/TransactionsList.jsx`
- [ ] `src/components/transactions/TransactionFilters.jsx`
- [ ] `src/components/transactions/TransactionItem.jsx`

#### Fase 5: Otras Páginas
- [ ] `src/components/accounts/AccountsPage.jsx`
- [ ] `src/components/reports/ReportsPage.jsx`

#### Archivo Principal
- [ ] `src/App.jsx`
- [ ] `src/main.jsx`

## 🚀 Inicio Rápido

### Prerrequisitos
- Node.js 18+
- npm o yarn
- Backend corriendo en `http://localhost:8000`

### Instalación

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

### Scripts Disponibles

```bash
npm run dev      # Servidor de desarrollo con hot reload
npm run build    # Build para producción
npm run preview  # Preview del build de producción
npm run lint     # Linter (si configurado)
```

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/       # Componentes React (pendiente)
│   ├── context/         # Context API
│   │   └── AppContext.jsx  ✅
│   ├── services/        # Servicios API
│   │   └── api.js          ✅
│   ├── styles/          # Estilos
│   │   └── globals.css     ✅
│   ├── App.jsx          # Componente raíz (pendiente)
│   └── main.jsx         # Entry point (pendiente)
├── .env                 # Variables de entorno ✅
├── .env.example         # Template ✅
├── ARCHITECTURE.md      # Documentación de arquitectura ✅
├── IMPLEMENTATION_GUIDE.md  # Guía de implementación ✅
├── README.md           # Este archivo
├── index.html
├── package.json
└── vite.config.js
```

## 🔌 Integración con Backend

### Endpoints Consumidos

Todos los endpoints están mapeados en [`src/services/api.js`](src/services/api.js):

| Funcionalidad | Método | Endpoint | Estado |
|---------------|--------|----------|---------|
| Crear transacción manual | POST | `/api/v1/transactions/manual` | ✅ |
| Crear por OCR | POST | `/api/v1/transactions/ocr` | ✅ |
| Listar transacciones | GET | `/api/v1/transactions` | ✅ |
| Obtener transacción | GET | `/api/v1/transactions/{id}` | ✅ |
| Actualizar transacción | PUT | `/api/v1/transactions/{id}` | ✅ |
| Eliminar transacción | DELETE | `/api/v1/transactions/{id}` | ✅ |
| Exportar transacciones | GET | `/api/v1/transactions/export` | ✅ |
| Listar categorías | GET | `/api/v1/categories` | ✅ |
| Crear regla categorización | POST | `/api/v1/categories/rules` | ✅ |
| Health check | GET | `/health` | ✅ |

### Configuración del API

```javascript
// .env
VITE_API_URL=http://localhost:8000

// En el código
import * as api from './services/api';

// Usar funciones
const transaction = await api.createManualTransaction(data);
const transactions = await api.listTransactions(filters, page, limit);
```

## 🎨 Sistema de Estilos

El proyecto utiliza CSS puro con todas las clases del MVP original:

```jsx
// Ejemplo de uso
<button className="btn btn-primary">
  <i className="fas fa-plus"></i>
  Registrar
</button>

<div className="modal show">
  <div className="modal-content">
    <div className="modal-header">
      <h2 className="modal-title">Título</h2>
      <button className="modal-close">×</button>
    </div>
  </div>
</div>
```

### Variables CSS Disponibles

```css
--primary: #0FA678;
--secondary: #F2F6F5;
--accent: #FFB300;
--error: #E86E6E;
--text-primary: #0B2B28;
--text-secondary: #5A726E;
--border: #E0EAE8;
--shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
--radius: 12px;
```

## 🔧 Uso del Context API

```jsx
import { useApp } from './context/AppContext';

function MyComponent() {
  const {
    // Autenticación
    user,
    isAuthenticated,
    login,
    logout,
    
    // Categorías
    categories,
    loadCategories,
    getCategoriesByType,
    
    // Transacciones
    createTransaction,
    updateTransaction,
    deleteTransaction,
    loadTransactions,
    refreshDashboard,
    
    // Notificaciones
    showNotification,
    
    // Loading
    globalLoading,
  } = useApp();

  const handleSubmit = async (data) => {
    try {
      await createTransaction(data);
      showNotification('Transacción creada', 'success');
    } catch (error) {
      showNotification(error.message, 'error');
    }
  };

  return (
    // JSX
  );
}
```

## 📖 Documentación

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura completa del proyecto
  - Estructura de componentes
  - Flujo de datos
  - Diagramas
  - Integración con backend

- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Guía paso a paso
  - Mapeo MVP HTML → React
  - Código de ejemplo para cada componente
  - Checklist de tareas
  - Mejores prácticas

## 🧪 Testing (Pendiente)

```bash
# Tests unitarios
npm run test

# Tests con cobertura
npm run test:coverage

# Tests E2E
npm run test:e2e
```

## 📊 Categorías del Backend

El backend proporciona 15 categorías predefinidas:

**Gastos (10):**
1. Alimentación (`cat-food`) 🍔
2. Transporte (`cat-transport`) 🚗
3. Servicios (`cat-utilities`) 💡
4. Arriendo (`cat-rent`) 🏠
5. Entretenimiento (`cat-entertainment`) 🎬
6. Salud (`cat-health`) ⚕️
7. Educación (`cat-education`) 📚
8. Compras (`cat-shopping`) 🛍️
9. Café/Restaurante (`cat-cafe`) ☕
10. Otros Gastos (`cat-other-expense`) 📦

**Ingresos (5):**
1. Salario (`cat-salary`) 💰
2. Freelance (`cat-freelance`) 💼
3. Ventas (`cat-sales`) 🏪
4. Inversiones (`cat-investment`) 📈
5. Otros Ingresos (`cat-other-income`) 💵

## 🚀 Próximos Pasos

1. **Implementar componentes base** (Fase 1)
   - NotificationContainer
   - Loading
   - Modal

2. **Implementar autenticación** (Fase 2)
   - LoginPage
   - Integración con contexto

3. **Implementar dashboard** (Fase 3)
   - Dashboard principal
   - Header con navegación
   - Cards de información

4. **Implementar transacciones** (Fase 4)
   - Modales de registro
   - Lista de transacciones
   - Filtros

Ver detalles en [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md)

## 🤝 Contribuir

1. Seguir la estructura de carpetas definida
2. Usar el Context API para estado global
3. Mantener los estilos CSS del MVP original
4. Documentar componentes con JSDoc
5. Implementar manejo de errores robusto

## 📝 Convenciones de Código

- **Nombres de componentes:** PascalCase (`Dashboard.jsx`)
- **Nombres de funciones:** camelCase (`handleSubmit`)
- **Constantes:** UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Archivos CSS:** kebab-case (`globals.css`)

## 🐛 Debugging

### Verificar conexión con API

```javascript
import { healthCheck } from './services/api';

const status = await healthCheck();
console.log('API Status:', status);
```

### Ver estado del contexto

```jsx
const app = useApp();
console.log('App State:', {
  user: app.user,
  isAuthenticated: app.isAuthenticated,
  categories: app.categories,
  transactions: app.transactions,
});
```

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

## 👥 Equipo

CajaClara Team - Medellín, Colombia

---

**Versión:** 1.0.0-mvp  
**Última actualización:** 2025-10-29

**Estado:** Infraestructura completa ✅ | Componentes React pendientes ⏳