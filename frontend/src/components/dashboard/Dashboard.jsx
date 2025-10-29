/**
 * Dashboard Principal
 * Integra todos los componentes del dashboard
 */

import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import Header from './Header';
import ApiStatus from './ApiStatus';
import WorkflowInfo from './WorkflowInfo';
import CashCard from './CashCard';
import GaugesCard from './GaugesCard';
import DateSelector from './DateSelector';
import AccountsCard from './AccountsCard';

export default function Dashboard({ onNavigate, onOpenModal }) {
    const { transactions, refreshDashboard } = useApp();
    const [selectedDate, setSelectedDate] = useState({
        month: new Date().getMonth(),
        year: new Date().getFullYear(),
    });
    const [accounts, setAccounts] = useState([]);
    const [dashboardData, setDashboardData] = useState({
        balance: 0,
        gauges: {
            balance: { percentage: 0, amount: 0 },
            cashflow: { percentage: 0, amount: 0 },
            spending: { percentage: 0, amount: 0 },
        },
    });

    // Calcular datos del dashboard basado en transacciones
    useEffect(() => {
        calculateDashboardData();
    }, [transactions, selectedDate]);

    const calculateDashboardData = () => {
        if (!transactions || transactions.length === 0) {
            setDashboardData({
                balance: 0,
                gauges: {
                    balance: { percentage: 65, amount: 650000 },
                    cashflow: { percentage: 40, amount: 400000 },
                    spending: { percentage: 25, amount: 250000 },
                },
            });
            return;
        }

        // Filtrar transacciones del mes seleccionado
        const filteredTransactions = transactions.filter((t) => {
            const transactionDate = new Date(t.transaction_date);
            return (
                transactionDate.getMonth() === selectedDate.month &&
                transactionDate.getFullYear() === selectedDate.year &&
                !t.deleted_at
            );
        });

        // Calcular totales
        let totalIncome = 0;
        let totalExpense = 0;

        filteredTransactions.forEach((t) => {
            if (t.transaction_type === 'income') {
                totalIncome += parseFloat(t.amount);
            } else if (t.transaction_type === 'expense') {
                totalExpense += parseFloat(t.amount);
            }
        });

        const balance = totalIncome - totalExpense;
        const maxAmount = Math.max(totalIncome, totalExpense, 1000000);

        setDashboardData({
            balance,
            gauges: {
                balance: {
                    percentage: Math.min(100, Math.abs(balance / maxAmount) * 100),
                    amount: Math.abs(balance),
                },
                cashflow: {
                    percentage: Math.min(100, (totalIncome / maxAmount) * 100),
                    amount: totalIncome,
                },
                spending: {
                    percentage: Math.min(100, (totalExpense / maxAmount) * 100),
                    amount: totalExpense,
                },
            },
        });
    };

    const handleRegisterAction = (action) => {
        switch (action) {
            case 'manual':
                onOpenModal('manualRecord');
                break;
            case 'visual':
                onOpenModal('visualRecord');
                break;
            case 'view':
                onNavigate('records');
                break;
            default:
                break;
        }
    };

    const handleAddAccount = () => {
        onOpenModal('addAccount');
    };

    const handleDateChange = (newDate) => {
        setSelectedDate(newDate);
        // Podría disparar recarga de transacciones filtradas
        refreshDashboard();
    };

    return (
        <div className="dashboard-container" style={{ display: 'block' }}>
            <Header
                activePage="dashboard"
                onNavigate={onNavigate}
                onRegisterAction={handleRegisterAction}
            />

            <div className="container">
                <ApiStatus isConnected={true} />

                <WorkflowInfo />

                <div className="main-content">
                    <div className="dashboard-left">
                        <CashCard
                            balance={dashboardData.balance}
                            onAddAccount={handleAddAccount}
                        />
                        <GaugesCard
                            balance={dashboardData.gauges.balance}
                            cashflow={dashboardData.gauges.cashflow}
                            spending={dashboardData.gauges.spending}
                        />
                    </div>

                    <div className="dashboard-right">
                        <DateSelector
                            selectedMonth={selectedDate.month}
                            selectedYear={selectedDate.year}
                            onDateChange={handleDateChange}
                        />
                        <AccountsCard
                            accounts={accounts}
                            onAddAccount={handleAddAccount}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}