/**
 * Contexto global de la aplicación CajaClara
 * Maneja estado global, autenticación, notificaciones y datos compartidos
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as api from '../services/api';

const AppContext = createContext();

export const useApp = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp debe ser usado dentro de AppProvider');
    }
    return context;
};

export const AppProvider = ({ children }) => {
    // Estado de autenticación
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [authLoading, setAuthLoading] = useState(true);

    // Estado de categorías (cache)
    const [categories, setCategories] = useState([]);
    const [categoriesLoading, setCategoriesLoading] = useState(false);

    // Estado de notificaciones
    const [notifications, setNotifications] = useState([]);

    // Estado de carga global
    const [globalLoading, setGlobalLoading] = useState(false);

    // Estado de transacciones (cache para dashboard)
    const [transactions, setTransactions] = useState([]);
    const [transactionsSummary, setTransactionsSummary] = useState(null);

    /**
     * Mostrar notificación
     */
    const showNotification = useCallback((message, type = 'info', duration = 5000) => {
        const id = Date.now();
        const notification = { id, message, type };

        setNotifications(prev => [...prev, notification]);

        if (duration > 0) {
            setTimeout(() => {
                removeNotification(id);
            }, duration);
        }

        return id;
    }, []);

    /**
     * Remover notificación
     */
    const removeNotification = useCallback((id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    }, []);

    /**
     * Login de usuario
     */
    const login = useCallback(async (email, password) => {
        try {
            setAuthLoading(true);
            const response = await api.login(email, password);
            setUser(response.user);
            setIsAuthenticated(true);
            showNotification('Inicio de sesión exitoso', 'success');
            return response;
        } catch (error) {
            showNotification(error.message || 'Error al iniciar sesión', 'error');
            throw error;
        } finally {
            setAuthLoading(false);
        }
    }, [showNotification]);

    /**
     * Login como invitado (MVP) - ahora usa credenciales reales
     */
    const loginAsGuest = useCallback(async () => {
        try {
            setAuthLoading(true);
            // Usar credenciales por defecto para MVP
            await login('demo@cajaclara.com', 'demo123');
        } catch (error) {
            showNotification('Error al entrar como invitado', 'error');
            throw error;
        } finally {
            setAuthLoading(false);
        }
    }, [login, showNotification]);

    /**
     * Logout de usuario
     */
    const logout = useCallback(() => {
        api.logout();
        setUser(null);
        setIsAuthenticated(false);
        setTransactions([]);
        setTransactionsSummary(null);
        showNotification('Sesión cerrada', 'info');
    }, [showNotification]);

    /**
     * Cargar categorías
     */
    const loadCategories = useCallback(async (transactionType = null, force = false) => {
        // Si ya tenemos categorías y no forzamos recarga, no hacer nada
        if (categories.length > 0 && !force) {
            return categories;
        }

        try {
            setCategoriesLoading(true);
            const response = await api.listCategories(transactionType);
            setCategories(response.categories || []);
            return response.categories || [];
        } catch (error) {
            showNotification('Error al cargar categorías', 'error');
            console.error('Error loading categories:', error);
            return [];
        } finally {
            setCategoriesLoading(false);
        }
    }, [categories, showNotification]);

    /**
     * Obtener categorías por tipo
     */
    const getCategoriesByType = useCallback((type) => {
        return categories.filter(cat => cat.transaction_type === type);
    }, [categories]);

    /**
     * Crear transacción
     */
    const createTransaction = useCallback(async (transactionData) => {
        try {
            setGlobalLoading(true);
            const transaction = await api.createManualTransaction(transactionData);

            // Actualizar lista local
            setTransactions(prev => [transaction, ...prev]);

            showNotification('Transacción registrada exitosamente', 'success');
            return transaction;
        } catch (error) {
            showNotification(error.message || 'Error al crear transacción', 'error');
            throw error;
        } finally {
            setGlobalLoading(false);
        }
    }, [showNotification]);

    /**
     * Actualizar transacción
     */
    const updateTransaction = useCallback(async (transactionId, updateData) => {
        try {
            setGlobalLoading(true);
            const updated = await api.updateTransaction(transactionId, updateData);

            // Actualizar lista local
            setTransactions(prev =>
                prev.map(t => t.id === transactionId ? updated : t)
            );

            showNotification('Transacción actualizada', 'success');
            return updated;
        } catch (error) {
            showNotification(error.message || 'Error al actualizar transacción', 'error');
            throw error;
        } finally {
            setGlobalLoading(false);
        }
    }, [showNotification]);

    /**
     * Eliminar transacción
     */
    const deleteTransaction = useCallback(async (transactionId) => {
        try {
            setGlobalLoading(true);
            await api.deleteTransaction(transactionId);

            // Remover de lista local
            setTransactions(prev => prev.filter(t => t.id !== transactionId));

            showNotification('Transacción eliminada', 'success');
        } catch (error) {
            showNotification(error.message || 'Error al eliminar transacción', 'error');
            throw error;
        } finally {
            setGlobalLoading(false);
        }
    }, [showNotification]);

    /**
     * Cargar transacciones
     */
    const loadTransactions = useCallback(async (filters = {}, page = 1, limit = 20) => {
        try {
            setGlobalLoading(true);
            const response = await api.listTransactions(filters, page, limit);

            if (page === 1) {
                setTransactions(response.transactions || []);
            } else {
                setTransactions(prev => [...prev, ...(response.transactions || [])]);
            }

            setTransactionsSummary(response.summary);

            return response;
        } catch (error) {
            showNotification('Error al cargar transacciones', 'error');
            throw error;
        } finally {
            setGlobalLoading(false);
        }
    }, [showNotification]);

    /**
     * Refrescar datos del dashboard
     */
    const refreshDashboard = useCallback(async () => {
        try {
            setGlobalLoading(true);

            // Cargar categorías si no están cargadas
            if (categories.length === 0) {
                await loadCategories();
            }

            // Cargar transacciones recientes
            const currentMonth = new Date();
            currentMonth.setDate(1);
            currentMonth.setHours(0, 0, 0, 0);

            const nextMonth = new Date(currentMonth);
            nextMonth.setMonth(nextMonth.getMonth() + 1);

            const filters = {
                start_date: currentMonth.toISOString(),
                end_date: nextMonth.toISOString(),
            };

            await loadTransactions(filters, 1, 100);

            showNotification('Dashboard actualizado', 'success', 2000);
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
        } finally {
            setGlobalLoading(false);
        }
    }, [categories.length, loadCategories, loadTransactions, showNotification]);

    // Verificar autenticación al montar
    useEffect(() => {
        const checkAuth = async () => {
            try {
                if (api.isAuthenticated()) {
                    // Verificar token con el backend
                    const userData = await api.getCurrentUser();
                    setUser(userData);
                    setIsAuthenticated(true);
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                api.logout();
            } finally {
                setAuthLoading(false);
            }
        };

        checkAuth();
    }, []);

    // Cargar categorías al autenticarse
    useEffect(() => {
        if (isAuthenticated && categories.length === 0) {
            loadCategories();
        }
    }, [isAuthenticated, categories.length, loadCategories]);

    const value = {
        // Autenticación
        user,
        isAuthenticated,
        authLoading,
        login,
        loginAsGuest,
        logout,

        // Categorías
        categories,
        categoriesLoading,
        loadCategories,
        getCategoriesByType,

        // Transacciones
        transactions,
        transactionsSummary,
        createTransaction,
        updateTransaction,
        deleteTransaction,
        loadTransactions,
        refreshDashboard,

        // Notificaciones
        notifications,
        showNotification,
        removeNotification,

        // Loading
        globalLoading,
        setGlobalLoading,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};