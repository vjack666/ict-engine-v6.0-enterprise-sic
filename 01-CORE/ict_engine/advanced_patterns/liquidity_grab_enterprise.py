#!/usr/bin/env python3
"""
🌊 LIQUIDITY GRAB DETECTOR ENTERPRISE v6.0
===========================================

Detector profesional de Liquidity Grab patterns según metodología ICT:
- Stop hunt detection (ruptura de highs/lows recientes)
- Quick reversal confirmation
- Volume spike validation
- Institutional footprint detection
- Confluencia con POI y Smart Money structures

FASE 5: Advanced Patterns Migration
Basado en: Judas Swing Enterprise v6.0 architecture
Target: Enterprise v6.0 SIC architecture

Autor: ICT Engine Team
Sprint: FASE 5 - Advanced Patterns
Fecha: 03 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import numpy as np

# ThreadSafe pandas import para runtime
from data_management.advanced_candle_downloader import _pandas_manager

# ✅ Integración con memoria histórica de CHoCH
try:
    from memory.choch_historical_memory import (
        adjust_confidence_with_memory as choch_adjust_confidence_with_memory,
        predict_target_based_on_history as choch_predict_target,
        find_similar_choch_in_history,
        calculate_historical_success_rate,
    )
    from memory.choch_helpers import estimate_break_level_from_swings as choch_estimate_break_level
    CHOCH_MEMORY_AVAILABLE = True
except Exception:
    CHOCH_MEMORY_AVAILABLE = False

    def choch_adjust_confidence_with_memory(base_confidence: float, symbol: str, timeframe: str, break_level: float) -> float:
        return float(base_confidence)

    def choch_predict_target(symbol: str, timeframe: str, direction: str, break_level: float, default_target: Optional[float] = None) -> Optional[float]:
        return default_target

    def find_similar_choch_in_history(symbol: str, timeframe: str, direction: Optional[str] = None, break_level_range: Optional[Tuple[float, float]] = None):
        return []

    def calculate_historical_success_rate(symbol: str, timeframe: str, direction: Optional[str] = None) -> float:
        return 0.0

    def choch_estimate_break_level(data: Any, direction: str, lookback: int = 20) -> float:
        try:
            recent = data.tail(lookback)
            if direction.lower() in ("buy", "bullish"):
                return float(recent['high'].max())
            elif direction.lower() in ("sell", "bearish"):
                return float(recent['low'].min())
            return float(recent['close'].iloc[-1])
        except Exception:
            return 0.0

# Import pandas solo para tipado estático
if TYPE_CHECKING:
    from typing import Any as DataFrameType
else:
    DataFrameType = Any

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - UNIFIED LOGGING OPTIMIZADO
try:
    from ..unified_logging import log_info, log_warning, log_error, log_debug, SmartTradingLogger, create_unified_logger
    from analysis.unified_memory_system import get_unified_memory_system
    from data_management.advanced_candle_downloader import _pandas_manager
    UNIFIED_MEMORY_AVAILABLE = True
    ENTERPRISE_COMPONENTS_AVAILABLE = True
except ImportError:
    try:
        # Fallback para imports desde nivel superior
        from protocols.unified_logging import get_unified_logger
        from analysis.unified_memory_system import get_unified_memory_system
        from data_management.advanced_candle_downloader import _pandas_manager
        UNIFIED_MEMORY_AVAILABLE = True
        ENTERPRISE_COMPONENTS_AVAILABLE = True
    except ImportError:
        # Fallback completo
        import logging
        _fallback_logger = logging.getLogger("LIQUIDITY_GRAB_FALLBACK")
        if not _fallback_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [LIQUIDITY_GRAB] [%(levelname)s] %(message)s', '%H:%M:%S')
            handler.setFormatter(formatter)
            _fallback_logger.addHandler(handler)
            _fallback_logger.setLevel(logging.INFO)
        
        def log_info(message: str, component: str = "LIQUIDITY_GRAB"):
            _fallback_logger.info(f"[{component}] {message}")
        def log_warning(message: str, component: str = "LIQUIDITY_GRAB"):
            _fallback_logger.warning(f"[{component}] {message}")
        def log_error(message: str, component: str = "LIQUIDITY_GRAB"):
            _fallback_logger.error(f"[{component}] {message}")
        def log_debug(message: str, component: str = "LIQUIDITY_GRAB"):
            _fallback_logger.debug(f"[{component}] {message}")
        
        SmartTradingLogger = Any
        create_unified_logger = lambda x: None
        UNIFIED_MEMORY_AVAILABLE = False
        ENTERPRISE_COMPONENTS_AVAILABLE = False
    
    def get_unified_memory_system() -> Optional[Any]:
        """Fallback para testing cuando UnifiedMemorySystem no está disponible"""
        return None

# Import shared enums
from enum import Enum
class TradingDirection(Enum):
    BUY = "buy"
    SELL = "sell"
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class LiquidityGrabType(Enum):
    """🌊 Tipos de Liquidity Grab según contexto ICT"""
    ASIAN_RANGE_GRAB = "asian_range_grab"        # Asia range liquidity sweep
    LONDON_BREAKOUT_GRAB = "london_breakout_grab"  # London session stops hunt
    NY_LIQUIDITY_SWEEP = "ny_liquidity_sweep"    # NY session aggressive grab
    WEEKLY_HIGH_GRAB = "weekly_high_grab"        # Weekly highs liquidity
    DAILY_LOW_GRAB = "daily_low_grab"            # Daily lows sweep
    LIQUIDITY_VOID_FILL = "liquidity_void_fill"  # Fill liquidity voids


class LiquidityGrabStatus(Enum):
    """📊 Status del Liquidity Grab"""
    SETUP_BUILDING = "setup_building"           # Acumulando stops
    STOPS_HUNTED = "stops_hunted"               # Stops cazados
    REVERSAL_ACTIVE = "reversal_active"         # Reversal en progreso
    PROFIT_TAKING = "profit_taking"             # Tomando ganancias
    INVALIDATED = "invalidated"                 # Setup invalidado
    COMPLETED = "completed"                     # Pattern completado


class LiquidityLevel(Enum):
    """💧 Niveles de liquidez"""
    HIGH_LIQUIDITY = "high_liquidity"           # Alta concentración
    MEDIUM_LIQUIDITY = "medium_liquidity"       # Liquidez moderada
    LOW_LIQUIDITY = "low_liquidity"             # Poca liquidez
    INSTITUTIONAL = "institutional"             # Liquidez institucional


@dataclass
class LiquidityGrabSignal:
    """🌊 Señal Liquidity Grab Enterprise v6.0"""
    signal_type: LiquidityGrabType
    confidence: float
    direction: TradingDirection
    liquidity_level: LiquidityLevel
    grab_price: float
    reversal_confirmation_price: float
    stops_hunted_estimate: int
    
    # 📊 Trading Levels
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    
    # 🔍 Pattern Analysis
    stop_hunt_strength: float
    reversal_speed_score: float
    volume_spike_intensity: float
    institutional_footprint_score: float
    liquidity_density: float
    smart_money_confirmation: bool
    
    # 📝 Metadata
    narrative: str
    timestamp: datetime
    session_context: Dict[str, Any]
    symbol: str
    timeframe: str
    
    # ✅ CHoCH MEMORY INTEGRATION
    choch_confidence_bonus: float = 0.0
    similar_choch_count: int = 0
    historical_success_rate: float = 0.0
    choch_level_estimate: float = 0.0
    
    # 🔄 Lifecycle 
    status: LiquidityGrabStatus = LiquidityGrabStatus.SETUP_BUILDING
    expiry_time: Optional[datetime] = None
    analysis_id: str = ""


class LiquidityGrabDetectorEnterprise:
    """
    🌊 LIQUIDITY GRAB DETECTOR ENTERPRISE v6.0
    ===========================================
    
    Detector profesional de patrones Liquidity Grab con:
    ✅ Stop hunt detection avanzado
    ✅ Quick reversal confirmation en tiempo real
    ✅ Volume spike validation 
    ✅ Institutional footprint detection
    ✅ Liquidity density mapping
    ✅ Smart Money confirmation
    ✅ UnifiedMemorySystem v6.1 integration
    ✅ SLUC v2.1 logging completo
    ✅ Real-time MT5 data support
    """

    def __init__(self, 
                 memory_system: Optional[Any] = None,
                 logger: Optional[Any] = None):
        """🚀 Inicializa Liquidity Grab Detector Enterprise"""
        # 🏗️ ENTERPRISE INFRASTRUCTURE
        self.memory_system = memory_system
        # Central SIC logger only
        self.logger = logger if logger is not None else None
        log_info("🌊 Inicializando Liquidity Grab Detector Enterprise v6.0")
        
        # 🎯 DETECTION CONFIGURATION
        self.config = {
            'min_confidence': 72.0,
            'stop_hunt_min_pips': 3,
            'stop_hunt_max_pips': 15,
            'reversal_confirmation_pips': 8,
            'quick_reversal_timeframe': 3,  # velas
            'volume_spike_threshold': 1.8,
            'institutional_threshold': 0.75,
            'liquidity_density_periods': 30,
            
            # Pesos para confidence scoring
            'stop_hunt_weight': 0.30,
            'reversal_speed_weight': 0.25,
            'volume_weight': 0.20,
            'institutional_weight': 0.15,
            'liquidity_density_weight': 0.10,
            
            # Bonos por confluencias
            'smart_money_bonus': 0.12,
            'session_timing_bonus': 0.08,
            'multiple_timeframe_bonus': 0.10,
            
            # ✅ CONFIGURACIÓN CHOCH MEMORIA
            'use_choch_memory': True,
            'choch_confidence_max_bonus': 10.0,
            'choch_level_lookback': 20
        }
        
        # 🌊 LIQUIDITY LEVELS MAPPING
        self.liquidity_levels = {
            'previous_day_high': {'weight': 0.9, 'type': LiquidityLevel.HIGH_LIQUIDITY},
            'previous_day_low': {'weight': 0.9, 'type': LiquidityLevel.HIGH_LIQUIDITY},
            'session_high': {'weight': 0.8, 'type': LiquidityLevel.MEDIUM_LIQUIDITY},
            'session_low': {'weight': 0.8, 'type': LiquidityLevel.MEDIUM_LIQUIDITY},
            'swing_high': {'weight': 0.7, 'type': LiquidityLevel.MEDIUM_LIQUIDITY},
            'swing_low': {'weight': 0.7, 'type': LiquidityLevel.MEDIUM_LIQUIDITY},
            'round_numbers': {'weight': 0.6, 'type': LiquidityLevel.LOW_LIQUIDITY},
            'institutional_levels': {'weight': 1.0, 'type': LiquidityLevel.INSTITUTIONAL}
        }
        
        # 💾 MEMORY INTEGRATION ENTERPRISE
        if UNIFIED_MEMORY_AVAILABLE:
            self.unified_memory = get_unified_memory_system()
            if self.unified_memory:
                log_info("✅ UnifiedMemorySystem v6.1 integrado exitosamente")
            else:
                log_warning("⚠️ UnifiedMemorySystem no inicializado - usando fallback")
                self.unified_memory = None
        else:
            log_warning("⚠️ UnifiedMemorySystem no disponible - usando pattern_memory local")
            self.unified_memory = None
        
        # Fallback local para compatibilidad
        self.pattern_memory = {
            'successful_grab_setups': [],
            'failed_grab_setups': [],
            'liquidity_performance': {},
            'institutional_patterns': []
        }
        
        # 📊 ESTADO INTERNO ENTERPRISE
        self.last_analysis = None
        self.detected_liquidity_levels = []
        self.current_grab_status = None
        self.session_stats = {}
        
        log_info("✅ Liquidity Grab Detector Enterprise v6.0 inicializado correctamente")

    def detect(self, data: DataFrameType, symbol: str, timeframe: str, **kwargs) -> Dict[str, Any]:
        """
        🎯 Método detect unificado para compatibilidad con dashboard
        
        Args:
            data: Datos de velas
            symbol: Símbolo del instrumento  
            timeframe: Marco temporal
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con resultado de detección compatible con dashboard
        """
        try:
            # Usar el método principal de detección
            signals = self.detect_liquidity_grab_patterns(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                current_price=kwargs.get('current_price', 0.0),
                detected_order_blocks=kwargs.get('detected_order_blocks'),
                market_structure_context=kwargs.get('market_structure_context')
            )
            
            if not signals:
                return {
                    'confidence': 0.0,
                    'strength': 0.0,
                    'direction': 'NEUTRAL',
                    'entry_zone': (0.0, 0.0),
                    'stop_loss': 0.0,
                    'take_profit_1': 0.0,
                    'narrative': 'No se detectaron patrones Liquidity Grab válidos',
                    'source': 'liquidity_grab_enterprise'
                }
            
            # Tomar la mejor señal
            best_signal = max(signals, key=lambda s: s.confidence)
            
            # Convertir a formato compatible con dashboard
            return {
                'confidence': best_signal.confidence,
                'strength': getattr(best_signal, 'grab_strength', best_signal.confidence),
                'direction': best_signal.direction.value if hasattr(best_signal.direction, 'value') else str(best_signal.direction),
                'entry_zone': (best_signal.entry_price - 5, best_signal.entry_price + 5),
                'stop_loss': best_signal.stop_loss,
                'take_profit_1': best_signal.take_profit_1,
                'take_profit_2': getattr(best_signal, 'take_profit_2', None),
                'risk_reward_ratio': abs(best_signal.take_profit_1 - best_signal.entry_price) / abs(best_signal.entry_price - best_signal.stop_loss) if best_signal.stop_loss != best_signal.entry_price else 0.0,
                'probability': best_signal.confidence * 0.75,  # Conservative estimate
                'session': 'LIQUIDITY_GRAB',
                'confluences': getattr(best_signal, 'confluences', []),
                'invalidation_criteria': f'Precio por encima de {best_signal.stop_loss}' if best_signal.direction == 'SELL' else f'Precio por debajo de {best_signal.stop_loss}',
                'narrative': best_signal.narrative,
                'source': 'liquidity_grab_enterprise'
            }
            
        except Exception as e:
            log_error(f"Error en detect method: {e}", "liquidity_grab_enterprise")
            return {
                'confidence': 0.0,
                'strength': 0.0,
                'direction': 'NEUTRAL',
                'entry_zone': (0.0, 0.0),
                'stop_loss': 0.0,
                'take_profit_1': 0.0,
                'narrative': f'Error en detección Liquidity Grab: {str(e)}',
                'source': 'liquidity_grab_enterprise_error'
            }

    def detect_liquidity_grab_patterns(self, 
                                      data: DataFrameType,
                                      symbol: str,
                                      timeframe: str,
                                      current_price: float = 0.0,
                                      detected_order_blocks: Optional[List[Dict]] = None,
                                      market_structure_context: Optional[Dict] = None) -> List[LiquidityGrabSignal]:
        """
        🌊 DETECCIÓN PRINCIPAL LIQUIDITY GRAB ENTERPRISE
        
        Args:
            data: Datos de velas (M5 primary)
            symbol: Par de divisa (ej: EURUSD)
            timeframe: Timeframe principal (M5 recomendado)
            current_price: Precio actual del mercado
            detected_order_blocks: Order Blocks detectados previamente
            market_structure_context: Contexto de estructura de mercado
            
        Returns:
            Lista de señales Liquidity Grab detectadas
        """
        try:
            # Obtener instancia thread-safe de pandas
            pd = _pandas_manager.get_safe_pandas_instance()
            
            log_info(f"🌊 Iniciando detección Liquidity Grab para {symbol} {timeframe}")
            
            # 🧹 VALIDACIONES INICIALES
            if data is None or data.empty:
                log_warning("❌ Sin datos para análisis Liquidity Grab")
                return []
            
            if len(data) < 30:  # Necesitamos datos suficientes para liquidity mapping
                log_warning(f"❌ Insuficientes datos: {len(data)} < 30 velas")
                return []
            
            # 📊 PREPARAR DATOS
            current_price = current_price or data['close'].iloc[-1]
            detected_order_blocks = detected_order_blocks or []
            
            # 1. 🌊 MAPEAR NIVELES DE LIQUIDEZ
            liquidity_map = self._map_liquidity_levels_enterprise(data)
            
            if not liquidity_map['levels']:
                log_debug("🌊 No se detectaron niveles de liquidez significativos")
                return []
            
            # 2. 🎯 DETECTAR STOP HUNT
            stop_hunt_score, hunt_details = self._detect_stop_hunt_enterprise(
                data, liquidity_map, current_price
            )
            
            if stop_hunt_score < 0.6:
                log_debug(f"🎯 Stop hunt insuficiente: {stop_hunt_score:.2f}")
                return []
            
            # 3. ⚡ VALIDAR QUICK REVERSAL
            reversal_score, reversal_speed = self._validate_quick_reversal_enterprise(
                data, hunt_details, current_price
            )
            
            # 4. 📈 ANALIZAR VOLUME SPIKE
            volume_score, volume_intensity = self._analyze_volume_spike_enterprise(data)
            
            # 5. 🏛️ DETECTAR INSTITUTIONAL FOOTPRINT
            institutional_score, smart_money_confirmed = self._detect_institutional_footprint_enterprise(
                data, hunt_details, detected_order_blocks
            )
            
            # 6. 💧 CALCULAR LIQUIDITY DENSITY
            density_score = self._calculate_liquidity_density_enterprise(
                liquidity_map, hunt_details
            )
            
            # 7. 🧮 CALCULAR CONFIANZA TOTAL ENTERPRISE
            total_confidence, choch_bonus = self._calculate_liquidity_grab_confidence_enterprise(
                stop_hunt_score, reversal_score, volume_score, 
                institutional_score, density_score,
                symbol=symbol, grab_price=hunt_details.get('hunt_price', current_price)
            )
            
            # 8. ✅ VALIDAR THRESHOLD
            if total_confidence < self.config['min_confidence']:
                log_debug(f"🌊 Confianza insuficiente: {total_confidence:.1f}% < {self.config['min_confidence']}%")
                return []
            
            # 9. 🌊 GENERAR SEÑAL LIQUIDITY GRAB ENTERPRISE
            signal = self._generate_liquidity_grab_signal_enterprise(
                grab_type=hunt_details.get('grab_type', LiquidityGrabType.ASIAN_RANGE_GRAB),
                confidence=total_confidence,
                direction=hunt_details.get('reversal_direction', TradingDirection.NEUTRAL),
                liquidity_level=hunt_details.get('liquidity_level', LiquidityLevel.MEDIUM_LIQUIDITY),
                grab_price=hunt_details.get('hunt_price', current_price),
                current_price=current_price,
                stop_hunt_score=stop_hunt_score,
                reversal_speed=reversal_speed,
                volume_intensity=volume_intensity,
                institutional_score=institutional_score,
                density_score=density_score,
                smart_money_confirmed=smart_money_confirmed,
                choch_bonus=choch_bonus,
                symbol=symbol,
                timeframe=timeframe,
                data=data
            )
            
            # 10. 💾 GUARDAR EN MEMORIA ENTERPRISE
            if signal:
                log_info(f"🌊 Liquidity Grab detectado: {signal.signal_type.value} - {signal.confidence:.1f}% confianza")
                if self.memory_system:
                    self._store_liquidity_grab_pattern_in_memory(signal)
            
            return [signal] if signal else []
            
        except Exception as e:
            log_error(f"❌ Error en detección Liquidity Grab: {e}")
            return []

    def _map_liquidity_levels_enterprise(self, data: DataFrameType) -> Dict[str, Any]:
        """🌊 Mapear niveles de liquidez enterprise"""
        try:
            # Obtener pandas instance
            pd = _pandas_manager.get_safe_pandas_instance()
            
            liquidity_levels = []
            
            # 📊 IDENTIFICAR HIGHS/LOWS SIGNIFICATIVOS
            lookback = min(len(data), self.config['liquidity_density_periods'])
            recent_data = data.tail(lookback)
            
            # Previous day high/low (más importantes)
            daily_high = recent_data['high'].max()
            daily_low = recent_data['low'].min()
            
            liquidity_levels.extend([
                {
                    'price': daily_high,
                    'type': 'previous_day_high',
                    'weight': self.liquidity_levels['previous_day_high']['weight'],
                    'liquidity_level': self.liquidity_levels['previous_day_high']['type'],
                    'stops_estimate': self._estimate_stops_at_level(recent_data, daily_high)
                },
                {
                    'price': daily_low,
                    'type': 'previous_day_low',
                    'weight': self.liquidity_levels['previous_day_low']['weight'],
                    'liquidity_level': self.liquidity_levels['previous_day_low']['type'],
                    'stops_estimate': self._estimate_stops_at_level(recent_data, daily_low)
                }
            ])
            
            # 📈 SWING HIGHS/LOWS
            swing_highs = self._identify_swing_highs(recent_data)
            swing_lows = self._identify_swing_lows(recent_data)
            
            for swing_high in swing_highs:
                liquidity_levels.append({
                    'price': swing_high,
                    'type': 'swing_high',
                    'weight': self.liquidity_levels['swing_high']['weight'],
                    'liquidity_level': self.liquidity_levels['swing_high']['type'],
                    'stops_estimate': self._estimate_stops_at_level(recent_data, swing_high)
                })
            
            for swing_low in swing_lows:
                liquidity_levels.append({
                    'price': swing_low,
                    'type': 'swing_low',
                    'weight': self.liquidity_levels['swing_low']['weight'],
                    'liquidity_level': self.liquidity_levels['swing_low']['type'],
                    'stops_estimate': self._estimate_stops_at_level(recent_data, swing_low)
                })
            
            # Ordenar por weight (importancia)
            liquidity_levels.sort(key=lambda x: x['weight'], reverse=True)
            
            log_debug(f"🌊 Mapeados {len(liquidity_levels)} niveles de liquidez")
            
            return {
                'levels': liquidity_levels,
                'total_levels': len(liquidity_levels),
                'high_liquidity_count': len([l for l in liquidity_levels if l['liquidity_level'] == LiquidityLevel.HIGH_LIQUIDITY]),
                'institutional_count': len([l for l in liquidity_levels if l['liquidity_level'] == LiquidityLevel.INSTITUTIONAL])
            }
            
        except Exception as e:
            log_error(f"Error mapeando niveles de liquidez: {e}")
            return {'levels': [], 'total_levels': 0, 'high_liquidity_count': 0, 'institutional_count': 0}

    def _detect_stop_hunt_enterprise(self, 
                                    data: DataFrameType,
                                    liquidity_map: Dict[str, Any],
                                    current_price: float) -> Tuple[float, Dict[str, Any]]:
        """🎯 Detección de stop hunt enterprise"""
        try:
            recent_data = data.tail(10)  # Últimas 10 velas para hunt detection
            
            best_hunt_score = 0.0
            best_hunt_details = {}
            
            # 🔍 VERIFICAR CADA NIVEL DE LIQUIDEZ
            for level in liquidity_map['levels']:
                level_price = level['price']
                level_weight = level['weight']
                
                # Verificar si hubo ruptura reciente de este nivel
                hunt_score, hunt_info = self._analyze_level_breach_enterprise(
                    recent_data, level_price, level_weight, current_price
                )
                
                if hunt_score > best_hunt_score:
                    best_hunt_score = hunt_score
                    best_hunt_details = {
                        'hunt_price': level_price,
                        'hunt_type': level['type'],
                        'liquidity_level': level['liquidity_level'],
                        'stops_hunted': level['stops_estimate'],
                        'reversal_direction': self._determine_reversal_direction(hunt_info),
                        'grab_type': self._classify_grab_type(level, hunt_info),
                        **hunt_info
                    }
            
            log_debug(f"🎯 Mejor stop hunt score: {best_hunt_score:.2f}")
            return best_hunt_score, best_hunt_details
            
        except Exception as e:
            log_error(f"Error detectando stop hunt: {e}")
            return 0.0, {}

    def _validate_quick_reversal_enterprise(self, 
                                           data: DataFrameType,
                                           hunt_details: Dict[str, Any],
                                           current_price: float) -> Tuple[float, float]:
        """⚡ Validación de quick reversal enterprise"""
        try:
            if not hunt_details:
                return 0.0, 0.0
            
            hunt_price = hunt_details.get('hunt_price', current_price)
            reversal_direction = hunt_details.get('reversal_direction', TradingDirection.NEUTRAL)
            
            if reversal_direction == TradingDirection.NEUTRAL:
                return 0.0, 0.0
            
            # Verificar velocidad de reversal
            recent_candles = data.tail(self.config['quick_reversal_timeframe'])
            
            if reversal_direction == TradingDirection.BUY:
                # Para reversal bullish, verificar distancia desde low
                lowest_point = recent_candles['low'].min()
                reversal_distance = (current_price - lowest_point) * 10000  # pips
                expected_reversal = self.config['reversal_confirmation_pips']
                
                if reversal_distance >= expected_reversal:
                    speed_score = min(reversal_distance / (expected_reversal * 2), 1.0)
                    log_debug(f"⚡ Quick reversal BULLISH: {reversal_distance:.1f} pips")
                    return speed_score, reversal_distance / 10000
            
            else:  # SELL
                # Para reversal bearish, verificar distancia desde high
                highest_point = recent_candles['high'].max()
                reversal_distance = (highest_point - current_price) * 10000  # pips
                expected_reversal = self.config['reversal_confirmation_pips']
                
                if reversal_distance >= expected_reversal:
                    speed_score = min(reversal_distance / (expected_reversal * 2), 1.0)
                    log_debug(f"⚡ Quick reversal BEARISH: {reversal_distance:.1f} pips")
                    return speed_score, reversal_distance / 10000
            
            return 0.0, 0.0
            
        except Exception as e:
            log_error(f"Error validando quick reversal: {e}")
            return 0.0, 0.0

    def _analyze_volume_spike_enterprise(self, data: DataFrameType) -> Tuple[float, float]:
        """📈 Análisis de volume spike enterprise"""
        try:
            if 'volume' not in data.columns or data['volume'].isna().all():
                return 0.5, 0.0  # Score neutro si no hay volume data
            
            recent_volume = data['volume'].tail(3).mean()
            avg_volume = data['volume'].tail(20).mean()
            
            if avg_volume == 0:
                return 0.5, 0.0
            
            volume_ratio = recent_volume / avg_volume
            
            if volume_ratio >= self.config['volume_spike_threshold']:
                intensity = min((volume_ratio - 1.0) / 2.0, 1.0)  # Normalizar intensidad
                score = 0.5 + (intensity * 0.5)  # Score entre 0.5 y 1.0
                
                log_debug(f"📈 Volume spike detectado: {volume_ratio:.2f}x")
                return score, intensity
            
            return 0.3, 0.0  # Score bajo si no hay spike
            
        except Exception as e:
            log_debug(f"Volume analysis no disponible: {e}")
            return 0.5, 0.0

    def _detect_institutional_footprint_enterprise(self, 
                                                  data: DataFrameType,
                                                  hunt_details: Dict[str, Any],
                                                  order_blocks: List[Dict]) -> Tuple[float, bool]:
        """🏛️ Detección de institutional footprint enterprise"""
        try:
            institutional_score = 0.5  # Base score
            smart_money_confirmed = False
            
            # 🎯 VERIFICAR CONFLUENCIA CON ORDER BLOCKS
            if order_blocks and hunt_details:
                hunt_price = hunt_details.get('hunt_price', 0)
                
                for ob in order_blocks:
                    ob_price = ob.get('price', ob.get('low', 0))
                    distance = abs(hunt_price - ob_price) / hunt_price
                    
                    if distance <= 0.003:  # 30 pips
                        institutional_score += 0.2
                        smart_money_confirmed = True
                        log_debug("🏛️ Order Block confluence confirmada")
            
            # 📊 VERIFICAR PATTERN STRENGTH
            stops_hunted = hunt_details.get('stops_hunted', 0)
            if stops_hunted > 100:  # Estimación significativa de stops
                institutional_score += 0.2
                
            # 🌊 VERIFICAR LIQUIDITY LEVEL IMPORTANCE
            liquidity_level = hunt_details.get('liquidity_level', LiquidityLevel.LOW_LIQUIDITY)
            if liquidity_level == LiquidityLevel.INSTITUTIONAL:
                institutional_score += 0.3
                smart_money_confirmed = True
            elif liquidity_level == LiquidityLevel.HIGH_LIQUIDITY:
                institutional_score += 0.1
            
            institutional_score = min(institutional_score, 1.0)
            
            if institutional_score >= self.config['institutional_threshold']:
                smart_money_confirmed = True
            
            log_debug(f"🏛️ Institutional footprint: {institutional_score:.2f}")
            return institutional_score, smart_money_confirmed
            
        except Exception as e:
            log_error(f"Error detectando institutional footprint: {e}")
            return 0.5, False

    def _calculate_liquidity_density_enterprise(self, 
                                               liquidity_map: Dict[str, Any],
                                               hunt_details: Dict[str, Any]) -> float:
        """💧 Calcular density de liquidez enterprise"""
        try:
            if not liquidity_map['levels'] or not hunt_details:
                return 0.3
            
            hunt_price = hunt_details.get('hunt_price', 0)
            high_liquidity_count = liquidity_map['high_liquidity_count']
            total_levels = liquidity_map['total_levels']
            
            # Score basado en concentración de liquidez
            if total_levels == 0:
                return 0.3
            
            density_ratio = high_liquidity_count / total_levels
            
            # Bonus si el hunt fue en nivel de alta liquidez
            hunt_level = hunt_details.get('liquidity_level', LiquidityLevel.LOW_LIQUIDITY)
            if hunt_level in [LiquidityLevel.HIGH_LIQUIDITY, LiquidityLevel.INSTITUTIONAL]:
                density_ratio += 0.3
            
            density_score = min(density_ratio, 1.0)
            
            log_debug(f"💧 Liquidity density: {density_score:.2f}")
            return density_score
            
        except Exception as e:
            log_error(f"Error calculando liquidity density: {e}")
            return 0.3

    def _calculate_liquidity_grab_confidence_enterprise(self,
                                                       stop_hunt_score: float,
                                                       reversal_score: float,
                                                       volume_score: float,
                                                       institutional_score: float,
                                                       density_score: float,
                                                       symbol: str = "",
                                                       timeframe: str = "",
                                                       grab_price: float = 0.0) -> Tuple[float, float]:
        """🧮 Cálculo de confianza Liquidity Grab enterprise ponderado"""
        try:
            total_confidence = (
                stop_hunt_score * self.config['stop_hunt_weight'] +
                reversal_score * self.config['reversal_speed_weight'] +
                volume_score * self.config['volume_weight'] +
                institutional_score * self.config['institutional_weight'] +
                density_score * self.config['liquidity_density_weight']
            ) * 100
            
            # 🚀 BONUS POR CONFLUENCIAS
            bonus = 0.0
            if institutional_score > 0.8:
                bonus += self.config['smart_money_bonus'] * 100
            if stop_hunt_score > 0.8 and reversal_score > 0.7:
                bonus += 7.0  # Perfect liquidity grab bonus
            if volume_score > 0.7 and density_score > 0.6:
                bonus += 5.0  # Volume + density confirmation
            
            # ✅ BONUS MEMORIA CHOCH
            choch_bonus = 0.0
            if (self.config['use_choch_memory'] and symbol and timeframe and grab_price > 0.0):
                try:
                    base_before_choch = total_confidence + bonus
                    adjusted = choch_adjust_confidence_with_memory(
                        base_confidence=base_before_choch,
                        symbol=symbol,
                        timeframe=timeframe,
                        break_level=grab_price,
                    )
                    choch_bonus = float(adjusted) - float(base_before_choch)
                    choch_bonus = max(-self.config['choch_confidence_max_bonus'], min(self.config['choch_confidence_max_bonus'], choch_bonus))
                    if abs(choch_bonus) > 0:
                        log_debug(f"🔥 CHoCH Memory Bonus: {choch_bonus:+.1f}% para nivel {grab_price}")
                except Exception as e:
                    log_error(f"Error aplicando CHoCH memory bonus: {e}")
                    choch_bonus = 0.0
            
            final_confidence = min(max(0.0, total_confidence + bonus + choch_bonus), 95.0)  # Max 95%
            
            log_debug(f"🧮 Liquidity Grab Confidence: {final_confidence:.1f}% (base: {total_confidence:.1f}%, bonus: {bonus:.1f}%, choch: {choch_bonus:.1f}%)")
            return final_confidence, choch_bonus
            
        except Exception as e:
            log_error(f"Error calculando confidence: {e}")
            return 50.0, 0.0

    def _generate_liquidity_grab_signal_enterprise(self, **kwargs) -> Optional[LiquidityGrabSignal]:
        """🌊 Generar señal Liquidity Grab enterprise completa"""
        try:
            # Extraer parámetros
            grab_type = kwargs.get('grab_type', LiquidityGrabType.ASIAN_RANGE_GRAB)
            confidence = kwargs.get('confidence', 0.0)
            direction = kwargs.get('direction', TradingDirection.NEUTRAL)
            liquidity_level = kwargs.get('liquidity_level', LiquidityLevel.MEDIUM_LIQUIDITY)
            grab_price = kwargs.get('grab_price', 0.0)
            current_price = kwargs.get('current_price', 0.0)
            symbol = kwargs.get('symbol', '')
            timeframe = kwargs.get('timeframe', '')
            
            # ✅ RECOPILAR DATOS CHOCH
            choch_bonus = 0.0
            similar_count = 0
            success_rate = 0.0
            choch_level = 0.0
            
            if self.config['use_choch_memory'] and symbol and timeframe and grab_price > 0.0:
                try:
                    # Buscar CHoCH similares 
                    similar_chochs = find_similar_choch_in_history(symbol=symbol, timeframe=timeframe)
                    similar_count = len(similar_chochs)
                    
                    # Calcular tasa de éxito histórica
                    if similar_count > 0:
                        dir_val = direction.value if hasattr(direction, 'value') else str(direction)
                        dir_str = 'BULLISH' if str(dir_val).lower() in ('buy','bullish') else ('BEARISH' if str(dir_val).lower() in ('sell','bearish') else None)
                        success_rate = calculate_historical_success_rate(symbol=symbol, timeframe=timeframe, direction=dir_str)
                    
                    # Obtener CHoCH level estimate
                    data_for_est = kwargs.get('data')
                    dir_val = direction.value if hasattr(direction, 'value') else str(direction)
                    choch_level = choch_estimate_break_level(data_for_est, dir_val, lookback=self.config.get('liquidity_density_periods', 20))
                    
                    # Bonus ya calculado en confidence
                    choch_bonus = kwargs.get('choch_bonus', 0.0)
                    
                except Exception as e:
                    log_error(f"Error recopilando datos CHoCH: {e}")
            
            # 📊 CALCULAR NIVELES DE TRADING
            entry_zone, stop_loss, tp1, tp2 = self._calculate_liquidity_grab_trading_levels_enterprise(
                current_price, direction, grab_price
            )
            
            # 📝 GENERAR NARRATIVA
            narrative = self._generate_liquidity_grab_narrative_enterprise(grab_type, direction, confidence, kwargs)
            
            # 🌊 CREAR SEÑAL COMPLETA
            signal = LiquidityGrabSignal(
                signal_type=grab_type,
                confidence=confidence,
                direction=direction,
                liquidity_level=liquidity_level,
                grab_price=grab_price,
                reversal_confirmation_price=current_price,
                stops_hunted_estimate=kwargs.get('stops_hunted', 0),
                entry_price=current_price,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                stop_hunt_strength=kwargs.get('stop_hunt_score', 0.0),
                reversal_speed_score=kwargs.get('reversal_speed', 0.0),
                volume_spike_intensity=kwargs.get('volume_intensity', 0.0),
                institutional_footprint_score=kwargs.get('institutional_score', 0.0),
                liquidity_density=kwargs.get('density_score', 0.0),
                smart_money_confirmation=kwargs.get('smart_money_confirmed', False),
                narrative=narrative,
                timestamp=datetime.now(),
                session_context=self._build_liquidity_grab_session_context(kwargs),
                symbol=symbol,
                timeframe=timeframe,
                choch_confidence_bonus=choch_bonus,
                similar_choch_count=similar_count,
                historical_success_rate=success_rate,
                choch_level_estimate=choch_level,
                status=LiquidityGrabStatus.REVERSAL_ACTIVE,
                expiry_time=datetime.now() + timedelta(hours=3),
                analysis_id=f"LG_{symbol}_{int(datetime.now().timestamp())}"
            )
            
            return signal
            
        except Exception as e:
            log_error(f"Error generando señal Liquidity Grab: {e}")
            return None

    # ===========================================
    # 🛠️ UTILITY METHODS ENTERPRISE
    # ===========================================

    def _estimate_stops_at_level(self, data: DataFrameType, price_level: float) -> int:
        """📊 Estimar stops en nivel de precio"""
        try:
            # Estimación basada en proximidad y actividad
            proximity_count = 0
            for _, candle in data.tail(20).iterrows():
                if abs(candle['high'] - price_level) <= 0.0002 or abs(candle['low'] - price_level) <= 0.0002:
                    proximity_count += 1
            
            # Estimación simplificada de stops
            base_estimate = 50  # Base de stops por nivel
            proximity_bonus = proximity_count * 20
            
            return base_estimate + proximity_bonus
            
        except Exception:
            return 50  # Fallback estimate

    def _identify_swing_highs(self, data: DataFrameType) -> List[float]:
        """📈 Identificar swing highs"""
        try:
            swing_highs = []
            highs = data['high'].values
            
            for i in range(2, len(highs) - 2):
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    swing_highs.append(highs[i])
            
            return swing_highs[-3:] if len(swing_highs) > 3 else swing_highs  # Últimos 3
            
        except Exception:
            return []

    def _identify_swing_lows(self, data: DataFrameType) -> List[float]:
        """📉 Identificar swing lows"""
        try:
            swing_lows = []
            lows = data['low'].values
            
            for i in range(2, len(lows) - 2):
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    swing_lows.append(lows[i])
            
            return swing_lows[-3:] if len(swing_lows) > 3 else swing_lows  # Últimos 3
            
        except Exception:
            return []

    def _analyze_level_breach_enterprise(self, 
                                        data: DataFrameType,
                                        level_price: float,
                                        level_weight: float,
                                        current_price: float) -> Tuple[float, Dict[str, Any]]:
        """🔍 Analizar ruptura de nivel enterprise"""
        try:
            breach_score = 0.0
            breach_info = {}
            
            # Verificar si hubo ruptura en las últimas velas
            for _, candle in data.iterrows():
                # Ruptura bullish del nivel
                if candle['high'] > level_price and candle['close'] < level_price:
                    pips_above = (candle['high'] - level_price) * 10000
                    if self.config['stop_hunt_min_pips'] <= pips_above <= self.config['stop_hunt_max_pips']:
                        breach_score = 0.7 + (level_weight * 0.3)
                        breach_info = {
                            'breach_type': 'bullish_hunt',
                            'max_penetration': pips_above,
                            'close_below': candle['close'] < level_price,
                            'breach_candle': candle
                        }
                        break
                
                # Ruptura bearish del nivel
                elif candle['low'] < level_price and candle['close'] > level_price:
                    pips_below = (level_price - candle['low']) * 10000
                    if self.config['stop_hunt_min_pips'] <= pips_below <= self.config['stop_hunt_max_pips']:
                        breach_score = 0.7 + (level_weight * 0.3)
                        breach_info = {
                            'breach_type': 'bearish_hunt',
                            'max_penetration': pips_below,
                            'close_above': candle['close'] > level_price,
                            'breach_candle': candle
                        }
                        break
            
            return breach_score, breach_info
            
        except Exception as e:
            log_error(f"Error analizando breach: {e}")
            return 0.0, {}

    def _determine_reversal_direction(self, hunt_info: Dict[str, Any]) -> TradingDirection:
        """🔄 Determinar dirección de reversal"""
        try:
            breach_type = hunt_info.get('breach_type', '')
            
            if breach_type == 'bullish_hunt':
                return TradingDirection.SELL  # Hunt bullish -> reversal bearish
            elif breach_type == 'bearish_hunt':
                return TradingDirection.BUY   # Hunt bearish -> reversal bullish
            
            return TradingDirection.NEUTRAL
            
        except Exception:
            return TradingDirection.NEUTRAL

    def _classify_grab_type(self, level: Dict[str, Any], hunt_info: Dict[str, Any]) -> LiquidityGrabType:
        """🏷️ Clasificar tipo de liquidity grab"""
        try:
            level_type = level.get('type', '')
            
            if 'daily' in level_type:
                return LiquidityGrabType.DAILY_LOW_GRAB if 'low' in level_type else LiquidityGrabType.WEEKLY_HIGH_GRAB
            elif 'swing' in level_type:
                return LiquidityGrabType.ASIAN_RANGE_GRAB
            elif level.get('liquidity_level') == LiquidityLevel.INSTITUTIONAL:
                return LiquidityGrabType.NY_LIQUIDITY_SWEEP
            
            return LiquidityGrabType.LONDON_BREAKOUT_GRAB  # Default
            
        except Exception:
            return LiquidityGrabType.ASIAN_RANGE_GRAB

    def _calculate_liquidity_grab_trading_levels_enterprise(self,
                                                           current_price: float,
                                                           direction: TradingDirection,
                                                           grab_price: float) -> Tuple[Tuple[float, float], float, float, float]:
        """📊 Calcular niveles de trading para Liquidity Grab"""
        try:
            if direction == TradingDirection.BUY:
                # Entry después de hunt bearish
                entry_zone = (current_price - 0.0005, current_price + 0.0010)
                stop_loss = grab_price - 0.0015  # Debajo del grab level
                take_profit_1 = current_price + 0.0040
                take_profit_2 = current_price + 0.0080
                
            else:  # SELL
                # Entry después de hunt bullish
                entry_zone = (current_price - 0.0010, current_price + 0.0005)
                stop_loss = grab_price + 0.0015  # Encima del grab level
                take_profit_1 = current_price - 0.0040
                take_profit_2 = current_price - 0.0080
            
            return entry_zone, stop_loss, take_profit_1, take_profit_2
            
        except Exception:
            return (current_price - 0.001, current_price + 0.001), current_price, current_price, current_price

    def _generate_liquidity_grab_narrative_enterprise(self,
                                                     grab_type: LiquidityGrabType,
                                                     direction: TradingDirection,
                                                     confidence: float,
                                                     context: Dict) -> str:
        """📝 Generar narrativa Liquidity Grab enterprise"""
        try:
            base_narrative = f"Liquidity Grab {direction.value} - {grab_type.value}"
            
            details = []
            if context.get('stop_hunt_score', 0) > 0.8:
                details.append("stop hunt fuerte")
            if context.get('smart_money_confirmed', False):
                details.append("Smart Money confirmado")
            if context.get('volume_intensity', 0) > 0.5:
                details.append("volume spike")
            if context.get('institutional_score', 0) > 0.7:
                details.append("footprint institucional")
            
            if details:
                base_narrative += f" con {', '.join(details)}"
            
            base_narrative += f". Confianza: {confidence:.1f}%"
            
            return base_narrative
            
        except Exception:
            return f"Liquidity Grab {direction.value} - Confianza: {confidence:.1f}%"

    def _build_liquidity_grab_session_context(self, kwargs: Dict) -> Dict[str, Any]:
        """🏗️ Construir contexto de sesión Liquidity Grab"""
        return {
            'stop_hunt_strength': kwargs.get('stop_hunt_score', 0),
            'reversal_speed': kwargs.get('reversal_speed', 0),
            'volume_confirmation': kwargs.get('volume_intensity', 0) > 0.5,
            'institutional_footprint': kwargs.get('institutional_score', 0),
            'liquidity_density': kwargs.get('density_score', 0),
            'smart_money_confirmed': kwargs.get('smart_money_confirmed', False),
            'pattern_strength': kwargs.get('confidence', 0) / 100.0
        }

    def _store_liquidity_grab_pattern_in_memory(self, signal: LiquidityGrabSignal):
        """💾 Guardar patrón Liquidity Grab usando UnifiedMemorySystem v6.1"""
        try:
            pattern_data = {
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'direction': signal.direction.value,
                'timestamp': signal.timestamp.isoformat() if hasattr(signal.timestamp, 'isoformat') else str(signal.timestamp),
                'symbol': signal.symbol,
                'timeframe': signal.timeframe,
                'grab_price': signal.grab_price,
                'liquidity_level': signal.liquidity_level.value,
                'stops_hunted_estimate': signal.stops_hunted_estimate,
                'pattern_type': 'liquidity_grab',
                'stop_hunt_strength': signal.stop_hunt_strength,
                'reversal_speed_score': signal.reversal_speed_score,
                'volume_spike_intensity': signal.volume_spike_intensity,
                'institutional_footprint_score': signal.institutional_footprint_score,
                'smart_money_confirmation': signal.smart_money_confirmation
            }
            
            if self.unified_memory:
                try:
                    self.unified_memory.update_market_memory(pattern_data, signal.symbol)
                    log_info(f"✅ Patrón Liquidity Grab almacenado en UnifiedMemorySystem: {signal.symbol} {signal.signal_type.value}")
                except Exception as e:
                    log_error(f"❌ Error almacenando en UnifiedMemorySystem: {e}")
                    self.pattern_memory['successful_grab_setups'].append(pattern_data)
            else:
                self.pattern_memory['successful_grab_setups'].append(pattern_data)
                log_debug("🔄 Patrón almacenado en memoria local (fallback)")
            
            # Limitar memoria local
            if len(self.pattern_memory['successful_grab_setups']) > 50:
                self.pattern_memory['successful_grab_setups'] = self.pattern_memory['successful_grab_setups'][-50:]
                
        except Exception as e:
            log_error(f"❌ Error crítico guardando patrón Liquidity Grab en memoria: {e}")




# ===========================================
# 🧪 TESTING & UTILITIES
# ===========================================

def create_test_liquidity_grab_detector() -> LiquidityGrabDetectorEnterprise:
    """🧪 Crear detector para testing"""
    return LiquidityGrabDetectorEnterprise()


# 🔗 ENTERPRISE COMPATIBILITY ALIAS
# ===========================================
# Alias para compatibilidad con imports existentes en dashboards
LiquidityGrabEnterprise = LiquidityGrabDetectorEnterprise


if __name__ == "__main__":
    # 🧪 Test básico
    detector = create_test_liquidity_grab_detector()
    print("✅ Liquidity Grab Detector Enterprise v6.0 - Test básico completado")
    
    # 🧪 Test alias
    enterprise_detector = LiquidityGrabEnterprise()
    print("✅ LiquidityGrabEnterprise alias working correctly")
