/**
 * Servicio API para CajaClara
 * Conecta el frontend React con el backend FastAPI
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

/**
 * Clase para manejar errores de la API
 */
class ApiError extends Error {
    constructor(message, code, status, details) {
        super(message);
        this.name = 'ApiError';
        this.code = code;
        this.status = status;
        this.details = details;
    }
}

/**
 * Función auxiliar para hacer requests HTTP
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${API_VERSION}${endpoint}`;

    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    // Agregar token JWT si existe
    const token = localStorage.getItem('auth_token');
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        mode: 'cors',
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        console.log(`🔍 API Request: ${options.method || 'GET'} ${url}`);
        const response = await fetch(url, config);
        console.log(`📡 API Response: ${response.status} ${response.statusText}`);

        // Si es 204 No Content, no hay body
        if (response.status === 204) {
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new ApiError(
                data.message || 'Error en la solicitud',
                data.code || 'UNKNOWN_ERROR',
                response.status,
                data.details || {}
            );
        }

        return data;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }

        // Error de red o parsing
        throw new ApiError(
            error.message || 'Error de conexión',
            'NETWORK_ERROR',
            0,
            {}
        );
    }
}

// ==================== TRANSACCIONES ====================

/**
 * Crear transacción manual
 * @param {Object} transactionData - Datos de la transacción
 * @returns {Promise<Object>} Transacción creada
 */
export async function createManualTransaction(transactionData) {
    return fetchAPI('/transactions/manual', {
        method: 'POST',
        body: JSON.stringify(transactionData),
    });
}

/**
 * Crear transacción por OCR
 * @param {FormData} formData - Datos del formulario con imagen
 * @returns {Promise<Object>} Transacción creada con datos OCR
 */
export async function createOcrTransaction(formData) {
    const url = `${API_BASE_URL}${API_VERSION}/transactions/ocr`;
    const token = localStorage.getItem('auth_token');

    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData, // No establecer Content-Type, el browser lo hace automáticamente
        });

        const data = await response.json();

        if (!response.ok) {
            throw new ApiError(
                data.message || 'Error procesando imagen',
                data.code || 'OCR_ERROR',
                response.status,
                data.details || {}
            );
        }

        return data;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new ApiError(
            error.message || 'Error de conexión',
            'NETWORK_ERROR',
            0,
            {}
        );
    }
}

/**
 * Listar transacciones con filtros
 * @param {Object} filters - Filtros de búsqueda
 * @param {number} page - Número de página
 * @param {number} limit - Registros por página
 * @returns {Promise<Object>} Lista paginada de transacciones
 */
export async function listTransactions(filters = {}, page = 1, limit = 20) {
    const params = new URLSearchParams();

    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.transaction_type) params.append('transaction_type', filters.transaction_type);
    if (filters.classification) params.append('classification', filters.classification);
    if (filters.category_id) params.append('category_id', filters.category_id);
    params.append('page', page);
    params.append('limit', limit);

    return fetchAPI(`/transactions?${params.toString()}`);
}

/**
 * Obtener detalle de transacción
 * @param {string} transactionId - UUID de la transacción
 * @returns {Promise<Object>} Detalle de la transacción
 */
export async function getTransaction(transactionId) {
    return fetchAPI(`/transactions/${transactionId}`);
}

/**
 * Actualizar transacción
 * @param {string} transactionId - UUID de la transacción
 * @param {Object} updateData - Datos a actualizar
 * @returns {Promise<Object>} Transacción actualizada
 */
export async function updateTransaction(transactionId, updateData) {
    return fetchAPI(`/transactions/${transactionId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
    });
}

/**
 * Eliminar transacción (soft delete)
 * @param {string} transactionId - UUID de la transacción
 * @returns {Promise<null>}
 */
export async function deleteTransaction(transactionId) {
    return fetchAPI(`/transactions/${transactionId}`, {
        method: 'DELETE',
    });
}

/**
 * Exportar transacciones
 * @param {string} format - Formato (csv, pdf)
 * @param {Object} filters - Filtros de exportación
 * @returns {Promise<Blob>} Archivo descargable
 */
export async function exportTransactions(format = 'csv', filters = {}) {
    const params = new URLSearchParams();
    params.append('format', format);

    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.classification) params.append('classification', filters.classification);

    const url = `${API_BASE_URL}${API_VERSION}/transactions/export?${params.toString()}`;
    const token = localStorage.getItem('auth_token');

    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { headers });

    if (!response.ok) {
        const data = await response.json();
        throw new ApiError(
            data.message || 'Error exportando datos',
            data.code || 'EXPORT_ERROR',
            response.status,
            data.details || {}
        );
    }

    return response.blob();
}

// ==================== CATEGORÍAS ====================

/**
 * Listar categorías disponibles
 * @param {string} transactionType - Filtrar por tipo (income, expense)
 * @param {string} search - Búsqueda por nombre
 * @returns {Promise<Object>} Lista de categorías
 */
export async function listCategories(transactionType = null, search = null) {
    const params = new URLSearchParams();

    if (transactionType) params.append('transaction_type', transactionType);
    if (search) params.append('search', search);

    const queryString = params.toString();
    return fetchAPI(`/categories${queryString ? '?' + queryString : ''}`);
}

/**
 * Crear regla de categorización automática
 * @param {Object} ruleData - Datos de la regla
 * @returns {Promise<Object>} Regla creada
 */
export async function createCategoryRule(ruleData) {
    return fetchAPI('/categories/rules', {
        method: 'POST',
        body: JSON.stringify(ruleData),
    });
}

// ==================== CUENTAS (ACCOUNTS) ====================

/**
 * Crear nueva cuenta
 * @param {Object} accountData - Datos de la cuenta
 * @returns {Promise<Object>} Cuenta creada
 */
export async function createAccount(accountData) {
    return fetchAPI('/accounts', {
        method: 'POST',
        body: JSON.stringify(accountData),
    });
}

/**
 * Listar cuentas del usuario
 * @returns {Promise<Array>} Lista de cuentas
 */
export async function listAccounts() {
    return fetchAPI('/accounts');
}

/**
 * Actualizar cuenta
 * @param {string} accountId - UUID de la cuenta
 * @param {Object} updateData - Datos a actualizar
 * @returns {Promise<Object>} Cuenta actualizada
 */
export async function updateAccount(accountId, updateData) {
    return fetchAPI(`/accounts/${accountId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
    });
}

/**
 * Eliminar cuenta
 * @param {string} accountId - UUID de la cuenta
 * @returns {Promise<null>}
 */
export async function deleteAccount(accountId) {
    return fetchAPI(`/accounts/${accountId}`, {
        method: 'DELETE',
    });
}

// ==================== AUTENTICACIÓN ====================

/**
 * Login de usuario
 * @param {string} email - Email del usuario
 * @param {string} password - Contraseña
 * @returns {Promise<Object>} Token y datos del usuario
 */
export async function login(email, password) {
    const response = await fetchAPI('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });

    // Guardar token en localStorage
    if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token);
    }

    return response;
}

/**
 * Logout de usuario
 */
export function logout() {
    localStorage.removeItem('auth_token');
}

/**
 * Verificar si el usuario está autenticado
 * @returns {boolean}
 */
export function isAuthenticated() {
    return !!localStorage.getItem('auth_token');
}

/**
 * Obtener usuario actual
 * @returns {Promise<Object>} Datos del usuario
 */
export async function getCurrentUser() {
    return fetchAPI('/auth/me');
}

// ==================== HEALTH CHECK ====================

/**
 * Verificar estado del API
 * @returns {Promise<Object>} Estado del servidor
 */
export async function healthCheck() {
    const url = `${API_BASE_URL}/health`;
    const response = await fetch(url);
    return response.json();
}

// ==================== UTILIDADES ====================

/**
 * Formatear monto en pesos colombianos
 * @param {number} amount - Monto a formatear
 * @returns {string} Monto formateado
 */
export function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}

/**
 * Formatear fecha
 * @param {string|Date} date - Fecha a formatear
 * @returns {string} Fecha formateada
 */
export function formatDate(date) {
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    }).format(new Date(date));
}

/**
 * Formatear fecha y hora
 * @param {string|Date} datetime - Fecha/hora a formatear
 * @returns {string} Fecha/hora formateada
 */
export function formatDateTime(datetime) {
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(datetime));
}

/**
 * Descargar archivo blob
 * @param {Blob} blob - Archivo a descargar
 * @param {string} filename - Nombre del archivo
 */
export function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Exportar clase de error para manejo en componentes
export { ApiError };

// Exportar configuración
export const API_CONFIG = {
    BASE_URL: API_BASE_URL,
    VERSION: API_VERSION,
    TIMEOUT: 30000, // 30 segundos
};
