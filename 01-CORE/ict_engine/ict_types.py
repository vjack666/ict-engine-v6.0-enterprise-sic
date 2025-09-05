"""
ICT Types v6.0 Enterprise - Estructuras de Datos ICT Fundamentales
================================================================

Definición de tipos, enums y dataclasses para el ICT Engine v6.1.0 Enterprise.
Integrado con SIC v3.1 Enterprise y SLUC v2.1 para máxima compatibilidad.

Características v6.0:
- Integración completa con SIC v3.1 Enterprise
- Logging centralizado con SLUC v2.1
- Smart Money Concepts types
- Market Structure types avanzados
- Performance optimizado
- Documentación enterprise

Autor: ICT Engine v6.1.0 Team
Versión: v6.1.0-enterprise
Fecha: Agosto 2025
"""

# =============================================================================
# IMPORTS VIA SIC v3.1 ENTERPRISE
# =============================================================================

# Imports básicos estándar (seguros)
from enum import Enum
import time
from datetime import datetime, time as time_obj
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field

# =============================================================================
# LOGGING VIA SLUC v2.1
# =============================================================================

def enviar_senal_log(nivel: str, mensaje: str, fuente: str = "ict_types", categoria: str = "ict"):
    """Función de logging simplificada para ICT Types"""
    print(f"[{nivel}] {fuente}: {mensaje}")

# =============================================================================
# ENUMS ICT FUNDAMENTALES
# =============================================================================

class ICTPattern(Enum):
    """🎯 Patrones ICT Enterprise v6.0"""
    # Patrones clásicos ICT
    JUDAS_SWING = "judas_swing"
    OPTIMAL_TRADE_ENTRY = "optimal_trade_entry"
    LIQUIDITY_GRAB = "liquidity_grab"
    SILVER_BULLET = "silver_bullet"
    POWER_OF_THREE = "power_of_three"
    
    # Estructura de mercado
    FAIR_VALUE_GAP = "fair_value_gap"
    ORDER_BLOCK = "order_block"
    BREAK_OF_STRUCTURE = "break_of_structure"
    CHANGE_OF_CHARACTER = "change_of_character"
    
    # Smart Money Concepts v6.0
    INSTITUTIONAL_ORDER_FLOW = "institutional_order_flow"
    SMART_MONEY_REVERSAL = "smart_money_reversal"
    LIQUIDITY_POOL_TARGETING = "liquidity_pool_targeting"
    STOP_HUNT_PATTERN = "stop_hunt_pattern"
    INDUCEMENT_MOVE = "inducement_move"
    
    # Patrones avanzados
    MORNING_REVERSAL = "morning_reversal"
    LONDON_CLOSE_REVERSAL = "london_close_reversal"
    NEW_YORK_BREAKOUT = "new_york_breakout"


class MarketPhase(Enum):
    """📊 Fases del mercado según metodología ICT"""
    ACCUMULATION = "accumulation"      # Smart Money acumulando posiciones
    MANIPULATION = "manipulation"     # Movimientos falsos para generar liquidez
    DISTRIBUTION = "distribution"     # Smart Money distribuyendo/saliendo
    REBALANCE = "rebalance"           # Corrección técnica/consolidación
    EXPANSION = "expansion"           # Movimiento institucional fuerte
    CONSOLIDATION = "consolidation"   # Rango de acumulación/distribución


class TradingDirection(Enum):
    """📈 Direcciones de trading"""
    BULLISH = "bullish"
    BEARISH = "bearish" 
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"
    
    # Aliases para compatibilidad con patrones enterprise
    BUY = "bullish"
    SELL = "bearish"


class SessionType(Enum):
    """🌍 Sesiones de trading ICT"""
    ASIAN = "asian"                   # 21:00-08:00 GMT - Baja volatilidad
    LONDON = "london"                 # 08:00-16:00 GMT - Establecimiento dirección
    NEW_YORK = "new_york"            # 13:00-21:00 GMT - Momentum y continuación
    LONDON_CLOSE = "london_close"    # 15:30-16:30 GMT - Movimientos finales
    OVERLAP = "overlap"              # 13:00-16:00 GMT - Máxima liquidez


class TimeFrame(Enum):
    """⏰ Timeframes para análisis multi-temporal"""
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


# =============================================================================
# SMART MONEY CONCEPTS v6.0
# =============================================================================

class SmartMoneyType(Enum):
    """💰 Tipos de Smart Money Concepts"""
    INSTITUTIONAL_BUYING = "institutional_buying"
    INSTITUTIONAL_SELLING = "institutional_selling"
    LIQUIDITY_GRAB_BULLISH = "liquidity_grab_bullish"
    LIQUIDITY_GRAB_BEARISH = "liquidity_grab_bearish"
    STOP_HUNT_UPWARD = "stop_hunt_upward"
    STOP_HUNT_DOWNWARD = "stop_hunt_downward"
    INDUCEMENT_BULLISH = "inducement_bullish"
    INDUCEMENT_BEARISH = "inducement_bearish"


class LiquidityLevel(Enum):
    """💧 Niveles de liquidez"""
    HIGH = "high"                     # Alta liquidez disponible
    MEDIUM = "medium"                 # Liquidez moderada
    LOW = "low"                       # Baja liquidez
    DEPLETED = "depleted"             # Liquidez agotada


class StructureType(Enum):
    """🏗️ Tipos de estructura de mercado"""
    # Change of Character
    CHOCH_BULLISH = "choch_bullish"
    CHOCH_BEARISH = "choch_bearish"
    
    # Break of Structure
    BOS_BULLISH = "bos_bullish"
    BOS_BEARISH = "bos_bearish"
    
    # Market States
    RANGE_BOUND = "range_bound"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    CONSOLIDATION = "consolidation"


class FVGType(Enum):
    """📊 Tipos de Fair Value Gap"""
    BULLISH_FVG = "bullish_fvg"
    BEARISH_FVG = "bearish_fvg"
    BALANCED_FVG = "balanced_fvg"
    PREMIUM_FVG = "premium_fvg"
    DISCOUNT_FVG = "discount_fvg"


class OrderBlockType(Enum):
    """📦 Tipos de Order Block"""
    BULLISH_OB = "bullish_ob"
    BEARISH_OB = "bearish_ob"
    BREAKER_BLOCK = "breaker_block"
    MITIGATION_BLOCK = "mitigation_block"


# =============================================================================
# DATACLASSES ICT ENTERPRISE
# =============================================================================

@dataclass
class ICTSignal:
    """🎯 Señal ICT unificada enterprise"""
    pattern_type: ICTPattern
    direction: TradingDirection
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    timestamp: datetime
    timeframe: TimeFrame
    session: SessionType
    market_phase: MarketPhase
    narrative: str
    confluence_factors: List[str] = field(default_factory=list)
    smart_money_confluence: bool = False
    structure_confluence: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class SmartMoneySignal:
    """💰 Señal Smart Money Concepts"""
    smart_money_type: SmartMoneyType
    direction: TradingDirection
    confidence: float
    liquidity_level: LiquidityLevel
    entry_price: float
    target_price: float
    invalidation_price: float
    timestamp: datetime
    timeframe: TimeFrame
    volume_confirmation: bool
    institutional_footprint: bool
    narrative: str
    confluence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketStructureData:
    """🏗️ Datos de estructura de mercado"""
    structure_type: StructureType
    break_level: float
    confirmation_level: float
    target_level: float
    timestamp: datetime
    timeframe: TimeFrame
    confidence: float
    swing_high: Optional[float] = None
    swing_low: Optional[float] = None
    previous_structure: Optional['MarketStructureData'] = None
    narrative: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FairValueGap:
    """📊 Fair Value Gap detectado"""
    fvg_type: FVGType
    high_price: float
    low_price: float
    gap_size: float
    origin_candle_index: int
    filled_percentage: float
    is_mitigated: bool
    mitigation_candle_index: Optional[int]
    timestamp: datetime
    timeframe: TimeFrame
    narrative: str
    confluence_with_structure: bool = False
    confluence_with_orderblock: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderBlock:
    """📦 Order Block detectado"""
    ob_type: OrderBlockType
    high_price: float
    low_price: float
    origin_candle_index: int
    reaction_strength: float
    test_count: int
    is_tested: bool
    is_broken: bool
    timestamp: datetime
    timeframe: TimeFrame
    volume_profile: Optional[float] = None
    institutional_signature: bool = False
    narrative: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LiquidityPool:
    """💧 Pool de liquidez identificado"""
    price_level: float
    liquidity_amount: float
    liquidity_level: LiquidityLevel
    pool_type: str  # "buy_stops", "sell_stops", "liquidity_void"
    timestamp: datetime
    timeframe: TimeFrame
    is_swept: bool = False
    sweep_timestamp: Optional[datetime] = None
    accumulation_period: int = 0  # Número de velas acumulando
    narrative: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# CONFIGURACIÓN ICT ENTERPRISE
# =============================================================================

@dataclass
class ICTConfig:
    """⚙️ Configuración ICT Enterprise"""
    # Timeframes para análisis
    primary_timeframe: TimeFrame = TimeFrame.H1
    secondary_timeframe: TimeFrame = TimeFrame.H4
    confirmation_timeframe: TimeFrame = TimeFrame.M15
    
    # Configuración de detección
    min_confidence: float = 75.0
    require_confluence: bool = True
    min_confluence_factors: int = 2
    
    # Smart Money settings
    enable_smart_money: bool = True
    liquidity_detection: bool = True
    stop_hunt_detection: bool = True
    
    # Sesiones activas
    active_sessions: List[SessionType] = field(default_factory=lambda: [
        SessionType.LONDON, SessionType.NEW_YORK, SessionType.OVERLAP
    ])
    
    # Risk management
    max_risk_per_trade: float = 2.0
    min_risk_reward: float = 1.5
    
    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # Performance
    enable_caching: bool = True
    cache_duration: int = 300  # 5 minutos
    
    def __post_init__(self):
        """Post-inicialización con logging"""
        if self.enable_logging:
            enviar_senal_log(
                "INFO", 
                f"ICT Config inicializada - Timeframe primario: {self.primary_timeframe.value}",
                "ict_types",
                "config"
            )


# =============================================================================
# FUNCIONES UTILITY
# =============================================================================

def validate_ict_signal(signal: ICTSignal) -> bool:
    """
    ✅ Valida una señal ICT
    
    Args:
        signal: Señal ICT a validar
        
    Returns:
        True si la señal es válida
    """
    try:
        # Validaciones básicas
        if signal.confidence < 0 or signal.confidence > 100:
            return False
            
        if signal.risk_reward_ratio < 0:
            return False
            
        if signal.entry_price <= 0:
            return False
            
        # Validar dirección vs precios
        if signal.direction == TradingDirection.BULLISH:
            if signal.take_profit <= signal.entry_price:
                return False
            if signal.stop_loss >= signal.entry_price:
                return False
        elif signal.direction == TradingDirection.BEARISH:
            if signal.take_profit >= signal.entry_price:
                return False
            if signal.stop_loss <= signal.entry_price:
                return False
                
        return True
        
    except Exception as e:
        enviar_senal_log("ERROR", f"Error validando señal ICT: {e}", "ict_types", "validation")
        return False


def create_ict_narrative(signal: ICTSignal) -> str:
    """
    📝 Crea narrativa para señal ICT
    
    Args:
        signal: Señal ICT
        
    Returns:
        Narrativa descriptiva
    """
    direction_text = "📈 BULLISH" if signal.direction == TradingDirection.BULLISH else "📉 BEARISH"
    
    narrative = f"{direction_text} {signal.pattern_type.value.upper()}\n"
    narrative += f"💪 Confianza: {signal.confidence:.1f}%\n"
    narrative += f"⚖️ R:R: {signal.risk_reward_ratio:.2f}\n"
    narrative += f"🕐 Sesión: {signal.session.value}\n"
    narrative += f"📊 Fase: {signal.market_phase.value}\n"
    
    if signal.confluence_factors:
        narrative += f"🎯 Confluencias: {', '.join(signal.confluence_factors)}\n"
        
    if signal.smart_money_confluence:
        narrative += "💰 Confluencia Smart Money ✅\n"
        
    if signal.structure_confluence:
        narrative += "🏗️ Confluencia Estructura ✅\n"
    
    return narrative


# =============================================================================
# LOGGING DE INICIALIZACIÓN
# =============================================================================

# Log de inicialización exitosa
enviar_senal_log(
    "INFO",
    "ICT Types v6.0 Enterprise inicializado correctamente",
    "ict_types",
    "init"
)

enviar_senal_log(
    "INFO", 
    f"Tipos disponibles: {len(ICTPattern.__members__)} patrones ICT, {len(SmartMoneyType.__members__)} Smart Money types",
    "ict_types",
    "init"
)
