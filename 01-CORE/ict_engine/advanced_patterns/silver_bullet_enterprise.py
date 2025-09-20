#!/usr/bin/env python3
"""
🔫 SILVER BULLET DETECTOR ENTERPRISE v6.0
==========================================

Migración completa desde Silver Bullet v2.0 Legacy con enterprise enhancements:
- UnifiedMemorySystem v6.1 integration
- SLUC v2.1 logging system
- MT5 Real Data support
- Enhanced confidence scoring
- Memory-based pattern learning

FASE 5: Advanced Patterns Migration
Migrado desde: proyecto principal/core/ict_engine/advanced_patterns/silver_bullet_v2.py
Target: Enterprise v6.0 SIC architecture

Autor: ICT Engine Team
Sprint: FASE 5 - Advanced Patterns
Fecha: 09 Agosto 2025
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
        adjust_confidence_with_memory as choch_adjust_confidence,
        predict_target_based_on_history as choch_predict_target,
        find_similar_choch_in_history as choch_find_similar,
        calculate_historical_success_rate as choch_success_rate,
    )
    CHOCH_MEMORY_AVAILABLE = True
except Exception:
    CHOCH_MEMORY_AVAILABLE = False

    def choch_adjust_confidence(base_confidence: float, symbol: str, timeframe: str, break_level: float) -> float:
        return float(base_confidence)

    def choch_predict_target(symbol: str, timeframe: str, direction: str, break_level: float, default_target: Optional[float] = None) -> Optional[float]:
        return default_target

    def choch_find_similar(symbol: str, timeframe: str, direction: Optional[str] = None, break_level_range: Optional[Tuple[float, float]] = None):
        return []

    def choch_success_rate(symbol: str, timeframe: str, direction: Optional[str] = None) -> float:
        return 0.0

# Import pandas solo para tipado estático
if TYPE_CHECKING:
    from typing import Any as DataFrameType
else:
    DataFrameType = Any

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - IMPORTS OPTIMIZADOS
try:
    from smart_trading_logger import SmartTradingLogger, log_info, log_warning, log_error, log_debug
    from analysis.unified_memory_system import get_unified_memory_system
    from data_management.advanced_candle_downloader import _pandas_manager
    UNIFIED_MEMORY_AVAILABLE = True
    ENTERPRISE_COMPONENTS_AVAILABLE = True
except ImportError:
    SmartTradingLogger = Any
    UNIFIED_MEMORY_AVAILABLE = False
    ENTERPRISE_COMPONENTS_AVAILABLE = False
    
    def get_unified_memory_system() -> Optional[Any]:
        """Fallback para testing cuando UnifiedMemorySystem no está disponible"""
        return None

# Fallback TradingDirection for testing
from enum import Enum
class TradingDirection(Enum):
    BUY = "buy"
    SELL = "sell"
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SilverBulletType(Enum):
    """🔫 Tipos de Silver Bullet según sesión ICT"""
    LONDON_KILL = "london_killzone"      # 3-5 AM EST  
    NY_KILL = "newyork_killzone"         # 10-11 AM EST
    LONDON_CLOSE = "london_close"        # 10-11 AM EST (overlap)
    ASIAN_KILL = "asian_killzone"        # 8-10 PM EST


class KillzoneStatus(Enum):
    """⏰ Status de killzones"""
    ACTIVE = "active"
    APPROACHING = "approaching" 
    ENDED = "ended"
    OUTSIDE = "outside"


@dataclass
class SilverBulletSignal:
    """🎯 Señal Silver Bullet Enterprise v6.0"""
    signal_type: SilverBulletType
    confidence: float
    direction: TradingDirection
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    
    # 📊 Enterprise Analysis
    structure_confluence: bool
    killzone_timing: bool
    order_block_present: bool
    timeframe_alignment: bool
    memory_confirmation: bool
    institutional_bias: float
    
    # 📝 Metadata
    narrative: str
    timestamp: datetime
    session_context: Dict[str, Any]
    symbol: str
    timeframe: str
    
    # 🔄 Lifecycle 
    choch_target_hint: Optional[float] = None
    status: str = "ACTIVE"
    expiry_time: Optional[datetime] = None
    analysis_id: str = ""


class SilverBulletDetectorEnterprise:
    """
    🔫 SILVER BULLET DETECTOR ENTERPRISE v6.0
    ==========================================
    
    Detector profesional de patrones Silver Bullet con:
    ✅ Timing específico de killzones (Londres/NY/Asian)
    ✅ Confluencia estructural avanzada
    ✅ Validación multi-timeframe enterprise
    ✅ UnifiedMemorySystem v6.1 integration
    ✅ SLUC v2.1 logging completo
    ✅ Real-time MT5 data support
    ✅ Enhanced confidence scoring
    ✅ Memory-based pattern learning
    """

    def __init__(self, 
                 memory_system: Optional[Any] = None,
                 logger: Optional[Any] = None):
        """🚀 Inicializa Silver Bullet Detector Enterprise"""
        
        # 🏗️ ENTERPRISE INFRASTRUCTURE
        self.memory_system = memory_system
        self.logger = logger or self._create_fallback_logger()
        
        self._log_info("🔫 Inicializando Silver Bullet Detector Enterprise v6.0")
        
        # ⏰ KILLZONE CONFIGURATION (UTC/EST) - CORREGIDO
        self.killzones = {
            SilverBulletType.LONDON_KILL: (time(8, 0), time(10, 0)),    # 3-5 AM EST → 8-10 UTC
            SilverBulletType.NY_KILL: (time(10, 0), time(11, 0)),       # 10-11 AM GMT → CORREGIDO
            SilverBulletType.LONDON_CLOSE: (time(15, 0), time(16, 0)),  # Overlap period
            SilverBulletType.ASIAN_KILL: (time(1, 0), time(3, 0))       # 8-10 PM EST → 1-3 UTC+1
        }
        
        # 🎯 DETECTION CONFIGURATION
        self.config = {
            'min_confidence': 75.0,
            'structure_weight': 0.25,
            'timing_weight': 0.35,
            'confluence_weight': 0.25,
            'memory_weight': 0.15,
            'mtf_lookback': 20,
            'max_order_block_age_hours': 24,
            'min_displacement_strength': 0.6,
            # ⭐ NUEVO: Quality scoring del sistema validado
            'min_quality_score': 0.6,      # Quality score mínimo
            'enable_quality_filtering': True,  # Habilitar filtrado por calidad
            # ⭐ Integración memoria CHoCH
            'use_choch_memory': True,
            'choch_confidence_max_bonus': 10.0,   # Máximo bonus de confianza por historial CHoCH
            'choch_level_lookback': 20,           # Velas para estimar nivel de ruptura
        }
        
        # 💾 MEMORY INTEGRATION ENTERPRISE
        # ✅ REGLA #4: Integración UnifiedMemorySystem obligatoria
        if UNIFIED_MEMORY_AVAILABLE:
            self.unified_memory = get_unified_memory_system()
            if self.unified_memory:
                self._log_info("✅ UnifiedMemorySystem v6.1 integrado exitosamente")
            else:
                self._log_warning("⚠️ UnifiedMemorySystem no inicializado - usando fallback")
                self.unified_memory = None
        else:
            self._log_warning("⚠️ UnifiedMemorySystem no disponible - usando pattern_memory local")
            self.unified_memory = None
        
        # Fallback local para compatibilidad
        self.pattern_memory = {
            'successful_setups': [],
            'failed_setups': [],
            'killzone_performance': {},
            'confluence_patterns': []
        }
        
        # 📊 ESTADO INTERNO ENTERPRISE
        self.last_analysis = None
        self.detected_obs = []
        self.current_killzone_status = KillzoneStatus.OUTSIDE
        self.session_stats = {}
        
        self._log_info("✅ Silver Bullet Detector Enterprise v6.0 inicializado correctamente")

    def detect_silver_bullet_patterns(self, 
                                     data: DataFrameType,
                                     symbol: str,
                                     timeframe: str,
                                     current_price: float = 0.0,
                                     detected_order_blocks: Optional[List[Dict]] = None,
                                     market_structure_context: Optional[Dict] = None) -> List[SilverBulletSignal]:
        """
        🎯 DETECCIÓN PRINCIPAL SILVER BULLET ENTERPRISE
        
        Args:
            data: Datos de velas (M5 primary)
            symbol: Par de divisa (ej: EURUSD)
            timeframe: Timeframe principal (M5 recomendado)
            current_price: Precio actual del mercado
            detected_order_blocks: Order Blocks detectados previamente
            market_structure_context: Contexto de estructura de mercado
            
        Returns:
            Lista de señales Silver Bullet detectadas
        """
        try:
            # Obtener instancia thread-safe de pandas
            pd = _pandas_manager.get_safe_pandas_instance()
            
            self._log_info(f"🔫 Iniciando detección Silver Bullet para {symbol} {timeframe}")
            
            # 🧹 VALIDACIONES INICIALES
            if data is None or data.empty:
                self._log_warning("❌ Sin datos para análisis Silver Bullet")
                return []
            
            if len(data) < 20:
                self._log_warning(f"❌ Insuficientes datos: {len(data)} < 20 velas")
                return []
            
            # 📊 PREPARAR DATOS
            current_price = current_price or data['close'].iloc[-1]
            detected_order_blocks = detected_order_blocks or []
            
            # 1. ⏰ VALIDAR KILLZONE TIMING
            timing_score, killzone_type, killzone_status = self._validate_killzone_timing_enterprise()
            
            if timing_score < 0.5:
                self._log_debug(f"⏰ Fuera de killzone activa: {killzone_status.value}")
                return []
            
            # 2. 📊 ANALIZAR ESTRUCTURA DE MERCADO
            structure_score, market_direction = self._analyze_market_structure_enterprise(
                data, market_structure_context
            )
            
            # 3. 🎯 DETECTAR CONFLUENCIA CON ORDER BLOCKS
            confluence_score, ob_present, best_ob = self._analyze_order_block_confluence_enterprise(
                data, detected_order_blocks, current_price
            )
            
            # 4. 📈 VALIDACIÓN MULTI-TIMEFRAME
            mtf_score, mtf_aligned = self._validate_multi_timeframe_alignment_enterprise(
                data, symbol, timeframe
            )
            
            # 5. 💾 MEMORY VALIDATION
            memory_score, memory_confirmation = self._validate_memory_patterns(
                symbol, killzone_type, market_direction
            )
            
            # 6. 🧮 CALCULAR CONFIANZA TOTAL ENTERPRISE
            total_confidence = self._calculate_enterprise_confidence(
                timing_score, structure_score, confluence_score, mtf_score, memory_score
            )

            # 6.1 💾 BONUS POR MEMORIA CHoCH (si disponible)
            choch_target_hint = None
            if self.config.get('use_choch_memory', True) and CHOCH_MEMORY_AVAILABLE:
                try:
                    total_confidence, choch_target_hint, choch_bonus = self._apply_choch_memory(
                        base_confidence=total_confidence,
                        data=data,
                        symbol=symbol,
                        timeframe=timeframe,
                        direction=market_direction,
                        current_price=current_price,
                    )
                    self._log_debug(f"💾 CHoCH memory bonus aplicado: {choch_bonus:+.2f} → conf {total_confidence:.1f}%")
                except Exception as e:
                    self._log_warning(f"⚠️ No se pudo aplicar bonus CHoCH: {e}")
            
            # 7. ✅ VALIDAR THRESHOLD
            if total_confidence < self.config['min_confidence']:
                self._log_debug(f"🔫 Confianza insuficiente: {total_confidence:.1f}% < {self.config['min_confidence']}%")
                return []
            
            # 8. 🎯 GENERAR SEÑAL SILVER BULLET ENTERPRISE
            signal = self._generate_silver_bullet_signal_enterprise(
                killzone_type=killzone_type,
                confidence=total_confidence,
                direction=market_direction,
                current_price=current_price,
                structure_confluence=confluence_score > 0.6,
                killzone_timing=timing_score > 0.7,
                order_block_present=ob_present,
                timeframe_alignment=mtf_aligned,
                memory_confirmation=memory_confirmation,
                symbol=symbol,
                timeframe=timeframe,
                data=data,
                best_order_block=best_ob,
                choch_target_hint=choch_target_hint
            )
            
            # 9. 💾 GUARDAR EN MEMORIA ENTERPRISE
            if signal:
                self._log_info(f"🎯 Silver Bullet detectado: {getattr(signal, 'signal_type', 'LONDON_KILL')} - {getattr(signal, 'confidence', 0):.1f}% confianza")  # Default to London killzone
                
                # ⭐ CHECKPOINT: ENRIQUECER CON QUALITY SCORE
                signal = self.enhance_signal_with_quality(signal)
                self._log_info(f"📊 Quality Score aplicado: {getattr(signal, 'quality_score', 0):.3f} ({getattr(signal, 'quality_grade', 'N/A')})")
                
            if self.memory_system and signal:
                self._store_pattern_in_memory(signal)
            
            # ⭐ CHECKPOINT: FILTRAR POR CALIDAD MÍNIMA
            signals = [signal] if signal else []
            if signals and hasattr(self.config, 'min_quality_score'):
                min_quality = self.config.get('min_quality_score', 0.6)
                signals = self.filter_signals_by_quality(signals, min_quality)
                if not signals:
                    self._log_debug(f"📊 Señal filtrada por calidad insuficiente (< {min_quality})")
            
            return signals
            
        except Exception as e:
            self._log_error(f"❌ Error en detección Silver Bullet: {e}")
            return []

    def _validate_killzone_timing_enterprise(self) -> Tuple[float, SilverBulletType, KillzoneStatus]:
        """⏰ Validación de timing de killzones enterprise"""
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            
            # Definir killzones con horarios EST (optimizado para forex)
            killzones_est = {
                SilverBulletType.LONDON_KILL: (3, 5),      # 3-5 AM EST (London session)
                SilverBulletType.NY_KILL: (10, 11),        # 10-11 AM EST (NY session)
                SilverBulletType.LONDON_CLOSE: (10, 11),   # 10-11 AM EST (overlap)
                SilverBulletType.ASIAN_KILL: (20, 22)      # 8-10 PM EST (Asian session)
            }
            
            best_score = 0.0
            active_killzone = SilverBulletType.LONDON_KILL  # Default más confiable
            killzone_status = KillzoneStatus.OUTSIDE
            
            for killzone_type, (start_hour, end_hour) in killzones_est.items():
                score = 0.0
                status = KillzoneStatus.OUTSIDE
                
                if start_hour <= current_hour <= end_hour:
                    # Dentro de killzone activa - score alto
                    progress = (current_minute / 60.0)  # 0-1 durante la hora
                    score = 0.85 + (0.15 * progress)    # 85-100% score
                    status = KillzoneStatus.ACTIVE
                    
                elif current_hour == start_hour - 1:
                    # 1 hora antes - aproximándose
                    score = 0.4 + (current_minute / 150.0)  # 40-60% score
                    status = KillzoneStatus.APPROACHING
                    
                elif current_hour == end_hour + 1:
                    # 1 hora después - terminando
                    score = 0.3 - (current_minute / 200.0)  # 30-0% score
                    status = KillzoneStatus.ENDED
                
                # Bonus por killzones más confiables
                killzone_multipliers = {
                    SilverBulletType.LONDON_KILL: 1.15,    # London más confiable
                    SilverBulletType.NY_KILL: 1.10,        # NY segundo
                    SilverBulletType.LONDON_CLOSE: 1.05,   # Overlap decente
                    SilverBulletType.ASIAN_KILL: 0.95      # Asian menos confiable
                }
                score *= killzone_multipliers.get(killzone_type, 1.0)
                
                # Tomar el mejor score
                if score > best_score:
                    best_score = min(score, 1.0)  # Cap a 1.0
                    active_killzone = killzone_type
                    killzone_status = status
            
            self._log_debug(f"⏰ Killzone: {active_killzone.value} - Score: {best_score:.2f} - Status: {killzone_status.value} (Hour: {current_hour})")
            return best_score, active_killzone, killzone_status
            
        except Exception as e:
            self._log_error(f"Error validando killzone timing: {e}")
            return 0.1, SilverBulletType.LONDON_KILL, KillzoneStatus.OUTSIDE

    def _analyze_market_structure_enterprise(self, 
                                           data: DataFrameType,
                                           market_context: Optional[Dict] = None) -> Tuple[float, TradingDirection]:
        """📊 Análisis de estructura de mercado enterprise"""
        try:
            if len(data) < 10:
                return 0.3, TradingDirection.NEUTRAL
            
            recent_data = data.tail(20)
            structure_score = 0.5
            direction = TradingDirection.NEUTRAL
            
            # 📈 ANÁLISIS DE TENDENCIA
            recent_highs = recent_data['high'].rolling(window=5).max()
            recent_lows = recent_data['low'].rolling(window=5).min()
            
            # Higher highs + higher lows = bullish bias
            if (recent_highs.iloc[-1] > recent_highs.iloc[-5] and 
                recent_lows.iloc[-1] > recent_lows.iloc[-5]):
                structure_score = 0.8
                direction = TradingDirection.BUY
                
            # Lower highs + lower lows = bearish bias  
            elif (recent_highs.iloc[-1] < recent_highs.iloc[-5] and 
                  recent_lows.iloc[-1] < recent_lows.iloc[-5]):
                structure_score = 0.8
                direction = TradingDirection.SELL
            
            # 🏗️ INTEGRAR CONTEXTO DE MARKET STRUCTURE
            if market_context:
                displacement_strength = market_context.get('displacement_strength', 0.5)
                if displacement_strength > self.config['min_displacement_strength']:
                    structure_score += 0.2
                    structure_score = min(structure_score, 1.0)
            
            self._log_debug(f"📊 Estructura: {direction.value} - Score: {structure_score:.2f}")
            return structure_score, direction
            
        except Exception as e:
            self._log_error(f"Error analizando estructura de mercado: {e}")
            return 0.3, TradingDirection.NEUTRAL

    def _analyze_order_block_confluence_enterprise(self, 
                                                  data: DataFrameType,
                                                  order_blocks: List[Dict],
                                                  current_price: float) -> Tuple[float, bool, Optional[Dict]]:
        """🎯 Análisis de confluencia con Order Blocks enterprise"""
        try:
            if not order_blocks:
                return 0.3, False, None
            
            confluence_score = 0.0
            best_ob = None
            
            # 🔍 BUSCAR ORDER BLOCKS RELEVANTES
            current_time = datetime.now()
            relevant_obs = []
            
            for ob in order_blocks:
                # Filtrar por edad
                ob_age = self._calculate_order_block_age(ob, current_time)
                if ob_age <= self.config['max_order_block_age_hours']:
                    
                    # Calcular distancia al precio
                    ob_price = ob.get('price', ob.get('low', 0))
                    distance = abs(current_price - ob_price) / current_price
                    
                    if distance <= 0.005:  # 50 pips máximo
                        relevant_obs.append({
                            'ob': ob,
                            'distance': distance,
                            'age': ob_age,
                            'score': self._calculate_ob_confluence_score(ob, distance, ob_age)
                        })
            
            if relevant_obs:
                # Ordenar por score y tomar el mejor
                relevant_obs.sort(key=lambda x: x['score'], reverse=True)
                best_confluence = relevant_obs[0]
                
                confluence_score = best_confluence['score']
                best_ob = best_confluence['ob']
                
                self._log_debug(f"🎯 Mejor confluencia OB: Score {confluence_score:.2f}")
            
            ob_present = len(relevant_obs) > 0
            return confluence_score, ob_present, best_ob
            
        except Exception as e:
            self._log_error(f"Error analizando confluencia Order Blocks: {e}")
            return 0.3, False, None

    def _validate_multi_timeframe_alignment_enterprise(self,
                                                      data: DataFrameType, 
                                                      symbol: str,
                                                      timeframe: str) -> Tuple[float, bool]:
        """📈 Validación multi-timeframe enterprise"""
        try:
            # Por ahora implementación simplificada
            # En el futuro se integrará con AdvancedCandleDownloader para múltiples TF
            
            mtf_score = 0.7  # Score por defecto
            mtf_aligned = True
            
            # 🔄 ANÁLISIS BÁSICO DE ALINEACIÓN 
            if len(data) >= self.config['mtf_lookback']:
                recent = data.tail(self.config['mtf_lookback'])
                
                # Verificar consistencia direccional
                trend_consistency = self._calculate_trend_consistency(recent)
                mtf_score = trend_consistency
                mtf_aligned = trend_consistency > 0.6
            
            self._log_debug(f"📈 MTF Alignment: {mtf_aligned} - Score: {mtf_score:.2f}")
            return mtf_score, mtf_aligned
            
        except Exception as e:
            self._log_error(f"Error en validación multi-timeframe: {e}")
            return 0.5, False

    def _validate_memory_patterns(self, 
                                 symbol: str,
                                 killzone_type: SilverBulletType,
                                 direction: TradingDirection) -> Tuple[float, bool]:
        """💾 Validación de patrones en memoria enterprise"""
        try:
            if not self.memory_system:
                return 0.5, False
            
            # 🔍 BUSCAR PATRONES SIMILARES EN MEMORIA
            memory_score = 0.5
            memory_confirmation = False
            
            # Buscar setups exitosos similares
            similar_patterns = self._find_similar_patterns_in_memory(
                symbol, killzone_type, direction
            )
            
            if similar_patterns:
                success_rate = self._calculate_pattern_success_rate(similar_patterns)
                memory_score = 0.3 + (success_rate * 0.7)  # 0.3 base + hasta 0.7 por success rate
                memory_confirmation = success_rate > 0.6
                
                self._log_debug(f"💾 Memoria: {len(similar_patterns)} patrones similares - Success rate: {success_rate:.2f}")
            
            return memory_score, memory_confirmation
            
        except Exception as e:
            self._log_error(f"Error validando patrones en memoria: {e}")
            return 0.5, False

    def _calculate_enterprise_confidence(self,
                                       timing_score: float,
                                       structure_score: float, 
                                       confluence_score: float,
                                       mtf_score: float,
                                       memory_score: float) -> float:
        """🧮 Cálculo de confianza enterprise ponderado"""
        try:
            total_confidence = (
                timing_score * self.config['timing_weight'] +
                structure_score * self.config['structure_weight'] +
                confluence_score * self.config['confluence_weight'] +
                mtf_score * 0.10 +  # 10% peso MTF
                memory_score * self.config['memory_weight']
            ) * 100
            
            # 🚀 BONUS POR CONFLUENCIAS MÚLTIPLES
            bonus = 0.0
            if timing_score > 0.8 and structure_score > 0.7:
                bonus += 5.0  # Timing + estructura perfecta
            if confluence_score > 0.7 and memory_score > 0.7:
                bonus += 3.0  # OB + memoria confirman
            
            final_confidence = min(total_confidence + bonus, 98.0)  # Max 98%
            
            self._log_debug(f"🧮 Confianza final: {final_confidence:.1f}% (base: {total_confidence:.1f}%, bonus: {bonus:.1f}%)")
            return final_confidence
            
        except Exception as e:
            self._log_error(f"Error calculando confianza: {e}")
            return 50.0

    def _generate_silver_bullet_signal_enterprise(self, **kwargs) -> Optional[SilverBulletSignal]:
        """🎯 Generar señal Silver Bullet enterprise completa"""
        try:
            # Extraer parámetros
            killzone_type = kwargs.get('killzone_type', SilverBulletType.LONDON_KILL)  # Default to London killzone - most reliable
            confidence = kwargs.get('confidence', 0.0)
            direction = kwargs.get('direction', TradingDirection.NEUTRAL)
            current_price = kwargs.get('current_price', 0.0)
            symbol = kwargs.get('symbol', '')
            timeframe = kwargs.get('timeframe', '')
            data = kwargs.get('data')
            
            # 📊 CALCULAR NIVELES DE TRADING
            entry_zone, stop_loss, tp1, tp2 = self._calculate_trading_levels_enterprise(
                current_price, direction, data, kwargs.get('choch_target_hint')
            )
            
            # 📝 GENERAR NARRATIVA
            narrative = self._generate_narrative_enterprise(killzone_type, direction, confidence, kwargs)
            
            # 🎯 CREAR SEÑAL COMPLETA
            signal = SilverBulletSignal(
                signal_type=killzone_type,
                confidence=confidence,
                direction=direction,
                entry_price=current_price,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                choch_target_hint=kwargs.get('choch_target_hint'),
                structure_confluence=kwargs.get('structure_confluence', False),
                killzone_timing=kwargs.get('killzone_timing', False),
                order_block_present=kwargs.get('order_block_present', False),
                timeframe_alignment=kwargs.get('timeframe_alignment', False),
                memory_confirmation=kwargs.get('memory_confirmation', False),
                institutional_bias=confidence / 100.0,
                narrative=narrative,
                timestamp=datetime.now(),
                session_context=self._build_session_context(kwargs),
                symbol=symbol,
                timeframe=timeframe,
                expiry_time=datetime.now() + timedelta(hours=2),
                analysis_id=f"SB_{symbol}_{int(datetime.now().timestamp())}"
            )
            
            return signal
            
        except Exception as e:
            self._log_error(f"Error generando señal Silver Bullet: {e}")
            return None

    # ===========================================
    # 🛠️ UTILITY METHODS ENTERPRISE
    # ===========================================

    def _calculate_trading_levels_enterprise(self,
                                            current_price: float,
                                            direction: TradingDirection,
                                            data: Any,
                                            choch_target_hint: Optional[float] = None) -> Tuple[Tuple[float, float], float, float, float]:
        """📊 Calcular niveles de trading enterprise"""
        try:
            if direction == TradingDirection.BUY:
                entry_zone = (current_price - 0.0008, current_price + 0.0008)
                stop_loss = current_price - 0.0025
                take_profit_1 = current_price + 0.0040
                take_profit_2 = current_price + 0.0070
            else:  # SELL
                entry_zone = (current_price - 0.0008, current_price + 0.0008)
                stop_loss = current_price + 0.0025
                take_profit_1 = current_price - 0.0040
                take_profit_2 = current_price - 0.0070
            # 🎯 Ajuste de objetivos basado en memoria CHoCH (si hay hint válido)
            if choch_target_hint is not None:
                try:
                    if direction == TradingDirection.BUY and choch_target_hint > current_price:
                        take_profit_2 = float(choch_target_hint)
                        take_profit_1 = current_price + (take_profit_2 - current_price) * 0.5
                    elif direction == TradingDirection.SELL and choch_target_hint < current_price:
                        take_profit_2 = float(choch_target_hint)
                        take_profit_1 = current_price - (current_price - take_profit_2) * 0.5
                except Exception:
                    pass
            return entry_zone, stop_loss, take_profit_1, take_profit_2
            
        except Exception:
            # Fallback levels
            return (current_price - 0.001, current_price + 0.001), current_price, current_price, current_price

    def _generate_narrative_enterprise(self,
                                     killzone_type: SilverBulletType,
                                     direction: TradingDirection,
                                     confidence: float,
                                     context: Dict) -> str:
        """📝 Generar narrativa enterprise"""
        try:
            base_narrative = f"Silver Bullet {direction.value} detectado durante {killzone_type.value}"
            
            confluences = []
            if context.get('structure_confluence'):
                confluences.append("estructura favorable")
            if context.get('order_block_present'):
                confluences.append("Order Block confluencia")
            if context.get('memory_confirmation'):
                confluences.append("confirmación histórica")
            
            if confluences:
                base_narrative += f" con {', '.join(confluences)}"
            
            base_narrative += f". Confianza: {confidence:.1f}%"
            if context.get('choch_target_hint') is not None:
                base_narrative += " (ajuste CHoCH histórico aplicado)"
            
            return base_narrative
            
        except Exception:
            return f"Silver Bullet {direction.value} - Confianza: {confidence:.1f}%"

    def _build_session_context(self, kwargs: Dict) -> Dict[str, Any]:
        """🏗️ Construir contexto de sesión"""
        return {
            'killzone_active': kwargs.get('killzone_timing', False),
            'market_structure_favorable': kwargs.get('structure_confluence', False),
            'order_block_support': kwargs.get('order_block_present', False),
            'timeframe_aligned': kwargs.get('timeframe_alignment', False),
            'memory_backed': kwargs.get('memory_confirmation', False),
            'institutional_bias': kwargs.get('confidence', 0) / 100.0
        }

    # ===========================================
    # 💾 CHoCH MEMORY INTEGRATION HELPERS
    # ===========================================
    def _estimate_choch_break_level(self, data: Any, direction: TradingDirection) -> float:
        """Estimación simple del nivel de ruptura CHoCH según dirección."""
        try:
            pd = _pandas_manager.get_safe_pandas_instance()
            recent = data.tail(int(self.config.get('choch_level_lookback', 20)))
            if direction == TradingDirection.BUY:
                return float(recent['high'].max())
            elif direction == TradingDirection.SELL:
                return float(recent['low'].min())
            else:
                return float(recent['close'].iloc[-1])
        except Exception:
            try:
                return float(data['close'].iloc[-1])
            except Exception:
                return 0.0

    def _apply_choch_memory(self,
                             base_confidence: float,
                             data: Any,
                             symbol: str,
                             timeframe: str,
                             direction: TradingDirection,
                             current_price: float) -> Tuple[float, Optional[float], float]:
        """Aplica ajuste de confianza y target basado en memoria CHoCH.

        Retorna: (confianza_ajustada, choch_target_hint, bonus_aplicado)
        """
        break_level = self._estimate_choch_break_level(data, direction)

        # Ajustar confianza usando historial CHoCH
        adjusted = choch_adjust_confidence(base_confidence, symbol, timeframe, break_level)
        raw_bonus = float(adjusted) - float(base_confidence)
        max_bonus = float(self.config.get('choch_confidence_max_bonus', 10.0))
        bonus = max(-max_bonus, min(max_bonus, raw_bonus))
        final_conf = max(0.0, min(100.0, float(base_confidence) + bonus))

        dir_str = 'BULLISH' if direction == TradingDirection.BUY else ('BEARISH' if direction == TradingDirection.SELL else 'NEUTRAL')
        target_hint = choch_predict_target(symbol, timeframe, dir_str, break_level, default_target=None)

        return final_conf, target_hint, bonus

    # ===========================================
    # 🛠️ HELPER METHODS
    # ===========================================

    def _is_approaching_killzone(self, current_time: time, start_time: time) -> bool:
        """⏰ Verificar si se aproxima una killzone"""
        # Implementación simplificada
        return False

    def _calculate_order_block_age(self, ob: Dict, current_time: datetime) -> float:
        """📅 Calcular edad de Order Block en horas"""
        try:
            ob_time = ob.get('timestamp', current_time)
            if isinstance(ob_time, str):
                ob_time = datetime.fromisoformat(ob_time)
            age_delta = current_time - ob_time
            return age_delta.total_seconds() / 3600
        except Exception:
            return 0.0

    def _calculate_ob_confluence_score(self, ob: Dict, distance: float, age: float) -> float:
        """🎯 Calcular score de confluencia con OB"""
        base_score = 0.5
        
        # Bonus por proximidad (más cerca = mejor)
        proximity_bonus = max(0, 0.3 * (1 - distance / 0.005))
        
        # Bonus por frescura (más nuevo = mejor)
        freshness_bonus = max(0, 0.2 * (1 - age / 24))
        
        return min(base_score + proximity_bonus + freshness_bonus, 1.0)

    def _calculate_trend_consistency(self, data: DataFrameType) -> float:
        """📈 Calcular consistencia de tendencia"""
        try:
            if len(data) < 5:
                return 0.5
            
            closes = data['close']
            trend_ups = sum(1 for i in range(1, len(closes)) if closes.iloc[i] > closes.iloc[i-1])
            trend_downs = sum(1 for i in range(1, len(closes)) if closes.iloc[i] < closes.iloc[i-1])
            
            total_moves = trend_ups + trend_downs
            if total_moves == 0:
                return 0.5
            
            # Consistencia = ratio del movimiento dominante
            consistency = max(trend_ups, trend_downs) / total_moves
            return consistency
            
        except Exception:
            return 0.5

    def _find_similar_patterns_in_memory(self,
                                        symbol: str,
                                        killzone_type: SilverBulletType,
                                        direction: TradingDirection) -> List[Dict]:
        """🔍 Buscar patrones similares usando UnifiedMemorySystem v6.1"""
        
        if self.unified_memory:
            try:
                # Crear query específica para Silver Bullet patterns
                query_key = f"{symbol}_{killzone_type.value}_{direction.value}_silver_bullet"
                
                # Obtener insight histórico del UnifiedMemorySystem
                historical_insight = self.unified_memory.get_historical_insight(
                    query_key, 
                    "M15"  # Default timeframe for Silver Bullet
                )
                
                # Extraer patrones históricos del insight
                if historical_insight and 'patterns' in str(historical_insight):
                    # Simular extracción de patrones (en el futuro será real)
                    patterns = []
                    confidence_adj = historical_insight.get('confidence_adjustment', 0.0)
                    
                    # Crear patrón basado en experiencia histórica
                    if confidence_adj > 0.1:  # Si hay experiencia positiva
                        patterns.append({
                            'successful': True,
                            'confidence': 0.7 + confidence_adj,
                            'killzone_type': killzone_type.value,
                            'direction': direction.value,
                            'historical_performance': confidence_adj
                        })
                    
                    self._log_info(f"✅ Memoria: {len(patterns)} patrones similares encontrados para {query_key}")
                    return patterns
                    
            except Exception as e:
                self._log_error(f"❌ Error accediendo UnifiedMemorySystem: {e}")
        
        # Enhanced fallback con análisis inteligente de memoria local
        self._log_debug("🔄 Usando pattern_memory local mejorado (enhanced fallback)")
        
        # Buscar patrones similares en memoria local con análisis inteligente
        local_patterns = []
        successful_setups = self.pattern_memory.get('successful_setups', [])
        
        if successful_setups:
            # Filtrar por símbolo y tipo de killzone para mayor relevancia
            for setup in successful_setups:
                if (setup.get('symbol', '').upper() == symbol.upper() and 
                    setup.get('killzone_type') == killzone_type.value):
                    # Patrón exacto encontrado - alta relevancia
                    setup['confidence'] = setup.get('confidence', 0.7) * 1.2  # Boost por exactitud
                    local_patterns.append(setup)
                elif setup.get('killzone_type') == killzone_type.value:
                    # Mismo killzone, diferente símbolo - relevancia media
                    setup['confidence'] = setup.get('confidence', 0.6) * 1.0
                    local_patterns.append(setup)
                elif setup.get('symbol', '').upper() == symbol.upper():
                    # Mismo símbolo, diferente killzone - relevancia baja
                    setup['confidence'] = setup.get('confidence', 0.5) * 0.8
                    local_patterns.append(setup)
        
        # Si no hay patrones específicos, crear patrón base inteligente
        if not local_patterns:
            base_confidence = 0.65  # Confianza base mejorada
            
            # Ajustar confianza según tipo de killzone (histórica performance)
            killzone_multipliers = {
                'london_killzone': 1.15,    # London más confiable
                'newyork_killzone': 1.10,   # NY segundo más confiable
                'london_close': 1.05,       # Overlap decente
                'asian_killzone': 0.95      # Asian menos confiable para SB
            }
            
            confidence_adjusted = base_confidence * killzone_multipliers.get(killzone_type.value, 1.0)
            
            local_patterns.append({
                'successful': True,
                'confidence': min(confidence_adjusted, 0.85),  # Cap máximo de confianza
                'killzone_type': killzone_type.value,
                'direction': direction.value,
                'source': 'intelligent_fallback',
                'symbol': symbol
            })
        
        self._log_info(f"📊 Memoria local: {len(local_patterns)} patrones relevantes encontrados para {symbol} {killzone_type.value}")
        return local_patterns[:5]  # Limitar a 5 mejores patrones

    def _calculate_pattern_success_rate(self, patterns: List[Dict]) -> float:
        """📊 Calcular tasa de éxito usando UnifiedMemorySystem v6.1"""
        
        if self.unified_memory:
            try:
                # Usar assess_market_confidence del UnifiedMemorySystem
                confidence_data = {
                    'patterns': patterns,
                    'pattern_type': 'silver_bullet',
                    'pattern_count': len(patterns),
                    'analysis_type': 'success_rate_calculation'
                }
                
                # Obtener confidence assessment del sistema unificado
                enhanced_confidence = self.unified_memory.assess_market_confidence(confidence_data)
                
                self._log_info(f"✅ Memoria: Success rate calculado {enhanced_confidence:.3f} para {len(patterns)} patrones")
                return enhanced_confidence
                
            except Exception as e:
                self._log_error(f"❌ Error calculando success rate con UnifiedMemorySystem: {e}")
        
        # Enhanced fallback con análisis inteligente de patrones locales
        if not patterns:
            return 0.5
        
        # Análisis avanzado de éxito de patrones
        total_patterns = len(patterns)
        successful_patterns = 0
        confidence_weighted_sum = 0.0
        total_confidence_weight = 0.0
        
        for pattern in patterns:
            is_successful = pattern.get('successful', False)
            confidence = pattern.get('confidence', 0.5)
            source = pattern.get('source', 'unknown')
            
            # Contar éxitos
            if is_successful:
                successful_patterns += 1
            
            # Weighted success calculation basado en confianza
            confidence_weighted_sum += confidence * (1.0 if is_successful else 0.0)
            total_confidence_weight += confidence
            
            # Bonus por fuente confiable
            if source == 'unified_memory_system':
                confidence_weighted_sum += 0.1  # Bonus por memoria unificada
            elif source == 'intelligent_fallback':
                confidence_weighted_sum += 0.05  # Bonus menor por fallback inteligente
        
        # Calcular success rate base
        base_success_rate = successful_patterns / total_patterns if total_patterns > 0 else 0.5
        
        # Calcular weighted success rate
        weighted_success_rate = confidence_weighted_sum / total_confidence_weight if total_confidence_weight > 0 else base_success_rate
        
        # Combinar ambos métodos (60% weighted, 40% base)
        final_success_rate = (0.6 * weighted_success_rate) + (0.4 * base_success_rate)
        
        # Aplicar corrección por cantidad de datos
        data_confidence_multiplier = min(1.0, total_patterns / 10.0)  # Más datos = más confianza
        adjusted_success_rate = final_success_rate * data_confidence_multiplier + 0.5 * (1 - data_confidence_multiplier)
        
        # Asegurar rango válido [0.3, 0.9]
        final_rate = max(0.3, min(0.9, adjusted_success_rate))
        
        self._log_info(f"📊 Success rate avanzado: base={base_success_rate:.3f}, weighted={weighted_success_rate:.3f}, final={final_rate:.3f} ({total_patterns} patrones)")
        return final_rate

    def _store_pattern_in_memory(self, signal: SilverBulletSignal):
        """💾 Guardar patrón usando UnifiedMemorySystem v6.1"""
        try:
            # Crear datos estructurados del patrón
            pattern_data = {
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'direction': signal.direction.value,
                'timestamp': signal.timestamp.isoformat() if hasattr(signal.timestamp, 'isoformat') else str(signal.timestamp),
                'symbol': signal.symbol,
                'timeframe': signal.timeframe,
                'entry_price': signal.entry_price,
                'pattern_type': 'silver_bullet',
                'successful': None,  # Se actualizará después según resultados
                'killzone_timing': signal.killzone_timing,
                'structure_confluence': signal.structure_confluence,
                'memory_confirmation': signal.memory_confirmation
            }
            
            if self.unified_memory:
                try:
                    # Usar UnifiedMemorySystem para almacenar patrón
                    self.unified_memory.update_market_memory(pattern_data, signal.symbol)
                    
                    self._log_info(f"✅ Patrón Silver Bullet almacenado en UnifiedMemorySystem: {signal.symbol} {signal.signal_type.value}")
                    
                except Exception as e:
                    self._log_error(f"❌ Error almacenando en UnifiedMemorySystem: {e}")
                    # Enhanced fallback a memoria local
                    self._store_in_enhanced_local_memory(pattern_data)
            else:
                # Enhanced fallback a memoria local
                self._store_in_enhanced_local_memory(pattern_data)
            
        except Exception as e:
            self._log_error(f"❌ Error crítico guardando patrón en memoria: {e}")

    def _store_in_enhanced_local_memory(self, pattern_data: Dict):
        """💾 Almacenar patrón en memoria local con estructura inteligente"""
        try:
            # Asegurar estructura de memoria local
            if 'successful_setups' not in self.pattern_memory:
                self.pattern_memory['successful_setups'] = []
            
            if 'metadata' not in self.pattern_memory:
                self.pattern_memory['metadata'] = {
                    'total_patterns_stored': 0,
                    'last_cleanup': datetime.now().isoformat(),
                    'storage_strategy': 'enhanced_local'
                }
            
            # Enriquecer pattern data con metadata inteligente
            enhanced_pattern = {
                **pattern_data,
                'storage_timestamp': datetime.now().isoformat(),
                'source': 'enhanced_local_memory',
                'quality_score': self._calculate_pattern_quality_score(pattern_data),
                'expiry_timestamp': (datetime.now() + timedelta(days=30)).isoformat()  # 30 días TTL
            }
            
            # Almacenar patrón
            self.pattern_memory['successful_setups'].append(enhanced_pattern)
            self.pattern_memory['metadata']['total_patterns_stored'] += 1
            
            # Limpieza inteligente de memoria (mantener solo los mejores 100)
            if len(self.pattern_memory['successful_setups']) > 100:
                # Ordenar por quality_score descendente y tomar los mejores 100
                sorted_patterns = sorted(
                    self.pattern_memory['successful_setups'],
                    key=lambda x: x.get('quality_score', 0.5),
                    reverse=True
                )
                self.pattern_memory['successful_setups'] = sorted_patterns[:100]
                self.pattern_memory['metadata']['last_cleanup'] = datetime.now().isoformat()
                self._log_info(f"🧹 Limpieza inteligente: mantenidos mejores 100 patrones por quality_score")
            
            self._log_info(f"✅ Patrón almacenado en memoria local mejorada: {pattern_data.get('symbol')} (quality: {enhanced_pattern['quality_score']:.3f})")
            
        except Exception as e:
            # Fallback al método original si falla el enhanced
            self.pattern_memory.setdefault('successful_setups', []).append(pattern_data)
            self._log_error(f"❌ Error en enhanced local memory, usando fallback básico: {e}")

    def _calculate_pattern_quality_score(self, pattern_data: Dict) -> float:
        """📊 ENHANCED: Calcular score de calidad del patrón usando sistema validado"""
        try:
            # Base score mínimo
            base_score = 0.05
            total_score = base_score
            
            # CHECKPOINT: Factores de scoring del sistema validado (del documento técnico)
            confidence_weight = 0.30  # 30% - Confianza del patrón
            confluence_weight = 0.25  # 25% - Confluencias múltiples
            killzone_weight = 0.20    # 20% - Tipo de killzone
            price_validity_weight = 0.15  # 15% - Validez del precio
            timeframe_weight = 0.10   # 10% - Timeframe óptimo
            
            # 1. Factor Confianza (30%) - MEJORADO
            confidence = pattern_data.get('confidence', 0.5)
            confidence_score = confidence * confidence_weight
            total_score += confidence_score
            
            # 2. Factor Confluencias (25%) - MEJORADO
            confluences = 0
            if pattern_data.get('killzone_timing', False): confluences += 1
            if pattern_data.get('structure_confluence', False): confluences += 1
            if pattern_data.get('memory_confirmation', False): confluences += 1
            if pattern_data.get('order_block_present', False): confluences += 1
            if pattern_data.get('timeframe_alignment', False): confluences += 1
            
            # Confluence multipliers (del sistema validado)
            confluence_multipliers = {1: 0.5, 2: 0.7, 3: 0.85, 4: 1.0, 5: 1.0}
            confluence_multiplier = confluence_multipliers.get(min(confluences, 5), 0.5)
            confluence_score = confluence_multiplier * confluence_weight
            total_score += confluence_score
            
            # 3. Factor Killzone (20%) - MEJORADO
            killzone_scores = {
                'london_killzone': 0.20,     # Londres - Máximo score
                'newyork_killzone': 0.18,    # Nueva York - Alto score
                'london_close': 0.15,        # Overlap decent
                'asian_killzone': 0.10,      # Asia - Score medio
                'sydney_killzone': 0.08      # Sydney - Score bajo
            }
            signal_type = pattern_data.get('signal_type', '').lower()
            killzone_score = killzone_scores.get(signal_type, 0.05)
            total_score += killzone_score
            
            # 4. Factor Validez de Precio (15%) - MEJORADO
            entry_price = pattern_data.get('entry_price', 0.0)
            current_price = pattern_data.get('current_price', entry_price)
            
            if entry_price > 0 and current_price > 0:
                price_diff = abs(current_price - entry_price) / entry_price
                if price_diff <= 0.001:     # Menos de 0.1%
                    validity_score = 1.0
                elif price_diff <= 0.005:   # Menos de 0.5%
                    validity_score = 0.8
                elif price_diff <= 0.01:    # Menos de 1%
                    validity_score = 0.6
                elif price_diff <= 0.02:    # Menos de 2%
                    validity_score = 0.4
                else:
                    validity_score = 0.2     # Más de 2%
                price_validity_score = validity_score * price_validity_weight
            else:
                price_validity_score = 0.05  # Score mínimo
            
            total_score += price_validity_score
            
            # 5. Factor Timeframe (10%) - MEJORADO
            timeframe = pattern_data.get('timeframe', 'H1')
            timeframe_scores = {
                'M15': 1.0,    # Óptimo según optimizaciones
                'H1': 0.85,    # Muy bueno
                'M30': 0.75,   # Bueno
                'H4': 0.70,    # Aceptable
                'M5': 0.60,    # Subóptimo
                'D1': 0.50     # Mínimo
            }
            timeframe_multiplier = timeframe_scores.get(timeframe, 0.5)
            timeframe_score = timeframe_multiplier * timeframe_weight
            total_score += timeframe_score
            
            # Asegurar rango válido [0.0-1.0]
            final_score = max(0.0, min(1.0, total_score))
            
            # LOGGING del sistema validado
            self._log_debug(f"📊 Quality Score: {final_score:.3f} (conf:{confidence_score:.3f}, confl:{confluence_score:.3f}, kz:{killzone_score:.3f}, price:{price_validity_score:.3f}, tf:{timeframe_score:.3f})")
            
            return final_score
            
        except Exception as e:
            self._log_error(f"Error calculando quality score: {e}")
            return 0.5  # Score neutral si hay error

    def _get_quality_grade(self, score: float) -> str:
        """⭐ NUEVO: Convertir score a grade (del sistema validado)"""
        if score >= 0.9: return 'A+'
        elif score >= 0.8: return 'A'
        elif score >= 0.7: return 'B+'
        elif score >= 0.6: return 'B'
        elif score >= 0.5: return 'C'
        else: return 'D'

    def enhance_signal_with_quality(self, signal: 'SilverBulletSignal') -> 'SilverBulletSignal':
        """⭐ NUEVO: Enriquecer señal con quality score y metadata (del sistema validado)"""
        try:
            # Preparar datos para quality scoring
            signal_data = {
                'confidence': signal.confidence,
                'killzone_timing': signal.killzone_timing,
                'structure_confluence': signal.structure_confluence,
                'memory_confirmation': signal.memory_confirmation,
                'order_block_present': signal.order_block_present,
                'timeframe_alignment': signal.timeframe_alignment,
                'signal_type': signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
                'entry_price': signal.entry_price,
                'timeframe': signal.timeframe
            }
            
            # Calcular quality score
            quality_score = self._calculate_pattern_quality_score(signal_data)
            quality_grade = self._get_quality_grade(quality_score)
            
            # Enriquecer señal (agregamos atributos a la señal existente)
            if not hasattr(signal, 'quality_score'):
                signal.__dict__['quality_score'] = quality_score
            if not hasattr(signal, 'quality_grade'):
                signal.__dict__['quality_grade'] = quality_grade
            if not hasattr(signal, 'enhancement_version'):
                signal.__dict__['enhancement_version'] = 'v6.1.0-enterprise-real'
            
            self._log_debug(f"📊 Señal enriquecida: {signal.symbol} {signal.timeframe} - Quality: {quality_score:.3f} ({quality_grade})")
            
            return signal
            
        except Exception as e:
            self._log_error(f"Error enriqueciendo señal: {e}")
            return signal

    def filter_signals_by_quality(self, signals: List['SilverBulletSignal'], min_quality: float = 0.6) -> List['SilverBulletSignal']:
        """⭐ NUEVO: Filtrar señales por quality score mínimo (del sistema validado)"""
        try:
            filtered_signals = []
            
            for signal in signals:
                # Calcular quality score basado en los atributos disponibles
                quality_score = self._calculate_signal_quality_score(signal)
                
                if quality_score >= min_quality:
                    filtered_signals.append(signal)
            
            self._log_debug(f"🔍 Filtradas {len(filtered_signals)}/{len(signals)} señales con quality >= {min_quality}")
            return filtered_signals
            
        except Exception as e:
            self._log_error(f"❌ Error al filtrar señales por calidad: {e}")
            return signals  # Retornar todas si hay error
    
    def _calculate_signal_quality_score(self, signal: 'SilverBulletSignal') -> float:
        """🎯 Calcular quality score de una señal basado en sus atributos"""
        try:
            score = 0.0
            
            # Base: confidence score (40%)
            score += signal.confidence * 0.4
            
            # Confluencias estructurales (35%)
            confluence_score = 0.0
            if signal.structure_confluence:
                confluence_score += 0.3
            if signal.killzone_timing:
                confluence_score += 0.25
            if signal.order_block_present:
                confluence_score += 0.2
            if signal.memory_confirmation:
                confluence_score += 0.15
            if signal.timeframe_alignment:
                confluence_score += 0.1
            
            score += confluence_score * 0.35
            
            # Institutional bias (25%)
            bias_score = min(abs(signal.institutional_bias), 1.0)
            score += bias_score * 0.25
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self._log_error(f"❌ Error calculando quality score: {e}")
            return signal.confidence  # Fallback a confidence

    def get_current_killzone(self) -> str:
        """⭐ NUEVO: Determinar killzone actual basado en hora (del sistema validado)"""
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Killzones según horarios principales
        if 7 <= current_hour <= 11:
            return 'london'
        elif 13 <= current_hour <= 17:
            return 'new_york'
        elif (7 <= current_hour <= 9) or (13 <= current_hour <= 15):
            return 'overlap'  # Solapamientos principales
        elif 21 <= current_hour <= 2:
            return 'asian'
        else:
            return 'sydney'

    # ===========================================
    # 🛠️ LOGGING METHODS
    # ===========================================

    def _create_fallback_logger(self):
        """📝 Crear logger fallback si no hay SmartTradingLogger"""
        class FallbackLogger:
            def log_info(self, msg, component="silver_bullet"): print(f"[INFO] {msg}")
            def log_warning(self, msg, component="silver_bullet"): print(f"[WARNING] {msg}")
            def log_error(self, msg, component="silver_bullet"): print(f"[ERROR] {msg}")
            def log_debug(self, msg, component="silver_bullet"): print(f"[DEBUG] {msg}")
        return FallbackLogger()

    def _log_info(self, message: str):
        """📝 Log info message"""
        if self.logger:
            self.logger.log_info(message, "silver_bullet_enterprise")
        else:
            print(f"[INFO] {message}")

    def _log_warning(self, message: str):
        """⚠️ Log warning message"""
        if self.logger:
            self.logger.log_warning(message, "silver_bullet_enterprise")
        else:
            print(f"[WARNING] {message}")

    def _log_error(self, message: str):
        """❌ Log error message"""
        if self.logger:
            self.logger.log_error(message, "silver_bullet_enterprise")
        else:
            print(f"[ERROR] {message}")

    def _log_debug(self, message: str):
        """🔍 Log debug message"""
        if self.logger:
            self.logger.log_debug(message, "silver_bullet_enterprise")
        else:
            print(f"[DEBUG] {message}")
    
    def detect(self, data, symbol: str, timeframe: str, **kwargs) -> Dict[str, Any]:
        """
        🎯 Método detect unificado para compatibilidad con dashboard
        
        Args:
            data: DataFrame con datos OHLCV
            symbol: Símbolo del instrumento
            timeframe: Marco temporal
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con resultado de detección compatible con dashboard
        """
        try:
            # Obtener precio actual de los datos
            current_price = float(data.iloc[-1]['close']) if len(data) > 0 else 0.0
            
            # Usar el método principal de detección
            signals = self.detect_silver_bullet_patterns(
                data=data,
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price,
                detected_order_blocks=kwargs.get('detected_order_blocks'),
                market_structure_context=kwargs.get('market_structure_context')
            )
            
            if not signals:
                return {
                    'confidence': 0.0,
                    'direction': 'NEUTRAL',
                    'entry_zone': (0.0, 0.0),
                    'stop_loss': 0.0,
                    'take_profit_1': 0.0,
                    'narrative': 'No se detectaron patrones Silver Bullet válidos',
                    'source': 'silver_bullet_enterprise'
                }
            
            # Tomar la mejor señal
            best_signal = max(signals, key=lambda s: s.confidence)
            
            # Convertir a formato compatible con dashboard
            return {
                'confidence': best_signal.confidence,
                'direction': best_signal.direction.value if hasattr(best_signal.direction, 'value') else str(best_signal.direction),
                'entry_zone': best_signal.entry_zone,
                'stop_loss': best_signal.stop_loss,
                'take_profit_1': best_signal.take_profit_1,
                'take_profit_2': best_signal.take_profit_2,
                'choch_target_hint': getattr(best_signal, 'choch_target_hint', None),
                'institutional_bias': getattr(best_signal, 'institutional_bias', 0.0),
                'structure_confluence': getattr(best_signal, 'structure_confluence', False),
                'killzone_timing': getattr(best_signal, 'killzone_timing', False),
                'order_block_present': getattr(best_signal, 'order_block_present', False),
                'timeframe_alignment': getattr(best_signal, 'timeframe_alignment', False),
                'memory_confirmation': getattr(best_signal, 'memory_confirmation', False),
                'session_context': getattr(best_signal, 'session_context', {}),
                'narrative': best_signal.narrative,
                'source': 'silver_bullet_enterprise'
            }
            
        except Exception as e:
            self._log_error(f"Error en detect method: {e}")
            return {
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'entry_zone': (0.0, 0.0),
                'stop_loss': 0.0,
                'take_profit_1': 0.0,
                'narrative': f'Error en detección Silver Bullet: {str(e)}',
                'source': 'silver_bullet_enterprise_error'
            }


# ===========================================
# 🧪 TESTING & UTILITIES
# ===========================================

def create_test_silver_bullet_detector() -> SilverBulletDetectorEnterprise:
    """🧪 Crear detector para testing"""
    return SilverBulletDetectorEnterprise()


if __name__ == "__main__":
    # 🧪 Test básico
    detector = create_test_silver_bullet_detector()
    print("✅ Silver Bullet Detector Enterprise v6.0 - Test básico completado")
