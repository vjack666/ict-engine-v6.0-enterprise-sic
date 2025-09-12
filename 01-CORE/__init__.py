#!/usr/bin/env python3
"""
Core Module - ICT Engine v6.1.0 Enterprise SIC
============================================

Módulo core del ICT Engine v6.1.0 que contiene la lógica principal
de trading y gestión de datos integrada con SIC v3.1 Enterprise.

Autor: ICT Engine v6.1.0 Enterprise Team
Versión: v6.1.0-enterprise
Fecha: Agosto 2025
"""

__version__ = "6.0.0-enterprise"
__author__ = "ICT Engine v6.1.0 Enterprise Team"

# Exports principales del módulo core
# __all__ temporalmente comentado hasta que se configuren los imports apropiados
# __all__ = [
#     'data_management',
#     'trading',
#     'risk_management', 
#     'analysis',
#     'ict_engine',
#     'smart_money_concepts',
#     'utils'
# ]

# Información del módulo
MODULE_INFO = {
    'name': 'core',
    'version': __version__,
    'description': 'Core functionality for ICT Engine v6.1.0 Enterprise',
    'sic_integration': 'v3.1',
    'components': [
        'data_management',
        'trading_engine', 
        'risk_management',
        'analytics',
        'analysis'  # ⚡ Agregado para dashboard
    ]
}
