#!/usr/bin/env python3
"""
🎯 SILVER BULLET DASHBOARD MODULE
=================================

Módulo principal del dashboard Silver Bullet Enterprise.
Incluye controles de trading en vivo, monitoreo en tiempo real,
y análisis completo del sistema Silver Bullet optimizado.

Componentes:
- ✅ Silver Bullet Live Trading Controls
- ✅ Real-time Performance Monitor
- ✅ Signal Analysis Dashboard
- ✅ Risk Management Interface (usando RiskManager existente)
- ✅ Trading Statistics Viewer

Versión: v6.1.0-enterprise-silver-bullet
"""

from .silver_bullet_tab import SilverBulletTab
from .trading_controls import TradingControls
from .signal_monitor import SignalMonitor
from .performance_analyzer import PerformanceAnalyzer

# Usar RiskManager existente del sistema
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "01-CORE"))

try:
    from risk_management import RiskManager
except ImportError as e:
    print(f"⚠️ RiskManager no disponible: {e}")
    RiskManager = None

__all__ = [
    'SilverBulletTab',
    'TradingControls', 
    'SignalMonitor',
    'PerformanceAnalyzer',
    'RiskManager'
]
