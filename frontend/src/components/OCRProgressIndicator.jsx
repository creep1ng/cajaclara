/**
 * Componente de indicador de progreso para OCR
 * Muestra el estado del procesamiento con animaciones y retroalimentación
 */

import React from 'react';

const OCRProgressIndicator = ({ 
    isActive, 
    progress = 0, 
    message = 'Procesando imagen...',
    showPercentage = true 
}) => {
    if (!isActive) return null;

    return (
        <div className="ocr-progress-overlay">
            <div className="ocr-progress-container">
                <div className="ocr-progress-content">
                    {/* Icono animado */}
                    <div className="ocr-progress-icon">
                        <div className="ocr-scanner">
                            <div className="scanner-line"></div>
                            <i className="fas fa-image"></i>
                        </div>
                    </div>
                    
                    {/* Mensaje */}
                    <div className="ocr-progress-message">
                        <h3>{message}</h3>
                        <p>Analizando el recibo con inteligencia artificial...</p>
                    </div>
                    
                    {/* Barra de progreso */}
                    <div className="ocr-progress-bar-container">
                        <div className="ocr-progress-bar">
                            <div 
                                className="ocr-progress-fill"
                                style={{ width: `${progress}%` }}
                            ></div>
                        </div>
                        {showPercentage && (
                            <span className="ocr-progress-percentage">
                                {Math.round(progress)}%
                            </span>
                        )}
                    </div>
                    
                    {/* Pasos del proceso */}
                    <div className="ocr-progress-steps">
                        <div className={`ocr-step ${progress >= 25 ? 'active' : ''}`}>
                            <div className="step-icon">
                                <i className="fas fa-upload"></i>
                            </div>
                            <span>Subiendo imagen</span>
                        </div>
                        <div className={`ocr-step ${progress >= 50 ? 'active' : ''}`}>
                            <div className="step-icon">
                                <i className="fas fa-eye"></i>
                            </div>
                            <span>Analizando texto</span>
                        </div>
                        <div className={`ocr-step ${progress >= 75 ? 'active' : ''}`}>
                            <div className="step-icon">
                                <i className="fas fa-brain"></i>
                            </div>
                            <span>Extrayendo datos</span>
                        </div>
                        <div className={`ocr-step ${progress >= 100 ? 'active' : ''}`}>
                            <div className="step-icon">
                                <i className="fas fa-check"></i>
                            </div>
                            <span>Completado</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OCRProgressIndicator;