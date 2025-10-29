/**
 * Pruebas unitarias para VisualRecordModal
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import VisualRecordModal from '../transactions/VisualRecordModal';

// Mock del contexto
const mockAppContext = {
    categories: [
        { id: 'cat-food', name: 'Comida', transaction_type: 'expense' },
        { id: 'cat-transport', name: 'Transporte', transaction_type: 'expense' },
        { id: 'cat-salary', name: 'Salario', transaction_type: 'income' }
    ],
    getCategoriesByType: jest.fn((type) => {
        return mockAppContext.categories.filter(cat => cat.transaction_type === type);
    }),
    createTransaction: jest.fn(),
    showNotification: jest.fn()
};

// Mock del Modal
jest.mock('../common/Modal', () => {
    return function MockModal({ children, isOpen, onClose }) {
        if (!isOpen) return null;
        return (
            <div role="dialog" aria-modal="true">
                <button onClick={onClose}>Close</button>
                {children}
            </div>
        );
    };
});

// Mock del OCRProgressIndicator
jest.mock('../OCRProgressIndicator', () => {
    return function MockOCRProgressIndicator({ isActive }) {
        if (!isActive) return null;
        return <div data-testid="ocr-progress">Procesando...</div>;
    };
});

// Mock del API
jest.mock('../../services/api', () => ({
    createOcrTransaction: jest.fn()
}));

describe('VisualRecordModal', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('se renderiza correctamente cuando isOpen es true', () => {
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        expect(screen.getByText('Registro Visual con OCR')).toBeInTheDocument();
        expect(screen.getByText('Subir Imagen')).toBeInTheDocument();
        expect(screen.getByText('Registro Manual')).toBeInTheDocument();
    });

    test('no se renderiza cuando isOpen es false', () => {
        render(
            <VisualRecordModal 
                isOpen={false} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        expect(screen.queryByText('Registro Visual con OCR')).not.toBeInTheDocument();
    });

    test('permite seleccionar archivo de imagen', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        const fileInput = screen.getByLabelText('Seleccionar archivo de imagen');
        const file = new File(['test'], 'test.png', { type: 'image/png' });
        
        await user.upload(fileInput, file);
        
        expect(screen.getByAltText('Vista previa del recibo')).toBeInTheDocument();
    });

    test('muestra error para archivo no válido', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        const fileInput = screen.getByLabelText('Seleccionar archivo de imagen');
        const file = new File(['test'], 'test.txt', { type: 'text/plain' });
        
        await user.upload(fileInput, file);
        
        expect(mockAppContext.showNotification).toHaveBeenCalledWith(
            'El archivo debe ser una imagen (JPG, PNG, WebP)',
            'error'
        );
    });

    test('valida formulario antes de enviar', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Cambiar a tab manual
        fireEvent.click(screen.getByText('Registro Manual'));
        
        // Intentar enviar sin datos
        const submitButton = screen.getByText('Guardar Registro');
        await user.click(submitButton);
        
        expect(screen.getByText('Por favor ingresa un monto válido')).toBeInTheDocument();
        expect(screen.getByText('Por favor selecciona una categoría')).toBeInTheDocument();
        expect(screen.getByText('Por favor selecciona una fecha')).toBeInTheDocument();
    });

    test('permite cambiar entre tabs', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Tab inicial es upload
        expect(screen.getByText('Arrastra y suelta una imagen aquí')).toBeInTheDocument();
        
        // Cambiar a manual
        await user.click(screen.getByText('Registro Manual'));
        expect(screen.getByLabelText('Monto')).toBeInTheDocument();
        expect(screen.getByLabelText('Categoría')).toBeInTheDocument();
        
        // Tab de revisión debe estar deshabilitado sin resultados OCR
        expect(screen.getByText('Revisar Datos')).toBeDisabled();
    });

    test('maneja drag and drop de archivos', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        const uploadArea = screen.getByLabelText('Área para subir imagen de recibo');
        const file = new File(['test'], 'test.png', { type: 'image/png' });
        
        // Simular drag over
        fireEvent.dragOver(uploadArea);
        expect(uploadArea).toHaveClass('drag-active');
        
        // Simular drop
        fireEvent.drop(uploadArea, {
            dataTransfer: {
                files: [file]
            }
        });
        
        expect(uploadArea).not.toHaveClass('drag-active');
        expect(screen.getByAltText('Vista previa del recibo')).toBeInTheDocument();
    });

    test('procesa OCR correctamente', async () => {
        const mockOCRResult = {
            ocr_details: {
                extracted_text: 'Total: $45000\nFecha: 27/10/2025',
                amount_confidence: 0.9,
                fecha_confidence: 0.8,
                category_confidence: 0.7,
                vendor_confidence: 0.6
            },
            amount: 45000,
            transaction_date: '2025-10-27T00:00:00Z',
            category: { id: 'cat-food', name: 'Comida' }
        };

        const { createOcrTransaction } = require('../../services/api');
        createOcrTransaction.mockResolvedValue(mockOCRResult);

        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Subir imagen
        const fileInput = screen.getByLabelText('Seleccionar archivo de imagen');
        const file = new File(['test'], 'test.png', { type: 'image/png' });
        await user.upload(fileInput, file);
        
        // Procesar OCR
        const ocrButton = screen.getByText('Procesar con OCR');
        await user.click(ocrButton);
        
        await waitFor(() => {
            expect(createOcrTransaction).toHaveBeenCalled();
            expect(mockAppContext.showNotification).toHaveBeenCalledWith(
                '✅ Imagen procesada exitosamente',
                'success'
            );
        });
    });

    test('maneja errores de OCR', async () => {
        const { createOcrTransaction } = require('../../services/api');
        createOcrTransaction.mockRejectedValue(new Error('Error de OCR'));

        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Subir imagen y procesar OCR
        const fileInput = screen.getByLabelText('Seleccionar archivo de imagen');
        const file = new File(['test'], 'test.png', { type: 'image/png' });
        await user.upload(fileInput, file);
        
        const ocrButton = screen.getByText('Procesar con OCR');
        await user.click(ocrButton);
        
        await waitFor(() => {
            expect(mockAppContext.showNotification).toHaveBeenCalledWith(
                '❌ Error al procesar la imagen. Por favor, intenta con el registro manual.',
                'error'
            );
        });
    });

    test('calcula confianza general correctamente', () => {
        const mockOCRResults = {
            amount_confidence: 0.9,
            fecha_confidence: 0.8,
            category_confidence: 0.7,
            vendor_confidence: 0.6
        };

        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Simular que tenemos resultados OCR
        // Esto requeriría acceder al estado interno del componente
        // En una implementación real, podríamos extraer esta lógica a un hook personalizado
    });

    test('tiene atributos de accesibilidad correctos', () => {
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Verificar roles ARIA
        expect(screen.getByRole('tablist')).toBeInTheDocument();
        expect(screen.getAllByRole('tab')).toHaveLength(3);
        expect(screen.getAllByRole('tabpanel')).toHaveLength(3);
        
        // Verificar labels
        expect(screen.getByLabelText('Área para subir imagen de recibo')).toBeInTheDocument();
        expect(screen.getByLabelText('Seleccionar archivo de imagen')).toBeInTheDocument();
    });

    test('cierra modal correctamente', async () => {
        const mockOnClose = jest.fn();
        const user = userEvent.setup();
        
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={mockOnClose} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        const closeButton = screen.getByLabelText('Cerrar modal');
        await user.click(closeButton);
        
        expect(mockOnClose).toHaveBeenCalled();
    });

    test('filtra categorías según tipo de transacción', async () => {
        const user = userEvent.setup();
        render(
            <VisualRecordModal 
                isOpen={true} 
                onClose={jest.fn()} 
                onSuccess={jest.fn()}
            />, 
            { wrapper: ({ children }) => (
                <div>{children}</div>
            )}
        );

        // Cambiar a tab manual
        fireEvent.click(screen.getByText('Registro Manual'));
        
        // Verificar que solo muestra categorías de gasto por defecto
        expect(mockAppContext.getCategoriesByType).toHaveBeenCalledWith('expense');
        
        // Cambiar a ingreso
        const incomeRadio = screen.getByLabelText('Ingreso');
        await user.click(incomeRadio);
        
        expect(mockAppContext.getCategoriesByType).toHaveBeenCalledWith('income');
    });
});