/**
 * Header del Dashboard
 * Incluye navegación y menú de registro
 */

import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';

export default function Header({ activePage, onNavigate, onRegisterAction }) {
    const { user, logout } = useApp();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Cerrar dropdown al hacer clic fuera
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownOpen(false);
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const handleDropdownToggle = (e) => {
        e.stopPropagation();
        setDropdownOpen(!dropdownOpen);
    };

    const handleRegisterClick = (action) => {
        setDropdownOpen(false);
        onRegisterAction(action);
    };

    const getUserInitials = () => {
        if (!user?.full_name) return 'JA';
        const names = user.full_name.split(' ');
        if (names.length >= 2) {
            return `${names[0][0]}${names[1][0]}`.toUpperCase();
        }
        return names[0].substring(0, 2).toUpperCase();
    };

    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    {/* Navegación */}
                    <div className="nav-tabs">
                        <div
                            className={`nav-tab ${activePage === 'dashboard' ? 'active' : ''}`}
                            onClick={() => onNavigate('dashboard')}
                        >
                            Dashboard
                        </div>
                        <div
                            className={`nav-tab ${activePage === 'records' ? 'active' : ''}`}
                            onClick={() => onNavigate('records')}
                        >
                            Ver registros
                        </div>
                        <div
                            className={`nav-tab ${activePage === 'accounts' ? 'active' : ''}`}
                            onClick={() => onNavigate('accounts')}
                        >
                            Accounts
                        </div>
                        <div
                            className={`nav-tab ${activePage === 'reports' ? 'active' : ''}`}
                            onClick={() => onNavigate('reports')}
                        >
                            Reports
                        </div>
                    </div>

                    {/* Acciones */}
                    <div className="header-actions">
                        {/* Dropdown de Registro */}
                        <div className="register-dropdown" ref={dropdownRef}>
                            <button
                                className="btn btn-register"
                                onClick={handleDropdownToggle}
                            >
                                <i className="fas fa-plus"></i>
                                Registrar
                                <i className="fas fa-chevron-down"></i>
                            </button>

                            <div className={`dropdown-menu ${dropdownOpen ? 'show' : ''}`}>
                                <button
                                    className="dropdown-item"
                                    onClick={() => handleRegisterClick('manual')}
                                >
                                    <i className="fas fa-keyboard"></i>
                                    Registro manual
                                </button>
                                <button
                                    className="dropdown-item"
                                    onClick={() => handleRegisterClick('visual')}
                                >
                                    <i className="fas fa-camera"></i>
                                    Registro visual
                                </button>
                                <div className="dropdown-divider"></div>
                                <button
                                    className="dropdown-item"
                                    onClick={() => handleRegisterClick('view')}
                                >
                                    <i className="fas fa-list"></i>
                                    Ver registros
                                </button>
                            </div>
                        </div>

                        {/* Avatar de Usuario */}
                        <div className="user-avatar">{getUserInitials()}</div>
                    </div>
                </div>
            </div>
        </header>
    );
}