/**
 * Página de Login
 * Permite iniciar sesión con email/password o como invitado
 */

import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';

export default function LoginPage() {
    const { login, loginAsGuest, authLoading } = useApp();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        remember: false,
    });
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.email || !formData.password) {
            return;
        }

        setLoading(true);
        try {
            await login(formData.email, formData.password);
        } catch (error) {
            console.error('Login failed:', error);
            // Error ya manejado en AppContext
        } finally {
            setLoading(false);
        }
    };

    const handleGuestLogin = async () => {
        setLoading(true);
        try {
            await loginAsGuest();
        } catch (error) {
            console.error('Guest login failed:', error);
            // Error ya manejado en AppContext
        } finally {
            setLoading(false);
        }
    };

    if (authLoading) {
        return (
            <div className="login-container">
                <div className="loading"></div>
            </div>
        );
    }

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="logo-container">
                    <div className="logo">
                        <div className="logo-icon">C</div>
                        <div className="logo-text">CajaClara</div>
                    </div>
                    <p className="tagline">Administra tu dinero con claridad</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="email">
                            Email/Usuario
                        </label>
                        <input
                            type="text"
                            id="email"
                            name="email"
                            className="form-input"
                            placeholder="Ingresa tu email o usuario"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            disabled={loading}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="password">
                            Contraseña
                        </label>
                        <div className="password-input-container">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                name="password"
                                className="form-input"
                                placeholder="Ingresa tu contraseña"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                disabled={loading}
                            />
                            <button
                                type="button"
                                className="toggle-password"
                                onClick={() => setShowPassword(!showPassword)}
                                disabled={loading}
                            >
                                <i className={`fas fa-eye${showPassword ? '-slash' : ''}`}></i>
                            </button>
                        </div>
                    </div>

                    <div className="checkbox-container">
                        <input
                            type="checkbox"
                            id="remember"
                            name="remember"
                            checked={formData.remember}
                            onChange={handleChange}
                            disabled={loading}
                        />
                        <label htmlFor="remember">Recordarme</label>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="loading"></span>
                                Iniciando sesión...
                            </>
                        ) : (
                            'Iniciar sesión'
                        )}
                    </button>
                </form>

                <div className="divider">
                    <span>O</span>
                </div>

                <button
                    className="btn btn-secondary"
                    onClick={handleGuestLogin}
                    disabled={loading}
                >
                    Entrar como invitado
                </button>

                <div className="form-footer">
                    <p>
                        ¿No tienes una cuenta? <a href="#">Regístrate</a>
                    </p>
                    <p>
                        <a href="#">¿Olvidaste tu contraseña?</a>
                    </p>
                </div>
            </div>

            {/* MVP Badge */}
            <div className="mvp-badge">
                <i className="fas fa-rocket"></i> MVP CajaClara
            </div>
        </div>
    );
}