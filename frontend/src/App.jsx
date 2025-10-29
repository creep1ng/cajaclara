/**
 * Componente Principal de la Aplicación
 * Maneja el enrutamiento y la integración de todos los componentes
 */

import React, { useState } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import LoginPage from './components/auth/LoginPage';
import Dashboard from './components/dashboard/Dashboard';
import NotificationContainer from './components/common/NotificationContainer';
import Loading from './components/common/Loading';
import ManualRecordModal from './components/transactions/ManualRecordModal';
import VisualRecordModal from './components/transactions/VisualRecordModal';

// Importar Font Awesome
import './styles/globals.css';

function AppContent() {
    const { isAuthenticated, authLoading } = useApp();
    const [activePage, setActivePage] = useState('dashboard');
    const [activeModal, setActiveModal] = useState(null);

    const handleNavigate = (page) => {
        setActivePage(page);
    };

    const handleOpenModal = (modalName) => {
        setActiveModal(modalName);
    };

    const handleCloseModal = () => {
        setActiveModal(null);
    };

    const handleModalSuccess = () => {
        // Refresh dashboard data
        // This is automatically handled by AppContext
    };

    // Mostrar loading mientras se verifica autenticación
    if (authLoading) {
        return <Loading fullscreen />;
    }

    // Si no está autenticado, mostrar página de login
    if (!isAuthenticated) {
        return (
            <>
                <LoginPage />
                <NotificationContainer />
            </>
        );
    }

    // Usuario autenticado - mostrar aplicación
    return (
        <>
            {/* Página Activa */}
            {activePage === 'dashboard' && (
                <Dashboard onNavigate={handleNavigate} onOpenModal={handleOpenModal} />
            )}

            {activePage === 'records' && (
                <div className="view-records-container" style={{ display: 'block' }}>
                    {/* TransactionsPage component - to be implemented */}
                    <div className="container">
                        <div style={{ padding: '40px', textAlign: 'center' }}>
                            <h2>Ver Registros</h2>
                            <p>Esta página se implementará próximamente</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => handleNavigate('dashboard')}
                            >
                                Volver al Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {activePage === 'accounts' && (
                <div className="accounts-container" style={{ display: 'block' }}>
                    {/* AccountsPage component - to be implemented */}
                    <div className="container">
                        <div style={{ padding: '40px', textAlign: 'center' }}>
                            <h2>Accounts</h2>
                            <p>Esta página se implementará próximamente</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => handleNavigate('dashboard')}
                            >
                                Volver al Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {activePage === 'reports' && (
                <div className="reports-container" style={{ display: 'block' }}>
                    {/* ReportsPage component - to be implemented */}
                    <div className="container">
                        <div style={{ padding: '40px', textAlign: 'center' }}>
                            <h2>Reports</h2>
                            <p>Esta página se implementará próximamente</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => handleNavigate('dashboard')}
                            >
                                Volver al Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modales */}
            <ManualRecordModal
                isOpen={activeModal === 'manualRecord'}
                onClose={handleCloseModal}
                onSuccess={handleModalSuccess}
            />

            <VisualRecordModal
                isOpen={activeModal === 'visualRecord'}
                onClose={handleCloseModal}
                onSuccess={handleModalSuccess}
            />

            {/* Modal de Agregar Cuenta - Placeholder */}
            {activeModal === 'addAccount' && (
                <div
                    className="modal"
                    style={{ display: 'flex' }}
                    onClick={handleCloseModal}
                >
                    <div
                        className="modal-content"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="modal-header">
                            <h3 className="modal-title">Agregar Nueva Cuenta</h3>
                            <button className="modal-close" onClick={handleCloseModal}>
                                &times;
                            </button>
                        </div>
                        <div className="modal-body">
                            <p>Funcionalidad de agregar cuenta próximamente</p>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-cancel" onClick={handleCloseModal}>
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Container de Notificaciones */}
            <NotificationContainer />

            {/* MVP Badge */}
            <div className="mvp-badge">
                <i className="fas fa-rocket"></i> MVP CajaClara
            </div>
        </>
    );
}

function App() {
    return (
        <AppProvider>
            <AppContent />
        </AppProvider>
    );
}

export default App;
