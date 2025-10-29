# Guía de Instalación y Ejecución - Frontend CajaClara

## 📋 Requisitos Previos

- Node.js 18+ (recomendado: 20.x)
- npm o yarn
- Backend de CajaClara corriendo en `http://localhost:8000`

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

Esto instalará todas las dependencias necesarias:

- **react** ^18.2.0 - Biblioteca principal de UI
- **react-dom** ^18.2.0 - Renderizado de React en el DOM
- **@vitejs/plugin-react** ^4.2.1 - Plugin de Vite para React
- **vite** ^5.0.8 - Herramienta de build ultrarrápida

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz de `frontend/` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

**Importante:** Todas las variables de entorno en Vite deben comenzar con `VITE_`

### Verificar Backend

Asegúrate de que el backend esté corriendo:

```bash
# En otra terminal, desde la raíz del proyecto
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verifica que el backend esté respondiendo:

```bash
curl http://localhost:8000/health
```

## 🏃 Ejecución

### Modo Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: **http://localhost:3000**

### Características del Modo Desarrollo

- ⚡ Hot Module Replacement (HMR) - Cambios instantáneos sin recargar
- 🔄 Auto-reload cuando cambias archivos
- 🐛 Source maps para debugging
- 📡 Proxy automático a la API en `/api/*`

### Build de Producción

```bash
npm run build
```

Esto generará los archivos optimizados en `frontend/dist/`

### Preview de Build

```bash
npm run preview
```

Previsualiza el build de producción en `http://localhost:4173`

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── auth/           # Login, autenticación
│   │   ├── common/         # Componentes reutilizables
│   │   ├── dashboard/      # Dashboard y sus partes
│   │   └── transactions/   # Modales de registro
│   ├── context/            # Context API (estado global)
│   ├── services/           # API client
│   ├── styles/             # CSS global
│   ├── App.jsx             # Componente raíz
│   └── main.jsx            # Punto de entrada
├── index.html              # HTML base
├── vite.config.js          # Configuración de Vite
├── package.json            # Dependencias
└── .env                    # Variables de entorno
```

## 🔐 Autenticación

### Login como Usuario

1. Ingresa email y contraseña
2. Haz clic en "Iniciar sesión"

### Login como Invitado (MVP)

1. Haz clic en "Entrar como invitado"
2. Esto te autenticará con el usuario demo del backend

**Nota:** En modo MVP, el login es simplificado. La autenticación completa se implementará en versiones futuras.

## 🎯 Funcionalidades Disponibles

### ✅ Implementadas

- **Login/Autenticación**
  - Login con credenciales
  - Login como invitado
  - Persistencia de sesión (localStorage)

- **Dashboard**
  - Visualización de balance
  - Medidores (gauges) animados
  - Selector de período/mes
  - Lista de cuentas
  - Indicador de estado de API

- **Registro Manual de Transacciones**
  - Tipos: Gasto, Ingreso, Transferencia
  - Categorización automática
  - Etiquetas personalizadas
  - Validación de formularios
  - Integración completa con API

- **Registro Visual (OCR)**
  - Subir foto de recibo
  - Drag & drop de imágenes
  - Vista previa de imagen
  - Procesamiento con OpenAI Vision API
  - Auto-completado de campos

- **Sistema de Notificaciones**
  - Notificaciones de éxito/error
  - Auto-cierre configurable
  - Stack de múltiples notificaciones

### 🚧 Pendientes (Próximas Versiones)

- Página de Ver Registros con filtros
- Página de Cuentas (CRUD completo)
- Página de Reportes con gráficas
- Exportación de datos (CSV, Excel)
- Tests unitarios e integración

## 🐛 Debugging

### Ver Logs de la Consola

Abre las DevTools del navegador (F12) y ve a la pestaña Console

### Verificar Requests a la API

En DevTools, ve a la pestaña Network para ver todas las llamadas HTTP

### Common Issues

#### Error: "Cannot find module 'react'"

```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

#### Error: "Failed to fetch" en API calls

- Verifica que el backend esté corriendo en `http://localhost:8000`
- Revisa la configuración de CORS en el backend
- Verifica la variable `VITE_API_BASE_URL` en `.env`

#### Estilos no se aplican correctamente

- Verifica que `frontend/src/styles/globals.css` exista
- Asegúrate de que Font Awesome se cargue (revisa Network en DevTools)
- Limpia la caché del navegador (Ctrl + Shift + R)

## 📊 Performance

### Optimizaciones Implementadas

- ✅ Code splitting automático con Vite
- ✅ Lazy loading de componentes
- ✅ Minificación en producción
- ✅ Tree shaking de dependencias no usadas
- ✅ Caché de assets estáticos

### Métricas Esperadas

- **First Contentful Paint:** < 1s
- **Time to Interactive:** < 2s
- **Bundle Size:** ~200KB (gzipped)

## 🔒 Seguridad

### Headers de Seguridad

El build de producción debe servirse con estos headers:

```
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

### Variables Sensibles

- ✅ API keys se pasan desde el backend (no en frontend)
- ✅ JWT tokens se almacenan en localStorage (MVP)
- ⚠️ En producción, considerar usar httpOnly cookies

## 📝 Scripts Disponibles

```bash
# Desarrollo
npm run dev              # Inicia servidor de desarrollo

# Build
npm run build           # Build de producción
npm run preview         # Preview del build

# Linting (cuando se configure)
npm run lint            # Ejecutar linter
npm run format          # Formatear código
```

## 🚀 Deployment

### Build para Producción

```bash
npm run build
```

### Servir Archivos Estáticos

Los archivos en `dist/` pueden servirse con cualquier servidor web estático:

```bash
# Con serve (npm install -g serve)
serve -s dist -p 3000

# Con Python
cd dist && python -m http.server 3000

# Con nginx
# Copiar dist/* a /var/www/html/
```

### Variables de Entorno en Producción

Asegúrate de configurar:

```env
VITE_API_BASE_URL=https://api.cajaclara.com
VITE_API_TIMEOUT=30000
```

## 📞 Soporte

Para problemas o preguntas:

1. Revisa esta documentación
2. Consulta `ARCHITECTURE.md` para entender la estructura
3. Revisa `IMPLEMENTATION_GUIDE.md` para detalles técnicos
4. Abre un issue en el repositorio

---

**Última actualización:** 2025-10-29  
**Versión:** 1.0.0-mvp