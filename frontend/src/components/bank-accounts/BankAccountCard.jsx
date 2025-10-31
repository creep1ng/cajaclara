/**
 * Componente BankAccountCard
 * Tarjeta individual que muestra información de una cuenta bancaria
 */

import React from 'react';

export default function BankAccountCard({ account, onEdit, onDelete }) {
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

    /**
     * Calcular diferencia entre saldo actual e inicial
     */
    const getBalanceDifference = () => {
        const diff = parseFloat(account.current_balance) - parseFloat(account.initial_balance);
        return diff;
    };

    const balanceDiff = getBalanceDifference();
    const hasGain = balanceDiff > 0;
    const hasLoss = balanceDiff < 0;

    return (
        <div className="bank-account-card" style={{ borderLeftColor: account.color }}>
            <div className="bank-account-header">
                <div className="bank-account-color" style={{ backgroundColor: account.color }}></div>
                <div className="bank-account-info">
                    <h3 className="bank-account-name">{account.name}</h3>
                    <p className="bank-account-id">ID: {account.id.substring(0, 8)}...</p>
                </div>
                <div className="bank-account-actions">
                    <button
                        className="btn-icon"
                        onClick={() => onEdit(account)}
                        title="Editar cuenta"
                    >
                        <i className="fas fa-edit"></i>
                    </button>
                    <button
                        className="btn-icon btn-danger"
                        onClick={() => onDelete(account)}
                        title="Eliminar cuenta"
                    >
                        <i className="fas fa-trash"></i>
                    </button>
                </div>
            </div>

            <div className="bank-account-balances">
                <div className="balance-item">
                    <span className="balance-label">Saldo inicial</span>
                    <span className="balance-value">
                        {formatCurrency(account.initial_balance)}
                    </span>
                </div>
                <div className="balance-item">
                    <span className="balance-label">Saldo actual</span>
                    <span className="balance-value balance-current">
                        {formatCurrency(account.current_balance)}
                    </span>
                </div>
            </div>

            {balanceDiff !== 0 && (
                <div className={`balance-diff ${hasGain ? 'positive' : hasLoss ? 'negative' : ''}`}>
                    <i className={`fas fa-${hasGain ? 'arrow-up' : 'arrow-down'}`}></i>
                    <span>
                        {hasGain ? '+' : ''}{formatCurrency(Math.abs(balanceDiff))}
                    </span>
                    <span className="diff-label">
                        {hasGain ? 'ganancia' : 'pérdida'}
                    </span>
                </div>
            )}

            <div className="bank-account-footer">
                <small className="text-muted">
                    Actualizada: {new Date(account.updated_at).toLocaleDateString('es-CO', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                    })}
                </small>
            </div>
        </div>
    );
}
