/**
 * Tarjeta de Cuentas
 * Muestra lista de cuentas con sus balances
 */

import React from 'react';

export default function AccountsCard({ accounts, onAddAccount }) {
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    return (
        <div className="accounts-card">
            <div className="accounts-header">
                <h3 className="accounts-title">Accounts</h3>
                <button className="btn btn-add-account" onClick={onAddAccount}>
                    <i className="fas fa-plus"></i>
                </button>
            </div>

            <div className="account-list">
                {accounts && accounts.length > 0 ? (
                    accounts.map((account) => (
                        <div key={account.id} className="account-item">
                            <span className="account-name">{account.name}</span>
                            <span className="account-amount">
                                {formatCurrency(account.current_balance || 0)}
                            </span>
                        </div>
                    ))
                ) : (
                    <>
                        <div className="account-item">
                            <span className="account-name">Ahorros</span>
                            <span className="account-amount">COP 0.00</span>
                        </div>
                        <div className="account-item">
                            <span className="account-name">Corriente</span>
                            <span className="account-amount">COP 0.00</span>
                        </div>
                        <div className="account-item">
                            <span className="account-name">Tarjeta de Crédito</span>
                            <span className="account-amount">COP 0.00</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}