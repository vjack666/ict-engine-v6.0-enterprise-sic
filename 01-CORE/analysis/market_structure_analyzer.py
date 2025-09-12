#!/usr/bin/env python3
"""
🏗️ MARKET STRUCTURE ANALYZER - ICT ENGINE v6.0 Enterprise SIC
=============================================================

Analizador avanzado de estructura de mercado para ICT Engine v6.1.0 Enterprise
que proporciona detección automática de:

📊 **Análisis de Estructura ICT:**
- Change of Character (CHoCH) detection
- Break of Structure (BOS) identification
- Fair Value Gap (FVG) analysis
- Order Block detection
- Swing point analysis

🎯 **Características v6.0 Enterprise:**
- Integración nativa con sistema centralizado Enterprise
- Análisis multi-timeframe inteligente
- Cache predictivo de patrones estructurales
- Debug avanzado con AdvancedDebugger
- Performance optimizada para real-time

🔄 **Pipeline Completo:**
1. Obtención de datos vía AdvancedCandleDownloader
2. Detección de swing points (Higher Highs/Lower Lows)
3. Identificación de cambios estructurales
4. Análisis de confluencias multi-timeframe
5. Generación de señales estructurales

Autor: ICT Engine v6.1.0 Enterprise Team
Versión: v6.1.0-enterprise
Fecha: Agosto 2025
"""

# ===============================
# IMPORTS ENTERPRISE SYSTEM
# ===============================
import sys
import os
import threading
import time
from typing import Dict, List, Optional, Callable, Any, Set, Tuple, Union, TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# Imports Enterprise System - CENTRAL BRIDGE SINCRONIZADO  
try:
    # TODO #3: Bridge mejorado al sistema SIC central
    
    # Construir rutas absolutas para SIC (v3.0 actual y v3.1 futuro)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # Subir 3 niveles: analysis -> 01-CORE -> ict-engine-v6.0
    workspace_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", ".."))
    
    possible_sic_paths = [
        # Ruta del SIC v3.0 actual (proyecto principal/docs/sistema)
        os.path.abspath(os.path.join(workspace_root, "proyecto principal", "docs", "sistema")),
        # Ruta backup del proyecto principal
        os.path.abspath(os.path.join(workspace_root, "proyecto principal", "backups", "PRE_PLAN_MANUAL", "sistema")),
        # Ruta del proyecto principal (para sistema centralizado)
        os.path.abspath(os.path.join(workspace_root, "proyecto principal", "sistema")),
        # Rutas alternativas
        os.path.abspath(os.path.join(workspace_root, "sistema")),
    ]
    
    SIC_V3_1_AVAILABLE = False
    SIC_BRIDGE_SOURCE = "FALLBACK_LOCAL"
    
    # Intentar cargar desde rutas locales primero
    for sic_path in possible_sic_paths:
        # print(f"[DEBUG] Verificando ruta: {sic_path}")
        # print(f"[DEBUG] Existe: {os.path.exists(sic_path)}")
        if os.path.exists(sic_path):
            try:
                if sic_path not in sys.path:
                    sys.path.insert(0, sic_path)
                    # print(f"[DEBUG] Agregado a sys.path: {sic_path}")
                    
                # Sistema centralizado activo - usar sistema actual como base
                try:
                    from sic import enviar_senal_log  # type: ignore # Test SIC v3.0
                    # print(f"[DEBUG] SIC v3.0 encontrado! Creando wrapper...")
                    # Wrapper classes se crean al final del bloque
                    
                    SIC_V3_1_AVAILABLE = True
                    SIC_BRIDGE_SOURCE = f"SIC_v3.0_WRAPPER_{os.path.basename(sic_path)}"
                    # print(f"[DEBUG] Wrapper configurado: {SIC_BRIDGE_SOURCE}")
                    break
                except ImportError as e:
                    # print(f"[DEBUG] SIC v3.0 falló: {e}")
                    pass
                        
            except Exception as e:
                # print(f"[DEBUG] Error general: {e}")
                # Remover de sys.path si falló
                if sic_path in sys.path:
                    sys.path.remove(sic_path)
                continue
    
    # Sistema centralizado activo - skip importación directa del sistema
    
except Exception as e:
    SIC_V3_1_AVAILABLE = False
    SIC_BRIDGE_SOURCE = f"ERROR_FALLBACK_{str(e)[:50]}"

# Declarar clases SIC usando patrones evitar redeclaración Pylance
if SIC_V3_1_AVAILABLE:
    # Crear clases wrapper para compatibilidad v3.1 cuando SIC está disponible  
    class _SICv31EnterpriseWrapper:
        def __init__(self):
            # print("📡 [SIC Bridge] Usando SIC v3.0 como base para v3.1 Enterprise")
            pass
    
    class _AdvancedDebuggerWrapper:
        def __init__(self): 
            pass
        def debug(self, msg): 
            enviar_senal_log("DEBUG", msg, __name__, "sic_bridge")  # type: ignore
    
    # Asignar a nombres finales
    SICv31Enterprise = _SICv31EnterpriseWrapper
    AdvancedDebugger = _AdvancedDebuggerWrapper
    
else:
    # Crear fallback classes si SIC no está disponible
    class _SICv31EnterpriseFallback:
        def __init__(self): 
            print("⚠️ [SIC Bridge] Sistema centralizado funcionando en modo standalone")
            print("ℹ️ [SIC Bridge] Usando fallback local para continuidad del sistema")
    
    class _AdvancedDebuggerFallback:
        def __init__(self): 
            pass
        def debug(self, msg): 
            print(f"[DEBUG-FALLBACK] {msg}")
    
    # Asignar a nombres finales
    SICv31Enterprise = _SICv31EnterpriseFallback
    AdvancedDebugger = _AdvancedDebuggerFallback

# Sistema de logging - BRIDGE CENTRAL SIC SINCRONIZADO
try:
    # TODO #3: Bridge mejorado al sistema de logging SIC central
    
    SIC_LOGGING_AVAILABLE = False
    LOGGING_BRIDGE_SOURCE = "FALLBACK_LOCAL"
    
    # Intentar desde rutas ya configuradas en sys.path (SIC v3.0)
    for path in sys.path:
        if 'sistema' in path and os.path.exists(path):
            try:
                from sic import enviar_senal_log  # type: ignore
                SIC_LOGGING_AVAILABLE = True
                LOGGING_BRIDGE_SOURCE = f"SIC_v3.0_PATH_{os.path.basename(path)}"
                break
            except ImportError:
                continue
    
    # Si no se encontró en sys.path, buscar en rutas conocidas con paths absolutos
    if not SIC_LOGGING_AVAILABLE:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # Usar la misma lógica de 3 niveles como arriba
        workspace_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", ".."))
        
        sic_logging_paths = [
            # SIC v3.0 actual
            os.path.abspath(os.path.join(workspace_root, "proyecto principal", "docs", "sistema")),
            # SIC v3.0 backup
            os.path.abspath(os.path.join(workspace_root, "proyecto principal", "backups", "PRE_PLAN_MANUAL", "sistema")),
        ]
        
        for sic_path in sic_logging_paths:
            if os.path.exists(sic_path):
                try:
                    if sic_path not in sys.path:
                        sys.path.insert(0, sic_path)
                    from sic import enviar_senal_log  # type: ignore
                    SIC_LOGGING_AVAILABLE = True
                    LOGGING_BRIDGE_SOURCE = f"SIC_v3.0_DIRECTO_{os.path.basename(sic_path)}"
                    break
                except ImportError:
                    if sic_path in sys.path:
                        sys.path.remove(sic_path)
                    continue
    
    # Skip importación directa legacy - sistema.sic no existe
    
except Exception as e:
    SIC_LOGGING_AVAILABLE = False
    LOGGING_BRIDGE_SOURCE = f"ERROR_FALLBACK_{str(e)[:30]}"

# Crear función fallback si logging SIC no está disponible
if not SIC_LOGGING_AVAILABLE:
    def enviar_senal_log(level, message, module, category="BRIDGE"):
        """Fallback para logging cuando SIC no está disponible"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {module}.{category}: {message}")

# Componentes v6.0 - Variables globales para evitar problemas de Pylance
AdvancedCandleDownloader = None
MT5DataManager = None
COMPONENTS_AVAILABLE = False

# Imports para type checking
if TYPE_CHECKING:
    from data_management.advanced_candle_downloader import AdvancedCandleDownloader as _AdvancedCandleDownloaderType
    from data_management.mt5_data_manager import MT5DataManager as _MT5DataManagerType
else:
    _AdvancedCandleDownloaderType = Any
    _MT5DataManagerType = Any

try:
    from data_management.advanced_candle_downloader import AdvancedCandleDownloader as _AdvancedCandleDownloader
    from data_management.mt5_data_manager import MT5DataManager as _MT5DataManager
    AdvancedCandleDownloader = _AdvancedCandleDownloader
    MT5DataManager = _MT5DataManager
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("⚠️ Algunos componentes v6.0 no están disponibles, usando fallbacks")
    
    # Fallback AdvancedCandleDownloader
    class _AdvancedCandleDownloaderFallback:
        def __init__(self):
            pass
        def get_data(self, *args, **kwargs):
            return None
    
    class _MT5DataManagerFallback:
        def __init__(self):
            pass
    
    AdvancedCandleDownloader = _AdvancedCandleDownloaderFallback
    MT5DataManager = _MT5DataManagerFallback

# ===============================
# TIPOS Y ENUMS ICT
# ===============================

class StructureType(Enum):
    """🏗️ Tipos de estructura de mercado ICT"""
    CHOCH_BULLISH = "choch_bullish"          # Change of Character alcista
    CHOCH_BEARISH = "choch_bearish"          # Change of Character bajista
    BOS_BULLISH = "bos_bullish"              # Break of Structure alcista
    BOS_BEARISH = "bos_bearish"              # Break of Structure bajista
    RANGE_BOUND = "range_bound"              # Rango lateral
    CONSOLIDATION = "consolidation"          # Consolidación


class FVGType(Enum):
    """📊 Tipos de Fair Value Gap"""
    BULLISH_FVG = "bullish_fvg"             # FVG alcista
    BEARISH_FVG = "bearish_fvg"             # FVG bajista
    BALANCED_FVG = "balanced_fvg"           # FVG balanceado
    PREMIUM_FVG = "premium_fvg"             # FVG en premium
    DISCOUNT_FVG = "discount_fvg"           # FVG en discount


class OrderBlockType(Enum):
    """📦 Tipos de Order Block"""
    BULLISH_OB = "bullish_ob"               # Order Block alcista
    BEARISH_OB = "bearish_ob"               # Order Block bajista
    BREAKER_BLOCK = "breaker_block"         # Breaker Block
    MITIGATION_BLOCK = "mitigation_block"   # Mitigation Block


class TradingDirection(Enum):
    """📈 Direcciones de trading"""
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


# ===============================
# DATACLASSES ICT
# ===============================

@dataclass
class SwingPoint:
    """🎯 Swing point detectado"""
    index: int
    price: float
    timestamp: datetime
    point_type: str  # 'high' o 'low'
    strength: float = 0.0
    confirmed: bool = False


@dataclass 
class MarketStructureSignal:
    """🏗️ Señal de estructura de mercado"""
    structure_type: StructureType
    confidence: float
    direction: TradingDirection
    break_level: float
    target_level: float
    narrative: str
    timestamp: datetime
    timeframe: str
    confluence_score: float
    fvg_present: bool
    order_block_present: bool
    
    # Nuevos campos v6.0
    swing_highs: List[SwingPoint] = field(default_factory=list)
    swing_lows: List[SwingPoint] = field(default_factory=list)
    sic_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FairValueGap:
    """📊 Fair Value Gap detectado"""
    fvg_type: FVGType
    high_price: float
    low_price: float
    origin_candle: int
    filled_percentage: float
    is_mitigated: bool
    mitigation_candle: Optional[int]
    narrative: str
    timestamp: datetime


@dataclass
class OrderBlock:
    """📦 Order Block detectado"""
    ob_type: OrderBlockType
    high_price: float
    low_price: float
    origin_candle: int
    reaction_strength: float
    is_tested: bool
    test_count: int
    narrative: str
    timestamp: datetime


# ===============================
# MARKET STRUCTURE ANALYZER
# ===============================

class MarketStructureAnalyzer:
    """
    🏗️ MARKET STRUCTURE ANALYZER v6.0 ENTERPRISE
    =============================================

    Analizador profesional de estructura de mercado ICT con:
    - Detección automática de CHoCH y BOS
    - Análisis multi-timeframe inteligente
    - Fair Value Gap detection avanzada
    - Order Block identification precisa
    - Integración completa con sistema centralizado
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        🏗️ Inicializa el Market Structure Analyzer v6.0
        
        Args:
            config: Configuración avanzada del analizador
        """
        
        # Configuración v6.0
        self._config = config or {}
        self._enable_debug = self._config.get('enable_debug', True)
        self._use_multi_timeframe = self._config.get('use_multi_timeframe', True)
        self._enable_cache = self._config.get('enable_cache', True)
        
        # Configuración de detección ICT
        self.min_confidence = self._config.get('min_confidence', 70.0)
        self.structure_lookback = self._config.get('structure_lookback', 50)
        self.swing_window = self._config.get('swing_window', 5)
        self.fvg_min_gap = self._config.get('fvg_min_gap', 0.0005)  # 5 pips
        self.ob_reaction_threshold = self._config.get('ob_reaction_threshold', 0.001)
        
        # Pesos de scoring ICT
        self.structure_weight = self._config.get('structure_weight', 0.40)
        self.momentum_weight = self._config.get('momentum_weight', 0.25)
        self.volume_weight = self._config.get('volume_weight', 0.20)
        self.confluence_weight = self._config.get('confluence_weight', 0.15)
        
        # Estado interno
        self.detected_fvgs: List[FairValueGap] = []
        self.detected_order_blocks: List[OrderBlock] = []
        self.structure_history: List[MarketStructureSignal] = []
        self.current_trend = TradingDirection.NEUTRAL
        
        # Componentes v6.0
        self._downloader: Optional[Any] = None
        self._pandas_module = None
        self._performance_metrics = []
        
        # Threading para análisis asíncrono
        self.lock = threading.Lock()
        self._analysis_cache = {}
        
        # Inicializar componentes
        self._initialize_components()
        
        # Log de inicialización con bridge SIC central
        bridge_info = {
            'sic_source': SIC_BRIDGE_SOURCE if 'SIC_BRIDGE_SOURCE' in globals() else 'UNKNOWN',
            'logging_source': LOGGING_BRIDGE_SOURCE if 'LOGGING_BRIDGE_SOURCE' in globals() else 'UNKNOWN',
            'sic_available': SIC_V3_1_AVAILABLE,
            'logging_available': SIC_LOGGING_AVAILABLE if 'SIC_LOGGING_AVAILABLE' in globals() else False
        }
        
        self._log_info(f"MarketStructureAnalyzer v6.0 inicializado - Bridge: {bridge_info['sic_source']}")
        self._log_debug(f"TODO #3: SIC Bridge Info: {bridge_info}")

    def _initialize_components(self):
        """🔧 Inicializa componentes v6.0 con singletons optimizados"""
        try:
            # Configurar downloader usando singleton
            if COMPONENTS_AVAILABLE:
                try:
                    from data_management.advanced_candle_downloader_singleton import get_advanced_candle_downloader
                    self._downloader = get_advanced_candle_downloader()
                    self._log_info("AdvancedCandleDownloader singleton conectado")
                except ImportError:
                    if AdvancedCandleDownloader:
                        self._downloader = AdvancedCandleDownloader()
                        self._log_info("AdvancedCandleDownloader conectado")
                    else:
                        self._log_warning("AdvancedCandleDownloader no disponible - usando fallback")
            else:
                self._log_warning("AdvancedCandleDownloader no disponible")
            
            # Configurar sistema centralizado si está disponible
            if SIC_V3_1_AVAILABLE:
                self._log_info("Integración del sistema centralizado activa")
            
        except Exception as e:
            self._log_error(f"Error inicializando componentes: {e}")

    def analyze_market_structure(self,
                               symbol: str,
                               timeframe: str = "M15",
                               lookback_days: int = 7,
                               current_price: Optional[float] = None) -> Optional[MarketStructureSignal]:
        """
        🏗️ ANÁLISIS COMPLETO DE ESTRUCTURA DE MERCADO v6.0
        
        Args:
            symbol: Símbolo a analizar (ej: "EURUSD")
            timeframe: Timeframe principal (ej: "M15")
            lookback_days: Días de historia para análisis
            current_price: Precio actual (opcional)
            
        Returns:
            MarketStructureSignal si se detecta cambio estructural
        """
        try:
            start_time = time.time()
            self._log_info(f"🏗️ Iniciando análisis Market Structure: {symbol} {timeframe}")
            
            # 1. 📥 OBTENER DATOS
            candles_data = self._get_market_data(symbol, timeframe, lookback_days)
            if candles_data is None or len(candles_data) < 50:
                self._log_warning(f"Insuficientes datos para {symbol} {timeframe}")
                return None
            
            # 2. 🎯 DETECTAR SWING POINTS
            swing_highs, swing_lows = self._detect_swing_points(candles_data)
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                self._log_debug("Insuficientes swing points para análisis")
                return None
            
            # 3. 🔍 DETECTAR CAMBIOS ESTRUCTURALES
            structure_result = self._detect_structure_change(
                candles_data, swing_highs, swing_lows, current_price
            )
            
            if structure_result[0] < 0.5:  # structure_score
                self._log_debug(f"Sin cambio estructural significativo: score={structure_result[0]:.2f}")
                return None
            
            structure_score, structure_type, break_level, target_level = structure_result
            
            # 4. 💨 ANALIZAR MOMENTUM
            momentum_score = self._analyze_momentum(candles_data, structure_type)
            
            # 5. 📊 ANALIZAR VOLUMEN
            volume_score = self._analyze_volume_structure(candles_data)
            
            # 6. 🔗 ANALIZAR CONFLUENCIAS MULTI-TIMEFRAME
            confluence_score = 0.5  # Default si no hay multi-timeframe
            if self._use_multi_timeframe:
                confluence_score = self._analyze_multi_timeframe_confluence(
                    symbol, timeframe, structure_type
                )
            
            # 7. 🧮 CALCULAR CONFIANZA TOTAL
            total_confidence = (
                structure_score * self.structure_weight +
                momentum_score * self.momentum_weight +
                volume_score * self.volume_weight +
                confluence_score * self.confluence_weight
            ) * 100
            
            # 8. ✅ VALIDAR THRESHOLD
            if total_confidence < self.min_confidence:
                self._log_debug(f"Confianza insuficiente: {total_confidence:.1f}% < {self.min_confidence}%")
                return None
            
            # 9. 💎 DETECTAR FVGs
            fvg_present = self._detect_fair_value_gaps(candles_data)
            
            # 10. 📦 DETECTAR ORDER BLOCKS
            ob_present = self._detect_order_blocks(candles_data)
            
            # 11. 🎯 GENERAR SEÑAL
            signal = self._generate_structure_signal(
                structure_type=structure_type,
                confidence=total_confidence,
                break_level=break_level,
                target_level=target_level,
                confluence_score=confluence_score,
                fvg_present=fvg_present,
                ob_present=ob_present,
                swing_highs=swing_highs,
                swing_lows=swing_lows,
                timeframe=timeframe,
                candles=candles_data
            )
            
            # 12. 📝 ACTUALIZAR ESTADO
            self._update_structure_state(structure_type, signal)
            
            # 13. 📊 MÉTRICAS DE PERFORMANCE
            analysis_time = time.time() - start_time
            self._performance_metrics.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis_time': analysis_time,
                'confidence': total_confidence,
                'timestamp': datetime.now()
            })
            
            self._log_info(f"🎯 Estructura detectada: {signal.structure_type.value} - {signal.confidence:.1f}% confianza")
            return signal
            
        except Exception as e:
            self._log_error(f"Error en análisis Market Structure: {e}")
            return None

    def _get_market_data(self, symbol: str, timeframe: str, lookback_days: int):
        """📥 Obtiene datos de mercado usando AdvancedCandleDownloader"""
        try:
            if not self._downloader:
                self._log_error("AdvancedCandleDownloader no disponible")
                return None
            
            # Calcular fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Descargar datos
            result = self._downloader.download_candles(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                save_to_file=False
            )
            
            if result and result.get('success', False):
                data = result.get('data')
                if data is not None and len(data) > 0:
                    self._log_info(f"✅ Datos obtenidos: {len(data)} velas {symbol} {timeframe}")
                    return data
            
            self._log_warning(f"Sin datos para {symbol} {timeframe}")
            return None
            
        except Exception as e:
            self._log_error(f"Error obteniendo datos: {e}")
            return None

    def _detect_swing_points(self, candles) -> Tuple[List[SwingPoint], List[SwingPoint]]:
        """🎯 Detecta swing highs y swing lows"""
        try:
            swing_highs = []
            swing_lows = []
            
            # Detectar swing highs
            for i in range(self.swing_window, len(candles) - self.swing_window):
                current_high = candles.iloc[i]['high']
                
                # Verificar que sea el máximo en la ventana
                is_swing_high = True
                for j in range(i - self.swing_window, i + self.swing_window + 1):
                    if j != i and candles.iloc[j]['high'] >= current_high:
                        is_swing_high = False
                        break
                
                if is_swing_high:
                    swing_point = SwingPoint(
                        index=i,
                        price=current_high,
                        timestamp=candles.index[i] if hasattr(candles.index[i], 'timestamp') else datetime.now(),
                        point_type='high',
                        strength=1.0,
                        confirmed=True
                    )
                    swing_highs.append(swing_point)
            
            # Detectar swing lows
            for i in range(self.swing_window, len(candles) - self.swing_window):
                current_low = candles.iloc[i]['low']
                
                # Verificar que sea el mínimo en la ventana
                is_swing_low = True
                for j in range(i - self.swing_window, i + self.swing_window + 1):
                    if j != i and candles.iloc[j]['low'] <= current_low:
                        is_swing_low = False
                        break
                
                if is_swing_low:
                    swing_point = SwingPoint(
                        index=i,
                        price=current_low,
                        timestamp=candles.index[i] if hasattr(candles.index[i], 'timestamp') else datetime.now(),
                        point_type='low',
                        strength=1.0,
                        confirmed=True
                    )
                    swing_lows.append(swing_point)
            
            self._log_debug(f"🎯 Swing points: {len(swing_highs)} highs, {len(swing_lows)} lows")
            return swing_highs, swing_lows
            
        except Exception as e:
            self._log_error(f"Error detectando swing points: {e}")
            return [], []

    def _detect_structure_change(self, candles, swing_highs: List[SwingPoint], swing_lows: List[SwingPoint], current_price: Optional[float]) -> Tuple[float, StructureType, float, float]:
        """🔍 Detecta cambios estructurales (CHoCH/BOS)"""
        try:
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return 0.0, StructureType.CONSOLIDATION, 0.0, 0.0  # Consolidación cuando faltan swing points
            
            # Obtener últimos swing points
            last_high = swing_highs[-1]
            prev_high = swing_highs[-2] if len(swing_highs) > 1 else swing_highs[-1]
            last_low = swing_lows[-1]
            prev_low = swing_lows[-2] if len(swing_lows) > 1 else swing_lows[-1]
            
            structure_score = 0.0
            structure_type = StructureType.CONSOLIDATION  # Consolidación es más específico que ranging
            break_level = 0.0
            target_level = 0.0
            
            # DETECTAR BOS ALCISTA (Rompe high anterior)
            if last_high.price > prev_high.price:
                if last_low.price > prev_low.price:  # HH + HL = BOS alcista
                    structure_score = 0.8
                    structure_type = StructureType.BOS_BULLISH
                    break_level = prev_high.price
                    target_level = last_high.price + (last_high.price - prev_high.price)
                else:  # HH + LL = CHoCH alcista
                    structure_score = 0.7
                    structure_type = StructureType.CHOCH_BULLISH
                    break_level = last_low.price
                    target_level = last_high.price
            
            # DETECTAR BOS BAJISTA (Rompe low anterior)
            elif last_low.price < prev_low.price:
                if last_high.price < prev_high.price:  # LL + LH = BOS bajista
                    structure_score = 0.8
                    structure_type = StructureType.BOS_BEARISH
                    break_level = prev_low.price
                    target_level = last_low.price - (prev_low.price - last_low.price)
                else:  # LL + HH = CHoCH bajista
                    structure_score = 0.7
                    structure_type = StructureType.CHOCH_BEARISH
                    break_level = last_high.price
                    target_level = last_low.price
            
            # DETECTAR CONSOLIDACIÓN
            else:
                # Verificar si está en rango
                high_range = max(last_high.price, prev_high.price)
                low_range = min(last_low.price, prev_low.price)
                range_size = high_range - low_range
                
                if range_size < (high_range * 0.01):  # Rango menor al 1%
                    structure_score = 0.4
                    structure_type = StructureType.CONSOLIDATION
                    break_level = high_range
                    target_level = low_range
            
            self._log_debug(f"🔍 Estructura: {structure_type.value} - Score: {structure_score:.2f}")
            return structure_score, structure_type, break_level, target_level
            
        except Exception as e:
            self._log_error(f"Error detectando cambio estructural: {e}")
            return 0.0, StructureType.CONSOLIDATION, 0.0, 0.0  # Consolidación en caso de error

    def _analyze_momentum(self, candles, structure_type: StructureType) -> float:
        """💨 Analiza momentum para confirmar estructura"""
        try:
            # Calcular momentum básico usando últimas 10 velas
            recent_candles = candles.tail(10)
            if len(recent_candles) < 5:
                return 0.5
            
            # Contar velas alcistas vs bajistas
            bullish_candles = sum(1 for _, row in recent_candles.iterrows() if row['close'] > row['open'])
            bearish_candles = len(recent_candles) - bullish_candles
            
            # Calcular ratio de momentum
            momentum_ratio = bullish_candles / len(recent_candles)
            
            # Ajustar según tipo de estructura
            if structure_type in [StructureType.BOS_BULLISH, StructureType.CHOCH_BULLISH]:
                # Para estructuras alcistas, momentum alto es bueno
                momentum_score = momentum_ratio
            elif structure_type in [StructureType.BOS_BEARISH, StructureType.CHOCH_BEARISH]:
                # Para estructuras bajistas, momentum bajo es bueno
                momentum_score = 1.0 - momentum_ratio
            else:
                momentum_score = 0.5
            
            self._log_debug(f"💨 Momentum score: {momentum_score:.2f}")
            return momentum_score
            
        except Exception as e:
            self._log_error(f"Error analizando momentum: {e}")
            return 0.5

    def _analyze_volume_structure(self, candles) -> float:
        """📊 Analiza estructura de volumen"""
        try:
            # Análisis básico de volumen
            if 'volume' not in candles.columns:
                return 0.5  # Sin datos de volumen, score neutral
            
            recent_volume = candles['volume'].tail(10)
            avg_volume = recent_volume.mean()
            latest_volume = recent_volume.iloc[-1]
            
            # Score basado en volumen relativo
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0
            volume_score = min(1.0, volume_ratio / 2.0)  # Normalizar
            
            self._log_debug(f"📊 Volume score: {volume_score:.2f}")
            return volume_score
            
        except Exception as e:
            self._log_error(f"Error analizando volumen: {e}")
            return 0.5

    def _analyze_multi_timeframe_confluence(self, symbol: str, main_timeframe: str, structure_type: StructureType) -> float:
        """
        🔗 TODO #3: ANÁLISIS MULTI-TIMEFRAME COMPLETO ENHANCED
        
        Implementa detección automática de confluencias entre múltiples timeframes
        usando ICTDataManager para verificar disponibilidad de datos y sincronización.
        
        TODO #3 ENHANCEMENTS:
        - Algoritmo de confluence scoring mejorado
        - Validación de structural strength 
        - Integración avanzada con cache system
        - Análisis H4→H1→M15 expandido
        """
        try:
            # FASE 1: Detección automática de datos disponibles - TODO #3 Enhanced
            required_timeframes = self._get_confluence_timeframes(main_timeframe)
            
            # TODO #3: Cache optimization check
            cache_status = self._check_cache_optimization_status(symbol, required_timeframes)
            
            # Verificar disponibilidad de datos usando ICTDataManager
            data_manager = self._get_or_create_data_manager()
            if data_manager:
                detection_result = data_manager.auto_detect_multi_tf_data([symbol], required_timeframes)
                
                if detection_result['sync_status'] == 'INSUFFICIENT':
                    # TODO #3: Aplicar lecciones de cache robustez del TODO #2
                    self._log_debug(f"🔄 TODO #3: Sincronizando datos {symbol} con cache optimization")
                    sync_result = data_manager.sync_multi_tf_data(symbol, required_timeframes)
                    
                    if sync_result['alignment_status'] != 'SYNCHRONIZED':
                        self._log_warning(f"⚠️ TODO #3: Sincronización fallida para {symbol}, usando análisis básico")
                        return 0.5  # Score básico sin confluencias
            
            # FASE 2: Análisis de confluencias por timeframe - TODO #3 Enhanced
            confluence_scores = {}
            structural_strength_scores = {}
            
            for tf in required_timeframes:
                if self._has_timeframe_data(symbol, tf):
                    # TODO #3: Análisis enhanced por timeframe
                    tf_score = self._analyze_timeframe_confluence(symbol, tf, structure_type, main_timeframe)
                    confluence_scores[tf] = tf_score
                    
                    # TODO #3: Validación de fuerza estructural
                    strength_score = self._validate_structural_strength(symbol, tf, structure_type)
                    structural_strength_scores[tf] = strength_score
                    
                    self._log_debug(f"📊 TODO #3: {symbol} {tf} confluence: {tf_score:.2f}, strength: {strength_score:.2f}")
            
            # FASE 3: Cálculo de score ponderado - TODO #3 Enhanced
            if not confluence_scores:
                self._log_warning(f"❌ TODO #3: No hay datos multi-TF para {symbol}")
                return 0.4  # Score bajo sin datos
            
            # TODO #3: Ponderación mejorada con structural strength
            weighted_score = self._calculate_enhanced_weighted_confluence(
                confluence_scores, structural_strength_scores, main_timeframe
            )
            
            # FASE 4: Boost por alineación múltiple - TODO #3 Enhanced
            alignment_boost = self._calculate_enhanced_alignment_boost(
                confluence_scores, structural_strength_scores
            )
            
            # FASE 5: Score final con validación ICT
            final_score = min(weighted_score + alignment_boost, 1.0)
            
            # TODO #3: Aplicar filtros de calidad ICT
            quality_filtered_score = self._apply_ict_quality_filters(
                final_score, confluence_scores, structural_strength_scores
            )
            
            # FASE 6: Log estructurado SLUC v2.1 - TODO #3 Enhanced
            self._log_enhanced_confluence_analysis(
                symbol, main_timeframe, confluence_scores, 
                structural_strength_scores, quality_filtered_score
            )
            
            self._log_debug(f"🔗 TODO #3: {symbol} Confluence final: {quality_filtered_score:.2f} (TFs: {len(confluence_scores)})")
            return quality_filtered_score
            
        except Exception as e:
            self._log_error(f"Error análisis multi-timeframe TODO #3: {e}")
            return 0.5
    
    def _get_confluence_timeframes(self, main_timeframe: str) -> List[str]:
        """📋 Obtener timeframes relevantes para confluencias - TODO #3 ENHANCED"""
        
        # TODO #3: Mapeo expandido H4→H1→M15 con mayor granularidad
        confluence_map = {
            'M1': ['M5', 'M15', 'M30'],      # Scalping confluence
            'M5': ['M15', 'M30', 'H1'],      # Intraday analysis
            'M15': ['M30', 'H1', 'H4'],      # Short-term structure
            'M30': ['H1', 'H4', 'D1'],       # Medium-term confluence
            'H1': ['H4', 'D1', 'W1'],        # Daily bias confirmation
            'H4': ['D1', 'W1', 'MN1'],       # Weekly structure + TODO #3
            'D1': ['W1', 'MN1'],             # Monthly bias - TODO #3
            'W1': ['MN1'],                   # Yearly structure
            'MN1': []                        # No higher TF needed
        }
        
        # TODO #3: Priorizar timeframes por relevancia ICT
        base_timeframes = confluence_map.get(main_timeframe, ['H4', 'D1'])
        
        # TODO #3: Agregar timeframes intermedios para mejor confluencia
        enhanced_timeframes = self._add_intermediate_timeframes(main_timeframe, base_timeframes)
        
        return enhanced_timeframes
    
    def _add_intermediate_timeframes(self, main_tf: str, base_tfs: List[str]) -> List[str]:
        """🔗 TODO #3: Agregar timeframes intermedios para análisis más preciso"""
        try:
            # Timeframes intermedios por categoría ICT
            intermediate_map = {
                'M15': ['M5'],           # Agregar M5 para precision entrada
                'H1': ['M15'],           # Agregar M15 para structure break
                'H4': ['H1', 'M30'],     # Agregar H1 y M30 para confluence
                'D1': ['H4', 'H1']       # Agregar H4 y H1 para daily bias
            }
            
            intermediates = intermediate_map.get(main_tf, [])
            
            # Combinar y remover duplicados manteniendo orden
            all_timeframes = intermediates + base_tfs
            unique_timeframes = []
            for tf in all_timeframes:
                if tf not in unique_timeframes:
                    unique_timeframes.append(tf)
            
            self._log_debug(f"🔗 TODO #3: {main_tf} → Timeframes: {unique_timeframes}")
            return unique_timeframes
            
        except Exception as e:
            self._log_error(f"Error agregando timeframes intermedios: {e}")
            return base_tfs
    
    def _get_or_create_data_manager(self):
        """🏭 Obtener o crear instancia de ICTDataManager usando singletons optimizados"""
        try:
            # Intentar usar singleton optimizado primero
            try:
                from data_management.ict_data_manager_singleton import get_ict_data_manager
                # Crear downloader singleton si no existe
                if not hasattr(self, '_data_manager'):
                    try:
                        from data_management.advanced_candle_downloader_singleton import get_advanced_candle_downloader
                        downloader = get_advanced_candle_downloader()
                    except ImportError:
                        try:
                            # Intentar import directo como fallback
                            from data_management.advanced_candle_downloader import AdvancedCandleDownloader as _DirectAdvancedCandleDownloader
                            downloader = _DirectAdvancedCandleDownloader()
                        except ImportError:
                            self._log_warning("AdvancedCandleDownloader no disponible en ninguna forma")
                            return None
                    
                    self._data_manager = get_ict_data_manager(downloader=downloader)
                
                return self._data_manager
            except ImportError:
                # Fallback a imports normales
                from data_management.ict_data_manager import ICTDataManager
                from data_management.advanced_candle_downloader import AdvancedCandleDownloader
                
                # Crear downloader si no existe
                if not hasattr(self, '_data_manager'):
                    downloader = AdvancedCandleDownloader()
                    self._data_manager = ICTDataManager(downloader=downloader)
                
                return self._data_manager
            
        except ImportError as e:
            self._log_warning(f"ICTDataManager no disponible: {e}")
            return None
        except Exception as e:
            self._log_error(f"Error creando ICTDataManager: {e}")
            return None
    
    def _has_timeframe_data(self, symbol: str, timeframe: str) -> bool:
        """✅ Verificar disponibilidad de datos para timeframe específico"""
        try:
            data_manager = self._get_or_create_data_manager()
            if data_manager:
                return data_manager._has_minimal_data(symbol, timeframe)
            else:
                # Fallback: verificar en memoria unificada
                return self._check_unified_memory_data(symbol, timeframe)
        except:
            return False
    
    def _check_unified_memory_data(self, symbol: str, timeframe: str) -> bool:
        """🧠 Verificar datos en memoria unificada como fallback"""
        try:
            # TODO: Implementar cuando unified_memory esté disponible
            # Por ahora usar verificación básica
            return self._has_basic_cache_data(symbol, timeframe)
        except:
            return False
    
    def _has_basic_cache_data(self, symbol: str, timeframe: str) -> bool:
        """📁 Verificar datos básicos en cache"""
        try:
            # Verificación básica de disponibilidad de datos
            cache_key = f"{symbol}_{timeframe}"
            return hasattr(self, '_analysis_cache') and cache_key in getattr(self, '_analysis_cache', {})
        except:
            return False
    
    def _analyze_timeframe_confluence(self, symbol: str, timeframe: str, 
                                    structure_type: StructureType, main_tf: str) -> float:
        """📊 TODO #3: Analizar confluencia en timeframe específico - ENHANCED"""
        try:
            score = 0.0
            
            # TODO #3: FACTOR 1 - Alineación estructural avanzada (35% peso)
            structure_alignment = self._check_structure_alignment_enhanced(symbol, timeframe, structure_type)
            score += structure_alignment * 0.35
            
            # TODO #3: FACTOR 2 - Niveles clave ICT (25% peso)
            key_levels_score = self._check_ict_levels_confluence(symbol, timeframe)
            score += key_levels_score * 0.25
            
            # TODO #3: FACTOR 3 - Momentum y volumen institucional (20% peso)
            momentum_score = self._check_institutional_momentum(symbol, timeframe, main_tf)
            score += momentum_score * 0.20
            
            # TODO #3: FACTOR 4 - Relevancia temporal ICT (10% peso)
            temporal_score = self._check_temporal_relevance_enhanced(timeframe, main_tf)
            score += temporal_score * 0.10
            
            # TODO #3: FACTOR 5 - Strength validation (10% peso)
            strength_score = self._validate_structural_strength(symbol, timeframe, structure_type)
            score += strength_score * 0.10
            
            final_score = min(score, 1.0)
            
            # TODO #3: Log detallado SLUC v2.1
            self._log_timeframe_analysis(symbol, timeframe, {
                'structure_alignment': structure_alignment,
                'ict_levels': key_levels_score,
                'institutional_momentum': momentum_score,
                'temporal_relevance': temporal_score,
                'structural_strength': strength_score,
                'final_score': final_score
            })
            
            return final_score
            
        except Exception as e:
            self._log_error(f"Error análisis confluencia {timeframe}: {e}")
            return 0.3
    
    def _check_structure_alignment(self, symbol: str, timeframe: str, structure_type: StructureType) -> float:
        """🔗 Verificar alineación de estructura entre timeframes"""
        try:
            # Implementación básica - verificar bias direccional
            if structure_type in [StructureType.BOS_BULLISH, StructureType.CHOCH_BULLISH]:
                return 0.7  # Simulación de alineación alcista
            elif structure_type in [StructureType.BOS_BEARISH, StructureType.CHOCH_BEARISH]:
                return 0.8  # Simulación de alineación bajista
            else:
                return 0.4  # Rango o indefinido
        except:
            return 0.5

    def _check_structure_alignment_enhanced(self, symbol: str, timeframe: str, structure_type: StructureType) -> float:
        """🔗 TODO #3: Verificar alineación estructural avanzada ICT"""
        try:
            base_alignment = self._check_structure_alignment(symbol, timeframe, structure_type)
            
            # TODO #3: Factores adicionales de alineación
            swing_alignment = self._check_swing_structure_alignment(symbol, timeframe)
            bos_choch_alignment = self._check_bos_choch_alignment(symbol, timeframe, structure_type)
            liquidity_alignment = self._check_liquidity_structure_alignment(symbol, timeframe)
            
            # Combinar factores con pesos ICT methodology
            enhanced_score = (
                base_alignment * 0.4 +
                swing_alignment * 0.25 +
                bos_choch_alignment * 0.25 +
                liquidity_alignment * 0.10
            )
            
            return min(enhanced_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error alineación estructural enhanced: {e}")
            return 0.5

    def _check_swing_structure_alignment(self, symbol: str, timeframe: str) -> float:
        """📈 TODO #3: Verificar alineación de swing structure"""
        try:
            # Implementación placeholder para swing highs/lows alignment
            return 0.6  # TODO: Implementar con datos reales
        except:
            return 0.5

    def _check_bos_choch_alignment(self, symbol: str, timeframe: str, structure_type: StructureType) -> float:
        """⚡ TODO #3: Verificar alineación BOS/CHoCH"""
        try:
            # Implementación placeholder para BOS/CHoCH detection
            return 0.7  # TODO: Integrar con BOS/CHoCH detector
        except:
            return 0.5

    def _check_liquidity_structure_alignment(self, symbol: str, timeframe: str) -> float:
        """💧 TODO #3: Verificar alineación con zonas de liquidez"""
        try:
            # Implementación placeholder para liquidity zones
            return 0.6  # TODO: Integrar con liquidity analyzer
        except:
            return 0.5
    
    def _check_key_levels_confluence(self, symbol: str, timeframe: str) -> float:
        """🎯 Verificar confluencia con niveles clave (soporte/resistencia)"""
        try:
            # Implementación básica - detección de niveles importantes
            # En implementación real, integraría con OrderBlockDetector y FVG
            return 0.6  # Score moderado por defecto
        except:
            return 0.5

    def _check_ict_levels_confluence(self, symbol: str, timeframe: str) -> float:
        """🎯 TODO #3: Verificar confluencia con niveles ICT específicos"""
        try:
            # Factores ICT levels
            fvg_confluence = self._check_fvg_confluence(symbol, timeframe)
            order_blocks_confluence = self._check_order_blocks_confluence(symbol, timeframe)
            breaker_blocks_confluence = self._check_breaker_blocks_confluence(symbol, timeframe)
            liquidity_levels_confluence = self._check_liquidity_levels_confluence(symbol, timeframe)
            
            # Combinar con pesos ICT methodology
            ict_score = (
                fvg_confluence * 0.30 +
                order_blocks_confluence * 0.35 +
                breaker_blocks_confluence * 0.20 +
                liquidity_levels_confluence * 0.15
            )
            
            return min(ict_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error ICT levels confluence: {e}")
            return 0.5

    def _check_fvg_confluence(self, symbol: str, timeframe: str) -> float:
        """💎 TODO #3: Verificar confluencia con Fair Value Gaps"""
        try:
            # TODO: Integrar con FVG detector real
            return 0.6  # Placeholder
        except:
            return 0.5

    def _check_order_blocks_confluence(self, symbol: str, timeframe: str) -> float:
        """📦 TODO #3: Verificar confluencia con Order Blocks"""
        try:
            # TODO: Integrar con Order Block detector
            return 0.7  # Placeholder
        except:
            return 0.5

    def _check_breaker_blocks_confluence(self, symbol: str, timeframe: str) -> float:
        """🔨 TODO #3: Verificar confluencia con Breaker Blocks"""
        try:
            # TODO: Integrar con Breaker Block detector
            return 0.6  # Placeholder
        except:
            return 0.5

    def _check_liquidity_levels_confluence(self, symbol: str, timeframe: str) -> float:
        """💧 TODO #3: Verificar confluencia con niveles de liquidez"""
        try:
            # TODO: Integrar con liquidity analyzer
            return 0.5  # Placeholder
        except:
            return 0.5
    
    def _check_momentum_confluence(self, symbol: str, timeframe: str, main_tf: str) -> float:
        """⚡ Verificar confluencia de momentum entre timeframes"""
        try:
            # Implementación básica - análisis de momentum direccional
            return 0.5  # Score neutral por defecto
        except:
            return 0.5

    def _check_institutional_momentum(self, symbol: str, timeframe: str, main_tf: str) -> float:
        """⚡ TODO #3: Verificar momentum institucional avanzado"""
        try:
            # Factores de momentum institucional
            volume_momentum = self._check_institutional_volume_momentum(symbol, timeframe)
            price_action_momentum = self._check_institutional_price_action(symbol, timeframe)
            order_flow_momentum = self._check_institutional_order_flow(symbol, timeframe)
            
            # Combinar factores con pesos smart money concepts
            institutional_score = (
                volume_momentum * 0.40 +
                price_action_momentum * 0.35 +
                order_flow_momentum * 0.25
            )
            
            return min(institutional_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error momentum institucional: {e}")
            return 0.5

    def _check_institutional_volume_momentum(self, symbol: str, timeframe: str) -> float:
        """📊 TODO #3: Analizar momentum de volumen institucional"""
        try:
            # TODO: Implementar con datos de volumen real
            return 0.6  # Placeholder
        except:
            return 0.5

    def _check_institutional_price_action(self, symbol: str, timeframe: str) -> float:
        """💹 TODO #3: Analizar price action institucional"""
        try:
            # TODO: Implementar con análisis de velas institucionales
            return 0.7  # Placeholder
        except:
            return 0.5

    def _check_institutional_order_flow(self, symbol: str, timeframe: str) -> float:
        """🌊 TODO #3: Analizar flujo de órdenes institucional"""
        try:
            # TODO: Implementar con análisis de order flow
            return 0.5  # Placeholder
        except:
            return 0.5

    def _check_temporal_relevance_enhanced(self, timeframe: str, main_tf: str) -> float:
        """⏰ TODO #3: Calcular relevancia temporal enhanced"""
        try:
            base_relevance = self._check_temporal_relevance(timeframe, main_tf)
            
            # TODO #3: Factores adicionales de relevancia temporal
            session_alignment = self._check_trading_session_alignment(timeframe, main_tf)
            volatility_timing = self._check_volatility_timing_relevance(timeframe)
            
            # Combinar factores
            enhanced_relevance = (
                base_relevance * 0.70 +
                session_alignment * 0.20 +
                volatility_timing * 0.10
            )
            
            return min(enhanced_relevance, 1.0)
            
        except Exception as e:
            self._log_error(f"Error relevancia temporal enhanced: {e}")
            return 0.5

    def _check_trading_session_alignment(self, timeframe: str, main_tf: str) -> float:
        """🕐 TODO #3: Verificar alineación con sesiones de trading"""
        try:
            # TODO: Implementar con análisis de sesiones
            return 0.7  # Placeholder
        except:
            return 0.5

    def _check_volatility_timing_relevance(self, timeframe: str) -> float:
        """⚡ TODO #3: Verificar relevancia de timing de volatilidad"""
        try:
            # TODO: Implementar con análisis de volatilidad
            return 0.6  # Placeholder
        except:
            return 0.5

    def _validate_structural_strength(self, symbol: str, timeframe: str, structure_type: StructureType) -> float:
        """💪 TODO #3: Validar fuerza estructural ICT"""
        try:
            # Factores de validación de fuerza
            reaction_strength = self._check_reaction_strength(symbol, timeframe)
            volume_confirmation = self._check_volume_confirmation(symbol, timeframe)
            follow_through = self._check_follow_through_strength(symbol, timeframe)
            
            # Combinar factores de fuerza
            strength_score = (
                reaction_strength * 0.40 +
                volume_confirmation * 0.35 +
                follow_through * 0.25
            )
            
            return min(strength_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error validación fuerza estructural: {e}")
            return 0.5

    def _check_reaction_strength(self, symbol: str, timeframe: str) -> float:
        """⚡ TODO #3: Verificar fuerza de reacción en niveles"""
        try:
            # TODO: Implementar con análisis de reacciones
            return 0.6  # Placeholder
        except:
            return 0.5

    def _check_volume_confirmation(self, symbol: str, timeframe: str) -> float:
        """📊 TODO #3: Verificar confirmación de volumen"""
        try:
            # TODO: Implementar con análisis de volumen
            return 0.7  # Placeholder
        except:
            return 0.5

    def _check_follow_through_strength(self, symbol: str, timeframe: str) -> float:
        """📈 TODO #3: Verificar fuerza de follow-through"""
        try:
            # TODO: Implementar con análisis de continuación
            return 0.6  # Placeholder
        except:
            return 0.5

    def _log_timeframe_analysis(self, symbol: str, timeframe: str, analysis_data: dict):
        """📝 TODO #3: Log detallado de análisis por timeframe"""
        try:
            log_data = {
                'event_type': 'timeframe_confluence_analysis',
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis_data': analysis_data,
                'timestamp': datetime.now()
            }
            
            self._log_debug(f"📊 {symbol} {timeframe}: {analysis_data}")
            
        except Exception as e:
            self._log_debug(f"Warning logging timeframe analysis: {e}")
    
    def _check_temporal_relevance(self, timeframe: str, main_tf: str) -> float:
        """⏰ Calcular relevancia temporal del timeframe"""
        try:
            # Mapeo de relevancia por proximidad temporal
            relevance_map = {
                ('M5', 'M15'): 0.9,    # Alta relevancia
                ('M15', 'M30'): 0.9,
                ('M30', 'H1'): 0.8,
                ('H1', 'H4'): 0.8,
                ('H4', 'D1'): 0.7,     # Relevancia moderada
            }
            
            return relevance_map.get((main_tf, timeframe), 0.5)
        except:
            return 0.5
    
    def _calculate_weighted_confluence(self, confluence_scores: Dict[str, float], main_tf: str) -> float:
        """⚖️ Calcular score ponderado de confluencias"""
        try:
            if not confluence_scores:
                return 0.0
            
            # Pesos por timeframe según distancia del principal
            weights = {
                'M5': 0.15, 'M15': 0.25, 'M30': 0.20,
                'H1': 0.20, 'H4': 0.30, 'D1': 0.35
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for tf, score in confluence_scores.items():
                weight = weights.get(tf, 0.1)
                weighted_sum += score * weight
                total_weight += weight
            
            return weighted_sum / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            self._log_error(f"Error calculando confluencia ponderada: {e}")
            return sum(confluence_scores.values()) / len(confluence_scores)
    
    def _calculate_alignment_boost(self, confluence_scores: Dict[str, float]) -> float:
        """🚀 Calcular boost por alineación múltiple"""
        try:
            if len(confluence_scores) < 2:
                return 0.0
            
            # Contar timeframes con confluencia fuerte (>0.6)
            strong_confluence_count = sum(1 for score in confluence_scores.values() if score > 0.6)
            
            # Boost progresivo por alineación múltiple
            if strong_confluence_count >= 3:
                return 0.15  # Alineación excepcional
            elif strong_confluence_count >= 2:
                return 0.10  # Alineación buena
            elif strong_confluence_count >= 1:
                return 0.05  # Alineación moderada
            else:
                return 0.0   # Sin alineación significativa
                
        except Exception as e:
            self._log_error(f"Error calculando boost alineación: {e}")
            return 0.0
    
    def _log_confluence_analysis(self, symbol: str, main_tf: str, 
                               confluence_scores: Dict[str, float], final_score: float):
        """📝 Log estructurado para análisis de confluencias (SLUC v2.1)"""
        try:
            # Preparar datos para SLUC v2.1
            analysis_data = {
                'event_type': 'multi_tf_confluence_analysis',
                'symbol': symbol,
                'main_timeframe': main_tf,
                'analyzed_timeframes': list(confluence_scores.keys()),
                'confluence_scores': confluence_scores,
                'final_confluence_score': final_score,
                'analysis_quality': 'HIGH' if len(confluence_scores) >= 2 else 'BASIC',
                'timestamp': datetime.now()
            }
            
            # Log con sistema unificado si disponible
            try:
                # TODO: Implementar cuando unified_memory esté disponible
                from analysis.unified_market_memory import update_market_memory
                update_market_memory(analysis_data)
            except ImportError:
                self._log_debug("Unified memory no disponible, continuando...")
            except Exception as e:
                self._log_debug(f"Warning updating unified memory: {e}")
            
        except Exception as e:
            self._log_debug(f"Warning logging confluencia: {e}")

    # ============================================
    # TODO #3: MÉTODOS AUXILIARES ENHANCED
    # ============================================

    def _check_cache_optimization_status(self, symbol: str, timeframes: List[str]) -> dict:
        """💾 TODO #3: Verificar estado de optimización del cache"""
        try:
            data_manager = self._get_or_create_data_manager()
            if data_manager:
                # Fix: Usar método correcto sin parámetros
                cache_status = data_manager.get_multi_tf_cache_status()
                return {
                    'status': 'CACHE_AVAILABLE',
                    'symbols_checked': [symbol],
                    'timeframes_checked': timeframes,
                    'cache_data': cache_status
                }
            return {'status': 'NO_CACHE_MANAGER'}
        except Exception as e:
            self._log_error(f"Error verificando cache status: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def _calculate_enhanced_weighted_confluence(self, confluence_scores: Dict[str, float], 
                                              strength_scores: Dict[str, float], main_tf: str) -> float:
        """⚖️ TODO #3: Calcular score ponderado enhanced con structural strength"""
        try:
            base_weighted = self._calculate_weighted_confluence(confluence_scores, main_tf)
            
            # TODO #3: Factor de fuerza estructural
            avg_strength = sum(strength_scores.values()) / len(strength_scores) if strength_scores else 0.5
            strength_multiplier = 0.8 + (avg_strength * 0.4)  # 0.8 - 1.2 range
            
            enhanced_score = base_weighted * strength_multiplier
            return min(enhanced_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error calculando confluencia enhanced: {e}")
            return self._calculate_weighted_confluence(confluence_scores, main_tf)

    def _calculate_enhanced_alignment_boost(self, confluence_scores: Dict[str, float], 
                                          strength_scores: Dict[str, float]) -> float:
        """🚀 TODO #3: Calcular boost enhanced por alineación múltiple"""
        try:
            base_boost = self._calculate_alignment_boost(confluence_scores)
            
            # TODO #3: Boost adicional por fuerza estructural consistente
            if strength_scores:
                consistent_strength = all(score > 0.6 for score in strength_scores.values())
                if consistent_strength:
                    strength_boost = 0.05  # Boost adicional por consistencia
                    return base_boost + strength_boost
            
            return base_boost
            
        except Exception as e:
            self._log_error(f"Error calculando boost enhanced: {e}")
            return self._calculate_alignment_boost(confluence_scores)

    def _apply_ict_quality_filters(self, score: float, confluence_scores: Dict[str, float], 
                                 strength_scores: Dict[str, float]) -> float:
        """🔍 TODO #3: Aplicar filtros de calidad ICT"""
        try:
            filtered_score = score
            
            # Filtro 1: Mínimo de timeframes para alta confianza
            if len(confluence_scores) < 2:
                filtered_score *= 0.8  # Penalizar poca diversidad temporal
            
            # Filtro 2: Consistencia de scores
            if confluence_scores:
                score_variance = self._calculate_score_variance(confluence_scores)
                if score_variance > 0.3:  # Alta varianza = inconsistencia
                    filtered_score *= 0.9
            
            # Filtro 3: Threshold mínimo de fuerza estructural
            if strength_scores:
                min_strength = min(strength_scores.values())
                if min_strength < 0.4:
                    filtered_score *= 0.85  # Penalizar debilidad estructural
            
            return min(filtered_score, 1.0)
            
        except Exception as e:
            self._log_error(f"Error aplicando filtros ICT: {e}")
            return score

    def _calculate_score_variance(self, scores: Dict[str, float]) -> float:
        """📊 TODO #3: Calcular varianza de scores para consistencia"""
        try:
            if len(scores) < 2:
                return 0.0
            
            mean_score = sum(scores.values()) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores.values()) / len(scores)
            return variance ** 0.5  # Standard deviation
            
        except:
            return 0.0

    def _log_enhanced_confluence_analysis(self, symbol: str, main_tf: str, 
                                        confluence_scores: Dict[str, float],
                                        strength_scores: Dict[str, float], 
                                        final_score: float):
        """📝 TODO #3: Log enhanced estructurado SLUC v2.1"""
        try:
            analysis_data = {
                'event_type': 'enhanced_multi_tf_confluence_analysis',
                'todo_version': 'TODO_3_ENHANCED',
                'symbol': symbol,
                'main_timeframe': main_tf,
                'analyzed_timeframes': list(confluence_scores.keys()),
                'confluence_scores': confluence_scores,
                'structural_strength_scores': strength_scores,
                'final_confluence_score': final_score,
                'analysis_quality': self._determine_analysis_quality(confluence_scores, strength_scores),
                'enhancement_factors': {
                    'timeframe_diversity': len(confluence_scores),
                    'avg_confluence': sum(confluence_scores.values()) / len(confluence_scores) if confluence_scores else 0,
                    'avg_strength': sum(strength_scores.values()) / len(strength_scores) if strength_scores else 0
                },
                'timestamp': datetime.now()
            }
            
            self._log_debug(f"📊 TODO #3 Enhanced: {symbol} analysis complete")
            
        except Exception as e:
            self._log_debug(f"Warning logging enhanced analysis: {e}")

    def _determine_analysis_quality(self, confluence_scores: Dict[str, float], 
                                  strength_scores: Dict[str, float]) -> str:
        """🎯 TODO #3: Determinar calidad del análisis"""
        try:
            timeframe_count = len(confluence_scores)
            avg_confluence = sum(confluence_scores.values()) / len(confluence_scores) if confluence_scores else 0
            avg_strength = sum(strength_scores.values()) / len(strength_scores) if strength_scores else 0
            
            if timeframe_count >= 3 and avg_confluence > 0.7 and avg_strength > 0.6:
                return 'ENTERPRISE_GRADE'
            elif timeframe_count >= 2 and avg_confluence > 0.6:
                return 'HIGH_QUALITY'
            elif timeframe_count >= 2:
                return 'STANDARD'
            else:
                return 'BASIC'
                
        except:
            return 'LOW'  # Safe default for confluence quality

    def _detect_fair_value_gaps(self, candles) -> bool:
        """💎 Detecta Fair Value Gaps"""
        try:
            # Implementación básica de FVG detection
            fvg_found = False
            
            for i in range(2, len(candles)):
                # Verificar FVG alcista
                prev_high = candles.iloc[i-2]['high']
                current_low = candles.iloc[i]['low']
                
                if current_low > prev_high:  # Gap alcista
                    gap_size = current_low - prev_high
                    if gap_size >= self.fvg_min_gap:
                        fvg = FairValueGap(
                            fvg_type=FVGType.BULLISH_FVG,
                            high_price=current_low,
                            low_price=prev_high,
                            origin_candle=i-1,
                            filled_percentage=0.0,
                            is_mitigated=False,
                            mitigation_candle=None,
                            narrative=f"Bullish FVG: {gap_size:.5f} gap",
                            timestamp=datetime.now()
                        )
                        self.detected_fvgs.append(fvg)
                        fvg_found = True
                
                # Verificar FVG bajista
                prev_low = candles.iloc[i-2]['low']
                current_high = candles.iloc[i]['high']
                
                if current_high < prev_low:  # Gap bajista
                    gap_size = prev_low - current_high
                    if gap_size >= self.fvg_min_gap:
                        fvg = FairValueGap(
                            fvg_type=FVGType.BEARISH_FVG,
                            high_price=prev_low,
                            low_price=current_high,
                            origin_candle=i-1,
                            filled_percentage=0.0,
                            is_mitigated=False,
                            mitigation_candle=None,
                            narrative=f"Bearish FVG: {gap_size:.5f} gap",
                            timestamp=datetime.now()
                        )
                        self.detected_fvgs.append(fvg)
                        fvg_found = True
            
            # Limpiar FVGs antiguos
            self.detected_fvgs = self.detected_fvgs[-20:]
            
            if fvg_found:
                self._log_debug(f"💎 FVGs detectados: {len(self.detected_fvgs)}")
            
            return fvg_found
            
        except Exception as e:
            self._log_error(f"Error detectando FVGs: {e}")
            return False

    def _detect_order_blocks(self, candles) -> bool:
        """📦 Detecta Order Blocks"""
        try:
            if len(candles) < 15:
                return False
            
            ob_found = False
            recent = candles.tail(20)
            
            for i in range(5, len(recent) - 5):
                candle = recent.iloc[i]
                
                # Verificar reacción fuerte desde este nivel
                reaction_score = self._calculate_reaction_strength(recent, i)
                
                if reaction_score > self.ob_reaction_threshold:
                    # Determinar tipo de Order Block
                    if candle['close'] > candle['open']:  # Bullish candle
                        ob_type = OrderBlockType.BULLISH_OB
                        narrative = f"Bullish Order Block: reacción {reaction_score:.4f}"
                    else:  # Bearish candle
                        ob_type = OrderBlockType.BEARISH_OB
                        narrative = f"Bearish Order Block: reacción {reaction_score:.4f}"
                    
                    order_block = OrderBlock(
                        ob_type=ob_type,
                        high_price=candle['high'],
                        low_price=candle['low'],
                        origin_candle=i,
                        reaction_strength=reaction_score,
                        is_tested=False,
                        test_count=0,
                        narrative=narrative,
                        timestamp=datetime.now()
                    )
                    
                    self.detected_order_blocks.append(order_block)
                    ob_found = True
                    self._log_debug(f"📦 Order Block detectado: {ob_type.value}")
            
            # Limpiar Order Blocks antiguos
            self.detected_order_blocks = self.detected_order_blocks[-10:]
            
            return ob_found
            
        except Exception as e:
            self._log_error(f"Error detectando Order Blocks: {e}")
            return False

    def _calculate_reaction_strength(self, candles, candle_index: int) -> float:
        """⚡ Calcula la fuerza de reacción desde un nivel"""
        try:
            if candle_index < 2 or candle_index >= len(candles) - 2:
                return 0.0
            
            candle = candles.iloc[candle_index]
            
            # Verificar reacción en velas posteriores
            reaction_strength = 0.0
            for i in range(candle_index + 1, min(candle_index + 5, len(candles))):
                next_candle = candles.iloc[i]
                
                # Medir distancia del precio de reacción
                if candle['close'] > candle['open']:  # Bullish OB
                    distance = abs(next_candle['low'] - candle['high'])
                else:  # Bearish OB
                    distance = abs(next_candle['high'] - candle['low'])
                
                # Convertir distancia a score
                price_range = candle['high'] - candle['low']
                if price_range > 0:
                    reaction_strength += distance / price_range
            
            return reaction_strength / 4  # Normalizar
            
        except Exception as e:
            self._log_error(f"Error calculando reacción: {e}")
            return 0.0

    def _generate_structure_signal(self, **kwargs) -> MarketStructureSignal:
        """🎯 Genera señal de estructura de mercado"""
        try:
            structure_type = kwargs.get('structure_type', StructureType.CONSOLIDATION)  # Consolidación más específico
            confidence = kwargs.get('confidence', 0.0)
            break_level = kwargs.get('break_level', 0.0)
            target_level = kwargs.get('target_level', 0.0)
            confluence_score = kwargs.get('confluence_score', 0.0)
            fvg_present = kwargs.get('fvg_present', False)
            ob_present = kwargs.get('ob_present', False)
            swing_highs = kwargs.get('swing_highs', [])
            swing_lows = kwargs.get('swing_lows', [])
            timeframe = kwargs.get('timeframe', 'M15')
            
            # Determinar dirección
            if structure_type in [StructureType.BOS_BULLISH, StructureType.CHOCH_BULLISH]:
                direction = TradingDirection.BUY
            elif structure_type in [StructureType.BOS_BEARISH, StructureType.CHOCH_BEARISH]:
                direction = TradingDirection.SELL
            else:
                direction = TradingDirection.NEUTRAL
            
            # Generar narrativa
            narrative = self._generate_narrative(structure_type, confidence, fvg_present, ob_present)
            
            # Crear señal
            signal = MarketStructureSignal(
                structure_type=structure_type,
                confidence=confidence,
                direction=direction,
                break_level=break_level,
                target_level=target_level,
                narrative=narrative,
                timestamp=datetime.now(),
                timeframe=timeframe,
                confluence_score=confluence_score,
                fvg_present=fvg_present,
                order_block_present=ob_present,
                swing_highs=swing_highs,
                swing_lows=swing_lows,
                sic_stats={'version': 'v6.0', 'analyzer': 'market_structure'}
            )
            
            return signal
            
        except Exception as e:
            self._log_error(f"Error generando señal: {e}")
            raise

    def _generate_narrative(self, structure_type: StructureType, confidence: float, fvg_present: bool, ob_present: bool) -> str:
        """📖 Genera narrativa descriptiva de la estructura"""
        narratives = {
            StructureType.BOS_BULLISH: f"Break of Structure Alcista detectado con {confidence:.1f}% confianza",
            StructureType.BOS_BEARISH: f"Break of Structure Bajista detectado con {confidence:.1f}% confianza",
            StructureType.CHOCH_BULLISH: f"Change of Character Alcista detectado con {confidence:.1f}% confianza",
            StructureType.CHOCH_BEARISH: f"Change of Character Bajista detectado con {confidence:.1f}% confianza",
            StructureType.CONSOLIDATION: f"Consolidación detectada con {confidence:.1f}% confianza",
        }
        
        base_narrative = narratives.get(structure_type, f"Estructura {structure_type.value} - {confidence:.1f}% confianza")
        
        # Agregar confluencias
        confluences = []
        if fvg_present:
            confluences.append("FVG presente")
        if ob_present:
            confluences.append("Order Block detectado")
        
        if confluences:
            base_narrative += f". Confluencias: {', '.join(confluences)}"
        
        return base_narrative

    def _update_structure_state(self, structure_type: StructureType, signal: MarketStructureSignal):
        """📝 Actualiza estado interno de estructura"""
        try:
            # Actualizar tendencia actual
            if structure_type in [StructureType.BOS_BULLISH, StructureType.CHOCH_BULLISH]:
                self.current_trend = TradingDirection.BUY
            elif structure_type in [StructureType.BOS_BEARISH, StructureType.CHOCH_BEARISH]:
                self.current_trend = TradingDirection.SELL
            
            # Agregar a historia
            self.structure_history.append(signal)
            
            # Mantener solo últimas 50 señales
            self.structure_history = self.structure_history[-50:]
            
        except Exception as e:
            self._log_error(f"Error actualizando estado: {e}")

    def get_current_structure_state(self) -> Dict[str, Any]:
        """📊 Obtiene estado actual de la estructura"""
        return {
            'current_trend': self.current_trend.value,
            'detected_fvgs': len(self.detected_fvgs),
            'detected_order_blocks': len(self.detected_order_blocks),
            'structure_history_count': len(self.structure_history),
            'last_analysis': self.structure_history[-1].timestamp if self.structure_history else None
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """📈 Obtiene métricas de performance"""
        if not self._performance_metrics:
            return {'total_analyses': 0}
        
        return {
            'total_analyses': len(self._performance_metrics),
            'avg_analysis_time': sum(m['analysis_time'] for m in self._performance_metrics) / len(self._performance_metrics),
            'avg_confidence': sum(m['confidence'] for m in self._performance_metrics) / len(self._performance_metrics),
            'recent_analyses': self._performance_metrics[-5:]
        }

    # ===============================
    # MÉTODOS DE LOGGING
    # ===============================
    
    def _log_info(self, message: str):
        """ℹ️ Log de información"""
        enviar_senal_log("INFO", f"[MarketStructureAnalyzer v6.0] {message}", __name__, "market_structure")
    
    def _log_warning(self, message: str):
        """⚠️ Log de advertencia"""
        enviar_senal_log("WARNING", f"[MarketStructureAnalyzer v6.0] {message}", __name__, "market_structure")
    
    def _log_error(self, message: str):
        """❌ Log de error"""
        enviar_senal_log("ERROR", f"[MarketStructureAnalyzer v6.0] {message}", __name__, "market_structure")
    
    def _log_debug(self, message: str):
        """🐛 Log de debug"""
        enviar_senal_log("DEBUG", f"[MarketStructureAnalyzer v6.0] {message}", __name__, "market_structure")


# ===============================
# FACTORY FUNCTIONS
# ===============================

def get_market_structure_analyzer(config: Optional[Dict[str, Any]] = None) -> MarketStructureAnalyzer:
    """
    🏭 Factory function para crear MarketStructureAnalyzer v6.0
    
    Args:
        config: Configuración opcional del analizador
        
    Returns:
        Instancia configurada de MarketStructureAnalyzer
    """
    default_config = {
        'enable_debug': True,
        'use_multi_timeframe': True,
        'enable_cache': True,
        'min_confidence': 70.0,
        'structure_lookback': 50,
        'swing_window': 5,
        'fvg_min_gap': 0.0005,
        'ob_reaction_threshold': 0.001
    }
    
    if config:
        default_config.update(config)
    
    return MarketStructureAnalyzer(config=default_config)


# ===============================
# TEST Y VALIDACIÓN
# ===============================

if __name__ == "__main__":
    print("🧪 Testing MarketStructureAnalyzer v6.0 Enterprise...")
    
    try:
        # Crear analizador con configuración de test
        test_config = {
            'enable_debug': True,
            'use_multi_timeframe': False,  # Simplificar para test
            'min_confidence': 60.0
        }
        
        analyzer = get_market_structure_analyzer(test_config)
        print("✅ MarketStructureAnalyzer creado exitosamente")
        
        # Test de análisis básico
        signal = analyzer.analyze_market_structure(
            symbol="EURUSD",
            timeframe="M15",
            lookback_days=3
        )
        
        if signal:
            print(f"✅ Señal generada: {signal.structure_type.value} - {signal.confidence:.1f}%")
        else:
            print("ℹ️ Sin señales estructurales detectadas")
        
        # Test de estado
        state = analyzer.get_current_structure_state()
        print(f"✅ Estado actual: {state}")
        
        # Test de métricas
        metrics = analyzer.get_performance_metrics()
        print(f"✅ Métricas: {metrics}")
        
        print("🎯 Test de MarketStructureAnalyzer v6.0 completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
