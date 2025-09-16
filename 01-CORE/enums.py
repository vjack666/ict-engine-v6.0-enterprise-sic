#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ICT ENGINE v6.0 ENTERPRISE - ENUMERATIONS
==========================================

Definiciones de enumeraciones para el sistema ICT Enterprise.
Incluye tipos de estructura, patrones y estados del sistema.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 2 Septiembre 2025
Versión: v6.0.0-enterprise
"""

from protocols.unified_logging import get_unified_logger
from enum import Enum, auto
from typing import List, Dict, Any

class StructureTypeV6(Enum):
    """
    🎯 Tipos de estructura de mercado ICT v6.0
    
    Enumeración para tipos de estructura de mercado utilizados
    en el análisis multi-timeframe y detección de patrones ICT.
    """
    
    # Break of Structure patterns
    BOS_BULLISH = "bos_bullish"
    BOS_BEARISH = "bos_bearish"
    
    # Change of Character patterns  
    CHOCH_BULLISH = "choch_bullish"
    CHOCH_BEARISH = "choch_bearish"
    
    # Market structure states
    CONSOLIDATION = "consolidation"
    BULLISH_STRUCTURE = "bullish_structure"
    BEARISH_STRUCTURE = "bearish_structure"
    
    # Advanced patterns
    LIQUIDITY_GRAB = "liquidity_grab"
    FAIR_VALUE_GAP = "fair_value_gap"
    ORDER_BLOCK = "order_block"
    BREAKER_BLOCK = "breaker_block"
    
    @classmethod
    def get_bullish_types(cls) -> List['StructureTypeV6']:
        """Retorna tipos de estructura bullish"""
        return [cls.BOS_BULLISH, cls.CHOCH_BULLISH, cls.BULLISH_STRUCTURE]
    
    @classmethod
    def get_bearish_types(cls) -> List['StructureTypeV6']:
        """Retorna tipos de estructura bearish"""
        return [cls.BOS_BEARISH, cls.CHOCH_BEARISH, cls.BEARISH_STRUCTURE]
    
    @classmethod
    def is_directional(cls, structure_type: 'StructureTypeV6') -> bool:
        """Verifica si el tipo de estructura es direccional"""
        return structure_type in (cls.get_bullish_types() + cls.get_bearish_types())

class PatternTypeV6(Enum):
    """
    📈 Tipos de patrones ICT v6.0
    
    Enumeración para tipos de patrones detectados por el
    sistema de análisis de patrones ICT Enterprise.
    """
    
    # Core ICT Patterns
    ORDER_BLOCK = "order_block"
    FAIR_VALUE_GAP = "fair_value_gap"
    BREAKER_BLOCK = "breaker_block"
    MITIGATION_BLOCK = "mitigation_block"
    
    # Smart Money Concepts
    LIQUIDITY_GRAB = "liquidity_grab"
    STOP_HUNT = "stop_hunt"
    MANIPULATION = "manipulation"
    INSTITUTIONAL_CANDLE = "institutional_candle"
    
    # Market Structure
    BREAK_OF_STRUCTURE = "break_of_structure"
    CHANGE_OF_CHARACTER = "change_of_character"
    MARKET_STRUCTURE_SHIFT = "market_structure_shift"
    
    # Advanced Patterns
    JUDAS_SWING = "judas_swing"
    SILVER_BULLET = "silver_bullet"
    POWER_OF_THREE = "power_of_three"
    OPTIMAL_TRADE_ENTRY = "optimal_trade_entry"

class TimeframeV6(Enum):
    """
    ⏰ Timeframes soportados ICT v6.0
    
    Enumeración para timeframes utilizados en análisis
    multi-timeframe del sistema ICT Enterprise.
    """
    
    # Higher Timeframes (HTF)
    MONTHLY = "M1"
    WEEKLY = "W1" 
    DAILY = "D1"
    H12 = "H12"
    H6 = "H6"
    H4 = "H4"
    H3 = "H3"
    H2 = "H2"
    H1 = "H1"
    
    # Lower Timeframes (LTF)
    M30 = "M30"
    M15 = "M15"
    M5 = "M5"
    M3 = "M3"
    M2 = "M2"
    M1 = "M1"
    
    @classmethod
    def get_htf_timeframes(cls) -> List['TimeframeV6']:
        """Retorna timeframes de alta temporalidad"""
        return [cls.MONTHLY, cls.WEEKLY, cls.DAILY, cls.H12, cls.H6, cls.H4]
    
    @classmethod
    def get_ltf_timeframes(cls) -> List['TimeframeV6']:
        """Retorna timeframes de baja temporalidad"""
        return [cls.M30, cls.M15, cls.M5, cls.M3, cls.M2, cls.M1]

class TradingDirectionV6(Enum):
    """
    📊 Direcciones de trading ICT v6.0
    
    Enumeración para direcciones de trading utilizadas
    en el sistema de análisis y toma de decisiones.
    """
    
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    CONSOLIDATION = "consolidation"
    
    @classmethod
    def get_directional(cls) -> List['TradingDirectionV6']:
        """Retorna direcciones direccionales (no neutral)"""
        return [cls.BULLISH, cls.BEARISH]

class SystemStateV6(Enum):
    """
    ⚙️ Estados del sistema ICT v6.0
    
    Enumeración para estados operativos del sistema
    ICT Engine Enterprise.
    """
    
    # Operational States
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    
    # Performance States
    OPTIMAL = "optimal"
    WARNING = "warning"
    CRITICAL = "critical"
    
    # Integration States
    SIC_AVAILABLE = "sic_available"
    SIC_FALLBACK = "sic_fallback"
    MT5_CONNECTED = "mt5_connected"
    MT5_DISCONNECTED = "mt5_disconnected"

class ConfidenceLevel(Enum):
    """
    🎯 Niveles de confianza ICT v6.0
    
    Enumeración para niveles de confianza en
    detección de patrones y señales de trading.
    """
    
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9
    EXCEPTIONAL = 0.95
    
    @classmethod
    def from_value(cls, value: float) -> 'ConfidenceLevel':
        """Convierte valor numérico a nivel de confianza"""
        if value >= 0.95:
            return cls.EXCEPTIONAL
        elif value >= 0.8:
            return cls.VERY_HIGH
        elif value >= 0.6:
            return cls.HIGH
        elif value >= 0.4:
            return cls.MEDIUM
        elif value >= 0.2:
            return cls.LOW
        else:
            return cls.VERY_LOW

# Diccionarios de mapeo para compatibilidad
STRUCTURE_TYPE_MAPPING = {
    "bos_bullish": StructureTypeV6.BOS_BULLISH,
    "bos_bearish": StructureTypeV6.BOS_BEARISH,
    "choch_bullish": StructureTypeV6.CHOCH_BULLISH,
    "choch_bearish": StructureTypeV6.CHOCH_BEARISH,
    "consolidation": StructureTypeV6.CONSOLIDATION,
    "bullish_structure": StructureTypeV6.BULLISH_STRUCTURE,
    "bearish_structure": StructureTypeV6.BEARISH_STRUCTURE,
}

TIMEFRAME_MAPPING = {
    "H4": TimeframeV6.H4,
    "M15": TimeframeV6.M15,
    "M5": TimeframeV6.M5,
    "H1": TimeframeV6.H1,
    "M30": TimeframeV6.M30,
    "D1": TimeframeV6.DAILY,
}

# Funciones de utilidad
def get_enum_info() -> Dict[str, Any]:
    """
    📋 Información completa de enumeraciones disponibles
    
    Returns:
        Diccionario con información de todas las enumeraciones
    """
    return {
        'version': 'v6.0.0-enterprise',
        'enums_available': {
            'StructureTypeV6': len(StructureTypeV6),
            'PatternTypeV6': len(PatternTypeV6),
            'TimeframeV6': len(TimeframeV6),
            'TradingDirectionV6': len(TradingDirectionV6),
            'SystemStateV6': len(SystemStateV6),
            'ConfidenceLevel': len(ConfidenceLevel),
        },
        'total_enums': 6,
        'compatibility_mappings': {
            'structure_types': len(STRUCTURE_TYPE_MAPPING),
            'timeframes': len(TIMEFRAME_MAPPING),
        }
    }

def validate_enum_compatibility() -> bool:
    """
    ✅ Validar compatibilidad de enumeraciones
    
    Returns:
        True si todas las enumeraciones son válidas
    """
    try:
        # Verificar que todas las enumeraciones tengan valores válidos
        for enum_class in [StructureTypeV6, PatternTypeV6, TimeframeV6, 
                          TradingDirectionV6, SystemStateV6, ConfidenceLevel]:
            if len(enum_class) == 0:
                return False
        
        # Verificar mapeos
        for mapping in [STRUCTURE_TYPE_MAPPING, TIMEFRAME_MAPPING]:
            if len(mapping) == 0:
                return False
        
        return True
    except Exception:
        return False

# Exports principales
__all__ = [
    'StructureTypeV6',
    'PatternTypeV6', 
    'TimeframeV6',
    'TradingDirectionV6',
    'SystemStateV6',
    'ConfidenceLevel',
    'STRUCTURE_TYPE_MAPPING',
    'TIMEFRAME_MAPPING',
    'get_enum_info',
    'validate_enum_compatibility'
]
