/**
 * Servicio API para gestión de cuentas bancarias
 * Endpoints para operaciones CRUD de cuentas bancarias
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

// ==================== CUENTAS BANCARIAS ====================

/**
 * Listar todas las cuentas bancarias del usuario
 * @returns {Promise<Object>} Lista de cuentas bancarias con total
 */
export async function listBankAccounts() {
    return fetchAPI('/bank-accounts');
}

/**
 * Crear cuenta bancaria
 * @param {Object} accountData - Datos de la cuenta
 * @param {string} accountData.name - Nombre de la cuenta (obligatorio)
 * @param {string} accountData.color - Color en formato hexadecimal (obligatorio)
 * @param {number} accountData.initial_balance - Saldo inicial (obligatorio)
 * @param {number} accountData.current_balance - Saldo actual (opcional)
 * @returns {Promise<Object>} Cuenta bancaria creada
 */
export async function createBankAccount(accountData) {
    return fetchAPI('/bank-accounts', {
        method: 'POST',
        body: JSON.stringify(accountData),
    });
}

/**
 * Obtener detalle de cuenta bancaria
 * @param {string} accountId - UUID de la cuenta
 * @returns {Promise<Object>} Detalle de la cuenta bancaria
 */
export async function getBankAccount(accountId) {
    return fetchAPI(`/bank-accounts/${accountId}`);
}

/**
 * Actualizar cuenta bancaria
 * @param {string} accountId - UUID de la cuenta
 * @param {Object} updateData - Datos a actualizar
 * @param {string} updateData.name - Nombre de la cuenta (opcional)
 * @param {string} updateData.color - Color en formato hexadecimal (opcional)
 * @param {number} updateData.initial_balance - Saldo inicial (opcional)
 * @param {number} updateData.current_balance - Saldo actual (opcional)
 * @returns {Promise<Object>} Cuenta bancaria actualizada
 */
export async function updateBankAccount(accountId, updateData) {
    return fetchAPI(`/bank-accounts/${accountId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
    });
}

/**
 * Eliminar cuenta bancaria
 * @param {string} accountId - UUID de la cuenta
 * @returns {Promise<null>}
 */
export async function deleteBankAccount(accountId) {
    return fetchAPI(`/bank-accounts/${accountId}`, {
        method: 'DELETE',
    });
}
