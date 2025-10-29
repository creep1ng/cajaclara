/**
 * Componente Modal reutilizable
 * Modal genérico que puede contener cualquier contenido
 */

import React, { useEffect } from 'react';

export default function Modal({
    isOpen,
    onClose,
    title,
    children,
    footer,
    size = 'medium', // 'small', 'medium', 'large'
}) {
    // Cerrar con tecla ESC
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [isOpen, onClose]);

    // Prevenir scroll del body cuando el modal está abierto
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const maxWidthClass = size === 'small' ? '500px' : size === 'large' ? '1200px' : '900px';

    return (
        <div className="modal show" onClick={onClose}>
            <div
                className="modal-content"
                style={{ maxWidth: maxWidthClass }}
                onClick={(e) => e.stopPropagation()}
            >
                {title && (
                    <div className="modal-header">
                        <h2 className="modal-title">{title}</h2>
                        <button className="modal-close" onClick={onClose}>
                            <i className="fas fa-times"></i>
                        </button>
                    </div>
                )}

                <div className="modal-body">{children}</div>

                {footer && <div className="modal-footer">{footer}</div>}
            </div>
        </div>
    );
}