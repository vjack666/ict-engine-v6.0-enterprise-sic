"""
🎯 Risk Management Module - ICT Engine v6.0 Enterprise
====================================================

Módulo de gestión de riesgo para el sistema ICT Engine v6.0 Enterprise.
Proporciona herramientas avanzadas de gestión de riesgo para trading live.

Componentes:
- RiskManager: Gestor principal de riesgo
- ICTRiskConfig: Configuración específica ICT
- RiskAlert: Sistema de alertas de riesgo
- RiskMetrics: Métricas de riesgo

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 14 Agosto 2025
"""

from .risk_manager import RiskManager, ICTRiskConfig, RiskAlert, RiskMetrics

# Nuevo módulo de cálculo de posiciones
try:
    from .position_sizing import (
        PositionSizingCalculator,
        PositionSizingParameters,
        PositionSizingResult,
        RiskMethod,
        RiskLevel,
        create_position_sizing_calculator,
        quick_position_calculation,
        calculate_conservative_position,
        calculate_moderate_position
    )
    POSITION_SIZING_AVAILABLE = True
except ImportError:
    PositionSizingCalculator = None
    PositionSizingParameters = None
    PositionSizingResult = None
    RiskMethod = None
    RiskLevel = None
    create_position_sizing_calculator = None
    quick_position_calculation = None
    calculate_conservative_position = None
    calculate_moderate_position = None
    POSITION_SIZING_AVAILABLE = False

__all__ = [
    # Módulos originales
    'RiskManager',
    'ICTRiskConfig', 
    'RiskAlert',
    'RiskMetrics',
    
    # Nuevo módulo PositionSizing
    'PositionSizingCalculator',
    'PositionSizingParameters',
    'PositionSizingResult',
    'RiskMethod',
    'RiskLevel',
    
    # Factory functions
    'create_position_sizing_calculator',
    'quick_position_calculation',
    'calculate_conservative_position',
    'calculate_moderate_position',
    
    # Flags de disponibilidad
    'POSITION_SIZING_AVAILABLE'
]

__version__ = "6.0.0"
