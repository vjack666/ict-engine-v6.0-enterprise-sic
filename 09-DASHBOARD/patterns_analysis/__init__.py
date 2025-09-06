"""
🎯 ICT PATTERNS ANALYSIS DASHBOARD MODULE
========================================

Módulo modular para análisis de patrones ICT en el dashboard.
Arquitectura escalable y auto-mantenible.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: Septiembre 6, 2025
Versión: v1.0.0-modular
"""

from .base_pattern_module import BasePatternDashboard
from .pattern_factory import PatternFactory
from .patterns_orchestrator import PatternsOrchestrator

__version__ = "1.0.0-modular"
__all__ = [
    'BasePatternDashboard',
    'PatternFactory', 
    'PatternsOrchestrator'
]
