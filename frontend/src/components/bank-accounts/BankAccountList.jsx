/**
 * Componente BankAccountList
 * Lista todas las cuentas bancarias del usuario con opciones de gestión
 */

import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import BankAccountCard from './BankAccountCard';
import BankAccountForm from './BankAccountForm';
import Modal from '../common/Modal';
import Loading from '../common/Loading';

export default function BankAccountList() {
    const {
        bankAccounts,
        bankAccountsLoading,
        loadBankAccounts,
        deleteBankAccount,
        showNotification,
    } = useApp();

    const [isFormModalOpen, setIsFormModalOpen] = useState(false);
    const [editingAccount, setEditingAccount] = useState(null);
    const [deletingAccount, setDeletingAccount] = useState(null);

    // Cargar cuentas al montar el componente
    useEffect(() => {
        loadBankAccounts();
    }, [loadBankAccounts]);

    /**
     * Abrir modal para crear nueva cuenta
     */
    const handleCreate = () => {
        setEditingAccount(null);
        setIsFormModalOpen(true);
    };

    /**
     * Abrir modal para editar cuenta
     */
    const handleEdit = (account) => {
        setEditingAccount(account);
        setIsFormModalOpen(true);
    };

    /**
     * Confirmar eliminación de cuenta
     */
    const handleDeleteClick = (account) => {
        setDeletingAccount(account);
    };

    /**
     * Ejecutar eliminación
     */
    const handleDeleteConfirm = async () => {
        if (!deletingAccount) return;

        try {
            await deleteBankAccount(deletingAccount.id);
            setDeletingAccount(null);
        } catch (error) {
            console.error('Error deleting bank account:', error);
        }
    };

    /**
     * Cancelar eliminación
     */
    const handleDeleteCancel = () => {
        setDeletingAccount(null);
    };

    /**
     * Cerrar modal de formulario
     */
    const handleFormSuccess = () => {
        setIsFormModalOpen(false);
        setEditingAccount(null);
        loadBankAccounts(true); // Forzar recarga
    };

    const handleFormCancel = () => {
        setIsFormModalOpen(false);
        setEditingAccount(null);
    };

    /**
     * Calcular total de saldos
     */
    const getTotalBalance = () => {
        return bankAccounts.reduce(
            (sum, account) => sum + parseFloat(account.current_balance || 0),
            0
        );
    };

    /**
     * Formatear número como moneda
     */
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    };

    if (bankAccountsLoading && bankAccounts.length === 0) {
        return (
            <div className="bank-accounts-container">
                <Loading message="Cargando cuentas bancarias..." />
            </div>
        );
    }

    return (
        <div className="bank-accounts-container">
            <div className="bank-accounts-header">
                <div className="header-content">
                    <h1 className="page-title">
                        <i className="fas fa-university"></i>
                        Mis Cuentas Bancarias
                    </h1>
                    <p className="page-subtitle">
                        Gestiona tus cuentas y visualiza tus saldos
                    </p>
                </div>
                <button className="btn btn-primary" onClick={handleCreate}>
                    <i className="fas fa-plus"></i>
                    Nueva Cuenta
                </button>
            </div>

            {/* Resumen total */}
            {bankAccounts.length > 0 && (
                <div className="total-balance-card">
                    <div className="total-balance-content">
                        <span className="total-balance-label">Saldo Total</span>
                        <span className="total-balance-amount">
                            {formatCurrency(getTotalBalance())}
                        </span>
                    </div>
                    <div className="total-balance-info">
                        <i className="fas fa-wallet"></i>
                        <span>{bankAccounts.length} cuenta{bankAccounts.length !== 1 ? 's' : ''}</span>
                    </div>
                </div>
            )}

            {/* Lista de cuentas */}
            {bankAccounts.length === 0 ? (
                <div className="empty-state">
                    <i className="fas fa-university empty-icon"></i>
                    <h3 className="empty-title">No tienes cuentas bancarias</h3>
                    <p className="empty-description">
                        Crea tu primera cuenta para comenzar a gestionar tus finanzas
                    </p>
                    <button className="btn btn-primary" onClick={handleCreate}>
                        <i className="fas fa-plus"></i>
                        Crear primera cuenta
                    </button>
                </div>
            ) : (
                <div className="bank-accounts-grid">
                    {bankAccounts.map(account => (
                        <BankAccountCard
                            key={account.id}
                            account={account}
                            onEdit={handleEdit}
                            onDelete={handleDeleteClick}
                        />
                    ))}
                </div>
            )}

            {/* Modal de formulario */}
            <Modal
                isOpen={isFormModalOpen}
                onClose={handleFormCancel}
                title={editingAccount ? 'Editar Cuenta Bancaria' : 'Nueva Cuenta Bancaria'}
                size="medium"
            >
                <BankAccountForm
                    account={editingAccount}
                    onSuccess={handleFormSuccess}
                    onCancel={handleFormCancel}
                />
            </Modal>

            {/* Modal de confirmación de eliminación */}
            <Modal
                isOpen={!!deletingAccount}
                onClose={handleDeleteCancel}
                title="Confirmar Eliminación"
                size="small"
            >
                <div className="delete-confirmation">
                    <p className="delete-message">
                        ¿Estás seguro de que deseas eliminar la cuenta{' '}
                        <strong>{deletingAccount?.name}</strong>?
                    </p>
                    <p className="delete-warning">
                        <i className="fas fa-exclamation-triangle"></i>
                        Esta acción no se puede deshacer.
                    </p>
                    <div className="delete-actions">
                        <button
                            className="btn btn-secondary"
                            onClick={handleDeleteCancel}
                        >
                            Cancelar
                        </button>
                        <button
                            className="btn btn-danger"
                            onClick={handleDeleteConfirm}
                        >
                            <i className="fas fa-trash"></i>
                            Eliminar Cuenta
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
