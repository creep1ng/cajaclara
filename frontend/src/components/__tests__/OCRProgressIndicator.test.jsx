/**
 * Pruebas unitarias para OCRProgressIndicator
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import OCRProgressIndicator from '../OCRProgressIndicator';

describe('OCRProgressIndicator', () => {
    test('no se renderiza cuando isActive es false', () => {
        render(
            <OCRProgressIndicator 
                isActive={false} 
                progress={0} 
                message="Procesando..." 
            />
        );
        
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
        expect(screen.queryByText('Procesando...')).not.toBeInTheDocument();
    });

    test('se renderiza correctamente cuando isActive es true', () => {
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={50} 
                message="Procesando imagen..." 
                showPercentage={true}
            />
        );
        
        expect(screen.getByText('Procesando imagen...')).toBeInTheDocument();
        expect(screen.getByText('50%')).toBeInTheDocument();
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    test('muestra el porcentaje cuando showPercentage es true', () => {
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={75} 
                showPercentage={true}
            />
        );
        
        expect(screen.getByText('75%')).toBeInTheDocument();
    });

    test('no muestra el porcentaje cuando showPercentage es false', () => {
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={75} 
                showPercentage={false}
            />
        );
        
        expect(screen.queryByText('75%')).not.toBeInTheDocument();
    });

    test('muestra todos los pasos del proceso', () => {
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={100} 
            />
        );
        
        expect(screen.getByText('Subiendo imagen')).toBeInTheDocument();
        expect(screen.getByText('Analizando texto')).toBeInTheDocument();
        expect(screen.getByText('Extrayendo datos')).toBeInTheDocument();
        expect(screen.getByText('Completado')).toBeInTheDocument();
    });

    test('aplica clase active a los pasos correctos según el progreso', () => {
        const { container } = render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={50} 
            />
        );
        
        const steps = container.querySelectorAll('.ocr-step');
        
        // Primeros dos pasos deben estar activos (50%)
        expect(steps[0]).toHaveClass('active');
        expect(steps[1]).toHaveClass('active');
        
        // Últimos dos pasos no deben estar activos
        expect(steps[2]).not.toHaveClass('active');
        expect(steps[3]).not.toHaveClass('active');
    });

    test('tiene atributos de accesibilidad correctos', () => {
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={30} 
            />
        );
        
        const progressBar = screen.getByRole('progressbar');
        expect(progressBar).toHaveAttribute('aria-valuenow', '30');
        expect(progressBar).toHaveAttribute('aria-valuemin', '0');
        expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });

    test('muestra el mensaje personalizado', () => {
        const customMessage = 'Procesando recibo de restaurante...';
        render(
            <OCRProgressIndicator 
                isActive={true} 
                progress={25} 
                message={customMessage}
            />
        );
        
        expect(screen.getByText(customMessage)).toBeInTheDocument();
    });
});