/**
 * Componente BankAccountForm
 * Formulario para crear y editar cuentas bancarias
 */

import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';

const PRESET_COLORS = [
    '#3B82F6', // Azul
    '#10B981', // Verde
    '#F59E0B', // Amarillo/Naranja
    '#EF4444', // Rojo
    '#8B5CF6', // Morado
    '#EC4899', // Rosa
    '#06B6D4', // Cyan
    '#F97316', // Naranja
    '#14B8A6', // Teal
    '#6366F1', // Indigo
];

export default function BankAccountForm({ account = null, onSuccess, onCancel }) {
    const { createBankAccount, updateBankAccount } = useApp();
    const isEditing = !!account;

    const [formData, setFormData] = useState({
        name: '',
        color: PRESET_COLORS[0],
        initial_balance: '',
        current_balance: '',
    });

    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Cargar datos si estamos editando
    useEffect(() => {
        if (account) {
            setFormData({
                name: account.name || '',
                color: account.color || PRESET_COLORS[0],
                initial_balance: account.initial_balance || '',
                current_balance: account.current_balance || '',
            });
        }
    }, [account]);

    /**
     * Manejar cambio en inputs
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));

        // Limpiar error del campo al escribir
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: null,
            }));
        }
    };

    /**
     * Validar formulario
     */
    const validate = () => {
        const newErrors = {};

        // Validar nombre
        if (!formData.name.trim()) {
            newErrors.name = 'El nombre de la cuenta es obligatorio';
        } else if (formData.name.trim().length > 100) {
            newErrors.name = 'El nombre no puede exceder 100 caracteres';
        }

        // Validar color
        const hexColorPattern = /^#[0-9A-Fa-f]{6}$/;
        if (!formData.color || !hexColorPattern.test(formData.color)) {
            newErrors.color = 'Selecciona un color válido';
        }

        // Validar saldo inicial
        if (formData.initial_balance === '' || formData.initial_balance === null) {
            newErrors.initial_balance = 'El saldo inicial es obligatorio';
        } else {
            const initialBalance = parseFloat(formData.initial_balance);
            if (isNaN(initialBalance) || initialBalance < 0) {
                newErrors.initial_balance = 'El saldo inicial debe ser un número positivo';
            }
        }

        // Validar saldo actual (opcional, pero si se provee debe ser válido)
        if (formData.current_balance !== '' && formData.current_balance !== null) {
            const currentBalance = parseFloat(formData.current_balance);
            if (isNaN(currentBalance) || currentBalance < 0) {
                newErrors.current_balance = 'El saldo actual debe ser un número positivo';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    /**
     * Manejar envío del formulario
     */
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validate()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const payload = {
                name: formData.name.trim(),
                color: formData.color.toUpperCase(),
                initial_balance: parseFloat(formData.initial_balance),
            };

            // Solo incluir current_balance si tiene valor
            if (formData.current_balance !== '' && formData.current_balance !== null) {
                payload.current_balance = parseFloat(formData.current_balance);
            }

            if (isEditing) {
                await updateBankAccount(account.id, payload);
            } else {
                await createBankAccount(payload);
            }

            // Resetear formulario
            setFormData({
                name: '',
                color: PRESET_COLORS[0],
                initial_balance: '',
                current_balance: '',
            });
            setErrors({});

            if (onSuccess) {
                onSuccess();
            }
        } catch (error) {
            console.error('Error saving bank account:', error);
            // El error ya se muestra en el contexto
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <form className="bank-account-form" onSubmit={handleSubmit}>
            {/* Nombre de la cuenta */}
            <div className="form-group">
                <label htmlFor="name" className="form-label">
                    Nombre de la cuenta *
                </label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    className={`form-input ${errors.name ? 'error' : ''}`}
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Ej: Cuenta Nómina, Ahorros, etc."
                    maxLength={100}
                />
                {errors.name && <span className="error-message">{errors.name}</span>}
            </div>

            {/* Color */}
            <div className="form-group">
                <label className="form-label">Color identificador *</label>
                <div className="color-picker">
                    {PRESET_COLORS.map(color => (
                        <button
                            key={color}
                            type="button"
                            className={`color-option ${formData.color === color ? 'selected' : ''}`}
                            style={{ backgroundColor: color }}
                            onClick={() => setFormData(prev => ({ ...prev, color }))}
                            title={color}
                        >
                            {formData.color === color && <i className="fas fa-check"></i>}
                        </button>
                    ))}
                </div>
                <div className="color-input-wrapper">
                    <input
                        type="text"
                        name="color"
                        className={`form-input color-hex-input ${errors.color ? 'error' : ''}`}
                        value={formData.color}
                        onChange={handleChange}
                        placeholder="#RRGGBB"
                        maxLength={7}
                    />
                    <div
                        className="color-preview"
                        style={{ backgroundColor: formData.color }}
                    ></div>
                </div>
                {errors.color && <span className="error-message">{errors.color}</span>}
            </div>

            {/* Saldo inicial */}
            <div className="form-group">
                <label htmlFor="initial_balance" className="form-label">
                    Saldo inicial *
                </label>
                <div className="input-with-prefix">
                    <span className="input-prefix">$</span>
                    <input
                        type="number"
                        id="initial_balance"
                        name="initial_balance"
                        className={`form-input ${errors.initial_balance ? 'error' : ''}`}
                        value={formData.initial_balance}
                        onChange={handleChange}
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                    />
                </div>
                {errors.initial_balance && (
                    <span className="error-message">{errors.initial_balance}</span>
                )}
            </div>

            {/* Saldo actual (opcional) */}
            <div className="form-group">
                <label htmlFor="current_balance" className="form-label">
                    Saldo actual <span className="optional-label">(opcional)</span>
                </label>
                <div className="input-with-prefix">
                    <span className="input-prefix">$</span>
                    <input
                        type="number"
                        id="current_balance"
                        name="current_balance"
                        className={`form-input ${errors.current_balance ? 'error' : ''}`}
                        value={formData.current_balance}
                        onChange={handleChange}
                        placeholder="Si es diferente al inicial"
                        step="0.01"
                        min="0"
                    />
                </div>
                {errors.current_balance && (
                    <span className="error-message">{errors.current_balance}</span>
                )}
                <small className="form-hint">
                    Si no lo especificas, será igual al saldo inicial
                </small>
            </div>

            {/* Botones */}
            <div className="form-actions">
                {onCancel && (
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={onCancel}
                        disabled={isSubmitting}
                    >
                        Cancelar
                    </button>
                )}
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? (
                        <>
                            <i className="fas fa-spinner fa-spin"></i>
                            {isEditing ? 'Actualizando...' : 'Creando...'}
                        </>
                    ) : (
                        <>
                            <i className={`fas fa-${isEditing ? 'save' : 'plus'}`}></i>
                            {isEditing ? 'Actualizar Cuenta' : 'Crear Cuenta'}
                        </>
                    )}
                </button>
            </div>
        </form>
    );
}
