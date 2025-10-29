/**
 * Modal de Registro Visual (OCR)
 * Permite registrar transacciones subiendo foto de recibo
 */

import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import Modal from '../common/Modal';
import { createOcrTransaction } from '../../services/api';

export default function VisualRecordModal({ isOpen, onClose, onSuccess }) {
    const { categories, getCategoriesByType, createTransaction, showNotification } = useApp();
    const [activeTab, setActiveTab] = useState('upload');
    const [loading, setLoading] = useState(false);
    const [imageFile, setImageFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const fileInputRef = useRef(null);
    const [formData, setFormData] = useState({
        amount: '',
        category_id: '',
        date: '',
        account: 'cash',
        notes: '',
    });

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
        }
    }, [isOpen]);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 10 * 1024 * 1024) {
                showNotification('La imagen no puede superar 10 MB', 'error');
                return;
            }

            setImageFile(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleUploadAreaClick = () => {
        fileInputRef.current?.click();
    };

    const handleRemoveImage = () => {
        setImageFile(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFileChangeFromFile(file);
        }
    };

    const handleFileChangeFromFile = (file) => {
        if (file.size > 10 * 1024 * 1024) {
            showNotification('La imagen no puede superar 10 MB', 'error');
            return;
        }

        setImageFile(file);
        const reader = new FileReader();
        reader.onload = (e) => {
            setImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const processOCR = async () => {
        if (!imageFile) {
            showNotification('Por favor selecciona una imagen', 'error');
            return;
        }

        setLoading(true);
        try {
            showNotification('Procesando imagen con OCR...', 'info');

            const formDataOCR = new FormData();
            formDataOCR.append('receipt_image', imageFile);
            formDataOCR.append('transaction_type', 'expense');
            formDataOCR.append('classification', 'personal');

            const result = await createOcrTransaction(formDataOCR);

            // Autocompletar campos con datos del OCR
            setFormData({
                amount: result.amount || '',
                category_id: result.category?.id || '',
                date: result.transaction_date
                    ? new Date(result.transaction_date).toISOString().split('T')[0]
                    : formData.date,
                account: 'cash',
                notes: result.description || '',
            });

            showNotification('✅ Imagen procesada exitosamente', 'success');
            setActiveTab('manual');
        } catch (error) {
            console.error('OCR Error:', error);
            showNotification(
                '❌ Error al procesar la imagen. Intenta con el registro manual.',
                'error'
            );
        } finally {
            setLoading(false);
        }
    };

    const validateForm = () => {
        if (!formData.amount || parseFloat(formData.amount) <= 0) {
            showNotification('Por favor ingresa un monto válido', 'error');
            return false;
        }
        if (!formData.category_id) {
            showNotification('Por favor selecciona una categoría', 'error');
            return false;
        }
        return true;
    };

    const handleSubmit = async () => {
        if (!validateForm()) return;

        setLoading(true);
        try {
            const transactionData = {
                amount: parseFloat(formData.amount),
                currency: 'COP',
                category_id: formData.category_id,
                description: formData.notes || undefined,
                transaction_type: 'expense',
                classification: 'personal',
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

    const handleClose = () => {
        if (!loading) {
            setImageFile(null);
            setImagePreview(null);
            setActiveTab('upload');
            setFormData({
                amount: '',
                category_id: '',
                date: '',
                account: 'cash',
                notes: '',
            });
            onClose();
        }
    };

    const expenseCategories = getCategoriesByType('expense');

    return (
        <Modal isOpen={isOpen} onClose={handleClose} size="large">
            <div className="visual-record-header">
                <h2 className="visual-record-title">Registro Visual</h2>
                <button className="visual-record-close" onClick={handleClose}>
                    <i className="fas fa-times"></i>
                </button>
            </div>

            <div className="visual-record-body">
                {/* Tabs */}
                <div className="visual-record-tabs">
                    <button
                        className={`visual-tab ${activeTab === 'upload' ? 'active' : ''}`}
                        onClick={() => setActiveTab('upload')}
                    >
                        Subir Imagen
                    </button>
                    <button
                        className={`visual-tab ${activeTab === 'manual' ? 'active' : ''}`}
                        onClick={() => setActiveTab('manual')}
                    >
                        Manual
                    </button>
                </div>

                <div className="visual-form-grid">
                    {/* Upload Area */}
                    {activeTab === 'upload' && !imagePreview && (
                        <div
                            className="visual-upload-area"
                            onClick={handleUploadAreaClick}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        >
                            <i className="fas fa-cloud-upload-alt upload-icon"></i>
                            <div className="upload-text">Arrastra y suelta una imagen aquí</div>
                            <div className="upload-subtext">o haz clic para seleccionar</div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                            />
                        </div>
                    )}

                    {/* Image Preview */}
                    {imagePreview && (
                        <div className="visual-preview" style={{ display: 'block' }}>
                            <img src={imagePreview} alt="Preview" className="preview-image" />
                            <button className="preview-remove" onClick={handleRemoveImage}>
                                <i className="fas fa-times"></i>
                            </button>
                        </div>
                    )}

                    {/* Monto */}
                    <div className="form-group">
                        <label className="form-label">
                            Monto <span className="required">*</span>
                        </label>
                        <div className="amount-input-group">
                            <span className="amount-currency">$</span>
                            <input
                                type="number"
                                name="amount"
                                className="amount-input"
                                placeholder="0.00"
                                step="0.01"
                                value={formData.amount}
                                onChange={handleChange}
                                disabled={loading}
                            />
                        </div>
                    </div>

                    {/* Categoría */}
                    <div className="form-group">
                        <label className="form-label">
                            Categoría <span className="required">*</span>
                        </label>
                        <div className="select-wrapper">
                            <select
                                name="category_id"
                                className="form-select"
                                value={formData.category_id}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                <option value="">Seleccionar categoría</option>
                                {expenseCategories.map((cat) => (
                                    <option key={cat.id} value={cat.id}>
                                        {cat.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Fecha */}
                    <div className="form-group">
                        <label className="form-label">Fecha</label>
                        <input
                            type="date"
                            name="date"
                            className="form-input"
                            value={formData.date}
                            onChange={handleChange}
                            disabled={loading}
                        />
                    </div>

                    {/* Cuenta */}
                    <div className="form-group">
                        <label className="form-label">Cuenta</label>
                        <div className="select-wrapper">
                            <select
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
                        <label className="form-label">Notas</label>
                        <textarea
                            name="notes"
                            className="form-input"
                            rows="3"
                            placeholder="Agregar notas..."
                            value={formData.notes}
                            onChange={handleChange}
                            disabled={loading}
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="manual-record-footer">
                    <div className="footer-info">
                        <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                            Los campos marcados con * son obligatorios
                        </span>
                    </div>
                    <div className="footer-actions">
                        <button
                            className="btn btn-cancel-record"
                            onClick={handleClose}
                            disabled={loading}
                        >
                            Cancelar
                        </button>
                        {imageFile && activeTab === 'upload' && (
                            <button
                                className="btn btn-primary"
                                onClick={processOCR}
                                disabled={loading}
                            >
                                {loading ? 'Procesando...' : 'Procesar con OCR'}
                            </button>
                        )}
                        <button
                            className="btn btn-add-record-confirm"
                            onClick={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? 'Guardando...' : 'Guardar Registro'}
                        </button>
                    </div>
                </div>
            </div>
        </Modal>
    );
}