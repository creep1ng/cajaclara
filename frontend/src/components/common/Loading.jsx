/**
 * Componente de loading/spinner
 * Puede mostrarse en fullscreen o inline
 */

import React from 'react';

export default function Loading({ fullscreen = false, size = 'medium' }) {
    if (fullscreen) {
        return (
            <div className="loading-overlay">
                <div className="spinner"></div>
            </div>
        );
    }

    const sizeClass = size === 'small' ? 'loading' : size === 'large' ? 'spinner' : 'loading';

    return (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
            <div className={sizeClass}></div>
        </div>
    );
}