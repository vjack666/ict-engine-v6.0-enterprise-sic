#!/usr/bin/env python3
"""
🔥 ICT ENGINE v6.0 ENTERPRISE - ADVANCED PATTERNS MODULE
=======================================================

Este módulo contiene patrones avanzados de ICT optimizados para trading enterprise.

Módulos disponibles:
- SilverBulletDetectorEnterprise: Detector enterprise de Silver Bullet kill zones
- JudasSwingDetectorEnterprise: Detector enterprise de Judas Swing patterns
- LiquidityGrabDetectorEnterprise: Detector enterprise de Liquidity Grab patterns

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 03 Septiembre 2025
"""

# Import base requerido para Silver Bullet Enterprise
from .silver_bullet_enterprise import (
    SilverBulletDetectorEnterprise,
    SilverBulletType,
    SilverBulletSignal,
    KillzoneStatus,
    TradingDirection
)

# Import para Judas Swing Enterprise
from .judas_swing_enterprise import (
    JudasSwingDetectorEnterprise,
    JudasSwingType,
    JudasSwingSignal,
    JudasSwingStatus
)

# Import para Liquidity Grab Enterprise
from .liquidity_grab_enterprise import (
    LiquidityGrabDetectorEnterprise,
    LiquidityGrabType,
    LiquidityGrabSignal,
    LiquidityGrabStatus,
    LiquidityLevel
)

# Import para Order Block Mitigation Enterprise
from .order_block_mitigation_enterprise import (
    OrderBlockMitigationDetectorEnterprise,
    OrderBlockMitigation,
    OrderBlockType,
    OrderBlockMitigationSignal,
    OrderBlockStatus,
    OrderBlockStrength
)

# Alias para compatibilidad con imports existentes
# OrderBlockMitigation ya está importado directamente arriba

# Import simplificado para compatibilidad
JudasSwingEnterprise = JudasSwingDetectorEnterprise
LiquidityGrabEnterprise = LiquidityGrabDetectorEnterprise

# Import para Pattern Analyzer Enterprise v6.0
from .pattern_analyzer_enterprise import (
    PatternAnalyzerEnterprise,
    PatternSignal,
    AnalysisResult,
    PatternType,
    ConfidenceLevel
)

# Versión y metadata
__version__ = "6.6.0"
__author__ = "ICT Engine v6.0 Enterprise Team"

# Exportaciones básicas funcionales
__all__ = [
    'SilverBulletDetectorEnterprise',
    'SilverBulletType',
    'SilverBulletSignal',
    'KillzoneStatus',
    'TradingDirection',
    'JudasSwingDetectorEnterprise',
    'JudasSwingType',
    'JudasSwingSignal',
    'JudasSwingStatus',
    'LiquidityGrabDetectorEnterprise',
    'LiquidityGrabType',
    'LiquidityGrabSignal',
    'LiquidityGrabStatus',
    'LiquidityLevel',
    'OrderBlockMitigationDetectorEnterprise',
    'OrderBlockMitigation',  # Alias para compatibilidad
    'OrderBlockType',
    'OrderBlockMitigationSignal',
    'OrderBlockStatus',
    'OrderBlockStrength',
    'JudasSwingEnterprise',  # Alias para compatibilidad
    'LiquidityGrabEnterprise',  # Alias para compatibilidad
    'PatternAnalyzerEnterprise',
    'PatternSignal',
    'AnalysisResult',
    'PatternType',
    'ConfidenceLevel'
]

# 🔄 COMPATIBILITY ALIASES para backwards compatibility
JudasSwingEnterprise = JudasSwingDetectorEnterprise
LiquidityGrabEnterprise = LiquidityGrabDetectorEnterprise
OrderBlockMitigation = OrderBlockMitigationDetectorEnterprise
SilverBulletEnterprise = SilverBulletDetectorEnterprise
