#!/usr/bin/env python3
"""
🎯 DASHBOARD TABS MODULE v6.0 ENTERPRISE
=======================================

Módulo de pestañas especializadas para el dashboard ICT Engine v6.0.
Contiene componentes de UI para diferentes aspectos del sistema de trading.

Pestañas disponibles:
- OrderBlocksTab: Visualización de Order Blocks en tiempo real

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 12 Septiembre 2025
"""

from .order_blocks_tab import OrderBlocksTab, create_order_blocks_tab
from .performance_tab import PerformanceTab, create_performance_tab  # nueva métrica de ejecución
from .risk_health_tab import RiskHealthTab, create_risk_health_tab  # nueva pestaña riesgo/salud

__all__ = [
    'OrderBlocksTab', 'create_order_blocks_tab',
    'PerformanceTab', 'create_performance_tab',
    'RiskHealthTab', 'create_risk_health_tab'
]