#!/usr/bin/env python3
"""
🔧 VALIDATION PIPELINE CORE MODULE - ICT ENGINE v6.0 ENTERPRISE
===============================================================

Módulo core del sistema de validación enterprise que contiene
las funcionalidades centrales de validación y coordinación.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: Septiembre 13, 2025
"""

from .validation_engine import (
    ValidationEngine,
    ValidationStatus,
    ValidationPriority, 
    ValidationRequest,
    ValidationResult,
    get_validation_engine
)

__version__ = "6.0.0-enterprise"
__author__ = "ICT Engine v6.0 Enterprise Team"

# Exports principales del módulo core
__all__ = [
    'ValidationEngine',
    'ValidationStatus', 
    'ValidationPriority',
    'ValidationRequest',
    'ValidationResult', 
    'get_validation_engine'
]

# Información del módulo
MODULE_INFO = {
    'name': 'validation_pipeline_core',
    'version': __version__,
    'description': 'Core validation engine for ICT Engine v6.0 Enterprise',
    'components': [
        'ValidationEngine',
        'ValidationStatus',
        'ValidationPriority',
        'ValidationRequest', 
        'ValidationResult'
    ]
}