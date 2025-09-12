#!/usr/bin/env python3
"""
🎯 ORDER BLOCK MITIGATION DETECTOR ENTERPRISE v6.0
==================================================

Detector profesional de Order Block Mitigation patterns según metodología ICT:
- Order Block identification (Breaker blocks, Demand/Supply zones)
- Mitigation validation (return to origin)
- Strength classification
- Institutional footprint detection
- Confluencia con Smart Money structures

FASE 5: Advanced Patterns Migration
Basado en: Liquidity Grab Enterprise v6.0 architecture
Target: Enterprise v6.0 SIC architecture

Autor: ICT Engine Team
Sprint: FASE 5 - Advanced Patterns
Fecha: 03 Septiembre 2025
"""

from datetime import datetime, time, timedelta
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
        from unified_logging import log_info, log_warning, log_error, log_debug, SmartTradingLogger, create_unified_logger
        from analysis.unified_memory_system import get_unified_memory_system
        from data_management.advanced_candle_downloader import _pandas_manager
        UNIFIED_MEMORY_AVAILABLE = True
        ENTERPRISE_COMPONENTS_AVAILABLE = True
    except ImportError:
        # Fallback completo
        import logging
        _fallback_logger = logging.getLogger("ORDER_BLOCK_MITIGATION_FALLBACK")
        if not _fallback_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [ORDER_BLOCK_MITIGATION] [%(levelname)s] %(message)s', '%H:%M:%S')
            handler.setFormatter(formatter)
            _fallback_logger.addHandler(handler)
            _fallback_logger.setLevel(logging.INFO)
        
        def log_info(message: str, component: str = "ORDER_BLOCK_MITIGATION"):
            _fallback_logger.info(f"[{component}] {message}")
        def log_warning(message: str, component: str = "ORDER_BLOCK_MITIGATION"):
            _fallback_logger.warning(f"[{component}] {message}")
        def log_error(message: str, component: str = "ORDER_BLOCK_MITIGATION"):
            _fallback_logger.error(f"[{component}] {message}")
        def log_debug(message: str, component: str = "ORDER_BLOCK_MITIGATION"):
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


class OrderBlockType(Enum):
    """🎯 Tipos de Order Block según contexto ICT"""
    BREAKER_BLOCK = "breaker_block"                    # Breaker block (inversión)
    DEMAND_ZONE = "demand_zone"                        # Zona de demanda institucional
    SUPPLY_ZONE = "supply_zone"                        # Zona de suministro institucional
    FAIR_VALUE_GAP = "fair_value_gap"                  # Fair Value Gap (FVG)
    BALANCED_PRICE_RANGE = "balanced_price_range"      # Balanced Price Range (BPR)
    MITIGATION_BLOCK = "mitigation_block"              # Mitigation Block reusado
    INSTITUTIONAL_ORDER_FLOW = "institutional_order_flow"  # Institutional Order Flow


class OrderBlockStatus(Enum):
    """📊 Status del Order Block"""
    ACTIVE = "active"                         # Activo esperando mitigation
    PARTIALLY_MITIGATED = "partially_mitigated"  # Parcialmente mitigado
    FULLY_MITIGATED = "fully_mitigated"       # Completamente mitigado
    INVALIDATED = "invalidated"               # Invalidado por nueva estructura
    REACTIVATED = "reactivated"               # Reactivado después de mitigation
    EXPIRED = "expired"                       # Expirado por tiempo


class OrderBlockStrength(Enum):
    """💪 Fuerza del Order Block"""
    WEAK = "weak"                            # Fuerza débil
    MODERATE = "moderate"                    # Fuerza moderada
    STRONG = "strong"                        # Fuerza fuerte
    INSTITUTIONAL = "institutional"          # Fuerza institucional
    PREMIUM = "premium"                      # Fuerza premium


@dataclass
class OrderBlockMitigation:
    """🎯 Order Block Mitigation Pattern v6.0"""
    # Identificación básica
    id: str
    block_type: OrderBlockType
    strength: OrderBlockStrength
    status: OrderBlockStatus
    
    # Precios de formación
    high: float
    low: float
    close: float
    open: float
    
    # Niveles clave
    mitigation_level: float
    origin_price: float
    
    # Métricas
    confidence: float
    size_pips: float
    age_candles: int
    volume_confirmation: float
    
    # Trading levels
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit: float
    
    # Metadata
    timestamp: datetime
    symbol: str
    timeframe: str
    narrative: str = ""
    
    # Validaciones
    is_active: bool = True
    mitigation_percentage: float = 0.0
    institutional_footprint: bool = False


@dataclass
class OrderBlockMitigationSignal:
    """🎯 Señal Order Block Mitigation Enterprise v6.0"""
    signal_type: OrderBlockType
    confidence: float
    direction: TradingDirection
    strength: OrderBlockStrength
    mitigation_level: float
    origin_price: float
    current_price: float
    
    # 📊 Order Block Details
    block_high: float
    block_low: float
    block_size_pips: float
    mitigation_percentage: float
    volume_confirmation: float
    institutional_validation: float
    
    # 📈 Trading Levels
    entry_price: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    
    # 🔍 Pattern Analysis
    time_to_mitigation: int  # velas
    approach_strength: float
    rejection_strength: float
    smart_money_confirmation: bool
    fair_value_gap_present: bool
    breaker_block_confirmed: bool
    
    # 📝 Metadata
    narrative: str
    timestamp: datetime
    session_context: Dict[str, Any]
    symbol: str
    timeframe: str
    
    # 🔄 Lifecycle 
    status: OrderBlockStatus = OrderBlockStatus.ACTIVE
    expiry_time: Optional[datetime] = None
    analysis_id: str = ""


class OrderBlockMitigationDetectorEnterprise:
    """
    🎯 ORDER BLOCK MITIGATION DETECTOR ENTERPRISE v6.0
    =================================================
    
    Detector profesional de patrones Order Block Mitigation con:
    ✅ Order Block identification avanzado
    ✅ Mitigation validation en tiempo real
    ✅ Strength classification automática
    ✅ Volume confirmation analysis
    ✅ Institutional validation
    ✅ Fair Value Gap detection
    ✅ Breaker Block confirmation
    ✅ UnifiedMemorySystem v6.1 integration
    ✅ SLUC v2.1 logging completo
    ✅ Real-time MT5 data support
    """

    def __init__(self, 
                 memory_system: Optional[Any] = None,
                 logger: Optional[Any] = None):
        """🚀 Inicializa Order Block Mitigation Detector Enterprise"""
        
        # 🏗️ ENTERPRISE INFRASTRUCTURE
        self.memory_system = memory_system
        # Usar logging central SIC directamente
        
        log_info("🎯 Inicializando Order Block Mitigation Detector Enterprise v6.0", "order_block_mitigation_enterprise")
        
        # 🎯 DETECTION CONFIGURATION
        self.config = {
            'min_confidence': 70.0,
            'min_block_size_pips': 5,
            'max_block_size_pips': 50,
            'mitigation_threshold': 0.5,  # 50% para considerar mitigation
            'full_mitigation_threshold': 0.8,  # 80% para full mitigation
            'max_time_to_mitigation': 50,  # velas
            'volume_spike_threshold': 1.5,
            'institutional_threshold': 0.7,
            
            # Pesos para confidence scoring
            'block_quality_weight': 0.25,
            'mitigation_strength_weight': 0.20,
            'volume_weight': 0.15,
            'institutional_weight': 0.15,
            'timing_weight': 0.10,
            'structure_weight': 0.15,
            
            # Bonos por confluencias
            'smart_money_bonus': 0.15,
            'fair_value_gap_bonus': 0.10,
            'breaker_block_bonus': 0.12,
            'session_timing_bonus': 0.08
        }
        
        # 🎯 ORDER BLOCK STRENGTH MAPPING
        self.strength_criteria = {
            OrderBlockStrength.WEAK: {'volume_min': 1.0, 'size_min': 5, 'institutional_min': 0.3},
            OrderBlockStrength.MODERATE: {'volume_min': 1.3, 'size_min': 10, 'institutional_min': 0.5},
            OrderBlockStrength.STRONG: {'volume_min': 1.8, 'size_min': 20, 'institutional_min': 0.7},
            OrderBlockStrength.INSTITUTIONAL: {'volume_min': 2.5, 'size_min': 30, 'institutional_min': 0.85},
            OrderBlockStrength.PREMIUM: {'volume_min': 3.0, 'size_min': 40, 'institutional_min': 0.95}
        }
        
        # 💾 MEMORY INTEGRATION ENTERPRISE
        if UNIFIED_MEMORY_AVAILABLE:
            self.unified_memory = get_unified_memory_system()
            if self.unified_memory:
                log_info("✅ UnifiedMemorySystem v6.1 integrado exitosamente", "order_block_mitigation_enterprise")
            else:
                log_warning("⚠️ UnifiedMemorySystem no inicializado - usando fallback", "order_block_mitigation_enterprise")
                self.unified_memory = None
        else:
            log_warning("⚠️ UnifiedMemorySystem no disponible - usando pattern_memory local", "order_block_mitigation_enterprise")
            self.unified_memory = None
        
        # Fallback local para compatibilidad
        self.pattern_memory = {
            'successful_mitigations': [],
            'failed_mitigations': [],
            'order_block_performance': {},
            'institutional_blocks': []
        }
        
        # 📊 ESTADO INTERNO ENTERPRISE
        self.last_analysis = None
        self.detected_order_blocks = []
        self.active_mitigations = []
        self.session_stats = {}
        
        log_info("✅ Order Block Mitigation Detector Enterprise v6.0 inicializado correctamente", "order_block_mitigation_enterprise")

    def detect_order_block_mitigation_patterns(self, 
                                              data: DataFrameType,
                                              symbol: str,
                                              timeframe: str,
                                              current_price: float = 0.0,
                                              detected_liquidity_grabs: Optional[List[Dict]] = None,
                                              market_structure_context: Optional[Dict] = None) -> List[OrderBlockMitigationSignal]:
        """
        🎯 DETECCIÓN PRINCIPAL ORDER BLOCK MITIGATION ENTERPRISE
        
        Args:
            data: Datos de velas (M5 primary)
            symbol: Par de divisa (ej: EURUSD)
            timeframe: Timeframe principal (M5 recomendado)
            current_price: Precio actual del mercado
            detected_liquidity_grabs: Liquidity Grabs detectados previamente
            market_structure_context: Contexto de estructura de mercado
            
        Returns:
            Lista de señales Order Block Mitigation detectadas
        """
        try:
            # Obtener instancia thread-safe de pandas
            pd = _pandas_manager.get_safe_pandas_instance()
            
            log_info(f"🎯 Iniciando detección Order Block Mitigation para {symbol} {timeframe}", "order_block_mitigation_enterprise")
            
            # 🧹 VALIDACIONES INICIALES
            if data is None or data.empty:
                log_warning("❌ Sin datos para análisis Order Block Mitigation", "order_block_mitigation_enterprise")
                return []
            
            if len(data) < 40:  # Necesitamos datos suficientes para OB detection
                log_warning(f"❌ Insuficientes datos: {len(data)} < 40 velas", "order_block_mitigation_enterprise")
                return []
            
            # 📊 PREPARAR DATOS
            current_price = current_price or data['close'].iloc[-1]
            detected_liquidity_grabs = detected_liquidity_grabs or []
            
            # 1. 🎯 IDENTIFICAR ORDER BLOCKS
            order_blocks = self._identify_order_blocks_enterprise(data)
            
            if not order_blocks:
                log_debug("🎯 No se detectaron Order Blocks significativos", "order_block_mitigation_enterprise")
                return []
            
            # 2. 🔍 VALIDAR MITIGATIONS
            mitigation_signals = []
            
            for order_block in order_blocks:
                mitigation_score, mitigation_details = self._validate_order_block_mitigation_enterprise(
                    data, order_block, current_price
                )
                
                if mitigation_score < 0.6:
                    continue
                
                # 3. 📈 ANALIZAR VOLUME CONFIRMATION
                volume_score, volume_strength = self._analyze_mitigation_volume_enterprise(
                    data, order_block, mitigation_details
                )
                
                # 4. 🏛️ VALIDAR INSTITUTIONAL FOOTPRINT
                institutional_score, smart_money_confirmed = self._validate_institutional_order_block_enterprise(
                    order_block, detected_liquidity_grabs, mitigation_details
                )
                
                # 5. 🧮 CALCULAR CONFIANZA TOTAL ENTERPRISE
                total_confidence = self._calculate_order_block_mitigation_confidence_enterprise(
                    mitigation_score, volume_score, institutional_score, 
                    order_block, mitigation_details
                )
                
                # 6. ✅ VALIDAR THRESHOLD
                if total_confidence < self.config['min_confidence']:
                    log_debug(f"🎯 Confianza insuficiente: {total_confidence:.1f}% < {self.config['min_confidence']}%", "order_block_mitigation_enterprise")
                    continue
                
                # 7. 🎯 GENERAR SEÑAL ORDER BLOCK MITIGATION ENTERPRISE
                signal = self._generate_order_block_mitigation_signal_enterprise(
                    order_block=order_block,
                    mitigation_details=mitigation_details,
                    confidence=total_confidence,
                    current_price=current_price,
                    volume_strength=volume_strength,
                    institutional_score=institutional_score,
                    smart_money_confirmed=smart_money_confirmed,
                    symbol=symbol,
                    timeframe=timeframe,
                    data=data
                )
                
                if signal:
                    mitigation_signals.append(signal)
                    log_info(f"🎯 Order Block Mitigation detectado: {signal.signal_type.value} - {signal.confidence:.1f}% confianza", "order_block_mitigation_enterprise")
            
            # 8. 💾 GUARDAR EN MEMORIA ENTERPRISE
            for signal in mitigation_signals:
                if self.memory_system:
                    self._store_order_block_mitigation_pattern_in_memory(signal)
            
            return mitigation_signals
            
        except Exception as e:
            log_error(f"❌ Error en detección Order Block Mitigation: {e}", "order_block_mitigation_enterprise")
            return []

    def _identify_order_blocks_enterprise(self, data: DataFrameType) -> List[Dict[str, Any]]:
        """🎯 Identificar Order Blocks enterprise"""
        try:
            order_blocks = []
            
            # 📊 ANALIZAR ÚLTIMAS 30 VELAS PARA OB DETECTION
            lookback = min(len(data), 30)
            recent_data = data.tail(lookback)
            
            # 🔍 BUSCAR BREAKER BLOCKS (cambios de estructura)
            breaker_blocks = self._identify_breaker_blocks_enterprise(recent_data)
            order_blocks.extend(breaker_blocks)
            
            # 📈 BUSCAR DEMAND/SUPPLY ZONES
            demand_zones = self._identify_demand_zones_enterprise(recent_data)
            supply_zones = self._identify_supply_zones_enterprise(recent_data)
            order_blocks.extend(demand_zones)
            order_blocks.extend(supply_zones)
            
            # 📊 BUSCAR FAIR VALUE GAPS
            fvg_blocks = self._identify_fair_value_gaps_enterprise(recent_data)
            order_blocks.extend(fvg_blocks)
            
            # Filtrar por tamaño mínimo y calidad
            filtered_blocks = []
            for block in order_blocks:
                block_size = abs(block['high'] - block['low']) * 10000  # pips
                if (self.config['min_block_size_pips'] <= block_size <= self.config['max_block_size_pips']):
                    block['size_pips'] = block_size
                    filtered_blocks.append(block)
            
            # Ordenar por relevancia/calidad
            filtered_blocks.sort(key=lambda x: x.get('quality_score', 0.5), reverse=True)
            
            log_debug(f"🎯 Order Blocks identificados: {len(filtered_blocks)}", "order_block_mitigation_enterprise")
            
            return filtered_blocks[:5]  # Top 5 OBs más relevantes
            
        except Exception as e:
            log_error(f"Error identificando Order Blocks: {e}", "order_block_mitigation_enterprise")
            return []

    def _identify_breaker_blocks_enterprise(self, data: DataFrameType) -> List[Dict[str, Any]]:
        """💥 Identificar Breaker Blocks enterprise"""
        try:
            breaker_blocks = []
            
            # Buscar cambios de estructura significativos
            for i in range(2, len(data) - 2):
                current_candle = data.iloc[i]
                prev_candle = data.iloc[i-1]
                next_candle = data.iloc[i+1]
                
                # Breaker block bullish (previous supply becomes demand)
                if (current_candle['close'] > prev_candle['high'] and 
                    current_candle['close'] > current_candle['open'] and
                    next_candle['low'] > prev_candle['low']):
                    
                    breaker_blocks.append({
                        'type': OrderBlockType.BREAKER_BLOCK,
                        'direction': TradingDirection.BUY,
                        'high': current_candle['high'],
                        'low': prev_candle['low'],
                        'origin_price': prev_candle['low'],
                        'timestamp': current_candle.name,
                        'quality_score': 0.8,
                        'candle_index': i
                    })
                
                # Breaker block bearish (previous demand becomes supply)
                elif (current_candle['close'] < prev_candle['low'] and 
                      current_candle['close'] < current_candle['open'] and
                      next_candle['high'] < prev_candle['high']):
                    
                    breaker_blocks.append({
                        'type': OrderBlockType.BREAKER_BLOCK,
                        'direction': TradingDirection.SELL,
                        'high': prev_candle['high'],
                        'low': current_candle['low'],
                        'origin_price': prev_candle['high'],
                        'timestamp': current_candle.name,
                        'quality_score': 0.8,
                        'candle_index': i
                    })
            
            return breaker_blocks
            
        except Exception as e:
            log_error(f"Error identificando Breaker Blocks: {e}", "order_block_mitigation_enterprise")
            return []

    def _identify_demand_zones_enterprise(self, data: DataFrameType) -> List[Dict[str, Any]]:
        """📈 Identificar Demand Zones enterprise"""
        try:
            demand_zones = []
            
            # Buscar zonas donde precio fue rechazado hacia arriba múltiples veces
            for i in range(5, len(data) - 5):
                base_candle = data.iloc[i]
                low_price = base_candle['low']
                
                # Contar rechazos en área alrededor del low
                rejection_count = 0
                for j in range(max(0, i-5), min(len(data), i+6)):
                    test_candle = data.iloc[j]
                    if abs(test_candle['low'] - low_price) <= 0.0005:  # 5 pips tolerance
                        if test_candle['close'] > test_candle['open']:  # Bullish rejection
                            rejection_count += 1
                
                if rejection_count >= 2:  # Al menos 2 rechazos
                    demand_zones.append({
                        'type': OrderBlockType.DEMAND_ZONE,
                        'direction': TradingDirection.BUY,
                        'high': base_candle['high'],
                        'low': low_price,
                        'origin_price': low_price,
                        'timestamp': base_candle.name,
                        'quality_score': min(0.4 + (rejection_count * 0.15), 0.9),
                        'candle_index': i,
                        'rejection_count': rejection_count
                    })
            
            return demand_zones
            
        except Exception as e:
            log_error(f"Error identificando Demand Zones: {e}", "order_block_mitigation_enterprise")
            return []

    def _identify_supply_zones_enterprise(self, data: DataFrameType) -> List[Dict[str, Any]]:
        """📉 Identificar Supply Zones enterprise"""
        try:
            supply_zones = []
            
            # Buscar zonas donde precio fue rechazado hacia abajo múltiples veces
            for i in range(5, len(data) - 5):
                base_candle = data.iloc[i]
                high_price = base_candle['high']
                
                # Contar rechazos en área alrededor del high
                rejection_count = 0
                for j in range(max(0, i-5), min(len(data), i+6)):
                    test_candle = data.iloc[j]
                    if abs(test_candle['high'] - high_price) <= 0.0005:  # 5 pips tolerance
                        if test_candle['close'] < test_candle['open']:  # Bearish rejection
                            rejection_count += 1
                
                if rejection_count >= 2:  # Al menos 2 rechazos
                    supply_zones.append({
                        'type': OrderBlockType.SUPPLY_ZONE,
                        'direction': TradingDirection.SELL,
                        'high': high_price,
                        'low': base_candle['low'],
                        'origin_price': high_price,
                        'timestamp': base_candle.name,
                        'quality_score': min(0.4 + (rejection_count * 0.15), 0.9),
                        'candle_index': i,
                        'rejection_count': rejection_count
                    })
            
            return supply_zones
            
        except Exception as e:
            log_error(f"Error identificando Supply Zones: {e}", "order_block_mitigation_enterprise")
            return []

    def _identify_fair_value_gaps_enterprise(self, data: DataFrameType) -> List[Dict[str, Any]]:
        """📊 Identificar Fair Value Gaps enterprise"""
        try:
            fvg_blocks = []
            
            # Buscar Fair Value Gaps (huecos en el precio)
            for i in range(1, len(data) - 1):
                prev_candle = data.iloc[i-1]
                current_candle = data.iloc[i]
                next_candle = data.iloc[i+1]
                
                # Bullish FVG (gap hacia arriba)
                if (prev_candle['high'] < next_candle['low'] and
                    current_candle['close'] > current_candle['open']):
                    
                    gap_size = (next_candle['low'] - prev_candle['high']) * 10000
                    if 3 <= gap_size <= 20:  # Gap size validation
                        fvg_blocks.append({
                            'type': OrderBlockType.FAIR_VALUE_GAP,
                            'direction': TradingDirection.BUY,
                            'high': next_candle['low'],
                            'low': prev_candle['high'],
                            'origin_price': prev_candle['high'],
                            'timestamp': current_candle.name,
                            'quality_score': 0.6,
                            'candle_index': i,
                            'gap_size_pips': gap_size
                        })
                
                # Bearish FVG (gap hacia abajo)
                elif (prev_candle['low'] > next_candle['high'] and
                      current_candle['close'] < current_candle['open']):
                    
                    gap_size = (prev_candle['low'] - next_candle['high']) * 10000
                    if 3 <= gap_size <= 20:  # Gap size validation
                        fvg_blocks.append({
                            'type': OrderBlockType.FAIR_VALUE_GAP,
                            'direction': TradingDirection.SELL,
                            'high': prev_candle['low'],
                            'low': next_candle['high'],
                            'origin_price': prev_candle['low'],
                            'timestamp': current_candle.name,
                            'quality_score': 0.6,
                            'candle_index': i,
                            'gap_size_pips': gap_size
                        })
            
            return fvg_blocks
            
        except Exception as e:
            log_error(f"Error identificando Fair Value Gaps: {e}", "order_block_mitigation_enterprise")
            return []

    def _validate_order_block_mitigation_enterprise(self, 
                                                   data: DataFrameType,
                                                   order_block: Dict[str, Any],
                                                   current_price: float) -> Tuple[float, Dict[str, Any]]:
        """🔍 Validar mitigation de Order Block enterprise"""
        try:
            block_high = order_block['high']
            block_low = order_block['low']
            block_direction = order_block['direction']
            block_origin = order_block['origin_price']
            
            mitigation_score = 0.0
            mitigation_details = {}
            
            # 📊 CALCULAR MITIGATION PERCENTAGE
            if block_direction == TradingDirection.BUY:
                # Para demand zone, mitigation es cuando precio retorna al bloque desde arriba
                if current_price <= block_high and current_price >= block_low:
                    distance_from_top = block_high - current_price
                    block_size = block_high - block_low
                    mitigation_percentage = distance_from_top / block_size if block_size > 0 else 0
                    mitigation_score = 0.7 + (mitigation_percentage * 0.3)
                elif current_price < block_low:
                    # Full penetration
                    mitigation_percentage = 1.0
                    mitigation_score = 1.0
                else:
                    mitigation_percentage = 0.0
                    mitigation_score = 0.0
            
            else:  # SELL
                # Para supply zone, mitigation es cuando precio retorna al bloque desde abajo
                if current_price >= block_low and current_price <= block_high:
                    distance_from_bottom = current_price - block_low
                    block_size = block_high - block_low
                    mitigation_percentage = distance_from_bottom / block_size if block_size > 0 else 0
                    mitigation_score = 0.7 + (mitigation_percentage * 0.3)
                elif current_price > block_high:
                    # Full penetration
                    mitigation_percentage = 1.0
                    mitigation_score = 1.0
                else:
                    mitigation_percentage = 0.0
                    mitigation_score = 0.0
            
            # 📈 VALIDAR APPROACH STRENGTH
            approach_strength = self._analyze_approach_to_order_block_enterprise(data, order_block, current_price)
            
            # 🔄 VALIDAR REJECTION STRENGTH
            rejection_strength = self._analyze_rejection_from_order_block_enterprise(data, order_block, current_price)
            
            mitigation_details = {
                'mitigation_percentage': mitigation_percentage,
                'approach_strength': approach_strength,
                'rejection_strength': rejection_strength,
                'mitigation_level': current_price,
                'block_penetration': mitigation_percentage >= self.config['mitigation_threshold'],
                'full_mitigation': mitigation_percentage >= self.config['full_mitigation_threshold']
            }
            
            # Ajustar score basado en approach y rejection
            final_score = mitigation_score * 0.6 + approach_strength * 0.2 + rejection_strength * 0.2
            
            log_debug(f"🎯 Mitigation validation: {final_score:.2f} (penetration: {mitigation_percentage:.1%})", "order_block_mitigation_enterprise")
            return final_score, mitigation_details
            
        except Exception as e:
            log_error(f"Error validando mitigation: {e}", "order_block_mitigation_enterprise")
            return 0.0, {}

    def _analyze_approach_to_order_block_enterprise(self, 
                                                   data: DataFrameType,
                                                   order_block: Dict[str, Any],
                                                   current_price: float) -> float:
        """📈 Analizar fuerza de approach al Order Block"""
        try:
            # Analizar últimas 10 velas para approach strength
            recent_data = data.tail(10)
            
            # Calcular momentum hacia el order block
            price_changes = recent_data['close'].diff().fillna(0)
            avg_momentum = abs(price_changes.mean())
            
            # Normalizar approach strength
            approach_strength = min(avg_momentum / 0.0005, 1.0)  # Normalize por 5 pips
            
            return approach_strength
            
        except Exception:
            return 0.5

    def _analyze_rejection_from_order_block_enterprise(self, 
                                                      data: DataFrameType,
                                                      order_block: Dict[str, Any],
                                                      current_price: float) -> float:
        """🔄 Analizar fuerza de rejection del Order Block"""
        try:
            # Buscar signos de rejection en las últimas velas
            recent_data = data.tail(5)
            
            rejection_signals = 0
            for _, candle in recent_data.iterrows():
                # Buscar wicks largos como señal de rejection
                upper_wick = candle['high'] - max(candle['open'], candle['close'])
                lower_wick = min(candle['open'], candle['close']) - candle['low']
                body_size = abs(candle['close'] - candle['open'])
                
                if body_size > 0:
                    upper_wick_ratio = upper_wick / body_size
                    lower_wick_ratio = lower_wick / body_size
                    
                    if max(upper_wick_ratio, lower_wick_ratio) > 2.0:  # Wick > 2x body
                        rejection_signals += 1
            
            rejection_strength = min(rejection_signals / 3.0, 1.0)  # Max 3 señales
            
            return rejection_strength
            
        except Exception:
            return 0.3

    def _analyze_mitigation_volume_enterprise(self, 
                                            data: DataFrameType,
                                            order_block: Dict[str, Any],
                                            mitigation_details: Dict[str, Any]) -> Tuple[float, float]:
        """📈 Analizar volume durante mitigation enterprise"""
        try:
            if 'volume' not in data.columns or data['volume'].isna().all():
                return 0.6, 0.0  # Score neutro si no hay volume data
            
            # Analizar volume en las últimas 5 velas (mitigation period)
            recent_volume = data['volume'].tail(5).mean()
            avg_volume = data['volume'].tail(20).mean()
            
            if avg_volume == 0:
                return 0.6, 0.0
            
            volume_ratio = recent_volume / avg_volume
            
            if volume_ratio >= self.config['volume_spike_threshold']:
                intensity = min((volume_ratio - 1.0) / 2.0, 1.0)  # Normalizar intensidad
                score = 0.6 + (intensity * 0.4)  # Score entre 0.6 y 1.0
                
                log_debug(f"📈 Volume confirmation durante mitigation: {volume_ratio:.2f}x", "order_block_mitigation_enterprise")
                return score, intensity
            
            return 0.4, 0.0  # Score bajo si no hay volume spike
            
        except Exception as e:
            log_debug(f"Volume analysis no disponible: {e}", "order_block_mitigation_enterprise")
            return 0.6, 0.0

    def _validate_institutional_order_block_enterprise(self, 
                                                      order_block: Dict[str, Any],
                                                      liquidity_grabs: List[Dict],
                                                      mitigation_details: Dict[str, Any]) -> Tuple[float, bool]:
        """🏛️ Validar institutional footprint del Order Block enterprise"""
        try:
            institutional_score = 0.5  # Base score
            smart_money_confirmed = False
            
            # 🎯 VERIFICAR CONFLUENCIA CON LIQUIDITY GRABS
            if liquidity_grabs:
                block_price = order_block['origin_price']
                
                for lg in liquidity_grabs:
                    lg_price = lg.get('grab_price', lg.get('price', 0))
                    distance = abs(block_price - lg_price) / block_price
                    
                    if distance <= 0.005:  # 50 pips confluence
                        institutional_score += 0.2
                        smart_money_confirmed = True
                        log_debug("🏛️ Liquidity Grab confluence confirmada", "order_block_mitigation_enterprise")
            
            # 📊 VERIFICAR BLOCK QUALITY
            quality_score = order_block.get('quality_score', 0.5)
            if quality_score > 0.8:
                institutional_score += 0.2
                
            # 🎯 VERIFICAR BLOCK TYPE
            block_type = order_block.get('type', OrderBlockType.DEMAND_ZONE)
            if block_type == OrderBlockType.BREAKER_BLOCK:
                institutional_score += 0.2
                smart_money_confirmed = True
            elif block_type == OrderBlockType.FAIR_VALUE_GAP:
                institutional_score += 0.1
            
            # 📈 VERIFICAR MITIGATION STRENGTH
            mitigation_percentage = mitigation_details.get('mitigation_percentage', 0)
            if mitigation_percentage >= 0.7:  # Strong mitigation
                institutional_score += 0.1
            
            institutional_score = min(institutional_score, 1.0)
            
            if institutional_score >= self.config['institutional_threshold']:
                smart_money_confirmed = True
            
            log_debug(f"🏛️ Institutional validation: {institutional_score:.2f}", "order_block_mitigation_enterprise")
            return institutional_score, smart_money_confirmed
            
        except Exception as e:
            log_error(f"Error validando institutional footprint: {e}", "order_block_mitigation_enterprise")
            return 0.5, False

    def _calculate_order_block_mitigation_confidence_enterprise(self,
                                                               mitigation_score: float,
                                                               volume_score: float,
                                                               institutional_score: float,
                                                               order_block: Dict[str, Any],
                                                               mitigation_details: Dict[str, Any]) -> float:
        """🧮 Cálculo de confianza Order Block Mitigation enterprise ponderado"""
        try:
            # Calcular block quality score
            block_quality = order_block.get('quality_score', 0.5)
            
            # Calcular timing score
            timing_score = 0.8  # Base timing score, mejorar con análisis temporal
            
            # Calcular structure score basado en tipo de block
            block_type = order_block.get('type', OrderBlockType.DEMAND_ZONE)
            if block_type == OrderBlockType.BREAKER_BLOCK:
                structure_score = 0.9
            elif block_type == OrderBlockType.FAIR_VALUE_GAP:
                structure_score = 0.7
            else:
                structure_score = 0.6
            
            total_confidence = (
                block_quality * self.config['block_quality_weight'] +
                mitigation_score * self.config['mitigation_strength_weight'] +
                volume_score * self.config['volume_weight'] +
                institutional_score * self.config['institutional_weight'] +
                timing_score * self.config['timing_weight'] +
                structure_score * self.config['structure_weight']
            ) * 100
            
            # 🚀 BONUS POR CONFLUENCIAS
            bonus = 0.0
            if institutional_score > 0.8:
                bonus += self.config['smart_money_bonus'] * 100
            if block_type == OrderBlockType.FAIR_VALUE_GAP:
                bonus += self.config['fair_value_gap_bonus'] * 100
            if block_type == OrderBlockType.BREAKER_BLOCK:
                bonus += self.config['breaker_block_bonus'] * 100
            if mitigation_details.get('full_mitigation', False):
                bonus += 8.0  # Full mitigation bonus
            
            final_confidence = min(total_confidence + bonus, 95.0)  # Max 95%
            
            log_debug(f"🧮 Order Block Mitigation Confidence: {final_confidence:.1f}% (base: {total_confidence:.1f}%, bonus: {bonus:.1f}%)", "order_block_mitigation_enterprise")
            return final_confidence
            
        except Exception as e:
            log_error(f"Error calculando confidence: {e}", "order_block_mitigation_enterprise")
            return 50.0

    def _generate_order_block_mitigation_signal_enterprise(self, **kwargs) -> Optional[OrderBlockMitigationSignal]:
        """🎯 Generar señal Order Block Mitigation enterprise completa"""
        try:
            # Extraer parámetros
            order_block = kwargs.get('order_block', {})
            mitigation_details = kwargs.get('mitigation_details', {})
            confidence = kwargs.get('confidence', 0.0)
            current_price = kwargs.get('current_price', 0.0)
            symbol = kwargs.get('symbol', '')
            timeframe = kwargs.get('timeframe', '')
            
            # 📊 CALCULAR STRENGTH
            strength = self._calculate_order_block_strength_enterprise(order_block, kwargs)
            
            # 📊 CALCULAR NIVELES DE TRADING
            entry_zone, stop_loss, tp1, tp2 = self._calculate_order_block_trading_levels_enterprise(
                current_price, order_block['direction'], order_block
            )
            
            # 📝 GENERAR NARRATIVA
            narrative = self._generate_order_block_narrative_enterprise(
                order_block['type'], order_block['direction'], confidence, kwargs
            )
            
            # 🎯 CREAR SEÑAL COMPLETA
            signal = OrderBlockMitigationSignal(
                signal_type=order_block['type'],
                confidence=confidence,
                direction=order_block['direction'],
                strength=strength,
                mitigation_level=current_price,
                origin_price=order_block['origin_price'],
                current_price=current_price,
                block_high=order_block['high'],
                block_low=order_block['low'],
                block_size_pips=order_block.get('size_pips', 0),
                mitigation_percentage=mitigation_details.get('mitigation_percentage', 0),
                volume_confirmation=kwargs.get('volume_strength', 0),
                institutional_validation=kwargs.get('institutional_score', 0),
                entry_price=current_price,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                time_to_mitigation=10,  # Placeholder
                approach_strength=mitigation_details.get('approach_strength', 0),
                rejection_strength=mitigation_details.get('rejection_strength', 0),
                smart_money_confirmation=kwargs.get('smart_money_confirmed', False),
                fair_value_gap_present=order_block['type'] == OrderBlockType.FAIR_VALUE_GAP,
                breaker_block_confirmed=order_block['type'] == OrderBlockType.BREAKER_BLOCK,
                narrative=narrative,
                timestamp=datetime.now(),
                session_context=self._build_order_block_session_context(kwargs),
                symbol=symbol,
                timeframe=timeframe,
                status=OrderBlockStatus.PARTIALLY_MITIGATED if mitigation_details.get('block_penetration', False) else OrderBlockStatus.ACTIVE,
                expiry_time=datetime.now() + timedelta(hours=4),
                analysis_id=f"OBM_{symbol}_{int(datetime.now().timestamp())}"
            )
            
            return signal
            
        except Exception as e:
            log_error(f"Error generando señal Order Block Mitigation: {e}", "order_block_mitigation_enterprise")
            return None

    # ===========================================
    # 🛠️ UTILITY METHODS ENTERPRISE
    # ===========================================

    def _calculate_order_block_strength_enterprise(self, 
                                                  order_block: Dict[str, Any],
                                                  context: Dict[str, Any]) -> OrderBlockStrength:
        """💪 Calcular fuerza del Order Block"""
        try:
            volume_strength = context.get('volume_strength', 0)
            size_pips = order_block.get('size_pips', 0)
            institutional_score = context.get('institutional_score', 0)
            
            # Evaluar contra criterios de strength
            for strength, criteria in reversed(list(self.strength_criteria.items())):
                if (volume_strength >= criteria['volume_min'] and
                    size_pips >= criteria['size_min'] and
                    institutional_score >= criteria['institutional_min']):
                    return strength
            
            return OrderBlockStrength.WEAK
            
        except Exception:
            return OrderBlockStrength.MODERATE

    def _calculate_order_block_trading_levels_enterprise(self,
                                                        current_price: float,
                                                        direction: TradingDirection,
                                                        order_block: Dict[str, Any]) -> Tuple[Tuple[float, float], float, float, float]:
        """📊 Calcular niveles de trading para Order Block Mitigation"""
        try:
            block_high = order_block['high']
            block_low = order_block['low']
            
            if direction == TradingDirection.BUY:
                # Entry en mitigation de demand zone
                entry_zone = (block_low, block_high)
                stop_loss = block_low - 0.0010  # 10 pips debajo del bloque
                take_profit_1 = current_price + 0.0030
                take_profit_2 = current_price + 0.0060
                
            else:  # SELL
                # Entry en mitigation de supply zone
                entry_zone = (block_low, block_high)
                stop_loss = block_high + 0.0010  # 10 pips encima del bloque
                take_profit_1 = current_price - 0.0030
                take_profit_2 = current_price - 0.0060
            
            return entry_zone, stop_loss, take_profit_1, take_profit_2
            
        except Exception:
            return (current_price - 0.001, current_price + 0.001), current_price, current_price, current_price

    def _generate_order_block_narrative_enterprise(self,
                                                  block_type: OrderBlockType,
                                                  direction: TradingDirection,
                                                  confidence: float,
                                                  context: Dict) -> str:
        """📝 Generar narrativa Order Block Mitigation enterprise"""
        try:
            base_narrative = f"Order Block Mitigation {direction.value} - {block_type.value}"
            
            details = []
            if context.get('smart_money_confirmed', False):
                details.append("Smart Money confirmado")
            if context.get('volume_strength', 0) > 0.5:
                details.append("volume confirmation")
            if block_type == OrderBlockType.BREAKER_BLOCK:
                details.append("Breaker Block")
            if block_type == OrderBlockType.FAIR_VALUE_GAP:
                details.append("Fair Value Gap")
            
            if details:
                base_narrative += f" con {', '.join(details)}"
            
            base_narrative += f". Confianza: {confidence:.1f}%"
            
            return base_narrative
            
        except Exception:
            return f"Order Block Mitigation {direction.value} - Confianza: {confidence:.1f}%"

    def _build_order_block_session_context(self, kwargs: Dict) -> Dict[str, Any]:
        """🏗️ Construir contexto de sesión Order Block Mitigation"""
        return {
            'mitigation_strength': kwargs.get('mitigation_details', {}).get('mitigation_percentage', 0),
            'approach_strength': kwargs.get('mitigation_details', {}).get('approach_strength', 0),
            'rejection_strength': kwargs.get('mitigation_details', {}).get('rejection_strength', 0),
            'volume_confirmation': kwargs.get('volume_strength', 0) > 0.5,
            'institutional_validation': kwargs.get('institutional_score', 0),
            'smart_money_confirmed': kwargs.get('smart_money_confirmed', False),
            'pattern_strength': kwargs.get('confidence', 0) / 100.0
        }

    def _store_order_block_mitigation_pattern_in_memory(self, signal: OrderBlockMitigationSignal):
        """💾 Guardar patrón Order Block Mitigation usando UnifiedMemorySystem v6.1"""
        try:
            pattern_data = {
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'direction': signal.direction.value,
                'timestamp': signal.timestamp.isoformat() if hasattr(signal.timestamp, 'isoformat') else str(signal.timestamp),
                'symbol': signal.symbol,
                'timeframe': signal.timeframe,
                'mitigation_level': signal.mitigation_level,
                'origin_price': signal.origin_price,
                'block_size_pips': signal.block_size_pips,
                'strength': signal.strength.value,
                'pattern_type': 'order_block_mitigation',
                'mitigation_percentage': signal.mitigation_percentage,
                'volume_confirmation': signal.volume_confirmation,
                'institutional_validation': signal.institutional_validation,
                'smart_money_confirmation': signal.smart_money_confirmation,
                'fair_value_gap_present': signal.fair_value_gap_present,
                'breaker_block_confirmed': signal.breaker_block_confirmed
            }
            
            if self.unified_memory:
                try:
                    self.unified_memory.update_market_memory(pattern_data, signal.symbol)
                    log_info(f"✅ Patrón Order Block Mitigation almacenado en UnifiedMemorySystem: {signal.symbol} {signal.signal_type.value}", "order_block_mitigation_enterprise")
                except Exception as e:
                    log_error(f"❌ Error almacenando en UnifiedMemorySystem: {e}", "order_block_mitigation_enterprise")
                    self.pattern_memory['successful_mitigations'].append(pattern_data)
            else:
                self.pattern_memory['successful_mitigations'].append(pattern_data)
                log_debug("🔄 Patrón almacenado en memoria local (fallback)")
            
            # Limitar memoria local
            if len(self.pattern_memory['successful_mitigations']) > 50:
                self.pattern_memory['successful_mitigations'] = self.pattern_memory['successful_mitigations'][-50:]
                
        except Exception as e:
            log_error(f"❌ Error crítico guardando patrón Order Block Mitigation en memoria: {e}", "order_block_mitigation_enterprise")

    # ===========================================
    # 🧪 TESTING & UTILITIES
    # ===========================================

def create_test_order_block_mitigation_detector() -> OrderBlockMitigationDetectorEnterprise:
    """🧪 Crear detector para testing"""
    return OrderBlockMitigationDetectorEnterprise()


if __name__ == "__main__":
    # 🧪 Test básico
    detector = create_test_order_block_mitigation_detector()
    print("✅ Order Block Mitigation Detector Enterprise v6.0 - Test básico completado")
