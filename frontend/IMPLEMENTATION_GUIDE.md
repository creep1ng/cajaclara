# Guía de Implementación - Frontend CajaClara

## 🎯 Estado Actual del Proyecto

### ✅ Completado

1. **Servicio API** ([`src/services/api.js`](src/services/api.js))
   - ✅ Todas las funciones para consumir endpoints del backend
   - ✅ Manejo de errores con `ApiError`
   - ✅ Funciones de formateo (moneda, fechas)
   - ✅ Autenticación con JWT
   - ✅ Exportación de transacciones

2. **Context API** ([`src/context/AppContext.jsx`](src/context/AppContext.jsx))
   - ✅ Estado global de autenticación
   - ✅ Cache de categorías
   - ✅ Gestión de transacciones
   - ✅ Sistema de notificaciones
   - ✅ Estados de carga

3. **Estilos Globales** ([`src/styles/globals.css`](src/styles/globals.css))
   - ✅ Todos los estilos del MVP original
   - ✅ Variables CSS
   - ✅ Componentes estilizados
   - ✅ Responsive design
   - ✅ Animaciones

4. **Configuración**
   - ✅ Variables de entorno (`.env`)
   - ✅ Documentación de arquitectura

### 📋 Mapeo Completo: MVP HTML → React

| Funcionalidad MVP HTML | Componente React | Endpoint API | Estado |
|------------------------|------------------|--------------|---------|
| Login page | `LoginPage.jsx` | `/auth/login` | Pendiente |
| Login como invitado | `GuestLogin.jsx` | N/A | Pendiente |
| Dashboard principal | `Dashboard.jsx` | `/transactions` | Pendiente |
| Header con navegación | `Header.jsx` | N/A | Pendiente |
| Dropdown "Registrar" | `RegisterDropdown.jsx` | N/A | Pendiente |
| Workflow Info | `WorkflowInfo.jsx` | N/A | Pendiente |
| API Status | `ApiStatus.jsx` | `/health` | Pendiente |
| Cash Card | `CashCard.jsx` | `/transactions` | Pendiente |
| Gauges (Balance/Cashflow) | `GaugesCard.jsx` | `/transactions` | Pendiente |
| Date Selector | `DateSelector.jsx` | N/A | Pendiente |
| Accounts Card | `AccountsCard.jsx` | `/accounts` | Pendiente |
| Registro Manual Modal | `ManualRecordModal.jsx` | `POST /transactions/manual` | Pendiente |
| Registro Visual Modal | `VisualRecordModal.jsx` | `POST /transactions/ocr` | Pendiente |
| Ver Registros | `TransactionsList.jsx` | `GET /transactions` | Pendiente |
| Filtros de búsqueda | `TransactionFilters.jsx` | N/A | Pendiente |
| Items de transacción | `TransactionItem.jsx` | `PUT/DELETE /transactions/{id}` | Pendiente |
| Página de Accounts | `AccountsPage.jsx` | `/accounts` | Pendiente |
| Página de Reports | `ReportsPage.jsx` | `/transactions` | Pendiente |
| Sistema de notificaciones | `NotificationContainer.jsx` | N/A | Pendiente |
| Modales genéricos | `Modal.jsx` | N/A | Pendiente |

## 🚀 Próximos Pasos de Implementación

### Fase 1: Componentes Base (Prioridad Alta)

#### 1. Componentes Comunes

**`src/components/common/Notification.jsx`**
```jsx
import React from 'react';
import { useApp } from '../../context/AppContext';

export default function NotificationContainer() {
  const { notifications, removeNotification } = useApp();

  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <div key={notification.id} className={`notification ${notification.type} show`}>
          <div className="notification-icon">
            <i className={`fas fa-${getIcon(notification.type)}`}></i>
          </div>
          <div className="notification-message">{notification.message}</div>
          <button className="notification-close" onClick={() => removeNotification(notification.id)}>
            <i className="fas fa-times"></i>
          </button>
        </div>
      ))}
    </div>
  );
}

function getIcon(type) {
  return type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info';
}
```

**`src/components/common/Loading.jsx`**
```jsx
export default function Loading({ fullscreen = false }) {
  if (fullscreen) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
      </div>
    );
  }
  return <div className="loading"></div>;
}
```

**`src/components/common/Modal.jsx`**
```jsx
import React from 'react';

export default function Modal({ isOpen, onClose, title, children, footer }) {
  if (!isOpen) return null;

  return (
    <div className="modal show" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="modal-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}
```

#### 2. Autenticación

**`src/components/auth/LoginPage.jsx`**
- Formulario de login con email/password
- Botón "Entrar como invitado"
- Validación de campos
- Integra con `login()` y `loginAsGuest()` del contexto

#### 3. Layout Principal

**`src/components/layout/Header.jsx`**
- Logo de CajaClara
- Navegación con tabs (Dashboard, Ver registros, Accounts, Reports)
- Dropdown "Registrar" con:
  - Registro manual
  - Registro visual
  - Ver registros
- Avatar de usuario

### Fase 2: Dashboard (Prioridad Alta)

**`src/components/dashboard/Dashboard.jsx`**
```jsx
import React, { useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import Header from '../layout/Header';
import WorkflowInfo from './WorkflowInfo';
import ApiStatus from './ApiStatus';
import CashCard from './CashCard';
import GaugesCard from './GaugesCard';
import DateSelector from './DateSelector';
import AccountsCard from './AccountsCard';

export default function Dashboard() {
  const { refreshDashboard, globalLoading } = useApp();

  useEffect(() => {
    refreshDashboard();
  }, []);

  if (globalLoading) return <Loading fullscreen />;

  return (
    <div className="dashboard-container">
      <Header />
      <div className="container">
        <ApiStatus />
        <WorkflowInfo />
        <div className="main-content">
          <div className="dashboard-left">
            <CashCard />
            <GaugesCard />
          </div>
          <div className="dashboard-right">
            <DateSelector />
            <AccountsCard />
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Componentes del Dashboard a crear:**
1. `WorkflowInfo.jsx` - 4 pasos del flujo de trabajo
2. `ApiStatus.jsx` - Indicador de conexión con API
3. `CashCard.jsx` - Total en caja + botón agregar cuenta
4. `GaugesCard.jsx` - 3 medidores (Balance, Cashflow, Spending)
5. `DateSelector.jsx` - Selector de período con meses
6. `AccountsCard.jsx` - Lista de cuentas del usuario

### Fase 3: Registro de Transacciones (Prioridad Alta)

**`src/components/transactions/ManualRecordModal.jsx`**

Características clave:
- Tabs para tipo: Gasto / Ingreso / Transferencia
- Categorías dinámicas según el tipo seleccionado
- Validación en tiempo real
- Integración con `createTransaction()` del contexto

```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  const transactionData = {
    amount: parseFloat(amount),
    currency: 'COP',
    category_id: category,
    description: description,
    transaction_type: activeTab, // 'expense' | 'income'
    classification: classification, // 'personal' | 'business'
    transaction_date: new Date(datetime).toISOString(),
    tags: labels,
  };

  try {
    await createTransaction(transactionData);
    showNotification('Transacción registrada exitosamente', 'success');
    onClose();
    // Opcionalmente: refreshDashboard()
  } catch (error) {
    showNotification(error.message, 'error');
  }
};
```

**`src/components/transactions/VisualRecordModal.jsx`**

Características clave:
- Drag & drop para imagen
- Preview de imagen
- Llamada a OCR API
- Formulario pre-poblado con datos extraídos
- Indicador de confianza del OCR

### Fase 4: Lista de Transacciones (Prioridad Media)

**`src/components/transactions/TransactionsList.jsx`**
- Header con botón "Nuevo registro" y "Exportar"
- Filtros de búsqueda
- Lista paginada
- Acciones: Editar / Eliminar

**`src/components/transactions/TransactionFilters.jsx`**
- Búsqueda por texto
- Filtro por tipo
- Filtro por categoría
- Filtro por fecha

**`src/components/transactions/TransactionItem.jsx`**
- Icono según tipo
- Categoría y fecha
- Monto con color según tipo
- Botones de acción

### Fase 5: Accounts y Reports (Prioridad Baja)

Estas páginas pueden implementarse después del MVP funcional.

## 📝 App.jsx Principal

```jsx
import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import LoginPage from './components/auth/LoginPage';
import Dashboard from './components/dashboard/Dashboard';
import TransactionsList from './components/transactions/TransactionsList';
import AccountsPage from './components/accounts/AccountsPage';
import ReportsPage from './components/reports/ReportsPage';
import NotificationContainer from './components/common/NotificationContainer';
import Loading from './components/common/Loading';
import './styles/globals.css';

function AppContent() {
  const { isAuthenticated, authLoading } = useApp();
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  if (authLoading) {
    return <Loading fullscreen />;
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const pages = {
    dashboard: <Dashboard setCurrentPage={setCurrentPage} />,
    transactions: <TransactionsList setCurrentPage={setCurrentPage} />,
    accounts: <AccountsPage setCurrentPage={setCurrentPage} />,
    reports: <ReportsPage setCurrentPage={setCurrentPage} />,
  };

  return (
    <>
      {pages[currentPage]}
      <NotificationContainer />
    </>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
```

## 📦 Dependencias Necesarias

Actualizar `package.json`:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.3.0"
  }
}
```

No se necesitan dependencias adicionales ya que usamos:
- Fetch API nativa (no axios)
- Context API (no Redux)
- CSS puro (no CSS-in-JS)

## 🔧 Configuración de Vite

**`vite.config.js`**
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

## 🧪 Testing de Integración

### Checklist de Pruebas

- [ ] Login como invitado funciona
- [ ] Dashboard carga transacciones correctamente
- [ ] Categorías se cargan dinámicamente
- [ ] Registro manual crea transacción en backend
- [ ] Registro visual procesa imagen OCR
- [ ] Filtros de transacciones funcionan
- [ ] Paginación funciona correctamente
- [ ] Editar transacción actualiza en backend
- [ ] Eliminar transacción hace soft delete
- [ ] Exportar descarga archivo CSV/PDF
- [ ] Notificaciones se muestran correctamente
- [ ] Estados de carga se muestran
- [ ] Errores se manejan apropiadamente
- [ ] Responsive design funciona en móvil

## 🚀 Comandos para Desarrollo

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## 📚 Recursos de Referencia

1. **MVP Original:** `frontend/MVP CAJA CLARA.html`
2. **OpenAPI Spec:** `backend/app/openapi.yaml`
3. **Backend Docs:** `backend/README.md`
4. **Arquitectura:** `frontend/ARCHITECTURE.md`
5. **API Service:** `frontend/src/services/api.js`
6. **Context:** `frontend/src/context/AppContext.jsx`

## 💡 Mejores Prácticas

1. **Siempre usar el contexto para operaciones de API**
   ```jsx
   const { createTransaction } = useApp();
   // En lugar de importar directamente desde api.js
   ```

2. **Validar formularios antes de enviar al backend**
   ```jsx
   if (!amount || amount <= 0) {
     showNotification('Monto debe ser mayor a 0', 'error');
     return;
   }
   ```

3. **Manejar estados de carga**
   ```jsx
   const [loading, setLoading] = useState(false);
   
   const handleSubmit = async () => {
     setLoading(true);
     try {
       await createTransaction(data);
     } finally {
       setLoading(false);
     }
   };
   ```

4. **Usar try-catch para errores de API**
   ```jsx
   try {
     await updateTransaction(id, data);
     showNotification('Actualizado', 'success');
   } catch (error) {
     showNotification(error.message, 'error');
   }
   ```

## 🎨 Mantenimiento de Estilos

Todos los estilos del MVP están en `src/styles/globals.css`. Los componentes React deben usar las clases CSS definidas allí para mantener consistencia visual.

## 🔄 Flujo de Desarrollo Recomendado

1. Crear componente base con estructura HTML del MVP
2. Aplicar clases CSS existentes
3. Conectar con Context API para datos
4. Implementar interacciones del usuario
5. Agregar validación
6. Manejar estados de carga y error
7. Probar integración con backend
8. Refactorizar si es necesario

---

**Próximo paso sugerido:** Comenzar con la Fase 1 - Componentes Base

**Estimación de tiempo:**
- Fase 1: 2-3 horas
- Fase 2: 4-5 horas
- Fase 3: 5-6 horas
- Fase 4: 3-4 horas
- Fase 5: 2-3 horas

**Total estimado:** 16-21 horas de desarrollo

---

**Versión:** 1.0.0  
**Fecha:** 2025-10-29