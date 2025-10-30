/**
 * Modal de Registro Manual
 * Permite registrar transacciones manualmente (Gasto, Ingreso, Transferencia)
 */

import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import Modal from '../common/Modal';

const TRANSACTION_TYPES = [
    { id: 'expense', label: 'Gasto' },
    { id: 'income', label: 'Ingreso' },
    { id: 'transfer', label: 'Transferencia' },
];

const PAYMENT_TYPES = [
    { value: 'cash', label: 'Efectivo' },
    { value: 'card', label: 'Tarjeta' },
    { value: 'transfer', label: 'Transferencia' },
    { value: 'check', label: 'Cheque' },
];

const PAYMENT_STATUS = [
    { value: 'cleared', label: 'Completado' },
    { value: 'pending', label: 'Pendiente' },
    { value: 'failed', label: 'Fallido' },
];

export default function ManualRecordModal({ isOpen, onClose, onSuccess }) {
    const { 
        categories, 
        getCategoriesByType, 
        createTransaction, 
        showNotification,
        bankAccounts,
        bankAccountsLoading,
        loadBankAccounts
    } = useApp();
    const [activeType, setActiveType] = useState('expense');
    const [loading, setLoading] = useState(false);
    const [labels, setLabels] = useState([]);
    const [formData, setFormData] = useState({
        amount: '',
        bank_account_id: '',
        category_id: '',
        description: '',
        payer: '',
        payment_type: 'cash',
        payment_status: 'cleared',
        transaction_date: '',
        from_bank_account_id: '',
        to_bank_account_id: '',
    });

    // Inicializar fecha/hora actual y cargar cuentas bancarias
    useEffect(() => {
        if (isOpen) {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');

            setFormData((prev) => ({
                ...prev,
                transaction_date: `${year}-${month}-${day}T${hours}:${minutes}`,
            }));

            // Cargar cuentas bancarias si no están cargadas
            if (bankAccounts.length === 0 && !bankAccountsLoading) {
                loadBankAccounts();
            }
        }
    }, [isOpen, bankAccounts.length, bankAccountsLoading, loadBankAccounts]);

    const handleTypeChange = (type) => {
        setActiveType(type);
        setFormData((prev) => ({
            ...prev,
            category_id: '',
        }));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleCategorySelect = (categoryId) => {
        setFormData((prev) => ({
            ...prev,
            category_id: categoryId,
        }));
    };

    const handleLabelKeyDown = (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const value = e.target.value.trim();
            if (value && !labels.includes(value)) {
                setLabels([...labels, value]);
                e.target.value = '';
            }
        }
    };

    const removeLabel = (index) => {
        setLabels(labels.filter((_, i) => i !== index));
    };

    const validateForm = () => {
        if (!formData.amount || parseFloat(formData.amount) <= 0) {
            showNotification('Por favor ingresa un monto válido', 'error');
            return false;
        }

        if (activeType === 'transfer') {
            if (!formData.from_bank_account_id) {
                showNotification('Por favor selecciona una cuenta de salida', 'error');
                return false;
            }
            if (!formData.to_bank_account_id) {
                showNotification('Por favor selecciona una cuenta de entrada', 'error');
                return false;
            }
            if (formData.from_bank_account_id === formData.to_bank_account_id) {
                showNotification('La cuenta de salida y entrada no pueden ser iguales', 'error');
                return false;
            }
        } else {
            if (!formData.bank_account_id) {
                showNotification('Por favor selecciona una cuenta bancaria', 'error');
                return false;
            }
            if (!formData.category_id) {
                showNotification('Por favor selecciona una categoría', 'error');
                return false;
            }
        }
        return true;
    };

    const handleSubmit = async (addAnother = false) => {
        if (!validateForm()) return;

        setLoading(true);
        try {
            const transactionData = {
                amount: parseFloat(formData.amount),
                currency: 'COP',
                description: formData.description || undefined,
                transaction_type: activeType,
                classification: 'personal', // Por ahora, hardcoded
                transaction_date: new Date(formData.transaction_date).toISOString(),
                tags: labels.length > 0 ? labels : undefined,
            };

            // Agregar campos específicos según el tipo de transacción
            if (activeType === 'transfer') {
                transactionData.from_bank_account_id = formData.from_bank_account_id;
                transactionData.to_bank_account_id = formData.to_bank_account_id;
            } else {
                transactionData.bank_account_id = formData.bank_account_id;
                transactionData.category_id = formData.category_id;
            }

            await createTransaction(transactionData);
            showNotification('✅ Registro agregado exitosamente', 'success');

            if (onSuccess) {
                onSuccess();
            }

            if (addAnother) {
                // Resetear formulario pero mantener tipo de transacción
                setFormData({
                    amount: '',
                    bank_account_id: formData.bank_account_id,
                    category_id: '',
                    description: '',
                    payer: '',
                    payment_type: 'cash',
                    payment_status: 'cleared',
                    transaction_date: formData.transaction_date,
                    from_bank_account_id: '',
                    to_bank_account_id: '',
                });
                setLabels([]);
            } else {
                onClose();
            }
        } catch (error) {
            console.error('Error creating transaction:', error);
            showNotification('❌ Error al guardar el registro', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        if (!loading) {
            setFormData({
                amount: '',
                bank_account_id: '',
                category_id: '',
                description: '',
                payer: '',
                payment_type: 'cash',
                payment_status: 'cleared',
                transaction_date: '',
                from_bank_account_id: '',
                to_bank_account_id: '',
            });
            setLabels([]);
            onClose();
        }
    };

    const typeCategories = getCategoriesByType(activeType);

    return (
        <Modal isOpen={isOpen} onClose={handleClose} size="large">
            <div className="manual-record-header">
                <h2 className="manual-record-title">Registro Manual</h2>
                <div className="record-tabs">
                    {TRANSACTION_TYPES.map((type) => (
                        <button
                            key={type.id}
                            className={`btn record-tab-btn ${activeType === type.id ? 'active' : ''}`}
                            onClick={() => handleTypeChange(type.id)}
                            disabled={loading}
                        >
                            {type.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="manual-record-body">
                {/* Sección Izquierda */}
                <div className="record-left-section">
                    {/* Monto */}
                    <div className="form-group">
                        <label className="form-label">
                            Monto <span className="required">*</span>
                        </label>
                        <div className="amount-input-group">
                            <span className="amount-currency">$</span>
                            <input
                                type="number"
                                name="amount"
                                className="amount-input"
                                placeholder="0.00"
                                step="0.01"
                                value={formData.amount}
                                onChange={handleChange}
                                disabled={loading}
                            />
                        </div>
                    </div>

                    {/* Cuenta Bancaria - Solo para Gasto e Ingreso */}
                    {activeType !== 'transfer' && (
                        <div className="form-group">
                            <label className="form-label">
                                Cuenta Bancaria <span className="required">*</span>
                            </label>
                            <div className="select-wrapper">
                                <select
                                    name="bank_account_id"
                                    className="form-select"
                                    value={formData.bank_account_id}
                                    onChange={handleChange}
                                    disabled={loading || bankAccountsLoading}
                                >
                                    <option value="">Seleccionar cuenta...</option>
                                    {bankAccounts.map((account) => (
                                        <option key={account.id} value={account.id}>
                                            {account.name} - ${account.saldo_actual?.toLocaleString('es-CO')}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            {bankAccounts.length === 0 && !bankAccountsLoading && (
                                <p className="form-hint" style={{ color: 'var(--error)', marginTop: '8px' }}>
                                    ⚠️ No hay cuentas bancarias. Crea una en Accounts.
                                </p>
                            )}
                        </div>
                    )}

                    {/* Cuentas de Transferencia - Solo para Transferencia */}
                    {activeType === 'transfer' && (
                        <>
                            <div className="form-group">
                                <label className="form-label">
                                    Cuenta de Salida <span className="required">*</span>
                                </label>
                                <div className="select-wrapper">
                                    <select
                                        name="from_bank_account_id"
                                        className="form-select"
                                        value={formData.from_bank_account_id}
                                        onChange={handleChange}
                                        disabled={loading || bankAccountsLoading}
                                    >
                                        <option value="">Seleccionar cuenta...</option>
                                        {bankAccounts.map((account) => (
                                            <option key={account.id} value={account.id}>
                                                {account.name} - ${account.saldo_actual?.toLocaleString('es-CO')}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                {bankAccounts.length === 0 && !bankAccountsLoading && (
                                    <p className="form-hint" style={{ color: 'var(--error)', marginTop: '8px' }}>
                                        ⚠️ No hay cuentas bancarias. Crea una en Accounts.
                                    </p>
                                )}
                            </div>

                            <div className="form-group">
                                <label className="form-label">
                                    Cuenta de Entrada <span className="required">*</span>
                                </label>
                                <div className="select-wrapper">
                                    <select
                                        name="to_bank_account_id"
                                        className="form-select"
                                        value={formData.to_bank_account_id}
                                        onChange={handleChange}
                                        disabled={loading || bankAccountsLoading}
                                    >
                                        <option value="">Seleccionar cuenta...</option>
                                        {bankAccounts.map((account) => (
                                            <option key={account.id} value={account.id}>
                                                {account.name} - ${account.saldo_actual?.toLocaleString('es-CO')}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                {bankAccounts.length === 0 && !bankAccountsLoading && (
                                    <p className="form-hint" style={{ color: 'var(--error)', marginTop: '8px' }}>
                                        ⚠️ No hay cuentas bancarias. Crea una en Accounts.
                                    </p>
                                )}
                            </div>
                        </>
                    )}

                    {/* Categoría - Solo para Gasto e Ingreso */}
                    {activeType !== 'transfer' && (
                        <div className="form-group">
                            <label className="form-label">
                                Categoría <span className="required">*</span>
                            </label>
                            <div className="select-wrapper">
                                <select
                                    name="category_id"
                                    className="form-select"
                                    value={formData.category_id}
                                    onChange={handleChange}
                                    disabled={loading}
                                >
                                    <option value="">Seleccionar categoría</option>
                                    {typeCategories.map((cat) => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Category Pills */}
                            <div className="category-pills">
                                {typeCategories.slice(0, 6).map((cat) => (
                                    <div
                                        key={cat.id}
                                        className={`category-pill ${formData.category_id === cat.id ? 'selected' : ''
                                            }`}
                                        onClick={() => handleCategorySelect(cat.id)}
                                    >
                                        {cat.name}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Etiquetas */}
                    <div className="form-group">
                        <label className="form-label">Etiquetas</label>
                        <div className="labels-input-container">
                            <div className="labels-display">
                                {labels.map((label, index) => (
                                    <div key={index} className="label-tag">
                                        {label}
                                        <span
                                            className="label-remove"
                                            onClick={() => removeLabel(index)}
                                        >
                                            ×
                                        </span>
                                    </div>
                                ))}
                                <input
                                    type="text"
                                    className="label-input"
                                    placeholder="Agregar etiquetas..."
                                    onKeyDown={handleLabelKeyDown}
                                    disabled={loading}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Fecha y Hora */}
                    <div className="form-group">
                        <label className="form-label">Fecha y Hora</label>
                        <input
                            type="datetime-local"
                            name="transaction_date"
                            className="datetime-input"
                            value={formData.transaction_date}
                            onChange={handleChange}
                            disabled={loading}
                        />
                    </div>
                </div>

                {/* Sección Derecha */}
                <div className="record-right-section">
                    <h3 className="other-details-title">Otros detalles</h3>

                    {/* Nota */}
                    <div className="form-group">
                        <label className="form-label">Nota</label>
                        <textarea
                            name="description"
                            className="form-input"
                            rows="3"
                            placeholder="Agregar una nota..."
                            value={formData.description}
                            onChange={handleChange}
                            disabled={loading}
                        />
                    </div>

                    {/* Pagador */}
                    <div className="form-group">
                        <label className="form-label">Pagador</label>
                        <input
                            type="text"
                            name="payer"
                            className="form-input"
                            placeholder="Ingrese nombre del pagador"
                            value={formData.payer}
                            onChange={handleChange}
                            disabled={loading}
                        />
                    </div>

                    {/* Tipo de pago */}
                    <div className="form-group">
                        <label className="form-label">Tipo de pago</label>
                        <div className="select-wrapper">
                            <select
                                name="payment_type"
                                className="form-select"
                                value={formData.payment_type}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                {PAYMENT_TYPES.map((type) => (
                                    <option key={type.value} value={type.value}>
                                        {type.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Estado del pago */}
                    <div className="form-group">
                        <label className="form-label">Estado del pago</label>
                        <div className="select-wrapper">
                            <select
                                name="payment_status"
                                className="form-select"
                                value={formData.payment_status}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                {PAYMENT_STATUS.map((status) => (
                                    <option key={status.value} value={status.value}>
                                        {status.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="manual-record-footer">
                <div className="footer-info">
                    <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                        Todos los campos marcados con * son obligatorios
                    </span>
                </div>
                <div className="footer-actions">
                    <button
                        className="btn btn-cancel-record"
                        onClick={handleClose}
                        disabled={loading}
                    >
                        Cancelar
                    </button>
                    <button
                        className="btn btn-add-record-confirm"
                        onClick={() => handleSubmit(false)}
                        disabled={loading}
                    >
                        {loading ? 'Guardando...' : 'Agregar registro'}
                    </button>
                    <button
                        className="btn btn-add-another"
                        onClick={() => handleSubmit(true)}
                        disabled={loading}
                    >
                        Agregar y crear otro
                    </button>
                </div>
            </div>
        </Modal>
    );
}