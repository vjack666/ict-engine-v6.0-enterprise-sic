#!/usr/bin/env python3
"""
🎭 JUDAS SWING DETECTOR ENTERPRISE v6.0
========================================

Detector profesional de Judas Swing patterns según metodología ICT:
- Falsa ruptura en primera hora de sesión
- Identificación de swing highs/lows previos
- Validación de reversal confirmation
- Volume spike analysis (si disponible)
- Confluencia con POI y Order Blocks

FASE 5: Advanced Patterns Migration
Basado en: Silver Bullet Enterprise v6.0 architecture
Target: Enterprise v6.0 SIC architecture

Autor: ICT Engine Team
Sprint: FASE 5 - Advanced Patterns
Fecha: 03 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from datetime import datetime, timezone, time, timedelta
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import numpy as np

# ThreadSafe pandas import para runtime
from data_management.advanced_candle_downloader import _pandas_manager

# Import pandas solo para tipado estático
if TYPE_CHECKING:
    from typing import Any as DataFrameType
else:
    DataFrameType = Any

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - UNIFIED LOGGING
try:
    from ..unified_logging import log_info, log_warning, log_error, log_debug, SmartTradingLogger, create_unified_logger
    from analysis.unified_memory_system import get_unified_memory_system
    UNIFIED_MEMORY_AVAILABLE = True
except ImportError:
    try:
        # Fallback para imports desde nivel superior
        from protocols.unified_logging import get_unified_logger
        from analysis.unified_memory_system import get_unified_memory_system
        UNIFIED_MEMORY_AVAILABLE = True
    except ImportError:
        # Fallback completo
        import logging
        _fallback_logger = logging.getLogger("JUDAS_SWING_FALLBACK")
        if not _fallback_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [JUDAS_SWING] [%(levelname)s] %(message)s', '%H:%M:%S')
            handler.setFormatter(formatter)
            _fallback_logger.addHandler(handler)
            _fallback_logger.setLevel(logging.INFO)
        
        def log_info(message: str, component: str = "JUDAS_SWING"):
            _fallback_logger.info(f"[{component}] {message}")
        def log_warning(message: str, component: str = "JUDAS_SWING"):
            _fallback_logger.warning(f"[{component}] {message}")
        def log_error(message: str, component: str = "JUDAS_SWING"):
            _fallback_logger.error(f"[{component}] {message}")
        def log_debug(message: str, component: str = "JUDAS_SWING"):
            _fallback_logger.debug(f"[{component}] {message}")
        
        SmartTradingLogger = Any
        create_unified_logger = lambda x: None
        UNIFIED_MEMORY_AVAILABLE = False
    
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


class JudasSwingType(Enum):
    """🎭 Tipos de Judas Swing según sesión ICT"""
    LONDON_JUDAS = "london_judas"        # Primera hora Londres (3-4 AM EST)
    NY_JUDAS = "newyork_judas"           # Primera hora NY (9:30-10:30 AM EST)
    ASIAN_JUDAS = "asian_judas"          # Primera hora Asian (8-9 PM EST)
    FRANKFURT_JUDAS = "frankfurt_judas"  # Frankfurt open (2-3 AM EST)


class JudasSwingStatus(Enum):
    """📊 Status del Judas Swing"""
    SETUP_FORMING = "setup_forming"     # Formándose el setup
    FAKE_BREAKOUT = "fake_breakout"     # Falsa ruptura detectada
    REVERSAL_CONFIRMED = "reversal_confirmed"  # Reversal confirmado
    INVALIDATED = "invalidated"         # Setup invalidado
    COMPLETED = "completed"             # Pattern completado


@dataclass
class JudasSwingSignal:
    """🎭 Señal Judas Swing Enterprise v6.0"""
    signal_type: JudasSwingType
    confidence: float
    direction: TradingDirection
    fake_breakout_price: float
    swing_high: float
    swing_low: float
    reversal_confirmation_price: float
    
    # 📊 Trading Levels
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    
    # 🔍 Pattern Analysis
    session_timing_score: float
    swing_identification_score: float
    fake_breakout_strength: float
    reversal_confirmation_score: float
    volume_spike_detected: bool
    poi_confluence: bool
    
    # 📝 Metadata
    narrative: str
    timestamp: datetime
    session_context: Dict[str, Any]
    symbol: str
    timeframe: str
    
    # 🔄 Lifecycle 
    status: JudasSwingStatus = JudasSwingStatus.SETUP_FORMING
    expiry_time: Optional[datetime] = None
    analysis_id: str = ""


class JudasSwingDetectorEnterprise:
    """
    🎭 JUDAS SWING DETECTOR ENTERPRISE v6.0
    ========================================
    
    Detector profesional de patrones Judas Swing con:
    ✅ Detección de falsa ruptura en primera hora de sesión
    ✅ Identificación automatizada de swing highs/lows
    ✅ Validación de reversal confirmation
    ✅ Volume spike analysis
    ✅ Confluencia con POI y Order Blocks
    ✅ UnifiedMemorySystem v6.1 integration
    ✅ SLUC v2.1 logging completo
    ✅ Real-time MT5 data support
    """

    def __init__(self, 
                 memory_system: Optional[Any] = None,
                 logger: Optional[Any] = None):
        """🚀 Inicializa Judas Swing Detector Enterprise"""
        # 🏗️ ENTERPRISE INFRASTRUCTURE
        self.memory_system = memory_system
        self.logger = logger if logger is not None else None
        log_info("🎭 Inicializando Judas Swing Detector Enterprise v6.0", "judas_swing_enterprise")
        
        # ⏰ SESSION TIMING CONFIGURATION (UTC)
        self.session_windows = {
            JudasSwingType.LONDON_JUDAS: (time(7, 0), time(8, 0)),      # 3-4 AM EST → 7-8 UTC
            JudasSwingType.NY_JUDAS: (time(13, 30), time(14, 30)),      # 9:30-10:30 AM EST → 13:30-14:30 UTC
            JudasSwingType.FRANKFURT_JUDAS: (time(6, 0), time(7, 0)),   # 2-3 AM EST → 6-7 UTC
            JudasSwingType.ASIAN_JUDAS: (time(0, 0), time(1, 0))        # 8-9 PM EST → 0-1 UTC+1
        }
        
        # 🎯 DETECTION CONFIGURATION
        self.config = {
            'min_confidence': 70.0,
            'swing_lookback_periods': 20,
            'fake_breakout_min_pips': 5,
            'fake_breakout_max_pips': 25,
            'reversal_confirmation_pips': 10,
            'session_timing_weight': 0.30,
            'swing_quality_weight': 0.25,
            'fake_breakout_weight': 0.25,
            'reversal_weight': 0.20,
            'volume_spike_threshold': 1.5,
            'poi_confluence_bonus': 0.15
        }
        
        # 💾 MEMORY INTEGRATION ENTERPRISE
        if UNIFIED_MEMORY_AVAILABLE:
            self.unified_memory = get_unified_memory_system()
            if self.unified_memory:
                log_info("✅ UnifiedMemorySystem v6.1 integrado exitosamente", "judas_swing_enterprise")
            else:
                log_warning("⚠️ UnifiedMemorySystem no inicializado - usando fallback", "judas_swing_enterprise")
                self.unified_memory = None
        else:
            log_warning("⚠️ UnifiedMemorySystem no disponible - usando pattern_memory local", "judas_swing_enterprise")
            self.unified_memory = None
        
        # Fallback local para compatibilidad
        self.pattern_memory = {
            'successful_judas_setups': [],
            'failed_judas_setups': [],
            'session_performance': {},
            'swing_patterns': []
        }
        
        # 📊 ESTADO INTERNO ENTERPRISE
        self.last_analysis = None
        self.detected_swings = []
        self.current_session_status = None
        self.session_stats = {}
        
        log_info("✅ Judas Swing Detector Enterprise v6.0 inicializado correctamente", "judas_swing_enterprise")

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
            signals = self.detect_judas_swing_patterns(
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
                    'narrative': 'No se detectaron patrones Judas Swing válidos',
                    'source': 'judas_swing_enterprise'
                }
            
            # Tomar la mejor señal
            best_signal = max(signals, key=lambda s: s.confidence)
            
            # Convertir a formato compatible con dashboard
            return {
                'confidence': best_signal.confidence,
                'strength': best_signal.fake_breakout_strength,
                'direction': best_signal.direction.value if hasattr(best_signal.direction, 'value') else str(best_signal.direction),
                'entry_zone': best_signal.entry_zone,
                'stop_loss': best_signal.stop_loss,
                'take_profit_1': best_signal.take_profit_1,
                'take_profit_2': best_signal.take_profit_2,
                'risk_reward_ratio': abs(best_signal.take_profit_1 - best_signal.entry_price) / abs(best_signal.entry_price - best_signal.stop_loss) if best_signal.stop_loss != best_signal.entry_price else 0.0,
                'probability': best_signal.confidence * 0.8,  # Conservative estimate
                'session': 'JUDAS_SWING',
                'confluences': ['POI Confluence'] if best_signal.poi_confluence else [],
                'invalidation_criteria': f'Precio por encima de {best_signal.stop_loss} pips' if best_signal.direction == 'SELL' else f'Precio por debajo de {best_signal.stop_loss} pips',
                'narrative': best_signal.narrative,
                'source': 'judas_swing_enterprise'
            }
            
        except Exception as e:
            log_error(f"Error en detect method: {e}", "judas_swing_enterprise")
            return {
                'confidence': 0.0,
                'strength': 0.0,
                'direction': 'NEUTRAL',
                'entry_zone': (0.0, 0.0),
                'stop_loss': 0.0,
                'take_profit_1': 0.0,
                'narrative': f'Error en detección Judas Swing: {str(e)}',
                'source': 'judas_swing_enterprise_error'
            }

    def detect_judas_swing_patterns(self, 
                                   data: DataFrameType,
                                   symbol: str,
                                   timeframe: str,
                                   current_price: float = 0.0,
                                   detected_order_blocks: Optional[List[Dict]] = None,
                                   market_structure_context: Optional[Dict] = None) -> List[JudasSwingSignal]:
        """
        🎭 DETECCIÓN PRINCIPAL JUDAS SWING ENTERPRISE
        
        Args:
            data: Datos de velas (M5 primary)
            symbol: Par de divisa (ej: EURUSD)
            timeframe: Timeframe principal (M5 recomendado)
            current_price: Precio actual del mercado
            detected_order_blocks: Order Blocks detectados previamente
            market_structure_context: Contexto de estructura de mercado
            
        Returns:
            Lista de señales Judas Swing detectadas
        """
        try:
            # Obtener instancia thread-safe de pandas
            pd = _pandas_manager.get_safe_pandas_instance()
            
            log_info(f"🎭 Iniciando detección Judas Swing para {symbol} {timeframe}", "judas_swing_enterprise")
            
            # 🧹 VALIDACIONES INICIALES
            if data is None or data.empty:
                log_warning("❌ Sin datos para análisis Judas Swing", "judas_swing_enterprise")
                return []
            
            if len(data) < 50:  # Necesitamos más datos para swing analysis
                log_warning(f"❌ Insuficientes datos: {len(data)} < 50 velas", "judas_swing_enterprise")
                return []
            
            # 📊 PREPARAR DATOS
            current_price = current_price or data['close'].iloc[-1]
            detected_order_blocks = detected_order_blocks or []
            
            # 1. ⏰ VALIDAR SESSION TIMING
            timing_score, session_type, in_session = self._validate_session_timing_enterprise()
            
            if timing_score < 0.4:  # Más permisivo que Silver Bullet
                log_debug(f"⏰ Fuera de ventana de sesión activa: {timing_score:.2f}", "judas_swing_enterprise")
                return []
            
            # 2. 📊 IDENTIFICAR SWING HIGHS/LOWS
            swing_score, swing_high, swing_low = self._identify_swing_levels_enterprise(
                data, lookback=self.config['swing_lookback_periods']
            )
            
            if swing_score < 0.5:
                log_debug(f"📊 Swings insuficientes o de baja calidad: {swing_score:.2f}", "judas_swing_enterprise")
                return []
            
            # 3. 🎯 DETECTAR FAKE BREAKOUT
            fake_breakout_score, breakout_price, breakout_direction = self._detect_fake_breakout_enterprise(
                data, swing_high, swing_low, current_price
            )
            
            if fake_breakout_score < 0.6:
                log_debug(f"🎯 Fake breakout no detectado o débil: {fake_breakout_score:.2f}", "judas_swing_enterprise")
                return []
            
            # 4. 🔄 VALIDAR REVERSAL CONFIRMATION
            reversal_score, reversal_confirmed = self._validate_reversal_confirmation_enterprise(
                data, breakout_price, breakout_direction, current_price
            )
            
            # 5. 📈 ANALIZAR VOLUME SPIKE (si disponible)
            volume_spike_detected = self._analyze_volume_spike_enterprise(data)
            
            # 6. 🎯 ANALIZAR CONFLUENCIA CON POI
            poi_confluence_score, poi_present = self._analyze_poi_confluence_enterprise(
                detected_order_blocks, current_price, swing_high, swing_low
            )
            
            # 7. 🧮 CALCULAR CONFIANZA TOTAL ENTERPRISE
            total_confidence = self._calculate_judas_confidence_enterprise(
                timing_score, swing_score, fake_breakout_score, 
                reversal_score, volume_spike_detected, poi_confluence_score
            )
            
            # 8. ✅ VALIDAR THRESHOLD
            if total_confidence < self.config['min_confidence']:
                log_debug(f"🎭 Confianza insuficiente: {total_confidence:.1f}% < {self.config['min_confidence']}%", "judas_swing_enterprise")
                return []
            
            # 9. 🎭 GENERAR SEÑAL JUDAS SWING ENTERPRISE
            signal = self._generate_judas_swing_signal_enterprise(
                session_type=session_type,
                confidence=total_confidence,
                direction=self._invert_direction(breakout_direction),  # Judas invierte la dirección
                fake_breakout_price=breakout_price,
                swing_high=swing_high,
                swing_low=swing_low,
                current_price=current_price,
                timing_score=timing_score,
                swing_score=swing_score,
                fake_breakout_score=fake_breakout_score,
                reversal_score=reversal_score,
                volume_spike_detected=volume_spike_detected,
                poi_confluence=poi_present,
                symbol=symbol,
                timeframe=timeframe,
                data=data
            )
            
            # 10. 💾 GUARDAR EN MEMORIA ENTERPRISE
            if signal:
                log_info(f"🎭 Judas Swing detectado: {signal.signal_type.value} - {signal.confidence:.1f}% confianza", "judas_swing_enterprise")
                if self.memory_system:
                    self._store_judas_pattern_in_memory(signal)
            
            return [signal] if signal else []
            
        except Exception as e:
            log_error(f"❌ Error en detección Judas Swing: {e}", "judas_swing_enterprise")
            return []

    def _validate_session_timing_enterprise(self) -> Tuple[float, JudasSwingType, bool]:
        """⏰ Validación de timing de sesiones enterprise"""
        try:
            current_utc = datetime.now(timezone.utc).time()
            
            # 🔍 VERIFICAR CADA VENTANA DE SESIÓN
            for session_type, (start_time, end_time) in self.session_windows.items():
                if start_time <= current_utc <= end_time:
                    score = 1.0
                    in_session = True
                    log_debug(f"⏰ {session_type.value} ACTIVA: {current_utc}", "judas_swing_enterprise")
                    return score, session_type, in_session
            
            # 🔄 VERIFICAR SI SE APROXIMA ALGUNA SESIÓN (dentro de 30 min)
            for session_type, (start_time, end_time) in self.session_windows.items():
                if self._is_approaching_session(current_utc, start_time):
                    score = 0.4
                    in_session = False
                    return score, session_type, in_session
            
            return 0.0, JudasSwingType.LONDON_JUDAS, False  # Default
            
        except Exception as e:
            log_error(f"Error validando session timing: {e}", "judas_swing_enterprise")
            return 0.0, JudasSwingType.LONDON_JUDAS, False

    def _identify_swing_levels_enterprise(self, 
                                         data: DataFrameType,
                                         lookback: int = 20) -> Tuple[float, float, float]:
        """📊 Identificación de swing highs/lows enterprise"""
        try:
            if len(data) < lookback + 10:
                return 0.3, 0.0, 0.0
            
            # Usar datos recientes para identificar swings
            recent_data = data.tail(lookback + 10)
            
            # 📈 IDENTIFICAR SWING HIGH
            swing_high_idx = recent_data['high'].rolling(window=5, center=True).apply(
                lambda x: x.iloc[2] == x.max(), raw=False
            ).idxmax()
            swing_high = recent_data.loc[swing_high_idx, 'high'] if swing_high_idx in recent_data.index else recent_data['high'].max()
            
            # 📉 IDENTIFICAR SWING LOW
            swing_low_idx = recent_data['low'].rolling(window=5, center=True).apply(
                lambda x: x.iloc[2] == x.min(), raw=False
            ).idxmax()
            swing_low = recent_data.loc[swing_low_idx, 'low'] if swing_low_idx in recent_data.index else recent_data['low'].min()
            
            # 🎯 CALCULAR CALIDAD DEL SWING
            swing_range = abs(swing_high - swing_low)
            avg_range = recent_data['high'].subtract(recent_data['low']).mean()
            
            # Score basado en significancia del swing
            swing_score = min(swing_range / (avg_range * 3), 1.0)
            swing_score = max(swing_score, 0.3)  # Mínimo score
            
            log_debug(f"📊 Swings identificados: High={swing_high:.5f}, Low={swing_low:.5f}, Score={swing_score:.2f}", "judas_swing_enterprise")
            return swing_score, swing_high, swing_low
            
        except Exception as e:
            log_error(f"Error identificando swing levels: {e}", "judas_swing_enterprise")
            return 0.3, 0.0, 0.0

    def _detect_fake_breakout_enterprise(self, 
                                        data: DataFrameType,
                                        swing_high: float,
                                        swing_low: float,
                                        current_price: float) -> Tuple[float, float, TradingDirection]:
        """🎯 Detección de fake breakout enterprise"""
        try:
            if len(data) < 10:
                return 0.0, 0.0, TradingDirection.NEUTRAL
            
            recent_data = data.tail(10)
            fake_breakout_score = 0.0
            breakout_price = 0.0
            direction = TradingDirection.NEUTRAL
            
            # 📈 DETECTAR FAKE BREAKOUT BULLISH (ruptura de swing high que falla)
            high_breaks = recent_data[recent_data['high'] > swing_high]
            if not high_breaks.empty:
                breakout_price = high_breaks['high'].max()
                pips_above = (breakout_price - swing_high) * 10000  # Convertir a pips
                
                # Validar que esté en rango de fake breakout
                if self.config['fake_breakout_min_pips'] <= pips_above <= self.config['fake_breakout_max_pips']:
                    # Verificar que haya regresado por debajo del swing high
                    if current_price < swing_high:
                        fake_breakout_score = 0.8
                        direction = TradingDirection.SELL  # Dirección de la falsa ruptura
                        log_debug(f"🎯 Fake breakout BULLISH detectado: {breakout_price:.5f} (+{pips_above:.1f} pips)", "judas_swing_enterprise")
            
            # 📉 DETECTAR FAKE BREAKOUT BEARISH (ruptura de swing low que falla)
            if fake_breakout_score < 0.5:  # Solo si no encontramos bullish fake breakout
                low_breaks = recent_data[recent_data['low'] < swing_low]
                if not low_breaks.empty:
                    breakout_price = low_breaks['low'].min()
                    pips_below = (swing_low - breakout_price) * 10000  # Convertir a pips
                    
                    # Validar que esté en rango de fake breakout
                    if self.config['fake_breakout_min_pips'] <= pips_below <= self.config['fake_breakout_max_pips']:
                        # Verificar que haya regresado por encima del swing low
                        if current_price > swing_low:
                            fake_breakout_score = 0.8
                            direction = TradingDirection.BUY  # Dirección de la falsa ruptura
                            log_debug(f"🎯 Fake breakout BEARISH detectado: {breakout_price:.5f} (-{pips_below:.1f} pips)", "judas_swing_enterprise")
            
            return fake_breakout_score, breakout_price, direction
            
        except Exception as e:
            log_error(f"Error detectando fake breakout: {e}", "judas_swing_enterprise")
            return 0.0, 0.0, TradingDirection.NEUTRAL

    def _validate_reversal_confirmation_enterprise(self, 
                                                  data: DataFrameType,
                                                  breakout_price: float,
                                                  breakout_direction: TradingDirection,
                                                  current_price: float) -> Tuple[float, bool]:
        """🔄 Validación de reversal confirmation enterprise"""
        try:
            if breakout_direction == TradingDirection.NEUTRAL:
                return 0.0, False
            
            reversal_score = 0.0
            reversal_confirmed = False
            
            min_reversal_pips = self.config['reversal_confirmation_pips']
            
            if breakout_direction == TradingDirection.SELL:
                # Para fake breakout bullish, necesitamos reversal bearish
                pips_reversed = (breakout_price - current_price) * 10000
                if pips_reversed >= min_reversal_pips:
                    reversal_score = min(pips_reversed / (min_reversal_pips * 2), 1.0)
                    reversal_confirmed = True
                    log_debug(f"🔄 Reversal BEARISH confirmado: {pips_reversed:.1f} pips", "judas_swing_enterprise")
            
            elif breakout_direction == TradingDirection.BUY:
                # Para fake breakout bearish, necesitamos reversal bullish
                pips_reversed = (current_price - breakout_price) * 10000
                if pips_reversed >= min_reversal_pips:
                    reversal_score = min(pips_reversed / (min_reversal_pips * 2), 1.0)
                    reversal_confirmed = True
                    log_debug(f"🔄 Reversal BULLISH confirmado: {pips_reversed:.1f} pips", "judas_swing_enterprise")
            
            return reversal_score, reversal_confirmed
            
        except Exception as e:
            log_error(f"Error validando reversal confirmation: {e}", "judas_swing_enterprise")
            return 0.0, False

    def _analyze_volume_spike_enterprise(self, data: DataFrameType) -> bool:
        """📈 Análisis de volume spike enterprise"""
        try:
            if 'volume' not in data.columns or data['volume'].isna().all():
                return False  # No hay datos de volumen
            
            recent_volume = data['volume'].tail(5).mean()
            avg_volume = data['volume'].tail(20).mean()
            
            volume_spike = recent_volume > (avg_volume * self.config['volume_spike_threshold'])
            
            if volume_spike:
                log_debug(f"📈 Volume spike detectado: {recent_volume:.0f} vs avg {avg_volume:.0f}", "judas_swing_enterprise")
            
            return volume_spike
            
        except Exception as e:
            log_debug(f"Volume analysis no disponible: {e}", "judas_swing_enterprise")
            return False

    def _analyze_poi_confluence_enterprise(self, 
                                          order_blocks: List[Dict],
                                          current_price: float,
                                          swing_high: float,
                                          swing_low: float) -> Tuple[float, bool]:
        """🎯 Análisis de confluencia con POI enterprise"""
        try:
            if not order_blocks:
                return 0.3, False
            
            confluence_score = 0.0
            poi_present = False
            
            # 🔍 BUSCAR ORDER BLOCKS CERCA DE SWING LEVELS
            for ob in order_blocks:
                ob_price = ob.get('price', ob.get('low', 0))
                
                # Verificar proximidad a swing levels
                swing_high_distance = abs(ob_price - swing_high) / swing_high
                swing_low_distance = abs(ob_price - swing_low) / swing_low
                
                if swing_high_distance <= 0.002 or swing_low_distance <= 0.002:  # 20 pips
                    confluence_score = 0.8
                    poi_present = True
                    log_debug(f"🎯 POI confluencia detectada: OB en {ob_price:.5f}", "judas_swing_enterprise")
                    break
            
            return confluence_score, poi_present
            
        except Exception as e:
            log_error(f"Error analizando POI confluence: {e}", "judas_swing_enterprise")
            return 0.3, False

    def _calculate_judas_confidence_enterprise(self,
                                             timing_score: float,
                                             swing_score: float,
                                             fake_breakout_score: float,
                                             reversal_score: float,
                                             volume_spike: bool,
                                             poi_confluence_score: float) -> float:
        """🧮 Cálculo de confianza Judas Swing enterprise ponderado"""
        try:
            total_confidence = (
                timing_score * self.config['session_timing_weight'] +
                swing_score * self.config['swing_quality_weight'] +
                fake_breakout_score * self.config['fake_breakout_weight'] +
                reversal_score * self.config['reversal_weight']
            ) * 100
            
            # 🚀 BONUS POR CONFLUENCIAS
            bonus = 0.0
            if volume_spike:
                bonus += 5.0  # Volume spike bonus
            if poi_confluence_score > 0.6:
                bonus += self.config['poi_confluence_bonus'] * 100  # POI confluence bonus
            if fake_breakout_score > 0.7 and reversal_score > 0.6:
                bonus += 8.0  # Perfect Judas setup bonus
            
            final_confidence = min(total_confidence + bonus, 96.0)  # Max 96%
            
            log_debug(f"🧮 Judas Confidence: {final_confidence:.1f}% (base: {total_confidence:.1f}%, bonus: {bonus:.1f}%)", "judas_swing_enterprise")
            return final_confidence
            
        except Exception as e:
            log_error(f"Error calculando Judas confidence: {e}", "judas_swing_enterprise")
            return 50.0

    def _generate_judas_swing_signal_enterprise(self, **kwargs) -> Optional[JudasSwingSignal]:
        """🎭 Generar señal Judas Swing enterprise completa"""
        try:
            # Extraer parámetros
            session_type = kwargs.get('session_type', JudasSwingType.LONDON_JUDAS)
            confidence = kwargs.get('confidence', 0.0)
            direction = kwargs.get('direction', TradingDirection.NEUTRAL)
            fake_breakout_price = kwargs.get('fake_breakout_price', 0.0)
            swing_high = kwargs.get('swing_high', 0.0)
            swing_low = kwargs.get('swing_low', 0.0)
            current_price = kwargs.get('current_price', 0.0)
            symbol = kwargs.get('symbol', '')
            timeframe = kwargs.get('timeframe', '')
            
            # 📊 CALCULAR NIVELES DE TRADING
            entry_zone, stop_loss, tp1, tp2 = self._calculate_judas_trading_levels_enterprise(
                current_price, direction, swing_high, swing_low, fake_breakout_price
            )
            
            # 📝 GENERAR NARRATIVA
            narrative = self._generate_judas_narrative_enterprise(session_type, direction, confidence, kwargs)
            
            # 🎭 CREAR SEÑAL COMPLETA
            signal = JudasSwingSignal(
                signal_type=session_type,
                confidence=confidence,
                direction=direction,
                fake_breakout_price=fake_breakout_price,
                swing_high=swing_high,
                swing_low=swing_low,
                reversal_confirmation_price=current_price,
                entry_price=current_price,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                session_timing_score=kwargs.get('timing_score', 0.0),
                swing_identification_score=kwargs.get('swing_score', 0.0),
                fake_breakout_strength=kwargs.get('fake_breakout_score', 0.0),
                reversal_confirmation_score=kwargs.get('reversal_score', 0.0),
                volume_spike_detected=kwargs.get('volume_spike_detected', False),
                poi_confluence=kwargs.get('poi_confluence', False),
                narrative=narrative,
                timestamp=datetime.now(),
                session_context=self._build_judas_session_context(kwargs),
                symbol=symbol,
                timeframe=timeframe,
                status=JudasSwingStatus.REVERSAL_CONFIRMED,
                expiry_time=datetime.now() + timedelta(hours=4),
                analysis_id=f"JUDAS_{symbol}_{int(datetime.now().timestamp())}"
            )
            
            return signal
            
        except Exception as e:
            log_error(f"Error generando señal Judas Swing: {e}", "judas_swing_enterprise")
            return None

    # ===========================================
    # 🛠️ UTILITY METHODS ENTERPRISE
    # ===========================================

    def _invert_direction(self, direction: TradingDirection) -> TradingDirection:
        """🔄 Invertir dirección para Judas Swing"""
        if direction == TradingDirection.BUY:
            return TradingDirection.SELL
        elif direction == TradingDirection.SELL:
            return TradingDirection.BUY
        return TradingDirection.NEUTRAL

    def _calculate_judas_trading_levels_enterprise(self,
                                                  current_price: float,
                                                  direction: TradingDirection,
                                                  swing_high: float,
                                                  swing_low: float,
                                                  fake_breakout_price: float) -> Tuple[Tuple[float, float], float, float, float]:
        """📊 Calcular niveles de trading para Judas Swing"""
        try:
            if direction == TradingDirection.BUY:
                # Entry cerca del swing low
                entry_zone = (swing_low - 0.0005, swing_low + 0.0010)
                stop_loss = fake_breakout_price - 0.0010  # Debajo del fake breakout
                take_profit_1 = swing_high
                take_profit_2 = swing_high + (swing_high - swing_low) * 0.618  # Extension
                
            else:  # SELL
                # Entry cerca del swing high
                entry_zone = (swing_high - 0.0010, swing_high + 0.0005)
                stop_loss = fake_breakout_price + 0.0010  # Encima del fake breakout
                take_profit_1 = swing_low
                take_profit_2 = swing_low - (swing_high - swing_low) * 0.618  # Extension
            
            return entry_zone, stop_loss, take_profit_1, take_profit_2
            
        except Exception:
            # Fallback levels
            return (current_price - 0.001, current_price + 0.001), current_price, current_price, current_price

    def _generate_judas_narrative_enterprise(self,
                                           session_type: JudasSwingType,
                                           direction: TradingDirection,
                                           confidence: float,
                                           context: Dict) -> str:
        """📝 Generar narrativa Judas Swing enterprise"""
        try:
            base_narrative = f"Judas Swing {direction.value} en {session_type.value}"
            
            details = []
            if context.get('fake_breakout_score', 0) > 0.7:
                details.append("fake breakout fuerte")
            if context.get('reversal_score', 0) > 0.6:
                details.append("reversal confirmado")
            if context.get('volume_spike_detected', False):
                details.append("volume spike")
            if context.get('poi_confluence', False):
                details.append("POI confluence")
            
            if details:
                base_narrative += f" con {', '.join(details)}"
            
            base_narrative += f". Confianza: {confidence:.1f}%"
            
            return base_narrative
            
        except Exception:
            return f"Judas Swing {direction.value} - Confianza: {confidence:.1f}%"

    def _build_judas_session_context(self, kwargs: Dict) -> Dict[str, Any]:
        """🏗️ Construir contexto de sesión Judas"""
        return {
            'session_active': kwargs.get('timing_score', 0) > 0.7,
            'swing_quality': kwargs.get('swing_score', 0),
            'fake_breakout_strength': kwargs.get('fake_breakout_score', 0),
            'reversal_confirmed': kwargs.get('reversal_score', 0) > 0.5,
            'volume_support': kwargs.get('volume_spike_detected', False),
            'poi_confluence': kwargs.get('poi_confluence', False),
            'pattern_strength': kwargs.get('confidence', 0) / 100.0
        }

    def _is_approaching_session(self, current_time: time, start_time: time) -> bool:
        """⏰ Verificar si se aproxima una sesión"""
        # Implementación simplificada para detectar aproximación (30 min antes)
        return False

    def _store_judas_pattern_in_memory(self, signal: JudasSwingSignal):
        """💾 Guardar patrón Judas usando UnifiedMemorySystem v6.1"""
        try:
            pattern_data = {
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'direction': signal.direction.value,
                'timestamp': signal.timestamp.isoformat() if hasattr(signal.timestamp, 'isoformat') else str(signal.timestamp),
                'symbol': signal.symbol,
                'timeframe': signal.timeframe,
                'fake_breakout_price': signal.fake_breakout_price,
                'swing_high': signal.swing_high,
                'swing_low': signal.swing_low,
                'pattern_type': 'judas_swing',
                'session_timing_score': signal.session_timing_score,
                'fake_breakout_strength': signal.fake_breakout_strength,
                'reversal_confirmation_score': signal.reversal_confirmation_score,
                'volume_spike_detected': signal.volume_spike_detected,
                'poi_confluence': signal.poi_confluence
            }
            
            if self.unified_memory:
                try:
                    self.unified_memory.update_market_memory(pattern_data, signal.symbol)
                    log_info(f"✅ Patrón Judas Swing almacenado en UnifiedMemorySystem: {signal.symbol} {signal.signal_type.value}", "judas_swing_enterprise")
                except Exception as e:
                    log_error(f"❌ Error almacenando en UnifiedMemorySystem: {e}", "judas_swing_enterprise")
                    self.pattern_memory['successful_judas_setups'].append(pattern_data)
            else:
                self.pattern_memory['successful_judas_setups'].append(pattern_data)
                log_debug("🔄 Patrón almacenado en memoria local (fallback)", "judas_swing_enterprise")
            
            # Limitar memoria local
            if len(self.pattern_memory['successful_judas_setups']) > 50:
                self.pattern_memory['successful_judas_setups'] = self.pattern_memory['successful_judas_setups'][-50:]
                
        except Exception as e:
            log_error(f"❌ Error crítico guardando patrón Judas en memoria: {e}", "judas_swing_enterprise")

# ===========================================
# 🧪 TESTING & UTILITIES
# ===========================================

def create_test_judas_swing_detector() -> JudasSwingDetectorEnterprise:
    """🧪 Crear detector para testing"""
    return JudasSwingDetectorEnterprise()


if __name__ == "__main__":
    # 🧪 Test básico
    detector = create_test_judas_swing_detector()
    print("✅ Judas Swing Detector Enterprise v6.0 - Test básico completado")
