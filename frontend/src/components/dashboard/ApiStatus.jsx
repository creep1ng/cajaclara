/**
 * Indicador de Estado de la API
 * Muestra si la API está conectada y sincronizada
 */

import React from 'react';

export default function ApiStatus({ isConnected = true }) {
    return (
        <div className="api-status">
            <div className="status-indicator"></div>
            <span className="status-text">
                {isConnected
                    ? 'API conectada y sincronizada'
                    : 'API desconectada - trabajando offline'}
            </span>
        </div>
    );
}