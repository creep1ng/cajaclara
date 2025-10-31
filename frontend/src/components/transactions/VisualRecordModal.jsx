/**
 * Modal de Registro Visual (OCR) Mejorado
 * Permite registrar transacciones subiendo foto de recibo con UX optimizada
 */

import React, { useState, useRef, useCallback } from 'react';
import { useApp } from '../../context/AppContext';
import Modal from '../common/Modal';
import OCRProgressIndicator from '../OCRProgressIndicator';
import { createOcrTransaction } from '../../services/api';
import '../../styles/ocr-modal.css';
import '../../styles/ocr-progress.css';

export default function VisualRecordModal({ isOpen, onClose, onSuccess }) {
    const { categories, getCategoriesByType, createTransaction, showNotification } = useApp();
    const [activeTab, setActiveTab] = useState('upload');
    const [loading, setLoading] = useState(false);
    const [ocrProcessing, setOcrProcessing] = useState(false);
    const [imageFile, setImageFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [ocrResults, setOcrResults] = useState(null);
    const [formData, setFormData] = useState({
        amount: '',
        category_id: '',
        date: '',
        account: 'cash',
        notes: '',
        transaction_type: 'expense',
        classification: 'personal'
    });
    const [errors, setErrors] = useState({});
    const [dragActive, setDragActive] = useState(false);

    const fileInputRef = useRef(null);
    const formRef = useRef(null);

    // Inicializar fecha actual
    React.useEffect(() => {
        if (isOpen) {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            setFormData((prev) => ({
                ...prev,
                date: `${year}-${month}-${day}`,
            }));
            setErrors({});
            setOcrResults(null);
        }
    }, [isOpen]);

    const handleFileChange = useCallback((e) => {
        const file = e.target.files[0];
        if (file) {
            validateAndProcessFile(file);
        }
    }, []);

    const validateAndProcessFile = useCallback((file) => {
        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
            showNotification('El archivo debe ser una imagen (JPG, PNG, WebP)', 'error');
            return;
        }

        // Validar tamaño (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('La imagen no puede superar 10 MB', 'error');
            return;
        }

        setImageFile(file);
        const reader = new FileReader();
        reader.onload = (e) => {
            setImagePreview(e.target.result);
            setErrors({});
        };
        reader.readAsDataURL(file);
    }, [showNotification]);

    const handleUploadAreaClick = useCallback(() => {
        fileInputRef.current?.click();
    }, []);

    const handleRemoveImage = useCallback(() => {
        setImageFile(null);
        setImagePreview(null);
        setOcrResults(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }, []);

    const handleChange = useCallback((e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));

        // Limpiar error del campo
        if (errors[name]) {
            setErrors((prev) => ({
                ...prev,
                [name]: '',
            }));
        }
    }, [errors]);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndProcessFile(e.dataTransfer.files[0]);
        }
    }, [validateAndProcessFile]);

    const processOCR = async () => {
        if (!imageFile) {
            setErrors({ image: 'Por favor selecciona una imagen' });
            return;
        }

        setOcrProcessing(true);
        setErrors({});

        try {
            showNotification('🔍 Analizando imagen con OCR...', 'info');

            const formDataOCR = new FormData();
            formDataOCR.append('receipt_image', imageFile);
            formDataOCR.append('transaction_type', formData.transaction_type);
            formDataOCR.append('classification', formData.classification);

            // Simular progreso
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress >= 90) {
                    clearInterval(progressInterval);
                }
                // Actualizar estado de progreso si es necesario
            }, 300);

            const result = await createOcrTransaction(formDataOCR);
            clearInterval(progressInterval);

            // Guardar resultados OCR
            setOcrResults(result.ocr_details);

            // Autocompletar campos con datos del OCR
            setFormData((prev) => {
                // Sanitize notes: remove Markdown code fences like ```json or ``` that may come from OCR output
                const rawNotes = result.description || prev.notes;
                const cleanNotes = rawNotes
                    ? rawNotes.replace(/```json\s*/g, '').replace(/```/g, '').trim()
                    : rawNotes;
                return {
                    ...prev,
                    amount: result.amount ? result.amount.toString() : prev.amount,
                    category_id: result.category?.id || prev.category_id,
                    date: result.transaction_date
                        ? new Date(result.transaction_date).toISOString().split('T')[0]
                        : prev.date,
                    notes: cleanNotes,
                };
            });

            showNotification('✅ Imagen procesada exitosamente', 'success');
            setActiveTab('review');

        } catch (error) {
            console.error('OCR Error:', error);

            // Manejo específico de errores
            if (error.code === 'INVALID_FILE_TYPE') {
                setErrors({ image: 'Tipo de archivo no válido' });
            } else if (error.code === 'FILE_TOO_LARGE') {
                setErrors({ image: 'El archivo es demasiado grande' });
            } else if (error.code === 'NO_TEXT_EXTRACTED') {
                setErrors({ image: 'No se pudo extraer texto de la imagen. Intenta con una mejor calidad.' });
            } else {
                setErrors({ image: 'Error al procesar la imagen. Intenta con el registro manual.' });
            }

            showNotification(
                '❌ Error al procesar la imagen. Por favor, intenta con el registro manual.',
                'error'
            );
        } finally {
            setOcrProcessing(false);
        }
    };

    const validateForm = useCallback(() => {
        const newErrors = {};

        if (!formData.amount || parseFloat(formData.amount) <= 0) {
            newErrors.amount = 'Por favor ingresa un monto válido';
        }

        if (!formData.category_id) {
            newErrors.category_id = 'Por favor selecciona una categoría';
        }

        if (!formData.date) {
            newErrors.date = 'Por favor selecciona una fecha';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData]);

    const handleSubmit = async () => {
        if (!validateForm()) return;

        setLoading(true);
        try {
            const transactionData = {
                amount: parseFloat(formData.amount),
                currency: 'COP',
                category_id: formData.category_id,
                description: formData.notes || undefined,
                transaction_type: formData.transaction_type,
                classification: formData.classification,
                transaction_date: new Date(formData.date).toISOString(),
            };

            await createTransaction(transactionData);
            showNotification('✅ Registro guardado exitosamente', 'success');

            if (onSuccess) {
                onSuccess();
            }

            handleClose();
        } catch (error) {
            console.error('Error creating transaction:', error);
            showNotification('❌ Error al guardar el registro', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = useCallback(() => {
        if (!loading && !ocrProcessing) {
            setImageFile(null);
            setImagePreview(null);
            setOcrResults(null);
            setActiveTab('upload');
            setFormData({
                amount: '',
                category_id: '',
                date: '',
                account: 'cash',
                notes: '',
                transaction_type: 'expense',
                classification: 'personal'
            });
            setErrors({});
            onClose();
        }
    }, [loading, ocrProcessing, onClose]);

    const expenseCategories = getCategoriesByType('expense');
    const incomeCategories = getCategoriesByType('income');

    // Calcular confianza general del OCR
    const getOverallConfidence = useCallback(() => {
        if (!ocrResults) return 0;

        const weights = {
            amount_confidence: 0.3,
            fecha_confidence: 0.2,
            category_confidence: 0.3,
            vendor_confidence: 0.2
        };

        return Object.entries(weights).reduce((total, [key, weight]) => {
            return total + (ocrResults[key] || 0) * weight;
        }, 0);
    }, [ocrResults]);

    const getConfidenceColor = useCallback((confidence) => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    }, []);

    const getConfidenceLabel = useCallback((confidence) => {
        if (confidence >= 0.8) return 'Alta';
        if (confidence >= 0.6) return 'Media';
        return 'Baja';
    }, []);

    return (
        <Modal isOpen={isOpen} onClose={handleClose} size="large" ariaLabel="Modal de registro visual con OCR">
            <div className="visual-record-header">
                <h2 className="visual-record-title">Registro Visual con OCR</h2>
                <button
                    className="visual-record-close"
                    onClick={handleClose}
                    aria-label="Cerrar modal"
                >
                    <i className="fas fa-times"></i>
                </button>
            </div>

            <div className="visual-record-body">
                {/* Tabs */}
                <div className="visual-record-tabs" role="tablist">
                    <button
                        className={`visual-tab ${activeTab === 'upload' ? 'active' : ''}`}
                        onClick={() => setActiveTab('upload')}
                        role="tab"
                        aria-selected={activeTab === 'upload'}
                        aria-controls="upload-panel"
                        id="upload-tab"
                    >
                        <i className="fas fa-camera"></i>
                        Subir Imagen
                    </button>
                    <button
                        className={`visual-tab ${activeTab === 'review' ? 'active' : ''}`}
                        onClick={() => setActiveTab('review')}
                        role="tab"
                        aria-selected={activeTab === 'review'}
                        aria-controls="review-panel"
                        id="review-tab"
                        disabled={!ocrResults}
                    >
                        <i className="fas fa-edit"></i>
                        Revisar Datos
                    </button>
                    <button
                        className={`visual-tab ${activeTab === 'manual' ? 'active' : ''}`}
                        onClick={() => setActiveTab('manual')}
                        role="tab"
                        aria-selected={activeTab === 'manual'}
                        aria-controls="manual-panel"
                        id="manual-tab"
                    >
                        <i className="fas fa-keyboard"></i>
                        Registro Manual
                    </button>
                </div>

                {/* Upload Panel */}
                <div
                    className={`tab-panel ${activeTab === 'upload' ? 'active' : ''}`}
                    id="upload-panel"
                    role="tabpanel"
                    aria-labelledby="upload-tab"
                >
                    {!imagePreview ? (
                        <div
                            className={`visual-upload-area ${dragActive ? 'drag-active' : ''} ${errors.image ? 'error' : ''}`}
                            onClick={handleUploadAreaClick}
                            onDrop={handleDrop}
                            onDragOver={handleDrag}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            tabIndex={0}
                            role="button"
                            aria-label="Área para subir imagen de recibo"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    handleUploadAreaClick();
                                }
                            }}
                        >
                            <i className="fas fa-cloud-upload-alt upload-icon"></i>
                            <div className="upload-text">
                                Arrastra y suelta una imagen aquí
                            </div>
                            <div className="upload-subtext">
                                o haz clic para seleccionar (JPG, PNG, WebP - máx. 10MB)
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                                aria-label="Seleccionar archivo de imagen"
                            />
                        </div>
                    ) : (
                        <div className="visual-preview-container">
                            <div className="visual-preview">
                                <img
                                    src={imagePreview}
                                    alt="Vista previa del recibo"
                                    className="preview-image"
                                />
                                <button
                                    className="preview-remove"
                                    onClick={handleRemoveImage}
                                    aria-label="Eliminar imagen"
                                >
                                    <i className="fas fa-times"></i>
                                </button>
                            </div>

                            {/* Tipo y clasificación */}
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Tipo de Transacción</label>
                                    <div className="radio-group">
                                        <label className="radio-option">
                                            <input
                                                type="radio"
                                                name="transaction_type"
                                                value="expense"
                                                checked={formData.transaction_type === 'expense'}
                                                onChange={handleChange}
                                                disabled={ocrProcessing}
                                            />
                                            <span>Gasto</span>
                                        </label>
                                        <label className="radio-option">
                                            <input
                                                type="radio"
                                                name="transaction_type"
                                                value="income"
                                                checked={formData.transaction_type === 'income'}
                                                onChange={handleChange}
                                                disabled={ocrProcessing}
                                            />
                                            <span>Ingreso</span>
                                        </label>
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Clasificación</label>
                                    <div className="radio-group">
                                        <label className="radio-option">
                                            <input
                                                type="radio"
                                                name="classification"
                                                value="personal"
                                                checked={formData.classification === 'personal'}
                                                onChange={handleChange}
                                                disabled={ocrProcessing}
                                            />
                                            <span>Personal</span>
                                        </label>
                                        <label className="radio-option">
                                            <input
                                                type="radio"
                                                name="classification"
                                                value="business"
                                                checked={formData.classification === 'business'}
                                                onChange={handleChange}
                                                disabled={ocrProcessing}
                                            />
                                            <span>Negocio</span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            {errors.image && (
                                <div className="error-message" role="alert">
                                    {errors.image}
                                </div>
                            )}

                            <button
                                className="btn btn-primary btn-large"
                                onClick={processOCR}
                                disabled={ocrProcessing}
                                aria-label="Procesar imagen con OCR"
                            >
                                {ocrProcessing ? (
                                    <>
                                        <i className="fas fa-spinner fa-spin"></i>
                                        Procesando con OCR...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-magic"></i>
                                        Procesar con OCR
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {/* Review Panel */}
                <div
                    className={`tab-panel ${activeTab === 'review' ? 'active' : ''}`}
                    id="review-panel"
                    role="tabpanel"
                    aria-labelledby="review-tab"
                >
                    {ocrResults && (
                        <div className="ocr-review-container">
                            {/* Indicadores de confianza */}
                            <div className="ocr-confidence-summary">
                                <h3>Confianza del Procesamiento</h3>
                                <div className="confidence-overall">
                                    <div className="confidence-bar">
                                        <div
                                            className="confidence-fill"
                                            style={{ width: `${getOverallConfidence() * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className={`confidence-value ${getConfidenceColor(getOverallConfidence())}`}>
                                        {Math.round(getOverallConfidence() * 100)}% - {getConfidenceLabel(getOverallConfidence())}
                                    </span>
                                </div>

                                <div className="confidence-details">
                                    <div className="confidence-item">
                                        <span>Monto:</span>
                                        <span className={getConfidenceColor(ocrResults.amount_confidence || 0)}>
                                            {Math.round((ocrResults.amount_confidence || 0) * 100)}%
                                        </span>
                                    </div>
                                    <div className="confidence-item">
                                        <span>Fecha:</span>
                                        <span className={getConfidenceColor(ocrResults.fecha_confidence || 0)}>
                                            {Math.round((ocrResults.fecha_confidence || 0) * 100)}%
                                        </span>
                                    </div>
                                    <div className="confidence-item">
                                        <span>Categoría:</span>
                                        <span className={getConfidenceColor(ocrResults.category_confidence || 0)}>
                                            {Math.round((ocrResults.category_confidence || 0) * 100)}%
                                        </span>
                                    </div>
                                    <div className="confidence-item">
                                        <span>Vendedor:</span>
                                        <span className={getConfidenceColor(ocrResults.vendor_confidence || 0)}>
                                            {Math.round((ocrResults.vendor_confidence || 0) * 100)}%
                                        </span>
                                    </div>
                                </div>
                            </div>


                            {/* Formulario con datos prellenados */}
                            <form ref={formRef} className="visual-form-grid" onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
                                {/* Monto */}
                                <div className="form-group">
                                    <label className="form-label" htmlFor="amount">
                                        Monto <span className="required" aria-label="requerido">*</span>
                                    </label>
                                    <div className="amount-input-group">
                                        <span className="amount-currency">$</span>
                                        <input
                                            type="number"
                                            id="amount"
                                            name="amount"
                                            className={`amount-input ${errors.amount ? 'error' : ''}`}
                                            placeholder="0.00"
                                            step="0.01"
                                            value={formData.amount}
                                            onChange={handleChange}
                                            disabled={loading}
                                            aria-describedby={errors.amount ? 'amount-error' : undefined}
                                            aria-invalid={!!errors.amount}
                                        />
                                    </div>
                                    {errors.amount && (
                                        <div id="amount-error" className="error-message" role="alert">
                                            {errors.amount}
                                        </div>
                                    )}
                                </div>

                                {/* Categoría */}
                                <div className="form-group">
                                    <label className="form-label" htmlFor="category_id">
                                        Categoría <span className="required" aria-label="requerido">*</span>
                                    </label>
                                    <div className="select-wrapper">
                                        <select
                                            id="category_id"
                                            name="category_id"
                                            className={`form-select ${errors.category_id ? 'error' : ''}`}
                                            value={formData.category_id}
                                            onChange={handleChange}
                                            disabled={loading}
                                            aria-describedby={errors.category_id ? 'category-error' : undefined}
                                            aria-invalid={!!errors.category_id}
                                        >
                                            <option value="">Seleccionar categoría</option>
                                            {(formData.transaction_type === 'expense' ? expenseCategories : incomeCategories).map((cat) => (
                                                <option key={cat.id} value={cat.id}>
                                                    {cat.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    {errors.category_id && (
                                        <div id="category-error" className="error-message" role="alert">
                                            {errors.category_id}
                                        </div>
                                    )}
                                </div>

                                {/* Fecha */}
                                <div className="form-group">
                                    <label className="form-label" htmlFor="date">
                                        Fecha <span className="required" aria-label="requerido">*</span>
                                    </label>
                                    <input
                                        type="date"
                                        id="date"
                                        name="date"
                                        className={`form-input ${errors.date ? 'error' : ''}`}
                                        value={formData.date}
                                        onChange={handleChange}
                                        disabled={loading}
                                        aria-describedby={errors.date ? 'date-error' : undefined}
                                        aria-invalid={!!errors.date}
                                    />
                                    {errors.date && (
                                        <div id="date-error" className="error-message" role="alert">
                                            {errors.date}
                                        </div>
                                    )}
                                </div>

                                {/* Cuenta */}
                                <div className="form-group">
                                    <label className="form-label" htmlFor="account">Cuenta</label>
                                    <div className="select-wrapper">
                                        <select
                                            id="account"
                                            name="account"
                                            className="form-select"
                                            value={formData.account}
                                            onChange={handleChange}
                                            disabled={loading}
                                        >
                                            <option value="cash">Efectivo</option>
                                            <option value="savings">Ahorros</option>
                                            <option value="checking">Corriente</option>
                                            <option value="credit">Tarjeta de Crédito</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Notas */}
                                <div className="form-group" style={{ gridColumn: 'span 2' }}>
                                    <label className="form-label" htmlFor="notes">Notas</label>
                                    <textarea
                                        id="notes"
                                        name="notes"
                                        className="form-input"
                                        rows="3"
                                        placeholder="Agregar notas..."
                                        value={formData.notes}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                </div>

                                {/* Botones de acción */}
                                <div className="form-actions" style={{ gridColumn: 'span 2' }}>
                                    <button
                                        type="button"
                                        className="btn btn-cancel-record"
                                        onClick={handleClose}
                                        disabled={loading}
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        type="submit"
                                        className="btn btn-add-record-confirm"
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <i className="fas fa-spinner fa-spin"></i>
                                                Guardando...
                                            </>
                                        ) : (
                                            <>
                                                <i className="fas fa-check"></i>
                                                Guardar Registro
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}
                </div>

                {/* Manual Panel */}
                <div
                    className={`tab-panel ${activeTab === 'manual' ? 'active' : ''}`}
                    id="manual-panel"
                    role="tabpanel"
                    aria-labelledby="manual-tab"
                >
                    <form ref={formRef} className="visual-form-grid" onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
                        {/* Tipo y clasificación */}
                        <div className="form-group">
                            <label className="form-label">Tipo de Transacción</label>
                            <div className="radio-group">
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="transaction_type"
                                        value="expense"
                                        checked={formData.transaction_type === 'expense'}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Gasto</span>
                                </label>
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="transaction_type"
                                        value="income"
                                        checked={formData.transaction_type === 'income'}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Ingreso</span>
                                </label>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Clasificación</label>
                            <div className="radio-group">
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="classification"
                                        value="personal"
                                        checked={formData.classification === 'personal'}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Personal</span>
                                </label>
                                <label className="radio-option">
                                    <input
                                        type="radio"
                                        name="classification"
                                        value="business"
                                        checked={formData.classification === 'business'}
                                        onChange={handleChange}
                                        disabled={loading}
                                    />
                                    <span>Negocio</span>
                                </label>
                            </div>
                        </div>

                        {/* Monto */}
                        <div className="form-group">
                            <label className="form-label" htmlFor="manual-amount">
                                Monto <span className="required" aria-label="requerido">*</span>
                            </label>
                            <div className="amount-input-group">
                                <span className="amount-currency">$</span>
                                <input
                                    type="number"
                                    id="manual-amount"
                                    name="amount"
                                    className={`amount-input ${errors.amount ? 'error' : ''}`}
                                    placeholder="0.00"
                                    step="0.01"
                                    value={formData.amount}
                                    onChange={handleChange}
                                    disabled={loading}
                                    aria-describedby={errors.amount ? 'manual-amount-error' : undefined}
                                    aria-invalid={!!errors.amount}
                                />
                            </div>
                            {errors.amount && (
                                <div id="manual-amount-error" className="error-message" role="alert">
                                    {errors.amount}
                                </div>
                            )}
                        </div>

                        {/* Categoría */}
                        <div className="form-group">
                            <label className="form-label" htmlFor="manual-category">
                                Categoría <span className="required" aria-label="requerido">*</span>
                            </label>
                            <div className="select-wrapper">
                                <select
                                    id="manual-category"
                                    name="category_id"
                                    className={`form-select ${errors.category_id ? 'error' : ''}`}
                                    value={formData.category_id}
                                    onChange={handleChange}
                                    disabled={loading}
                                    aria-describedby={errors.category_id ? 'manual-category-error' : undefined}
                                    aria-invalid={!!errors.category_id}
                                >
                                    <option value="">Seleccionar categoría</option>
                                    {(formData.transaction_type === 'expense' ? expenseCategories : incomeCategories).map((cat) => (
                                        <option key={cat.id} value={cat.id}>
                                            {cat.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            {errors.category_id && (
                                <div id="manual-category-error" className="error-message" role="alert">
                                    {errors.category_id}
                                </div>
                            )}
                        </div>

                        {/* Fecha */}
                        <div className="form-group">
                            <label className="form-label" htmlFor="manual-date">
                                Fecha <span className="required" aria-label="requerido">*</span>
                            </label>
                            <input
                                type="date"
                                id="manual-date"
                                name="date"
                                className={`form-input ${errors.date ? 'error' : ''}`}
                                value={formData.date}
                                onChange={handleChange}
                                disabled={loading}
                                aria-describedby={errors.date ? 'manual-date-error' : undefined}
                                aria-invalid={!!errors.date}
                            />
                            {errors.date && (
                                <div id="manual-date-error" className="error-message" role="alert">
                                    {errors.date}
                                </div>
                            )}
                        </div>

                        {/* Cuenta */}
                        <div className="form-group">
                            <label className="form-label" htmlFor="manual-account">Cuenta</label>
                            <div className="select-wrapper">
                                <select
                                    id="manual-account"
                                    name="account"
                                    className="form-select"
                                    value={formData.account}
                                    onChange={handleChange}
                                    disabled={loading}
                                >
                                    <option value="cash">Efectivo</option>
                                    <option value="savings">Ahorros</option>
                                    <option value="checking">Corriente</option>
                                    <option value="credit">Tarjeta de Crédito</option>
                                </select>
                            </div>
                        </div>

                        {/* Notas */}
                        <div className="form-group" style={{ gridColumn: 'span 2' }}>
                            <label className="form-label" htmlFor="manual-notes">Notas</label>
                            <textarea
                                id="manual-notes"
                                name="notes"
                                className="form-input"
                                rows="3"
                                placeholder="Agregar notas..."
                                value={formData.notes}
                                onChange={handleChange}
                                disabled={loading}
                            />
                        </div>

                        {/* Botones de acción */}
                        <div className="form-actions" style={{ gridColumn: 'span 2' }}>
                            <button
                                type="button"
                                className="btn btn-cancel-record"
                                onClick={handleClose}
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="btn btn-add-record-confirm"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <i className="fas fa-spinner fa-spin"></i>
                                        Guardando...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-check"></i>
                                        Guardar Registro
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* Indicador de progreso OCR */}
            <OCRProgressIndicator
                isActive={ocrProcessing}
                progress={ocrProcessing ? 75 : 0}
                message="Procesando imagen con OCR..."
                showPercentage={true}
            />
        </Modal>
    );
}