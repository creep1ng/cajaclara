/**
 * Selector de Fecha/Período
 * Permite seleccionar mes y tipo de rango temporal
 */

import React, { useState } from 'react';

const MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const TIME_RANGES = [
    { id: 'custom', label: 'Custom range' },
    { id: 'weeks', label: 'Weeks' },
    { id: 'months', label: 'Months' },
    { id: 'years', label: 'Years' },
];

export default function DateSelector({ selectedMonth, selectedYear, onDateChange }) {
    const [activeRange, setActiveRange] = useState('months');

    const handleMonthClick = (monthIndex) => {
        onDateChange({
            month: monthIndex,
            year: selectedYear,
        });
    };

    const handleRangeClick = (rangeId) => {
        setActiveRange(rangeId);
        // En el futuro, esto podría cambiar la vista del dashboard
    };

    const getMonthDisplay = () => {
        return `${MONTHS[selectedMonth]} ${selectedYear}`;
    };

    const getCurrentMonthIndex = () => {
        const now = new Date();
        return now.getMonth();
    };

    return (
        <div className="date-selector-card">
            <div className="date-selector-header">
                <h3 className="date-selector-title">Period</h3>
                <div className="date-display">
                    <i className="fas fa-calendar"></i>
                    <span>{getMonthDisplay()}</span>
                </div>
            </div>

            <div className="time-range-options">
                {TIME_RANGES.map((range) => (
                    <div
                        key={range.id}
                        className={`time-range-option ${activeRange === range.id ? 'active' : ''}`}
                        onClick={() => handleRangeClick(range.id)}
                    >
                        {range.label}
                    </div>
                ))}
            </div>

            <div className="months-grid">
                {MONTHS.map((month, index) => (
                    <div
                        key={month}
                        className={`month-item ${index === selectedMonth ? 'current' : ''
                            }`}
                        onClick={() => handleMonthClick(index)}
                    >
                        {month}
                    </div>
                ))}
            </div>
        </div>
    );
}