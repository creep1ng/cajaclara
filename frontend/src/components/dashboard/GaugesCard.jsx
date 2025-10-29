/**
 * Tarjeta de Medidores (Gauges)
 * Muestra Balance, Cash Flow y Spending como medidores semicirculares
 */

import React, { useEffect, useRef } from 'react';

export default function GaugesCard({ balance, cashflow, spending }) {
    const balanceRef = useRef(null);
    const cashflowRef = useRef(null);
    const spendingRef = useRef(null);

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    const animateGauge = (gaugeElement, valueElement, sublabelElement, percentage, value) => {
        if (!gaugeElement || !valueElement || !sublabelElement) return;

        const rotation = 180 * (percentage / 100);

        gaugeElement.style.background = `conic-gradient(
      from 180deg,
      var(--primary) 0deg,
      var(--primary) ${rotation}deg,
      transparent ${rotation}deg
    )`;

        // Animar el porcentaje
        let currentPercentage = 0;
        const increment = percentage / 30;
        const interval = setInterval(() => {
            currentPercentage += increment;
            if (currentPercentage >= percentage) {
                currentPercentage = percentage;
                clearInterval(interval);
            }

            valueElement.textContent = `${Math.round(currentPercentage)}%`;

            const mockValue = Math.round((currentPercentage / 100) * value);
            sublabelElement.textContent = formatCurrency(mockValue);
        }, 50);
    };

    useEffect(() => {
        // Pequeño delay para animación suave
        const timeout = setTimeout(() => {
            animateGauge(
                balanceRef.current,
                balanceRef.current?.parentElement.querySelector('.gauge-value'),
                balanceRef.current?.parentElement.querySelector('.gauge-sublabel'),
                balance.percentage,
                balance.amount
            );
            animateGauge(
                cashflowRef.current,
                cashflowRef.current?.parentElement.querySelector('.gauge-value'),
                cashflowRef.current?.parentElement.querySelector('.gauge-sublabel'),
                cashflow.percentage,
                cashflow.amount
            );
            animateGauge(
                spendingRef.current,
                spendingRef.current?.parentElement.querySelector('.gauge-value'),
                spendingRef.current?.parentElement.querySelector('.gauge-sublabel'),
                spending.percentage,
                spending.amount
            );
        }, 500);

        return () => clearTimeout(timeout);
    }, [balance, cashflow, spending]);

    return (
        <div className="gauges-card">
            <div className="gauges-container">
                {/* Balance Gauge */}
                <div className="gauge">
                    <div className="gauge-circle">
                        <div className="gauge-circle-bg"></div>
                        <div className="gauge-circle-fill" ref={balanceRef}></div>
                        <div className="gauge-circle-mask"></div>
                        <div className="gauge-value">0%</div>
                    </div>
                    <div className="gauge-label">BALANCE</div>
                    <div className="gauge-sublabel">COP 0.00</div>
                </div>

                {/* Cash Flow Gauge */}
                <div className="gauge">
                    <div className="gauge-circle">
                        <div className="gauge-circle-bg"></div>
                        <div className="gauge-circle-fill" ref={cashflowRef}></div>
                        <div className="gauge-circle-mask"></div>
                        <div className="gauge-value">0%</div>
                    </div>
                    <div className="gauge-label">CASH FLOW</div>
                    <div className="gauge-sublabel">COP 0.00</div>
                </div>

                {/* Spending Gauge */}
                <div className="gauge">
                    <div className="gauge-circle">
                        <div className="gauge-circle-bg"></div>
                        <div className="gauge-circle-fill" ref={spendingRef}></div>
                        <div className="gauge-circle-mask"></div>
                        <div className="gauge-value">0%</div>
                    </div>
                    <div className="gauge-label">SPENDING</div>
                    <div className="gauge-sublabel">COP 0.00</div>
                </div>
            </div>
        </div>
    );
}