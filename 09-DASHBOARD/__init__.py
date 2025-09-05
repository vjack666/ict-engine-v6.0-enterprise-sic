"""
🎯 ICT Dashboard v6.1 Enterprise - Main Module
============================================

Dashboard modular principal del ICT Engine v6.1 Enterprise.
Basado en tests existentes y diseñado para producción.

Características:
- ✅ Interfaz modular Rich/Textual
- ✅ Datos en tiempo real del sistema FVG
- ✅ Análisis de coherencia integrado
- ✅ Monitoreo de patrones ICT
- ✅ Sistema de alertas inteligente
- ✅ Métricas de rendimiento

Versión: v6.1.0-enterprise-dashboard
Fecha: 4 de Septiembre 2025
"""

from .ict_dashboard import ICTDashboard
from .core import DashboardEngine
from .data.data_collector import RealICTDataCollector, DashboardData
from .widgets import MainDashboardInterface
from .components import FVGStatsWidget, MarketDataWidget, CoherenceAnalysisWidget, AlertsWidget

__version__ = "6.1.0-enterprise"
__author__ = "ICT Engine v6.1 Enterprise Team"

__all__ = [
    'ICTDashboard',
    'DashboardEngine',
    'RealICTDataCollector',
    'DashboardData',
    'MainDashboardInterface',
    'FVGStatsWidget',
    'MarketDataWidget',
    'CoherenceAnalysisWidget', 
    'AlertsWidget'
]
