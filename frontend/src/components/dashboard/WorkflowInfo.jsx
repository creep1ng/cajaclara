/**
 * Información del Flujo de Trabajo
 * Muestra los 4 pasos del flujo de trabajo de la aplicación
 */

import React from 'react';

const WORKFLOW_STEPS = [
    {
        number: 1,
        title: 'Registrar',
        description: 'Elige registro manual o visual desde + Registrar',
    },
    {
        number: 2,
        title: 'Completar',
        description: 'Llena los campos requeridos y pulsa Guardar',
    },
    {
        number: 3,
        title: 'Sincronizar',
        description: 'El registro se envía a la API y se persiste',
    },
    {
        number: 4,
        title: 'Actualizar',
        description: 'Dashboard y Ver registros se actualizan en tiempo real',
    },
];

export default function WorkflowInfo() {
    return (
        <div className="workflow-info">
            <h2 className="workflow-title">Flujo de Trabajo</h2>
            <div className="workflow-steps">
                {WORKFLOW_STEPS.map((step) => (
                    <div key={step.number} className="workflow-step">
                        <div className="step-number">{step.number}</div>
                        <div className="step-content">
                            <div className="step-title">{step.title}</div>
                            <div className="step-description">{step.description}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}