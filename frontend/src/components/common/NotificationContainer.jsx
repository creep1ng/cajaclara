/**
 * Contenedor de notificaciones
 * Muestra las notificaciones del sistema en la esquina superior derecha
 */

import React from 'react';
import { useApp } from '../../context/AppContext';

export default function NotificationContainer() {
    const { notifications, removeNotification } = useApp();

    if (notifications.length === 0) {
        return null;
    }

    const getIcon = (type) => {
        switch (type) {
            case 'success':
                return 'fa-check';
            case 'error':
                return 'fa-exclamation';
            case 'info':
                return 'fa-info';
            default:
                return 'fa-info';
        }
    };

    return (
        <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1001 }}>
            {notifications.map((notification) => (
                <div
                    key={notification.id}
                    className={`notification ${notification.type} show`}
                    style={{ marginBottom: '10px' }}
                >
                    <div className="notification-icon">
                        <i className={`fas ${getIcon(notification.type)}`}></i>
                    </div>
                    <div className="notification-message">{notification.message}</div>
                    <button
                        className="notification-close"
                        onClick={() => removeNotification(notification.id)}
                    >
                        <i className="fas fa-times"></i>
                    </button>
                </div>
            ))}
        </div>
    );
}