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

__all__ = [
    'RiskManager',
    'ICTRiskConfig', 
    'RiskAlert',
    'RiskMetrics'
]

__version__ = "6.0.0"
