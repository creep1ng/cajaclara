/**
 * Tarjeta de Cash/Balance
 * Muestra el balance total y botón para agregar cuenta
 */

import React from 'react';

export default function CashCard({ balance, onAddAccount }) {
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    return (
        <div className="cash-card">
            <div className="cash-header">
                <h2 className="cash-title">Cash</h2>
                <button className="btn btn-add-account" onClick={onAddAccount}>
                    <i className="fas fa-plus"></i>
                    Add Account
                </button>
            </div>
            <div className="cash-amount">{formatCurrency(balance)}</div>
        </div>
    );
}