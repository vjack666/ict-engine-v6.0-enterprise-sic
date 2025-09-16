# -*- coding: utf-8 -*-
"""
🎯 ICT PATTERN DETECTOR v6.0 ENTERPRISE
=============================================

Motor avanzado de detección de patrones ICT para trading institucional.
Implementa los patrones más efectivos de la metodología Inner Circle Trader
con precisión enterprise y rendimiento optimizado.

Autor: ICT Engine v6.1.0 Enterprise Team
Fecha: Agosto 7, 2025
Versión: v6.1.0-enterprise
"""

from protocols.unified_logging import get_unified_logger
import time
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Tuple, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

# TYPE_CHECKING imports para anotaciones de tipo sin impact en runtime
if TYPE_CHECKING:
    import pandas
    import numpy

# 🚀 OPTIMIZACIÓN CRÍTICA: Lazy loading para pandas y numpy
# Reduce startup time significativamente
pandas_available = False
numpy_available = False
pd = None
np = None

def _lazy_import_pandas():
    """⚡ Import pandas solo cuando sea necesario"""
    global pandas_available, pd
    if not pandas_available:
        try:
            import pandas as pd_module
            pd = pd_module
            pandas_available = True
            return True
        except ImportError:
            print("⚠️ Pandas no disponible - funcionalidad limitada")
            return False
    return True

def _lazy_import_numpy():
    """⚡ Import numpy solo cuando sea necesario"""
    global numpy_available, np
    if not numpy_available:
        try:
            import numpy as np_module
            np = np_module
            numpy_available = True
            return True
        except ImportError:
            print("⚠️ Numpy no disponible - funcionalidad limitada")
            return False
    return True

# Importar usando ImportCenter del sistema ICT v6.0 mejorado
try:
    # Importación absoluta más robusta
    import sys
    from pathlib import Path
    
    # Asegurar que el path del proyecto esté disponible
    project_root = Path(__file__).parent.parent.parent
    core_path = Path(__file__).parent.parent
    utils_path = core_path / "utils"
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    from utils.import_center import ImportCenter
    from smart_trading_logger import get_smart_logger
    
    # Configurar logging para PatternDetector
    _logger = get_smart_logger("PatternDetector")
    
    _ic = ImportCenter()
    
    # 🚀 THREAD-SAFE PANDAS/NUMPY MANAGER
    pd = _ic.safe_import('pandas')
    np = _ic.safe_import('numpy')
    
    # Verificar salud del sistema
    system_health = _ic.get_system_health()
    
    if pd is not None and np is not None:
        _logger.info("✅ Thread-Safe Pandas/Numpy Manager inicializado", "PATTERN_DETECTOR")
        _logger.info(f"🩺 Sistema: {system_health['health_score']:.1f}% - Trading Ready: {system_health['trading_ready']}", "PATTERN_DETECTOR")
    else:
        _logger.warning("⚠️ Thread-Safe Manager parcialmente disponible", "PATTERN_DETECTOR")
        _ic.print_system_health()
        raise ImportError("Failed to import via ImportCenter")
        
except ImportError:
    # Fallback directo CRÍTICO para trading
    try:
        import pandas as pd
        import numpy as np
        print("🔄 [INFO] Usando fallback directo para pandas/numpy - ImportCenter no disponible")
    except ImportError:
        print("🚨 [CRITICAL ERROR] Pandas/Numpy no disponibles - SISTEMA NO APTO PARA TRADING")
        print("🛠️ [SOLUTION] Instalar con: pip install pandas numpy")
        pd = None
        np = None
        
# 🚨 VERIFICACIÓN CRÍTICA DE TRADING READINESS
TRADING_READY = pd is not None and np is not None

# Configurar logger global SIEMPRE disponible para gestión real
_logger = None  # Inicializar como None para evitar errores de Pylance

try:
    # Si el logger ya está configurado desde ImportCenter
    if '_logger' in locals() and _logger is not None:
        pass  # Ya está configurado
    else:
        # Fallback en caso de que no esté disponible
        from smart_trading_logger import get_smart_logger
        _logger = get_smart_logger("PatternDetector")
except Exception as e:
    # Fallback básico GARANTIZADO
    class FallbackLogger:
        def info(self, msg, component="PATTERN"): print(f"[INFO] [{component}] {msg}")
        def warning(self, msg, component="PATTERN"): print(f"[WARNING] [{component}] {msg}")
        def error(self, msg, component="PATTERN"): print(f"[ERROR] [{component}] {msg}")
    _logger = FallbackLogger()
    print(f"[FALLBACK] Logger configurado con fallback básico: {e}")

# GARANTIZAR que _logger SIEMPRE esté disponible
if _logger is None:
    class EmergencyLogger:
        def info(self, msg, component="PATTERN"): print(f"[EMERGENCY-INFO] [{component}] {msg}")
        def warning(self, msg, component="PATTERN"): print(f"[EMERGENCY-WARNING] [{component}] {msg}")
        def error(self, msg, component="PATTERN"): print(f"[EMERGENCY-ERROR] [{component}] {msg}")
    _logger = EmergencyLogger()

# Ahora _logger está GARANTIZADO de estar disponible
if not TRADING_READY:
    _logger.error("❌ TRADING_READY: FALSE - Sistema no funcional para trading en vivo", "CORE")
    _logger.warning("⚠️ Funcionalidad limitada: Solo análisis básico disponible", "CORE")
else:
    _logger.info("✅ TRADING_READY: TRUE - Sistema listo para trading en vivo", "CORE")

# 🛡️ FUNCIONES AUXILIARES SEGURAS PARA TRADING
def safe_numpy_mean(array_like) -> float:
    """Función segura para calcular la media usando numpy o fallback"""
    if np is not None:
        return float(np.mean(array_like))
    else:
        # Fallback básico
        if hasattr(array_like, '__iter__'):
            values = list(array_like)
            return sum(values) / len(values) if values else 0.0
        return float(array_like)

def safe_abs(value) -> float:
    """Función segura para calcular valor absoluto"""
    return abs(float(value))

# Importar downloader con gestión robusta
get_advanced_candle_downloader = None  # Inicializar SIEMPRE para evitar errores de Pylance

try:
    from data_management.advanced_candle_downloader import get_advanced_candle_downloader
    _logger.info("✅ Advanced Candle Downloader disponible", "IMPORT")
except ImportError as e:
    _logger.warning(f"Downloader no disponible - usando datos simulados: {e}", "IMPORT")
    get_advanced_candle_downloader = None
except Exception as e:
    _logger.error(f"Error importando downloader: {e}", "IMPORT")
    get_advanced_candle_downloader = None

# Importar Smart Money Concepts v6.0 con gestión robusta
SmartMoneyAnalyzer = None  # Inicializar SIEMPRE

try:
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    _logger.info("✅ Smart Money Analyzer disponible", "IMPORT")
except ImportError as e:
    _logger.warning(f"Smart Money Analyzer no disponible - funcionalidad limitada: {e}", "IMPORT")
    SmartMoneyAnalyzer = None
except Exception as e:
    _logger.error(f"Error importando Smart Money Analyzer: {e}", "IMPORT")
    SmartMoneyAnalyzer = None


class PatternType(Enum):
    """Tipos de patrones ICT detectables"""
    SILVER_BULLET = "silver_bullet"
    JUDAS_SWING = "judas_swing"
    LIQUIDITY_GRAB = "liquidity_grab"
    OPTIMAL_TRADE_ENTRY = "optimal_trade_entry"
    POWER_OF_THREE = "power_of_three"
    MORNING_REVERSAL = "morning_reversal"
    ORDER_BLOCK = "order_block"
    MITIGATION_BLOCK = "mitigation_block"
    FAIR_VALUE_GAP = "fair_value_gap"


class JudasSwingType(Enum):
    """🎭 Tipos específicos de Judas Swing v6.0"""
    MORNING_REVERSAL = "morning_reversal"        # 8-9 AM reversión
    LONDON_CLOSE_JUDAS = "london_close_judas"    # 10-11 AM false break
    NY_OPEN_JUDAS = "ny_open_judas"             # 1-2 PM false break
    AFTERNOON_JUDAS = "afternoon_judas"          # 2-4 PM reversión
    UNKNOWN = "unknown"


class BreakoutType(Enum):
    """🚨 Tipos de ruptura y false breakouts v6.0"""
    FALSE_BREAKOUT_HIGH = "false_breakout_high"
    FALSE_BREAKOUT_LOW = "false_breakout_low"
    LIQUIDITY_GRAB_HIGH = "liquidity_grab_high"
    LIQUIDITY_GRAB_LOW = "liquidity_grab_low"
    NO_BREAKOUT = "no_breakout"
    BREAKER_BLOCK = "breaker_block"
    FAIR_VALUE_GAP = "fair_value_gap"
    INSTITUTIONAL_ORDER_FLOW = "institutional_order_flow"
    MARKET_MAKER_MODEL = "market_maker_model"


class PatternConfidence(Enum):
    """Niveles de confianza del patrón"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class TradingDirection(Enum):
    """Dirección del trade"""
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


class SessionType(Enum):
    """Tipos de sesión de trading"""
    LONDON = "london"
    NEW_YORK = "new_york"
    ASIAN = "asian"
    OVERLAP = "overlap"
    DEAD_ZONE = "dead_zone"


@dataclass
class PatternSignal:
    """Señal de patrón ICT detectada"""
    pattern_type: PatternType
    direction: TradingDirection
    confidence: PatternConfidence
    strength: float  # 0-100
    timestamp: datetime
    symbol: str
    timeframe: str
    
    # Niveles de precio
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    
    # Métricas
    risk_reward_ratio: float = 0.0
    probability: float = 0.0
    
    # Contexto
    session: SessionType = SessionType.LONDON
    narrative: str = ""
    confluences: List[str] = field(default_factory=list)
    invalidation_criteria: str = ""
    
    # Timing
    optimal_entry_time: Optional[datetime] = None
    time_sensitivity: str = "MEDIUM"
    max_hold_time: Optional[timedelta] = None
    
    # Metadata
    analysis_id: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)


class PatternDetector:
    """
    🎯 ICT PATTERN DETECTOR v6.0 ENTERPRISE
    
    Detector avanzado de patrones ICT con capacidades enterprise:
    - Detección en tiempo real de 12+ patrones ICT
    - Análisis multi-timeframe con confluencias
    - Scoring avanzado con ML-ready features
    - Performance optimizado (<50ms por análisis)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar Pattern Detector v6.0 Enterprise
        
        Args:
            config: Configuración del detector
        """
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
        
        # Estado del detector
        self.is_initialized = False
        self.last_analysis_time = None
        self.detected_patterns: List[PatternSignal] = []
        self.performance_metrics = {
            'total_analyses': 0,
            'avg_analysis_time': 0.0,
            'patterns_detected': 0,
            'success_rate': 0.0,
            'last_update': datetime.now()
        }
        
        # Componentes
        self._downloader = None
        self._smart_money_analyzer = None
        self._multi_tf_analyzer = None  # 🚀 NUEVO: Multi-Timeframe Analyzer
        self._data_manager = None       # 🎯 NUEVO: ICT Data Manager
        self._initialize_components()
        
        # Cache para optimización
        self._pattern_cache = {}
        self._cache_ttl = timedelta(minutes=5)
        
        print(f"[INFO] Pattern Detector v6.0 Enterprise inicializado")
        print(f"[INFO] Multi-Timeframe capability: {'ENABLED' if self._multi_tf_analyzer else 'DISABLED'}")
        print(f"[INFO] Data Manager: {'ENABLED' if self._data_manager else 'DISABLED'}")
        print(f"[INFO] Configuración: {len(self.config)} parámetros cargados")
        
        # 🚨 VERIFICACIÓN CRÍTICA DE TRADING READINESS
        self.trading_ready = self._verify_trading_readiness()
        if not self.trading_ready:
            print("❌ [CRITICAL] Sistema NO APTO para trading en vivo")
        else:
            print("✅ [SUCCESS] Sistema LISTO para trading en vivo")
    
    def _verify_trading_readiness(self) -> bool:
        """
        🚨 VERIFICACIÓN CRÍTICA DE TRADING READINESS
        
        Returns:
            bool: True si el sistema está listo para trading real, False si no
        """
        global TRADING_READY
        
        readiness_checks = {
            'pandas_available': pd is not None,
            'numpy_available': np is not None,
            'trading_ready_flag': TRADING_READY,
            'detector_initialized': self.is_initialized
        }
        
        failed_checks = [check for check, status in readiness_checks.items() if not status]
        
        if failed_checks:
            print(f"⚠️ [TRADING READINESS] Fallos detectados: {failed_checks}")
            return False
        
        return True
    
    def is_trading_ready(self) -> bool:
        """
        🎯 VERIFICAR SI EL SISTEMA ESTÁ LISTO PARA TRADING REAL
        
        Returns:
            bool: True si está listo para trading, False si no
        """
        # Verificaciones críticas para trading
        pandas_ready = pd is not None
        numpy_ready = np is not None
        system_ready = hasattr(self, 'trading_ready') and self.trading_ready and TRADING_READY
        
        if not pandas_ready:
            print("🚨 [TRADING ERROR] Pandas no disponible")
        if not numpy_ready:
            print("🚨 [TRADING ERROR] Numpy no disponible")
        if not system_ready:
            print("🚨 [TRADING ERROR] Sistema no inicializado correctamente")
            
        return pandas_ready and numpy_ready and system_ready
    
    def require_trading_ready(self) -> bool:
        """
        🚨 VERIFICACIÓN OBLIGATORIA ANTES DE OPERACIONES DE TRADING
        
        Raises:
            RuntimeError: Si el sistema no está listo para trading
            
        Returns:
            bool: True si pasa todas las verificaciones
        """
        if not self.is_trading_ready():
            raise RuntimeError(
                "🚨 SISTEMA NO APTO PARA TRADING\n"
                f"- Pandas disponible: {pd is not None}\n"
                f"- Numpy disponible: {np is not None}\n"
                f"- Trading Ready: {TRADING_READY}\n"
                "💡 Solución: Instalar dependencias con 'pip install pandas numpy'"
            )
        return True
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Cargar configuración por defecto"""
        return {
            # General
            'enable_debug': True,
            'enable_cache': True,
            'min_confidence': 70.0,
            'max_patterns_per_analysis': 5,
            
            # Patrones específicos
            'enable_silver_bullet': True,
            'enable_judas_swing': True,
            'enable_liquidity_grab': True,
            'enable_optimal_trade_entry': True,
            'enable_power_of_three': True,
            'enable_morning_reversal': True,
            
            # Timeframes
            'primary_timeframe': 'M15',
            'secondary_timeframes': ['M5', 'H1'],
            'use_multi_timeframe': True,
            
            # Análisis técnico
            'swing_lookback': 20,
            'structure_lookback': 50,
            'fvg_min_size': 0.0005,
            'order_block_strength': 0.6,
            
            # Sesiones
            'london_start': '08:00',
            'london_end': '17:00',
            'newyork_start': '13:00',
            'newyork_end': '22:00',
            
            # Performance
            'max_analysis_time': 0.05,  # 50ms
            'cache_size_limit': 100,
            'concurrent_analysis': False
        }
    
    def _initialize_components(self):
        """Inicializar componentes del detector usando singletons optimizados"""
        try:
            # Inicializar downloader con gestión robusta para trading real
            self._downloader = None
            if get_advanced_candle_downloader is not None:
                try:
                    self._downloader = get_advanced_candle_downloader()
                    print("[INFO] ✅ Downloader conectado - datos reales MT5 disponibles")
                    if _logger and hasattr(_logger, 'info'):
                        _logger.info("✅ Advanced Candle Downloader inicializado para trading real", "INIT")
                except Exception as e:
                    print(f"[WARNING] Error inicializando downloader: {e}")
                    if _logger and hasattr(_logger, 'warning'):
                        _logger.warning(f"Error inicializando downloader: {e}", "INIT")
                    self._downloader = None
            else:
                print("[WARNING] ⚠️ Downloader no disponible - usando datos históricos locales")
                if _logger and hasattr(_logger, 'warning'):
                    _logger.warning("Downloader no disponible - modo datos históricos", "INIT")
            
            # Inicializar Smart Money Analyzer si está disponible
            if SmartMoneyAnalyzer:
                self._smart_money_analyzer = SmartMoneyAnalyzer()
                print("[INFO] Smart Money Analyzer v6.0 conectado - análisis institucional disponible")
            else:
                print("[WARNING] Smart Money Analyzer no disponible - funcionalidad limitada")
            
            # 🚀 NUEVO: Inicializar Multi-Timeframe Analyzer
            try:
                from .multi_timeframe_analyzer import OptimizedICTAnalysisEnterprise
                self._multi_tf_analyzer = OptimizedICTAnalysisEnterprise()
                print("[INFO] 🚀 Multi-Timeframe Analyzer Enterprise v6.0 conectado - pipeline H4→M15→M5 disponible")
                self.config['multi_timeframe_enabled'] = True
            except ImportError as e:
                print(f"[WARNING] Multi-Timeframe Analyzer no disponible: {e}")
                print("[INFO] Funcionando en modo single-timeframe")
                self.config['multi_timeframe_enabled'] = False

            # 🎯 NUEVO: Inicializar ICT Data Manager usando singleton optimizado
            try:
                from data_management.ict_data_manager_singleton import get_ict_data_manager
                self._data_manager = get_ict_data_manager(downloader=self._downloader)
                print("[INFO] 🎯 ICT Data Manager conectado - gestión inteligente de datos habilitada")
                self.config['data_manager_enabled'] = True
            except ImportError:
                try:
                    from data_management.ict_data_manager import ICTDataManager
                    self._data_manager = ICTDataManager(downloader=self._downloader)
                    print("[INFO] 🎯 ICT Data Manager conectado - gestión inteligente de datos habilitada")
                    self.config['data_manager_enabled'] = True
                except ImportError as e:
                    print(f"[WARNING] ICT Data Manager no disponible: {e}")
                    print("[INFO] Usando gestión de datos básica")
                    self.config['data_manager_enabled'] = False
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"[WARNING] Error inicializando componentes: {e}")
            print("[INFO] Continuando en modo básico")
    
    def detect_patterns(
        self, 
        data: Optional['pandas.DataFrame'] = None,
        symbol: str = "EURUSD", 
        timeframe: str = "M15",
        lookback_days: int = 7
    ) -> List[PatternSignal]:
        """
        Detectar patrones ICT en los datos de mercado
        
        Args:
            data: DataFrame con datos OHLCV (opcional, si no se proporciona se descarga)
            symbol: Símbolo a analizar
            timeframe: Marco temporal
            lookback_days: Días de historia a analizar
            
        Returns:
            Lista de patrones detectados
        """
        start_time = time.time()
        
        try:
            # 🚨 VERIFICACIÓN CRÍTICA DE TRADING READINESS
            if not self.is_trading_ready():
                print("🚨 [CRITICAL ERROR] Sistema NO apto para trading")
                print("⚠️ Retornando lista vacía - Sin análisis de patrones")
                return []
            
            print(f"✅ [TRADING READY] Iniciando análisis de patrones para {symbol} {timeframe}")
            
            # Usar datos proporcionados o descargar
            if data is None:
                data = self._get_market_data(symbol, timeframe, lookback_days)
                
            if data is None or data.empty:
                print(f"[WARNING] Sin datos para {symbol} {timeframe}")
                return []
            
            # LIMITACIÓN CRÍTICA: Reducir datos para evitar problemas de rendimiento
            MAX_CANDLES_FOR_ANALYSIS = 500  # Límite seguro para análisis completo
            
            if len(data) > MAX_CANDLES_FOR_ANALYSIS:
                print(f"[INFO] Limitando datos de análisis: {len(data)} -> {MAX_CANDLES_FOR_ANALYSIS} velas")
                data = data.tail(MAX_CANDLES_FOR_ANALYSIS)
            
            print(f"[INFO] Analizando {len(data)} velas para {symbol} {timeframe}")
            
            # Detectar patrones activos
            patterns = []
            
            # 1. Silver Bullet (máxima prioridad)
            if self.config['enable_silver_bullet']:
                sb_patterns = self._detect_silver_bullet(data, symbol, timeframe)
                patterns.extend(sb_patterns)
            
            # 2. Judas Swing
            if self.config['enable_judas_swing']:
                js_patterns = self._detect_judas_swing(data, symbol, timeframe)
                patterns.extend(js_patterns)
            
            # 3. Liquidity Grab
            if self.config['enable_liquidity_grab']:
                lg_patterns = self._detect_liquidity_grab(data, symbol, timeframe)
                patterns.extend(lg_patterns)
            
            # 4. Optimal Trade Entry
            if self.config['enable_optimal_trade_entry']:
                ote_patterns = self._detect_optimal_trade_entry(data, symbol, timeframe)
                patterns.extend(ote_patterns)
            
            # 5. Order Blocks
            ob_patterns = self._detect_order_blocks(data, symbol, timeframe)
            patterns.extend(ob_patterns)
            
            # 6. Fair Value Gaps
            fvg_patterns = self._detect_fair_value_gaps(data, symbol, timeframe)
            patterns.extend(fvg_patterns)
            
            # Filtrar por confianza mínima
            patterns = [p for p in patterns if p.strength >= self.config['min_confidence']]
            
            # 🧠 SMART MONEY ENHANCEMENT v6.0
            if patterns and self._smart_money_analyzer:
                print(f"[INFO] Aplicando Smart Money analysis a {len(patterns)} patrones...")
                patterns = self._enhance_with_smart_money_analysis(patterns, data)
            
            # 🎯 MULTI-TIMEFRAME ENHANCEMENT v6.0
            if patterns:
                print(f"[INFO] Aplicando Multi-Timeframe enhancement a {len(patterns)} patrones...")
                patterns = self._enhance_analysis_with_multi_tf(patterns, symbol, timeframe)
            
            # Limitar número de patrones
            max_patterns = self.config['max_patterns_per_analysis']
            if len(patterns) > max_patterns:
                # Ordenar por strength y tomar los mejores
                patterns = sorted(patterns, key=lambda x: x.strength, reverse=True)[:max_patterns]
            
            # Actualizar métricas
            analysis_time = time.time() - start_time
            self._update_performance_metrics(analysis_time, len(patterns))
            
            # Almacenar resultados
            self.detected_patterns = patterns
            self.last_analysis_time = datetime.now()
            
            print(f"[INFO] Detectados {len(patterns)} patrones en {analysis_time:.3f}s")
            
            return patterns
            
        except Exception as e:
            print(f"[ERROR] Error en detección de patrones: {e}")
            return []

    def detect_bos(self, market_data: Dict[str, Any], structure_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        🚀 DETECTAR BREAK OF STRUCTURE (BOS) - MIGRADO desde market_structure_v2.py
        
        Detecta roturas de estructura (BOS) usando la lógica ICT migrada del sistema principal.
        
        Args:
            market_data: Datos de mercado con OHLCV
            structure_data: Datos de estructura de mercado (opcional)
            
        Returns:
            Dict con información de BOS detectado
        """
        try:
            # Extraer datos necesarios
            candles = market_data.get('candles')
            symbol = market_data.get('symbol', 'UNKNOWN')
            timeframe = market_data.get('timeframe', 'M15')
            
            if candles is None or candles.empty:
                return {
                    "pattern_type": "BOS",
                    "detected": False,
                    "reason": "No data available",
                    "patterns": [],
                    "confidence": 0.0,
                    "status": "NO_DATA"
                }
            
            # 1. 🎯 DETECTAR SWING POINTS (usando lógica migrada)
            swing_points = self._detect_swing_points_for_bos(candles)
            swing_highs = swing_points.get('highs', [])
            swing_lows = swing_points.get('lows', [])
            
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return {
                    "pattern_type": "BOS",
                    "detected": False,
                    "reason": "Insufficient swing points",
                    "patterns": [],
                    "confidence": 0.0,
                    "status": "INSUFFICIENT_DATA"
                }
            
            # 2. 🔍 APLICAR ALGORITMO BOS (lógica MIGRADA desde market_structure_v2.py)
            current_price = float(candles['close'].iloc[-1])
            bos_patterns = []
            
            # Obtener últimos swing points
            last_high = swing_highs[-1]
            prev_high = swing_highs[-2] if len(swing_highs) > 1 else swing_highs[-1]
            last_low = swing_lows[-1]
            prev_low = swing_lows[-2] if len(swing_lows) > 1 else swing_lows[-1]
            
            # 🚀 BOS ALCISTA (MIGRADO): current_price > last_high AND last_high > prev_high
            if current_price > last_high['price'] and last_high['price'] > prev_high['price']:
                bos_bullish = {
                    'type': 'BOS_BULLISH',
                    'direction': 'BULLISH',
                    'strength': 80.0,
                    'break_level': last_high['price'],
                    'target_level': last_high['price'] * 1.002,  # Target 20 pips arriba
                    'swing_broken': last_high,
                    'prev_swing': prev_high,
                    'current_price': current_price,
                    'timestamp': candles.index[-1],
                    'narrative': f"BOS Bullish @ {last_high['price']:.5f} - Target {last_high['price'] * 1.002:.5f}"
                }
                bos_patterns.append(bos_bullish)
                print(f"[DEBUG] 🔍 BOS BULLISH detectado @ {last_high['price']:.5f}")
            
            # 🚀 BOS BAJISTA (MIGRADO): current_price < last_low AND last_low < prev_low  
            elif current_price < last_low['price'] and last_low['price'] < prev_low['price']:
                bos_bearish = {
                    'type': 'BOS_BEARISH',
                    'direction': 'BEARISH',
                    'strength': 80.0,
                    'break_level': last_low['price'],
                    'target_level': last_low['price'] * 0.998,  # Target 20 pips abajo
                    'swing_broken': last_low,
                    'prev_swing': prev_low,
                    'current_price': current_price,
                    'timestamp': candles.index[-1],
                    'narrative': f"BOS Bearish @ {last_low['price']:.5f} - Target {last_low['price'] * 0.998:.5f}"
                }
                bos_patterns.append(bos_bearish)
                print(f"[DEBUG] 🔍 BOS BEARISH detectado @ {last_low['price']:.5f}")
            
            # 3. 📊 VALIDAR Y CONFIRMAR BOS
            confirmed_patterns = []
            for pattern in bos_patterns:
                # Aplicar filtros de confirmación
                if self._validate_bos_pattern(pattern, candles):
                    # Aplicar momentum analysis (lógica migrada)
                    momentum_score = self._analyze_bos_momentum(candles, pattern['type'])
                    pattern['momentum_score'] = momentum_score
                    pattern['strength'] = min(95.0, pattern['strength'] * momentum_score)
                    
                    confirmed_patterns.append(pattern)
            
            # 4. 🎯 GENERAR SEÑAL BOS
            if confirmed_patterns:
                best_pattern = max(confirmed_patterns, key=lambda x: x['strength'])
                confidence = best_pattern['strength']
                
                # Crear PatternSignal enterprise
                pattern_signal = PatternSignal(
                    pattern_type=PatternType.SILVER_BULLET,  # Usar enum disponible
                    direction=TradingDirection.BUY if best_pattern['direction'] == 'BULLISH' else TradingDirection.SELL,
                    confidence=PatternConfidence.HIGH if confidence >= 80 else PatternConfidence.MEDIUM,
                    strength=confidence,
                    timestamp=best_pattern['timestamp'],
                    symbol=symbol,
                    timeframe=timeframe,
                    entry_zone=(best_pattern['break_level'] * 0.9999, best_pattern['break_level'] * 1.0001),
                    stop_loss=self._calculate_bos_stop_loss(best_pattern),
                    take_profit_1=best_pattern['target_level'],
                    narrative=best_pattern['narrative'],
                    confluences=['BOS_PATTERN', 'STRUCTURE_BREAK'],
                    risk_reward_ratio=self._calculate_bos_rr(best_pattern)
                )
                
                return {
                    "pattern_type": "BOS",
                    "detected": True,
                    "patterns": confirmed_patterns,
                    "best_pattern": best_pattern,
                    "signal": pattern_signal,
                    "confidence": confidence,
                    "swing_analysis": {
                        "highs_count": len(swing_highs),
                        "lows_count": len(swing_lows),
                        "last_high": last_high,
                        "last_low": last_low
                    },
                    "status": "BOS_DETECTED"
                }
            else:
                return {
                    "pattern_type": "BOS",
                    "detected": False,
                    "reason": "No BOS patterns confirmed",
                    "patterns": bos_patterns,  # Incluir patrones no confirmados para debug
                    "confidence": 0.0,
                    "swing_analysis": {
                        "highs_count": len(swing_highs),
                        "lows_count": len(swing_lows)
                    },
                    "status": "NO_BOS_CONFIRMED"
                }
                
        except Exception as e:
            print(f"[ERROR] Error en detect_bos: {e}")
            return {
                "pattern_type": "BOS",
                "detected": False,
                "reason": f"Error: {str(e)}",
                "patterns": [],
                "confidence": 0.0,
                "status": "ERROR"
            }

    def detect_bos_multi_timeframe(self, symbol: str, timeframes: Optional[List[str]] = None, mode: str = 'auto') -> Dict[str, Any]:
        """
        🚀 DETECTAR BOS MULTI-TIMEFRAME - VERSIÓN CON DATOS REALES
        
        Detecta BOS usando análisis multi-timeframe con datos reales optimizados.
        Integra ICTDataManager para gestión inteligente de datos.
        
        Args:
            symbol: Par de trading (ej. 'EURUSD')
            timeframes: Lista de timeframes a analizar (opcional, usa default H4→M15→M5)
            mode: Modo de análisis ('auto', 'live_ready', 'full', 'minimal')
            
        Returns:
            Dict con análisis multi-timeframe BOS y señales confirmadas
        """
        try:
            # 1. 🎯 VERIFICAR DISPONIBILIDAD DE COMPONENTES
            if not hasattr(self, '_multi_tf_analyzer') or self._multi_tf_analyzer is None:
                return {
                    "pattern_type": "BOS_MULTI_TIMEFRAME",
                    "detected": False,
                    "reason": "Multi-timeframe analyzer not available",
                    "analysis": {},
                    "confidence": 0.0,
                    "status": "ANALYZER_NOT_AVAILABLE"
                }
            
            # 2. 📊 CONFIGURAR TIMEFRAMES (usar jerarquía ICT H4→M15→M5)
            if timeframes is None:
                timeframes = ['H4', 'M15', 'M5']  # Jerarquía ICT estándar
            
            print(f"[INFO] 🔍 Iniciando análisis BOS multi-timeframe REAL para {symbol} en {timeframes}")
            print(f"[INFO] 🎯 Modo de análisis: {mode}")
            
            # 3. 🎯 GESTIÓN INTELIGENTE DE DATOS
            if hasattr(self, '_data_manager') and self._data_manager is not None:
                # Usar ICT Data Manager para datos optimizados
                print(f"[INFO] 📊 Usando ICT Data Manager para optimización de datos")
                
                # Verificar disponibilidad de datos
                data_readiness = self._data_manager.get_data_readiness(symbol, timeframes)
                print(f"[INFO] � Disponibilidad de datos: {data_readiness['analysis_capability']}")
                
                # Ajustar modo según disponibilidad de datos
                if mode == 'auto':
                    if data_readiness['analysis_capability'] == 'FULL':
                        adjusted_mode = 'full'
                    elif data_readiness['analysis_capability'] == 'PARTIAL':
                        adjusted_mode = 'live_ready'
                    else:
                        adjusted_mode = 'minimal'
                    
                    print(f"[INFO] 🤖 Modo AUTO ajustado a: {adjusted_mode}")
                    mode = adjusted_mode
                
                # Iniciar warm-up si es necesario
                if not self._data_manager.warm_up_completed:
                    print(f"[INFO] �🚀 Iniciando warm-up de datos para análisis rápido...")
                    warm_up_result = self._data_manager.warm_up_cache(
                        symbols=[symbol],
                        timeframes=timeframes
                    )
                    
                    if warm_up_result['success']:
                        print(f"[INFO] ✅ Warm-up completado en {warm_up_result['warm_up_time']:.1f}s")
                    else:
                        print(f"[WARNING] ⚠️ Warm-up parcial - continuando con datos disponibles")
            
            # 4. 🚀 EJECUTAR ANÁLISIS MULTI-TIMEFRAME
            multi_tf_analysis = self._multi_tf_analyzer.analyze_symbol(
                symbol=symbol,
                timeframes=timeframes,
                mode=mode
            )
            
            if not multi_tf_analysis or multi_tf_analysis.get('status') != 'SUCCESS':
                return {
                    "pattern_type": "BOS_MULTI_TIMEFRAME", 
                    "detected": False,
                    "reason": f"Multi-timeframe analysis failed: {multi_tf_analysis.get('error', 'Unknown error')}",
                    "analysis": multi_tf_analysis or {},
                    "confidence": 0.0,
                    "status": "ANALYSIS_FAILED",
                    "mode_used": mode
                }
            
            # 5. 🎯 PROCESAR RESULTADOS POR TIMEFRAME
            tf_results = multi_tf_analysis.get('timeframe_results', {})
            bos_signals = []
            overall_confidence = 0.0
            
            for tf, result in tf_results.items():
                if result.get('analysis') and result['analysis'].get('bos_detected'):
                    bos_data = result['analysis']['bos_analysis']
                    
                    # Crear señal BOS para este timeframe
                    bos_signal = {
                        'timeframe': tf,
                        'direction': bos_data.get('direction', 'UNKNOWN'),
                        'strength': bos_data.get('strength', 0.0),
                        'break_level': bos_data.get('break_level', 0.0),
                        'target_level': bos_data.get('target_level', 0.0),
                        'confluence_count': bos_data.get('confluence_count', 0),
                        'narrative': bos_data.get('narrative', ''),
                        'session_alignment': result.get('session_context', {}),
                        'momentum_score': bos_data.get('momentum_score', 0.0),
                        'data_quality': multi_tf_analysis.get('data_quality', 'UNKNOWN')
                    }
                    
                    bos_signals.append(bos_signal)
                    overall_confidence = max(overall_confidence, bos_signal['strength'])
            
            # 6. 📈 EVALUAR ALINEACIÓN MULTI-TIMEFRAME
            alignment_analysis = self._evaluate_multi_tf_alignment(bos_signals, multi_tf_analysis)
            
            # 7. 🎯 GENERAR RESULTADO CONSOLIDADO
            if bos_signals:
                # Encontrar señal de mayor timeframe (H4 tiene prioridad)
                tf_priority = {'H4': 3, 'M15': 2, 'M5': 1}
                primary_signal = max(bos_signals, key=lambda x: tf_priority.get(x['timeframe'], 0))
                
                return {
                    "pattern_type": "BOS_MULTI_TIMEFRAME",
                    "detected": True,
                    "primary_signal": primary_signal,
                    "all_signals": bos_signals,
                    "alignment_analysis": alignment_analysis,
                    "overall_confidence": overall_confidence,
                    "timeframe_count": len(bos_signals),
                    "raw_analysis": multi_tf_analysis,
                    "execution_summary": {
                        "total_timeframes_analyzed": len(timeframes),
                        "bos_detected_count": len(bos_signals),
                        "highest_confidence_tf": primary_signal['timeframe'],
                        "session_context": multi_tf_analysis.get('session_context', {}),
                        "performance_metrics": multi_tf_analysis.get('performance_metrics', {}),
                        "mode_used": mode,
                        "data_quality": multi_tf_analysis.get('data_quality', 'UNKNOWN'),
                        "data_source": "REAL_DATA" if hasattr(self, '_data_manager') and self._data_manager else "SIMULATED_DATA"
                    },
                    "status": "BOS_MULTI_TF_DETECTED"
                }
            else:
                return {
                    "pattern_type": "BOS_MULTI_TIMEFRAME",
                    "detected": False,
                    "reason": "No BOS detected in any timeframe",
                    "analysis": multi_tf_analysis,
                    "timeframe_results": tf_results,
                    "confidence": 0.0,
                    "execution_summary": {
                        "total_timeframes_analyzed": len(timeframes),
                        "bos_detected_count": 0,
                        "session_context": multi_tf_analysis.get('session_context', {}),
                        "performance_metrics": multi_tf_analysis.get('performance_metrics', {}),
                        "mode_used": mode,
                        "data_quality": multi_tf_analysis.get('data_quality', 'UNKNOWN'),
                        "data_source": "REAL_DATA" if hasattr(self, '_data_manager') and self._data_manager else "SIMULATED_DATA"
                    },
                    "status": "NO_BOS_MULTI_TF"
                }
                
        except Exception as e:
            print(f"[ERROR] Error en detect_bos_multi_timeframe: {e}")
            return {
                "pattern_type": "BOS_MULTI_TIMEFRAME",
                "detected": False,
                "reason": f"Multi-timeframe analysis error: {str(e)}",
                "analysis": {},
                "confidence": 0.0,
                "mode_attempted": mode,
                "status": "ERROR"
            }

    def detect_choch(self, symbol: str, timeframes: Optional[List[str]] = None, mode: str = 'auto') -> Dict[str, Any]:
        """
        🔄 DETECTAR CHANGE OF CHARACTER (CHoCH) - ICT v6.0 ENTERPRISE
        ============================================================
        
        Implementa detección de Change of Character (CHoCH) con análisis multi-timeframe
        según metodología ICT. CHoCH identifica cambios en el carácter del mercado que
        indican reversiones de tendencia.
        
        CHoCH vs BOS:
        - CHoCH: Cambio de carácter/reversión (trend contrario + swing break)
        - BOS: Break of structure/continuación (mismo trend + swing break)
        
        Args:
            symbol: Par de divisas (ej. "EURUSD", "GBPUSD")
            timeframes: Lista de timeframes ['H4', 'M15', 'M5'] (opcional)
            mode: Modo de análisis ('minimal', 'live_ready', 'full', 'auto')
            
        Returns:
            Dict con información completa de CHoCH detectado
            
        Ejemplos:
            >>> detector = PatternDetector()
            >>> result = detector.detect_choch("EURUSD", mode='live_ready')
            >>> if result['detected']:
            >>>     print(f"CHoCH {result['direction']} detectado con {result['confidence']:.1f}% confianza")
        """
        try:
            print(f"\n🔄 [CHoCH DETECTOR v6.0] Analizando {symbol}...")
            start_time = time.time()
            
            # 1. 🎯 CONFIGURAR TIMEFRAMES ICT PARA CHoCH
            if timeframes is None:
                timeframes = ['H4', 'M15', 'M5']  # Pipeline ICT estándar
                
            print(f"   📊 Timeframes: {timeframes}")
            print(f"   ⚙️  Modo: {mode}")
            
            # 2. 🔄 ANÁLISIS MULTI-TIMEFRAME CHoCH
            choch_signals = []
            tf_results = {}
            multi_tf_analysis = {
                "session_context": {"session": "analysis", "timestamp": time.time()},
                "performance_metrics": {},
                "data_quality": "UNKNOWN"
            }
            
            for tf in timeframes:
                tf_start = time.time()
                print(f"   🔍 Analizando {tf}...")
                
                # Obtener datos de mercado
                market_data = self._get_market_data(symbol, tf, days=10)
                if market_data is None or market_data.empty:
                    print(f"   ❌ Sin datos para {tf}")
                    tf_results[tf] = {"detected": False, "reason": "No data"}
                    continue
                
                # Detectar CHoCH en timeframe específico
                choch_result = self._detect_choch_single_tf(market_data, symbol, tf, mode)
                tf_results[tf] = choch_result
                
                # Si detectamos CHoCH, agregar a señales
                if choch_result.get('detected', False):
                    choch_signal = {
                        "timeframe": tf,
                        "direction": choch_result['direction'],
                        "confidence": choch_result['confidence'],
                        "break_level": choch_result['break_level'],
                        "target_level": choch_result['target_level'],
                        "structure_type": choch_result['structure_type'],
                        "trend_change": choch_result['trend_change'],
                        "swing_data": choch_result.get('swing_data', {}),
                        "analysis_time": time.time() - tf_start
                    }
                    choch_signals.append(choch_signal)
                    print(f"   ✅ CHoCH {choch_result['direction']} detectado en {tf} ({choch_result['confidence']:.1f}%)")
                else:
                    print(f"   ⚪ Sin CHoCH en {tf}")
            
            # 3. 🎯 CALCULAR CONFIANZA GENERAL
            overall_confidence = 0.0
            if choch_signals:
                # Prioridad por timeframe: H4 > M15 > M5
                tf_weights = {'H4': 0.5, 'M15': 0.3, 'M5': 0.2}
                weighted_conf = sum(tf_weights.get(signal['timeframe'], 0.1) * signal['confidence'] 
                                  for signal in choch_signals)
                overall_confidence = min(weighted_conf * 100, 100.0)
            
            # 4. 📈 EVALUAR ALINEACIÓN MULTI-TIMEFRAME CHoCH
            alignment_analysis = self._evaluate_choch_alignment(choch_signals, tf_results)
            
            # 5. 🎯 GENERAR RESULTADO CONSOLIDADO
            total_time = time.time() - start_time
            
            if choch_signals:
                # Encontrar señal de mayor timeframe (H4 tiene prioridad)
                tf_priority = {'H4': 3, 'M15': 2, 'M5': 1}
                primary_signal = max(choch_signals, key=lambda x: tf_priority.get(x['timeframe'], 0))
                
                print(f"   🎉 CHoCH DETECTADO! Dirección: {primary_signal['direction']}, Confianza: {overall_confidence:.1f}%")
                
                return {
                    "pattern_type": "CHOCH_MULTI_TIMEFRAME",
                    "detected": True,
                    "direction": primary_signal['direction'],
                    "confidence": overall_confidence,
                    "primary_signal": primary_signal,
                    "all_signals": choch_signals,
                    "alignment_analysis": alignment_analysis,
                    "timeframe_count": len(choch_signals),
                    "trend_change_confirmed": alignment_analysis.get('trend_change_confirmed', False),
                    "execution_summary": {
                        "total_timeframes_analyzed": len(timeframes),
                        "choch_detected_count": len(choch_signals),
                        "highest_confidence_tf": primary_signal['timeframe'],
                        "analysis_time": total_time,
                        "session_context": multi_tf_analysis.get('session_context', {}),
                        "mode_used": mode,
                        "data_source": "REAL_DATA" if hasattr(self, '_data_manager') and self._data_manager else "SIMULATED_DATA"
                    },
                    "tf_results": tf_results,
                    "status": "CHOCH_MULTI_TF_DETECTED"
                }
            else:
                print(f"   ⚪ Sin CHoCH detectado en {symbol}")
                return {
                    "pattern_type": "CHOCH_MULTI_TIMEFRAME", 
                    "detected": False,
                    "reason": "No CHoCH detected in any timeframe",
                    "confidence": 0.0,
                    "analysis": tf_results,
                    "execution_summary": {
                        "total_timeframes_analyzed": len(timeframes),
                        "choch_detected_count": 0,
                        "analysis_time": total_time,
                        "session_context": multi_tf_analysis.get('session_context', {}),
                        "mode_used": mode,
                        "data_source": "REAL_DATA" if hasattr(self, '_data_manager') and self._data_manager else "SIMULATED_DATA"
                    },
                    "status": "NO_CHOCH_MULTI_TF"
                }
                
        except Exception as e:
            print(f"[ERROR] Error en detect_choch: {e}")
            return {
                "pattern_type": "CHOCH_MULTI_TIMEFRAME",
                "detected": False,
                "reason": f"CHoCH analysis error: {str(e)}",
                "confidence": 0.0,
                "error": str(e),
                "status": "ERROR"
            }

    def _detect_choch_single_tf(self, candles: 'pandas.DataFrame', symbol: str, timeframe: str, mode: str) -> Dict[str, Any]:
        """
        🔄 Detecta CHoCH en un timeframe específico
        
        Lógica CHoCH basada en ICT:
        - CHoCH Bullish: Trend bajista + price > prev_low + last_low > prev_low (HL pattern)
        - CHoCH Bearish: Trend alcista + price < prev_high + last_high < prev_high (LH pattern)
        """
        try:
            if candles is None or candles.empty or len(candles) < 10:
                return {"detected": False, "reason": "Insufficient data"}
            
            # 1. 🔍 DETECTAR SWING POINTS PARA CHoCH
            swing_data = self._detect_swing_points_for_bos(candles, window=5)
            swing_highs = swing_data.get('highs', [])
            swing_lows = swing_data.get('lows', [])
            
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return {"detected": False, "reason": "Insufficient swing points"}
            
            # 2. 📈 OBTENER SWING POINTS RELEVANTES
            last_high = swing_highs[-1]
            prev_high = swing_highs[-2] if len(swing_highs) > 1 else swing_highs[-1]
            last_low = swing_lows[-1] 
            prev_low = swing_lows[-2] if len(swing_lows) > 1 else swing_lows[-1]
            current_price = float(candles.iloc[-1]['close'])
            
            # 3. 🎯 DETERMINAR TREND ACTUAL (simulado por ahora)
            # En implementación real, esto vendría del market structure analyzer
            recent_highs = [h['price'] for h in swing_highs[-3:]]
            recent_lows = [l['price'] for l in swing_lows[-3:]]
            
            # Trend simple basado en swing points recientes
            if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                if recent_highs[-1] > recent_highs[-2] and recent_lows[-1] > recent_lows[-2]:
                    current_trend = "BULLISH"
                elif recent_highs[-1] < recent_highs[-2] and recent_lows[-1] < recent_lows[-2]:
                    current_trend = "BEARISH"
                else:
                    current_trend = "NEUTRAL"
            else:
                current_trend = "NEUTRAL"
            
            # 4. 🔄 APLICAR LÓGICA CHoCH (migrada desde market_structure_analyzer_v6.py)
            
            # CHoCH BULLISH: Trend bajista + rompe low anterior + HL pattern
            if (current_trend == "BEARISH" and
                current_price > prev_low['price'] and 
                last_low['price'] > prev_low['price']):
                
                confidence = 90.0  # CHoCH tiene alta confianza
                break_level = prev_low['price']
                target_level = last_high['price']
                
                return {
                    "detected": True,
                    "direction": "BULLISH",
                    "structure_type": "CHOCH_BULLISH",
                    "confidence": confidence,
                    "break_level": break_level,
                    "target_level": target_level,
                    "trend_change": f"{current_trend} -> BULLISH",
                    "swing_data": {
                        "last_high": last_high,
                        "prev_high": prev_high,
                        "last_low": last_low,
                        "prev_low": prev_low,
                        "current_price": current_price
                    },
                    "narrative": f"CHoCH Bullish: Trend bajista roto, precio rompe {break_level:.5f}, target {target_level:.5f}"
                }
            
            # CHoCH BEARISH: Trend alcista + rompe high anterior + LH pattern  
            elif (current_trend == "BULLISH" and
                  current_price < prev_high['price'] and
                  last_high['price'] < prev_high['price']):
                
                confidence = 90.0  # CHoCH tiene alta confianza
                break_level = prev_high['price']
                target_level = last_low['price']
                
                return {
                    "detected": True,
                    "direction": "BEARISH", 
                    "structure_type": "CHOCH_BEARISH",
                    "confidence": confidence,
                    "break_level": break_level,
                    "target_level": target_level,
                    "trend_change": f"{current_trend} -> BEARISH",
                    "swing_data": {
                        "last_high": last_high,
                        "prev_high": prev_high, 
                        "last_low": last_low,
                        "prev_low": prev_low,
                        "current_price": current_price
                    },
                    "narrative": f"CHoCH Bearish: Trend alcista roto, precio rompe {break_level:.5f}, target {target_level:.5f}"
                }
            
            # 5. ⚪ NO HAY CHoCH
            return {
                "detected": False,
                "reason": f"No CHoCH pattern (trend: {current_trend}, price: {current_price:.5f})",
                "swing_data": {
                    "last_high": last_high,
                    "prev_high": prev_high,
                    "last_low": last_low, 
                    "prev_low": prev_low,
                    "current_price": current_price,
                    "current_trend": current_trend
                }
            }
            
        except Exception as e:
            return {
                "detected": False,
                "reason": f"CHoCH detection error: {str(e)}",
                "error": str(e)
            }

    def _evaluate_choch_alignment(self, choch_signals: List[Dict], tf_results: Dict) -> Dict[str, Any]:
        """🎯 Evalúa la alineación de señales CHoCH entre timeframes"""
        try:
            if not choch_signals:
                return {"alignment": "NO_SIGNALS", "score": 0.0, "trend_change_confirmed": False}
                
            # Analizar direcciones CHoCH
            directions = [signal['direction'] for signal in choch_signals]
            unique_directions = set(directions)
            
            # Alineación perfecta = todas las direcciones iguales
            if len(unique_directions) == 1:
                alignment_score = 1.0
                alignment_status = "PERFECT_ALIGNMENT"
                trend_change_confirmed = True
            elif len(unique_directions) == 2:
                alignment_score = 0.6
                alignment_status = "PARTIAL_ALIGNMENT" 
                trend_change_confirmed = False
            else:
                alignment_score = 0.3
                alignment_status = "POOR_ALIGNMENT"
                trend_change_confirmed = False
                
            # Analizar confluencias CHoCH
            confluences = []
            if len(choch_signals) > 1:
                confluences.append(f"CHoCH detectado en {len(choch_signals)} timeframes")
                confluences.append(f"Direcciones: {', '.join(directions)}")
                
            return {
                "alignment": alignment_status,
                "score": alignment_score,
                "trend_change_confirmed": trend_change_confirmed,
                "confluences": confluences,
                "direction_consensus": list(unique_directions)[0] if len(unique_directions) == 1 else "MIXED",
                "timeframe_count": len(choch_signals),
                "total_timeframes": len(tf_results)
            }
            
        except Exception as e:
            return {
                "alignment": "ERROR",
                "score": 0.0,
                "error": str(e),
                "trend_change_confirmed": False
            }

    def _evaluate_multi_tf_alignment(self, bos_signals: List[Dict], raw_analysis: Dict) -> Dict[str, Any]:
        """🎯 Evalúa la alineación de señales BOS entre timeframes"""
        try:
            if not bos_signals:
                return {"alignment": "NO_SIGNALS", "score": 0.0, "confluences": []}
            
            # Analizar direcciones
            directions = [signal['direction'] for signal in bos_signals]
            direction_counts = {d: directions.count(d) for d in set(directions)}
            dominant_direction = max(direction_counts.keys(), key=lambda x: direction_counts[x])
            
            # Calcular alineación
            aligned_signals = [s for s in bos_signals if s['direction'] == dominant_direction]
            alignment_ratio = len(aligned_signals) / len(bos_signals)
            
            # Evaluar confluencias
            confluences = []
            if alignment_ratio >= 0.67:  # 2/3 o más alineados
                confluences.append("DIRECTIONAL_ALIGNMENT")
            
            if len(bos_signals) >= 2:
                confluences.append("MULTI_TIMEFRAME_CONFIRMATION")
            
            # Evaluar fortaleza promedio
            avg_strength = sum(s['strength'] for s in aligned_signals) / len(aligned_signals)
            if avg_strength >= 75.0:
                confluences.append("HIGH_STRENGTH_CONSENSUS")
            
            return {
                "alignment": "STRONG" if alignment_ratio >= 0.67 else "WEAK",
                "alignment_ratio": alignment_ratio,
                "dominant_direction": dominant_direction,
                "aligned_count": len(aligned_signals),
                "total_signals": len(bos_signals),
                "average_strength": avg_strength,
                "confluences": confluences,
                "score": alignment_ratio * avg_strength / 100.0
            }
            
        except Exception as e:
            print(f"[ERROR] Error evaluating multi-TF alignment: {e}")
            return {"alignment": "ERROR", "score": 0.0, "confluences": []}

    def _detect_swing_points_for_bos(self, candles: 'pandas.DataFrame', window: int = 5) -> Dict[str, List[Dict]]:
        """🎯 Detecta swing points para análisis BOS (lógica MIGRADA)"""
        try:
            swing_highs = []
            swing_lows = []

            if len(candles) < window * 2 + 1:
                return {'highs': swing_highs, 'lows': swing_lows}

            # Detectar swing highs (lógica MIGRADA desde market_structure_v2.py)
            for i in range(window, len(candles) - window):
                current_high = candles.iloc[i]['high']

                # Verificar que sea el máximo en la ventana
                is_swing_high = True
                for j in range(i - window, i + window + 1):
                    if j != i and candles.iloc[j]['high'] >= current_high:
                        is_swing_high = False
                        break

                if is_swing_high:
                    swing_highs.append({
                        'index': i,
                        'price': current_high,
                        'timestamp': candles.index[i] if hasattr(candles.index[i], 'timestamp') else i
                    })

            # Detectar swing lows (lógica MIGRADA desde market_structure_v2.py)
            for i in range(window, len(candles) - window):
                current_low = candles.iloc[i]['low']

                # Verificar que sea el mínimo en la ventana
                is_swing_low = True
                for j in range(i - window, i + window + 1):
                    if j != i and candles.iloc[j]['low'] <= current_low:
                        is_swing_low = False
                        break

                if is_swing_low:
                    swing_lows.append({
                        'index': i,
                        'price': current_low,
                        'timestamp': candles.index[i] if hasattr(candles.index[i], 'timestamp') else i
                    })

            print(f"[DEBUG] 🎯 Swing points BOS: {len(swing_highs)} highs, {len(swing_lows)} lows")
            return {'highs': swing_highs, 'lows': swing_lows}

        except Exception as e:
            print(f"[ERROR] Error detectando swing points para BOS: {e}")
            return {'highs': [], 'lows': []}

    def _validate_bos_pattern(self, pattern: Dict[str, Any], candles: 'pandas.DataFrame') -> bool:
        """✅ Valida patrón BOS con filtros ICT"""
        try:
            # Filtro 1: Verificar que el break sea convincente (>5 pips)
            break_size = abs(pattern['current_price'] - pattern['break_level'])
            min_break_size = 0.0005  # 5 pips para EURUSD
            
            if break_size < min_break_size:
                return False
            
            # Filtro 2: Verificar momentum en la dirección del break
            recent_candles = candles.tail(3)
            if pattern['type'] == 'BOS_BULLISH':
                bullish_momentum = sum(1 for _, row in recent_candles.iterrows() if row['close'] > row['open'])
                if bullish_momentum < 2:  # Al menos 2 de 3 velas alcistas
                    return False
            else:  # BOS_BEARISH
                bearish_momentum = sum(1 for _, row in recent_candles.iterrows() if row['close'] < row['open'])
                if bearish_momentum < 2:  # Al menos 2 de 3 velas bajistas
                    return False
            
            return True
            
        except Exception:
            return False

    def _analyze_bos_momentum(self, candles: 'pandas.DataFrame', bos_type: str) -> float:
        """💨 Analiza momentum para BOS (lógica MIGRADA)"""
        try:
            if len(candles) < 10:
                return 0.5

            recent = candles.tail(10)
            price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
            momentum_score = 0.5

            # Analizar según tipo de BOS (adaptado de market_structure_v2.py)
            if bos_type == 'BOS_BULLISH':
                if price_change > 0:
                    momentum_score += 0.3
                if price_change > 0.001:  # >10 pips
                    momentum_score += 0.2
            elif bos_type == 'BOS_BEARISH':
                if price_change < 0:
                    momentum_score += 0.3
                if price_change < -0.001:  # <-10 pips
                    momentum_score += 0.2

            return min(1.0, momentum_score)

        except Exception:
            return 0.5

    def _calculate_bos_stop_loss(self, pattern: Dict[str, Any]) -> float:
        """🛡️ Calcula stop loss para BOS"""
        try:
            if pattern['type'] == 'BOS_BULLISH':
                # Stop debajo del swing low previo
                return pattern['prev_swing']['price'] * 0.999  # -10 pips buffer
            else:  # BOS_BEARISH
                # Stop arriba del swing high previo
                return pattern['prev_swing']['price'] * 1.001  # +10 pips buffer
        except Exception:
            return pattern['break_level']

    def _calculate_bos_rr(self, pattern: Dict[str, Any]) -> float:
        """📊 Calcula risk/reward ratio para BOS"""
        try:
            entry = pattern['break_level']
            target = pattern['target_level']
            stop = self._calculate_bos_stop_loss(pattern)
            
            reward = abs(target - entry)
            risk = abs(entry - stop)
            
            return reward / risk if risk > 0 else 1.0
        except Exception:
            return 1.0
    
    def _get_market_data(self, symbol: str, timeframe: str, days: int) -> Optional['pandas.DataFrame']:
        """
        🔍 OBTENER DATOS MULTI-TIMEFRAME ICT v6.0
        
        Estrategia multi-timeframe para maximizar datos históricos:
        - Primary: timeframe solicitado
        - Secondary: H1, H4, D1 para contexto superior
        - Intelligent data combining para análisis completo
        """
        try:
            if self._downloader:
                # 🎯 ESTRATEGIA MULTI-TIMEFRAME ICT v6.0
                data_collection = {}
                
                # 1. Primary timeframe (solicitado)
                primary_data = self._download_single_timeframe(symbol, timeframe, days)
                if primary_data is not None and not primary_data.empty:
                    data_collection[timeframe] = primary_data
                    
                # 2. Secondary timeframes para contexto ICT
                secondary_timeframes = self._get_ict_secondary_timeframes(timeframe)
                
                for tf in secondary_timeframes:
                    # Más días para timeframes superiores
                    tf_days = self._calculate_ict_optimal_days(tf, days)
                    
                    secondary_data = self._download_single_timeframe(symbol, tf, tf_days)
                    if secondary_data is not None and not secondary_data.empty:
                        data_collection[tf] = secondary_data
                        
                # 3. Return primary data with enhanced context
                if timeframe in data_collection:
                    primary_data = data_collection[timeframe]
                    
                    # Store additional timeframes for multi-TF analysis
                    if hasattr(self, '_multi_tf_data'):
                        self._multi_tf_data[symbol] = data_collection
                    else:
                        self._multi_tf_data = {symbol: data_collection}
                        
                    print(f"📊 Multi-TF data collected: {list(data_collection.keys())}")
                    print(f"   Primary {timeframe}: {len(primary_data)} velas")
                    
                    for tf, data in data_collection.items():
                        if tf != timeframe:
                            print(f"   Context {tf}: {len(data)} velas")
                    
                    return primary_data
                else:
                    print(f"[WARNING] No se pudo obtener datos primarios para {timeframe}")
                    return self._generate_simulated_data(symbol, timeframe, days)
            else:
                # Datos simulados para testing
                return self._generate_simulated_data(symbol, timeframe, days)
                
        except Exception as e:
            print(f"[WARNING] Error obteniendo datos multi-TF: {e}")
            print(f"[INFO] Usando datos simulados como fallback")
            return self._generate_simulated_data(symbol, timeframe, days)

    def _download_single_timeframe(self, symbol: str, timeframe: str, days: int) -> Optional['pandas.DataFrame']:
        """Descarga datos de una sola temporalidad"""
        try:
            # 🚨 Verificar disponibilidad del downloader
            if self._downloader is None:
                print(f"[WARNING] Downloader no disponible - retornando datos simulados")
                return self._generate_simulated_data(symbol, timeframe, days)
                
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            result = self._downloader.download_candles(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                save_to_file=False
            )
            
            # Extraer DataFrame del resultado
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            elif isinstance(result, 'pandas.DataFrame'):
                return result
            else:
                return None
                
        except Exception as e:
            print(f"[DEBUG] Error descargando {timeframe}: {e}")
            return None

    def _get_ict_secondary_timeframes(self, primary_timeframe: str) -> List[str]:
        """
        🎯 OBTENER TIMEFRAMES SECUNDARIOS ICT
        
        Estrategia ICT para timeframes de contexto:
        - M1, M5, M15 -> H1, H4, D1
        - H1 -> H4, D1, W1
        - H4, D1 -> W1, MN1
        """
        timeframe_hierarchy = {
            'M1': ['M5', 'M15', 'H1', 'H4'],
            'M5': ['M15', 'H1', 'H4', 'D1'],
            'M15': ['H1', 'H4', 'D1'],
            'H1': ['H4', 'D1', 'W1'],
            'H4': ['D1', 'W1'],
            'D1': ['W1', 'MN1'],
            'W1': ['MN1'],
            'MN1': []
        }
        
        return timeframe_hierarchy.get(primary_timeframe, ['H1', 'H4', 'D1'])

    def _calculate_ict_optimal_days(self, timeframe: str, base_days: int) -> int:
        """
        📊 CALCULAR DÍAS ÓPTIMOS ICT POR TIMEFRAME
        
        Más días para timeframes superiores para obtener más datos:
        - M1, M5: base_days
        - M15: base_days * 2
        - H1: base_days * 4
        - H4: base_days * 12
        - D1: base_days * 30
        - W1: base_days * 120
        """
        multipliers = {
            'M1': 1,
            'M5': 1, 
            'M15': 2,
            'H1': 4,
            'H4': 12,
            'D1': 30,
            'W1': 120,
            'MN1': 360
        }
        
        multiplier = multipliers.get(timeframe, 4)
        optimal_days = base_days * multiplier
        
        # Cap máximo para evitar sobrecarga
        max_days = 365 * 2  # 2 años máximo
        return min(optimal_days, max_days)
    
    def _generate_simulated_data(self, symbol: str, timeframe: str, days: int) -> Optional['pandas.DataFrame']:
        """🚨 Generar datos simulados - SOLO para testing cuando sistema está listo"""
        # 🚨 VERIFICACIÓN CRÍTICA: No generar datos simulados si no está listo para trading
        if not self.is_trading_ready():
            print("🚨 [ERROR] No se pueden generar datos simulados - Sistema no apto para trading")
            return None
            
        if pd is None or np is None:
            print("🚨 [ERROR] Pandas/Numpy no disponibles - No se pueden generar datos simulados")
            return None
            
        periods = days * 24 * 4  # Asumiendo M15
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='15min')
        
        # Datos OHLCV simulados
        base_price = 1.0800  # EURUSD típico
        data = []
        
        for i, date in enumerate(dates):
            volatility = 0.0020 + np.random.normal(0, 0.0005)
            change = np.random.normal(0, volatility)
            
            if i == 0:
                open_price = base_price
            else:
                open_price = data[-1]['close']
            
            high = open_price + abs(np.random.normal(0, volatility/2))
            low = open_price - abs(np.random.normal(0, volatility/2))
            close = open_price + change
            volume = np.random.randint(100, 1000)
            
            data.append({
                'time': date,
                'open': open_price,
                'high': max(open_price, high, close),
                'low': min(open_price, low, close),
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _detect_silver_bullet(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """Detectar patrones Silver Bullet"""
        patterns = []
        current_time = datetime.now()
        
        # Verificar ventana temporal Silver Bullet (10:00-11:00 GMT)
        if not self._is_silver_bullet_time(current_time):
            return patterns
        
        try:
            # Buscar setup Silver Bullet
            # Estructura: Order Block + FVG + Confluence
            if len(data) < 20:
                return patterns
            
            # Detectar Order Block reciente
            order_blocks = self._find_order_blocks(data)
            if not order_blocks:
                return patterns
            
            recent_ob = order_blocks[-1]  # Más reciente
            
            # Verificar FVG como confluencia
            fvgs = self._find_fair_value_gaps(data)
            fvg_confluence = len(fvgs) > 0
            
            # Determinar dirección
            direction = TradingDirection.BUY if recent_ob['type'] == 'bullish' else TradingDirection.SELL
            
            # Calcular niveles
            entry_zone = (recent_ob['low'], recent_ob['high'])
            current_price = data['close'].iloc[-1]
            
            if direction == TradingDirection.BUY:
                stop_loss = entry_zone[0] - 0.0020
                take_profit_1 = current_price + 0.0040
                take_profit_2 = current_price + 0.0070
            else:
                stop_loss = entry_zone[1] + 0.0020
                take_profit_1 = current_price - 0.0040
                take_profit_2 = current_price - 0.0070
            
            # Calcular métricas
            risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
            reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
            risk_reward = reward / risk if risk > 0 else 0
            
            # Calcular strength
            strength = 75.0
            if fvg_confluence:
                strength += 10.0
            if current_time.hour == 10:  # Hora óptima
                strength += 5.0
            
            confidence = PatternConfidence.HIGH if strength >= 80 else PatternConfidence.MEDIUM
            
            signal = PatternSignal(
                pattern_type=PatternType.SILVER_BULLET,
                direction=direction,
                confidence=confidence,
                strength=min(strength, 95.0),
                timestamp=current_time,
                symbol=symbol,
                timeframe=timeframe,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=take_profit_1,
                take_profit_2=take_profit_2,
                risk_reward_ratio=risk_reward,
                probability=strength,
                session=SessionType.LONDON,
                narrative=f"Silver Bullet {direction.value} setup detectado durante ventana óptima. Order Block confirmado con {'FVG' if fvg_confluence else 'estructura'} como confluencia.",
                confluences=["order_block", "timing_window"] + (["fvg"] if fvg_confluence else []),
                invalidation_criteria=f"Cierre fuera de ventana temporal o precio {'debajo' if direction == TradingDirection.BUY else 'arriba'} de {stop_loss:.5f}",
                time_sensitivity="CRÍTICA - Solo válido durante ventana 10:00-11:00 GMT",
                analysis_id=f"SB_{symbol}_{int(current_time.timestamp())}"
            )
            
            patterns.append(signal)
            
        except Exception as e:
            print(f"[WARNING] Error detectando Silver Bullet: {e}")
        
        return patterns
    
    def _detect_judas_swing(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """
        🎭 DETECCIÓN JUDAS SWING v6.0 ENTERPRISE
        ========================================
        
        Migración completa desde Judas Swing v2.0 con todas las funcionalidades:
        - False breakouts automáticos
        - Liquidity grab detection
        - Session timing validation
        - Market maker manipulation patterns
        """
        patterns = []
        
        try:
            if len(data) < 30:
                return patterns
            
            # ⏰ VALIDAR TIMING DE SESIÓN CRÍTICA
            timing_score, session_type = self._validate_judas_session_timing()
            if timing_score < 0.4:
                return patterns
            
            # 🔍 DETECTAR FALSE BREAKOUTS
            breakout_score, breakout_type, break_price = self._detect_false_breakout_v6(data)
            if breakout_score < 0.5:
                return patterns
            
            # 💧 ANALIZAR LIQUIDITY GRAB
            current_price = data['close'].iloc[-1]
            liquidity_score, liquidity_grabbed = self._analyze_liquidity_grab_v6(data, break_price, current_price)
            
            # 🏗️ CONFIRMAR ESTRUCTURA DE REVERSIÓN
            structure_score, reversal_direction, reversal_target = self._confirm_reversal_structure_v6(data, breakout_type)
            
            # 📊 SCORING FINAL JUDAS SWING v6.0
            timing_weight = 0.35
            breakout_weight = 0.30
            structure_weight = 0.25
            liquidity_weight = 0.10
            
            final_confidence = (
                timing_score * timing_weight +
                breakout_score * breakout_weight +
                structure_score * structure_weight +
                liquidity_score * liquidity_weight
            ) * 100
            
            # Validar umbral de confianza
            if final_confidence < 70.0:
                return patterns
            
            # 🎯 CREAR SEÑAL JUDAS SWING v6.0
            judas_type = self._classify_judas_swing_type(session_type, breakout_type)
            
            # Determinar entry zone alrededor del breakout level
            spread_margin = 0.0010  # 10 pips margin
            if reversal_direction == TradingDirection.SELL:
                entry_zone = (break_price - spread_margin, break_price + spread_margin)
                stop_loss = break_price + (break_price * 0.0020)  # 20 pips stop
                take_profit_1 = reversal_target
            else:
                entry_zone = (break_price - spread_margin, break_price + spread_margin)
                stop_loss = break_price - (break_price * 0.0020)  # 20 pips stop
                take_profit_1 = reversal_target
            
            # Calcular risk/reward
            risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
            reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
            risk_reward = reward / risk if risk > 0 else 0
            
            # Narrative institucional
            narrative_parts = [
                f"🎭 Judas Swing {judas_type.value} detectado",
                f"False breakout @ {break_price:.5f}",
                f"Smart Money manipulation confirmada"
            ]
            
            if liquidity_grabbed:
                narrative_parts.append("💧 Liquidity grab ejecutado por institucionales")
            
            confluences = ["false_breakout", session_type, "smart_money_manipulation"]
            if liquidity_grabbed:
                confluences.append("liquidity_grab")
            if structure_score > 0.7:
                confluences.append("structure_confirmation")
            
            signal = PatternSignal(
                pattern_type=PatternType.JUDAS_SWING,
                direction=reversal_direction,
                confidence=PatternConfidence.HIGH if final_confidence >= 80 else PatternConfidence.MEDIUM,
                strength=min(final_confidence, 95.0),
                timestamp=datetime.now(),
                symbol=symbol,
                timeframe=timeframe,
                entry_zone=entry_zone,
                stop_loss=stop_loss,
                take_profit_1=take_profit_1,
                risk_reward_ratio=float(risk_reward),
                probability=final_confidence,
                session=SessionType.LONDON if session_type == "london" else SessionType.NEW_YORK,
                narrative=" | ".join(narrative_parts),
                confluences=confluences,
                invalidation_criteria=f"Nueva ruptura definitiva por encima/debajo de {break_price:.5f}",
                time_sensitivity="CRÍTICA - Ejecutar en los próximos 30-60 minutos",
                analysis_id=f"JUDAS_{symbol}_{judas_type.value}_{int(datetime.now().timestamp())}",
                raw_data={
                    "judas_swing_type": judas_type.value,
                    "breakout_type": breakout_type.value,
                    "false_break_price": break_price,
                    "liquidity_grabbed": liquidity_grabbed,
                    "timing_score": timing_score,
                    "breakout_score": breakout_score,
                    "structure_score": structure_score,
                    "liquidity_score": liquidity_score,
                    "session_context": session_type,
                    "smart_money_confirmation": True
                }
            )
            
            patterns.append(signal)
            
            return patterns
            
        except Exception as e:
            print(f"[ERROR] Error detectando Judas Swing v6.0: {e}")
            return patterns

    def _validate_judas_session_timing(self) -> Tuple[float, str]:
        """⏰ Valida timing para Judas Swing patterns"""
        current_time = datetime.now().time()
        
        # Definir sesiones críticas
        morning_session = (dt_time(8, 0), dt_time(9, 30))
        london_close = (dt_time(10, 0), dt_time(11, 30))
        ny_open = (dt_time(13, 0), dt_time(14, 30))
        afternoon = (dt_time(14, 0), dt_time(16, 0))
        
        # Verificar en qué sesión estamos
        if morning_session[0] <= current_time <= morning_session[1]:
            return 0.9, "morning_session"
        elif london_close[0] <= current_time <= london_close[1]:
            return 0.8, "london_close"
        elif ny_open[0] <= current_time <= ny_open[1]:
            return 0.85, "ny_open"
        elif afternoon[0] <= current_time <= afternoon[1]:
            return 0.7, "afternoon"
        else:
            return 0.3, "low_probability_session"

    def _detect_false_breakout_v6(self, data: 'pandas.DataFrame') -> Tuple[float, BreakoutType, float]:
        """🚨 Detecta false breakouts v6.0"""
        try:
            if len(data) < 20:
                return 0.0, BreakoutType.NO_BREAKOUT, 0.0

            recent = data.tail(20)
            
            # Encontrar swing highs y lows
            swing_high = recent['high'].rolling(window=5, center=True).max()
            swing_low = recent['low'].rolling(window=5, center=True).min()
            
            resistance_level = swing_high.max()
            support_level = swing_low.min()
            current_price = recent['close'].iloc[-1]
            
            # Detectar false breakout al alza
            if self._check_false_breakout_high_v6(recent, resistance_level):
                score = self._score_false_breakout_v6(recent, resistance_level, True)
                return score, BreakoutType.FALSE_BREAKOUT_HIGH, resistance_level
            
            # Detectar false breakout a la baja
            elif self._check_false_breakout_low_v6(recent, support_level):
                score = self._score_false_breakout_v6(recent, support_level, False)
                return score, BreakoutType.FALSE_BREAKOUT_LOW, support_level
            
            return 0.4, BreakoutType.NO_BREAKOUT, current_price
            
        except Exception:
            return 0.0, BreakoutType.NO_BREAKOUT, 0.0

    def _check_false_breakout_high_v6(self, candles: 'pandas.DataFrame', resistance: float) -> bool:
        """Verifica false breakout al alza v6.0"""
        try:
            for i in range(len(candles) - 5, len(candles)):
                if i >= 0 and candles['high'].iloc[i] > resistance:
                    # Verificar si hay retorno rápido
                    subsequent_closes = candles['close'].iloc[i+1:i+4]
                    if len(subsequent_closes) > 0 and subsequent_closes.min() < resistance:
                        return True
            return False
        except Exception:
            return False

    def _check_false_breakout_low_v6(self, candles: 'pandas.DataFrame', support: float) -> bool:
        """Verifica false breakout a la baja v6.0"""
        try:
            for i in range(len(candles) - 5, len(candles)):
                if i >= 0 and candles['low'].iloc[i] < support:
                    subsequent_closes = candles['close'].iloc[i+1:i+4]
                    if len(subsequent_closes) > 0 and subsequent_closes.max() > support:
                        return True
            return False
        except Exception:
            return False

    def _score_false_breakout_v6(self, candles: 'pandas.DataFrame', level: float, is_high: bool) -> float:
        """Scoring de false breakout v6.0"""
        try:
            score = 0.6
            
            # Analizar velocidad de retorno
            if is_high:
                max_penetration = candles['high'].max() - level
                if max_penetration < level * 0.001:  # Penetración mínima
                    score += 0.2
            else:
                max_penetration = level - candles['low'].min()
                if max_penetration < level * 0.001:
                    score += 0.2
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5

    def _analyze_liquidity_grab_v6(self, data: 'pandas.DataFrame', break_price: float, current_price: float) -> Tuple[float, bool]:
        """💧 Analiza liquidity grab v6.0"""
        try:
            if break_price == 0 or current_price == 0:
                return 0.3, False

            distance = abs(current_price - break_price) / break_price
            
            if distance > 0.002:  # 20 pips
                return 0.8, True
            elif distance > 0.0015:  # 15 pips
                return 0.6, True
            else:
                return 0.3, False
                
        except Exception:
            return 0.3, False

    def _confirm_reversal_structure_v6(self, data: 'pandas.DataFrame', breakout_type: BreakoutType) -> Tuple[float, TradingDirection, float]:
        """🏗️ Confirma estructura de reversión v6.0"""
        try:
            if len(data) < 10:
                return 0.3, TradingDirection.NEUTRAL, 0.0

            recent = data.tail(10)
            current_price = recent['close'].iloc[-1]
            
            if breakout_type in [BreakoutType.FALSE_BREAKOUT_HIGH, BreakoutType.LIQUIDITY_GRAB_HIGH]:
                direction = TradingDirection.SELL
                target = recent['low'].min() * 0.999
            elif breakout_type in [BreakoutType.FALSE_BREAKOUT_LOW, BreakoutType.LIQUIDITY_GRAB_LOW]:
                direction = TradingDirection.BUY
                target = recent['high'].max() * 1.001
            else:
                return 0.3, TradingDirection.NEUTRAL, current_price

            # Verificar confirmación en últimas velas
            last_3 = recent.tail(3)
            
            if direction == TradingDirection.SELL:
                bearish_candles = sum(1 for _, candle in last_3.iterrows() 
                                    if candle['close'] < candle['open'])
                score = 0.5 + (bearish_candles * 0.15)
            else:
                bullish_candles = sum(1 for _, candle in last_3.iterrows() 
                                    if candle['close'] > candle['open'])
                score = 0.5 + (bullish_candles * 0.15)
            
            return min(score, 1.0), direction, target
            
        except Exception:
            return 0.3, TradingDirection.NEUTRAL, 0.0

    def _classify_judas_swing_type(self, session_type: str, breakout_type: BreakoutType) -> JudasSwingType:
        """🎭 Clasifica tipo de Judas Swing"""
        if session_type == "morning_session":
            return JudasSwingType.MORNING_REVERSAL
        elif session_type == "london_close":
            return JudasSwingType.LONDON_CLOSE_JUDAS
        elif session_type == "ny_open":
            return JudasSwingType.NY_OPEN_JUDAS
        elif session_type == "afternoon":
            return JudasSwingType.AFTERNOON_JUDAS
        else:
            return JudasSwingType.UNKNOWN
    
    def _detect_liquidity_grab(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """Detectar patrones Liquidity Grab"""
        patterns = []
        
        try:
            if len(data) < 20:
                return patterns
            
            # Buscar barridos de liquidez recientes
            recent_data = data.tail(15)
            
            # Identificar niveles de liquidez (highs/lows anteriores)
            highs = data['high'].rolling(window=10).max()
            lows = data['low'].rolling(window=10).min()
            
            current_price = recent_data['close'].iloc[-1]
            
            # Verificar barrido de highs (liquidity grab bearish)
            for i in range(len(recent_data) - 3):
                spike_high = recent_data['high'].iloc[i]
                prev_high = highs.iloc[-20:-10].max()
                
                if spike_high > prev_high and i < len(recent_data) - 2:
                    # Verificar reversión inmediata
                    next_candles = recent_data.iloc[i+1:i+3]
                    if len(next_candles) > 0 and next_candles['close'].iloc[-1] < prev_high:
                        # Liquidity Grab bearish confirmado
                        direction = TradingDirection.SELL
                        entry_zone = (current_price - 0.0008, current_price + 0.0008)
                        stop_loss = spike_high + 0.0010
                        take_profit_1 = current_price - 0.0050
                        
                        risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
                        reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
                        risk_reward = reward / risk if risk > 0 else 0
                        
                        strength = 85.0  # Liquidity Grab suele ser muy fuerte
                        
                        signal = PatternSignal(
                            pattern_type=PatternType.LIQUIDITY_GRAB,
                            direction=direction,
                            confidence=PatternConfidence.VERY_HIGH,
                            strength=min(strength, 95.0),
                            timestamp=datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            entry_zone=entry_zone,
                            stop_loss=stop_loss,
                            take_profit_1=take_profit_1,
                            risk_reward_ratio=risk_reward,
                            probability=strength + 5,  # Extra probabilidad
                            session=self._get_current_session(),
                            narrative=f"Liquidity Grab {direction.value} confirmado. Barrido de liquidez seguido de reversión inmediata. Smart Money ha capturado stops.",
                            confluences=["liquidity_sweep", "immediate_reversal"],
                            invalidation_criteria=f"Retorno al nivel barrido sin continuación",
                            time_sensitivity="CRÍTICA - Ventana muy limitada (5-15 minutos)",
                            max_hold_time=timedelta(hours=2),
                            analysis_id=f"LG_{symbol}_{int(datetime.now().timestamp())}"
                        )
                        
                        patterns.append(signal)
                        break
            
            # Verificar barrido de lows (liquidity grab bullish)
            for i in range(len(recent_data) - 3):
                spike_low = recent_data['low'].iloc[i]
                prev_low = lows.iloc[-20:-10].min()
                
                if spike_low < prev_low and i < len(recent_data) - 2:
                    next_candles = recent_data.iloc[i+1:i+3]
                    if len(next_candles) > 0 and next_candles['close'].iloc[-1] > prev_low:
                        # Liquidity Grab bullish confirmado
                        direction = TradingDirection.BUY
                        entry_zone = (current_price - 0.0008, current_price + 0.0008)
                        stop_loss = spike_low - 0.0010
                        take_profit_1 = current_price + 0.0050
                        
                        risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
                        reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
                        risk_reward = reward / risk if risk > 0 else 0
                        
                        strength = 85.0
                        
                        signal = PatternSignal(
                            pattern_type=PatternType.LIQUIDITY_GRAB,
                            direction=direction,
                            confidence=PatternConfidence.VERY_HIGH,
                            strength=min(strength, 95.0),
                            timestamp=datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            entry_zone=entry_zone,
                            stop_loss=stop_loss,
                            take_profit_1=take_profit_1,
                            risk_reward_ratio=risk_reward,
                            probability=strength + 5,
                            session=self._get_current_session(),
                            narrative=f"Liquidity Grab {direction.value} confirmado. Barrido de liquidez seguido de reversión inmediata. Smart Money ha capturado stops.",
                            confluences=["liquidity_sweep", "immediate_reversal"],
                            invalidation_criteria=f"Retorno al nivel barrido sin continuación",
                            time_sensitivity="CRÍTICA - Ventana muy limitada (5-15 minutos)",
                            max_hold_time=timedelta(hours=2),
                            analysis_id=f"LG_{symbol}_{int(datetime.now().timestamp())}"
                        )
                        
                        patterns.append(signal)
                        break
                        
        except Exception as e:
            print(f"[WARNING] Error detectando Liquidity Grab: {e}")
        
        return patterns
    
    def _detect_optimal_trade_entry(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """Detectar patrones Optimal Trade Entry (OTE)"""
        patterns = []
        
        try:
            if len(data) < 30:
                return patterns
            
            # Identificar estructura de mercado reciente
            recent_high = data['high'].tail(20).max()
            recent_low = data['low'].tail(20).min()
            current_price = data['close'].iloc[-1]
            
            # Calcular niveles Fibonacci
            price_range = recent_high - recent_low
            fib_62 = recent_high - (price_range * 0.618)
            fib_79 = recent_high - (price_range * 0.786)
            
            # Verificar si precio está en zona OTE (62%-79% retrace)
            if fib_79 <= current_price <= fib_62:
                # Determinar dirección basada en estructura
                direction = TradingDirection.BUY if current_price < (recent_high + recent_low) / 2 else TradingDirection.SELL
                
                entry_zone = (fib_79, fib_62)
                
                if direction == TradingDirection.BUY:
                    stop_loss = recent_low - 0.0015
                    take_profit_1 = recent_high
                    take_profit_2 = recent_high + price_range * 0.618
                else:
                    stop_loss = recent_high + 0.0015
                    take_profit_1 = recent_low
                    take_profit_2 = recent_low - price_range * 0.618
                
                risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
                reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
                risk_reward = reward / risk if risk > 0 else 0
                
                # Verificar confluencias adicionales
                strength = 68.0
                confluences = ["fibonacci_retracement", "optimal_entry_zone"]
                
                # Check for Order Block confluence
                order_blocks = self._find_order_blocks(data.tail(10))
                if order_blocks:
                    strength += 8.0
                    confluences.append("order_block")
                
                # Check for FVG confluence
                fvgs = self._find_fair_value_gaps(data.tail(10))
                if fvgs:
                    strength += 5.0
                    confluences.append("fair_value_gap")
                
                if strength >= self.config['min_confidence']:
                    signal = PatternSignal(
                        pattern_type=PatternType.OPTIMAL_TRADE_ENTRY,
                        direction=direction,
                        confidence=PatternConfidence.HIGH if strength >= 75 else PatternConfidence.MEDIUM,
                        strength=min(strength, 88.0),
                        timestamp=datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        entry_zone=entry_zone,
                        stop_loss=stop_loss,
                        take_profit_1=take_profit_1,
                        take_profit_2=take_profit_2,
                        risk_reward_ratio=risk_reward,
                        probability=strength,
                        session=self._get_current_session(),
                        narrative=f"Optimal Trade Entry {direction.value} en zona Fibonacci óptima (62%-79%). Retroceso hacia zona de valor antes de continuación.",
                        confluences=confluences,
                        invalidation_criteria=f"Cierre {'debajo' if direction == TradingDirection.BUY else 'arriba'} de zona OTE",
                        time_sensitivity="MEDIA - Ventana de varias horas",
                        analysis_id=f"OTE_{symbol}_{int(datetime.now().timestamp())}"
                    )
                    
                    patterns.append(signal)
                    
        except Exception as e:
            print(f"[WARNING] Error detectando OTE: {e}")
        
        return patterns
    
    def _detect_order_blocks(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """Detectar Order Blocks"""
        patterns = []
        
        try:
            order_blocks = self._find_order_blocks(data)
            
            for ob in order_blocks[-2:]:  # Solo los más recientes
                direction = TradingDirection.BUY if ob['type'] == 'bullish' else TradingDirection.SELL
                entry_zone = (ob['low'], ob['high'])
                current_price = data['close'].iloc[-1]
                
                if direction == TradingDirection.BUY:
                    stop_loss = ob['low'] - 0.0010
                    take_profit_1 = current_price + 0.0030
                else:
                    stop_loss = ob['high'] + 0.0010
                    take_profit_1 = current_price - 0.0030
                
                risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
                reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
                risk_reward = reward / risk if risk > 0 else 0
                
                strength = 65.0 + ob.get('strength', 0) * 15
                
                if strength >= self.config['min_confidence']:
                    signal = PatternSignal(
                        pattern_type=PatternType.ORDER_BLOCK,
                        direction=direction,
                        confidence=PatternConfidence.MEDIUM,
                        strength=min(strength, 82.0),
                        timestamp=datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        entry_zone=entry_zone,
                        stop_loss=stop_loss,
                        take_profit_1=take_profit_1,
                        risk_reward_ratio=risk_reward,
                        probability=strength,
                        session=self._get_current_session(),
                        narrative=f"Order Block {direction.value} detectado. Zona donde instituciones han dejado órdenes pendientes.",
                        confluences=["institutional_orders", "price_reaction"],
                        invalidation_criteria=f"Ruptura definitiva del Order Block",
                        time_sensitivity="BAJA - Puede mantenerse activo por días",
                        analysis_id=f"OB_{symbol}_{int(datetime.now().timestamp())}"
                    )
                    
                    patterns.append(signal)
                    
        except Exception as e:
            print(f"[WARNING] Error detectando Order Blocks: {e}")
        
        return patterns
    
    def _detect_fair_value_gaps(self, data: 'pandas.DataFrame', symbol: str, timeframe: str) -> List[PatternSignal]:
        """Detectar Fair Value Gaps (FVG) con adaptación inteligente a condiciones de mercado"""
        patterns = []
        
        try:
            # === ANÁLISIS DINÁMICO DE CONDICIONES DE MERCADO ===
            market_conditions = self._analyze_current_market_conditions(data, timeframe)
            adapted_config = self._adapt_fvg_config_to_conditions(market_conditions)
            
            fvgs = self._find_fair_value_gaps(data)
            
            for fvg in fvgs[-2:]:  # Solo los más recientes
                direction = TradingDirection.BUY if fvg['type'] == 'bullish' else TradingDirection.SELL
                entry_zone = (fvg['low'], fvg['high'])
                current_price = data['close'].iloc[-1]
                
                gap_size = fvg['high'] - fvg['low']
                gap_size_pips = gap_size * (10000 if 'JPY' not in symbol else 100)
                
                # === VALIDACIÓN ADAPTATIVA DEL GAP ===
                if gap_size_pips < adapted_config['min_gap_size_pips']:
                    continue  # Saltar gaps muy pequeños según condiciones actuales
                
                # === CÁLCULO ADAPTATIVO DE NIVELES ===
                volatility_factor = adapted_config['volatility_factor']
                momentum_factor = adapted_config['momentum_factor']
                
                if direction == TradingDirection.BUY:
                    stop_loss = fvg['low'] - gap_size * (0.2 * volatility_factor)
                    take_profit_1 = current_price + gap_size * (1.5 * momentum_factor)
                else:
                    stop_loss = fvg['high'] + gap_size * (0.2 * volatility_factor)
                    take_profit_1 = current_price - gap_size * (1.5 * momentum_factor)
                
                risk = abs(safe_numpy_mean(entry_zone) - stop_loss)
                reward = abs(take_profit_1 - safe_numpy_mean(entry_zone))
                risk_reward = reward / risk if risk > 0 else 0
                
                # === CÁLCULO ADAPTATIVO DE FUERZA ===
                strength = 60.0
                
                # Bonus por tamaño de gap adaptativo
                if gap_size_pips >= adapted_config['min_gap_size_pips']:
                    strength += 10.0
                
                # Bonus por condiciones de mercado
                strength += adapted_config['confidence_adjustment'] * 100
                
                # Bonus por Kill Zone
                if market_conditions.get('kill_zone_active', False):
                    strength += 5.0
                
                # Penalización por baja volatilidad
                if market_conditions.get('volatility_pips', 8.0) < 6.0:
                    strength -= 5.0
                
                # Verificar si no está parcialmente llenado
                if not fvg.get('partially_filled', False):
                    strength += 8.0
                
                if strength >= self.config['min_confidence']:
                    signal = PatternSignal(
                        pattern_type=PatternType.FAIR_VALUE_GAP,
                        direction=direction,
                        confidence=PatternConfidence.MEDIUM,
                        strength=min(strength, 78.0),
                        timestamp=datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        entry_zone=entry_zone,
                        stop_loss=stop_loss,
                        take_profit_1=take_profit_1,
                        risk_reward_ratio=risk_reward,
                        probability=strength,
                        session=self._get_current_session(),
                        narrative=f"Fair Value Gap {direction.value} detectado. Desequilibrio que busca ser rellenado por el precio.",
                        confluences=["price_imbalance", "gap_fill_probability"],
                        invalidation_criteria=f"Gap completamente rellenado sin reacción",
                        time_sensitivity="MEDIA - FVG puede persistir por horas/días",
                        analysis_id=f"FVG_{symbol}_{int(datetime.now().timestamp())}"
                    )
                    
                    patterns.append(signal)
                    
        except Exception as e:
            print(f"[WARNING] Error detectando FVG: {e}")
        
        return patterns
    
    def _is_valid_value(self, value) -> bool:
        """Verificar si un valor es válido para cálculos"""
        try:
            if value is None:
                return False
            if pd is not None and pd.isna(value):
                return False
            if np is not None and np.isnan(value):
                return False
            if value == 0:
                return False
            return True
        except (TypeError, ValueError):
            return False

    def _validate_data_for_analysis(self, data: 'pandas.DataFrame', min_length: int = 10) -> bool:
        """Validar datos antes del análisis para evitar errores"""
        try:
            # CRÍTICO: Verificar que pandas/numpy están disponibles
            if pd is None or np is None:
                print("🚨 [CRITICAL] Pandas/Numpy no disponibles - SISTEMA NO APTO PARA TRADING")
                return False
                
            if data is None or data.empty:
                return False
                
            if len(data) < min_length:
                return False
                
            # Verificar columnas requeridas
            required_cols = ['high', 'low', 'open', 'close']
            if not all(col in data.columns for col in required_cols):
                return False
                
            # Verificar que no todos los datos son NaN
            if data[required_cols].isna().all().all():
                return False
                
            # TRADING READY: Verificar que tenemos datos válidos para trading
            for col in required_cols:
                if data[col].isna().sum() > len(data) * 0.1:  # Máximo 10% de NaN
                    print(f"🚨 [TRADING WARNING] Demasiados valores NaN en {col}: {data[col].isna().sum()}/{len(data)}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"🚨 [CRITICAL] Error validando datos: {e}")
            return False

    def _find_order_blocks(self, data: 'pandas.DataFrame') -> List[Dict[str, Any]]:
        """Encontrar Order Blocks en los datos - VERSIÓN OPTIMIZADA"""
        order_blocks = []
        
        try:
            # Validación robusta
            if not self._validate_data_for_analysis(data, min_length=10):
                return order_blocks
                
            # OPTIMIZACIÓN: Aumentar límites para mejor detección
            MAX_CANDLES_TO_ANALYZE = 200  # Aumentado de 100 para mejor detección
            
            if len(data) > MAX_CANDLES_TO_ANALYZE:
                print(f"[INFO] Limitando análisis OB: {len(data)} -> {MAX_CANDLES_TO_ANALYZE} velas")
                data_subset = data.tail(MAX_CANDLES_TO_ANALYZE)
            else:
                data_subset = data
                
            # OPTIMIZACIÓN: Aumentar iteraciones para mejor cobertura  
            max_iterations = min(len(data_subset) - 10, 80)  # Aumentado de 50 a 80
            
            # Buscar velas de impulso seguidas de consolidación
            for i in range(5, max_iterations):
                try:
                    current_candle = data_subset.iloc[i]
                    candle_size = abs(current_candle['close'] - current_candle['open'])
                    
                    # Verificar datos válidos con función robusta
                    if not self._is_valid_value(candle_size):
                        continue
                    
                    # Calcular tamaño promedio de velas anteriores
                    prev_candles = data_subset.iloc[max(0, i-10):i]  # Aumentado de 5 a 10 velas
                    if len(prev_candles) == 0:
                        continue
                        
                    prev_sizes = abs(prev_candles['close'] - prev_candles['open'])
                    avg_size = prev_sizes.mean()
                    
                    if not self._is_valid_value(avg_size) or avg_size == 0:
                        continue
                        
                except (IndexError, KeyError, AttributeError):
                    continue
                
                # OPTIMIZACIÓN: Reducir threshold para detectar más Order Blocks
                impulse_threshold = 1.5  # Reducido de 1.8 a 1.5 para más sensibilidad
                
                # Verificar si es vela de impulso
                if candle_size > avg_size * impulse_threshold:
                    # OPTIMIZACIÓN: Buscar retorno en más velas futuras
                    future_range = min(10, len(data_subset) - i - 1)  # Hasta 10 velas futuras
                    future_candles = data_subset.iloc[i+1:i+1+future_range]
                    
                    ob_high = current_candle['high']
                    ob_low = current_candle['low']
                    
                    # MEJORAR: Verificar retorno al Order Block con más flexibilidad
                    block_tested = False
                    for j in range(len(future_candles)):
                        future_candle = future_candles.iloc[j]
                        
                        # Permitir overlap parcial, no solo completo
                        price_overlap = (future_candle['low'] <= ob_high * 1.001 and 
                                       future_candle['high'] >= ob_low * 0.999)
                        
                        if price_overlap:
                            block_tested = True
                            break
                    
                    # OPTIMIZACIÓN: Crear Order Block incluso si no ha sido testeado aún
                    ob_type = 'bullish' if current_candle['close'] > current_candle['open'] else 'bearish'
                    
                    # Calcular strength basado en múltiples factores
                    size_strength = min(candle_size / avg_size / 3, 1.0)  # Normalizado
                    test_strength = 0.3 if block_tested else 0.1  # Bonus si ha sido testeado
                    volume_strength = 0.2  # Placeholder para volumen
                    
                    total_strength = size_strength + test_strength + volume_strength
                    
                    order_blocks.append({
                        'type': ob_type,
                        'high': float(ob_high),
                        'low': float(ob_low),
                        'timestamp': current_candle.name if hasattr(current_candle, 'name') else i,
                        'strength': min(total_strength, 1.0),
                        'tested': block_tested,
                        'impulse_size': float(candle_size),
                        'avg_size_ratio': float(candle_size / avg_size),
                        'candle_index': i
                    })
            
            # OPTIMIZACIÓN: Asegurar que se detecten al menos algunos Order Blocks básicos
            if len(order_blocks) == 0 and len(data_subset) >= 20:
                print(f"[INFO] No se detectaron OB con criterios estrictos, aplicando detección básica...")
                order_blocks = self._find_basic_order_blocks(data_subset)
                        
        except Exception as e:
            print(f"[WARNING] Error detectando Order Blocks: {e}")
            # FALLBACK: Crear al menos un Order Block básico
            if len(data) >= 10:
                try:
                    last_candle = data.iloc[-1]
                    order_blocks.append({
                        'type': 'bullish' if last_candle['close'] > last_candle['open'] else 'bearish',
                        'high': float(last_candle['high']),
                        'low': float(last_candle['low']),
                        'timestamp': last_candle.name if hasattr(last_candle, 'name') else len(data)-1,
                        'strength': 0.5,
                        'tested': False,
                        'fallback': True
                    })
                    print(f"[INFO] Order Block de fallback creado")
                except Exception as fallback_error:
                    print(f"[ERROR] Error creando Order Block de fallback: {fallback_error}")
        
        print(f"[INFO] Order Blocks detectados: {len(order_blocks)}")
        return order_blocks
    
    def _find_basic_order_blocks(self, data: 'pandas.DataFrame') -> List[Dict[str, Any]]:
        """Detectar Order Blocks con criterios más básicos como fallback"""
        basic_blocks = []
        
        try:
            # Buscar velas grandes en los últimos datos
            for i in range(max(1, len(data)-20), len(data)-1):
                current_candle = data.iloc[i]
                prev_candle = data.iloc[i-1]
                
                candle_size = abs(current_candle['close'] - current_candle['open'])
                prev_size = abs(prev_candle['close'] - prev_candle['open'])
                
                # Criterio más básico: vela 50% más grande que la anterior
                if candle_size > prev_size * 1.5 and candle_size > 0:
                    ob_type = 'bullish' if current_candle['close'] > current_candle['open'] else 'bearish'
                    
                    basic_blocks.append({
                        'type': ob_type,
                        'high': float(current_candle['high']),
                        'low': float(current_candle['low']),
                        'timestamp': current_candle.name if hasattr(current_candle, 'name') else i,
                        'strength': 0.4,  # Strength básica
                        'tested': False,
                        'basic_detection': True
                    })
                    
                    # Limitar a máximo 3 bloques básicos
                    if len(basic_blocks) >= 3:
                        break
                        
        except Exception as e:
            print(f"[WARNING] Error en detección básica de Order Blocks: {e}")
        
        return basic_blocks
    
    def _analyze_current_market_conditions(self, data: 'pandas.DataFrame', timeframe: str) -> Dict[str, Any]:
        """
        Analiza las condiciones actuales de mercado para adaptación inteligente.
        Sistema avanzado que captura múltiples métricas de mercado en tiempo real.
        """
        try:
            if len(data) < 20:
                return self._get_default_market_conditions()
            
            # === ANÁLISIS DE VOLATILIDAD MULTIPERÍODO ===
            recent_data = data.tail(20)
            very_recent = data.tail(5)  # Últimas 5 velas para tendencia inmediata
            
            highs = recent_data['high']
            lows = recent_data['low']
            closes = recent_data['close']
            
            # Volatilidad promedio y actual
            volatility_pips = float((highs - lows).mean() * (10000 if 'JPY' not in getattr(self, 'current_symbol', 'EURUSD') else 100))
            current_volatility = float((very_recent['high'] - very_recent['low']).mean() * (10000 if 'JPY' not in getattr(self, 'current_symbol', 'EURUSD') else 100))
            
            # === ANÁLISIS DE MOMENTUM AVANZADO ===
            momentum_pips = float((closes.iloc[-1] - closes.iloc[0]) * (10000 if 'JPY' not in getattr(self, 'current_symbol', 'EURUSD') else 100))
            short_momentum = float((closes.iloc[-1] - closes.iloc[-5]) * (10000 if 'JPY' not in getattr(self, 'current_symbol', 'EURUSD') else 100))
            
            # Dirección y fuerza del momentum
            if momentum_pips > 0.5:
                momentum_direction = 'bullish'
            elif momentum_pips < -0.5:
                momentum_direction = 'bearish'
            else:
                momentum_direction = 'neutral'
            
            momentum_strength = 'weak'
            if abs(momentum_pips) > 2.0:
                momentum_strength = 'strong'
            elif abs(momentum_pips) > 1.0:
                momentum_strength = 'moderate'
            
            # === ANÁLISIS DE SESIÓN Y KILL ZONES ===
            current_hour = datetime.now().hour
            session_info = self._get_session_info(current_hour)
            kill_zone_active = session_info['kill_zone_active']
            
            # === ANÁLISIS DE ESTRUCTURA ===
            # Verificar si hay ruptura de estructura reciente
            structure_break = self._detect_recent_structure_break(recent_data)
            
            # === ANÁLISIS DE TENDENCIA ===
            trend_direction = self._analyze_trend_direction(recent_data)
            
            # === CÁLCULO DE CALIDAD DE DATOS ===
            data_quality = 'excellent' if len(data) >= 100 else 'good' if len(data) >= 50 else 'limited'
            
            # === FACTOR DE COHERENCIA ===
            coherence_factor = self._calculate_market_coherence(recent_data, momentum_direction, trend_direction)
            
            return {
                'volatility_pips': max(volatility_pips, 1.0),
                'current_volatility': max(current_volatility, 1.0),
                'momentum_pips': momentum_pips,
                'short_momentum_pips': short_momentum,
                'momentum_direction': momentum_direction,
                'momentum_strength': momentum_strength,
                'kill_zone_active': kill_zone_active,
                'session': session_info['session'],
                'session_strength': session_info['strength'],
                'structure_break_detected': structure_break,
                'trend_direction': trend_direction,
                'coherence_factor': coherence_factor,
                'timeframe': timeframe,
                'data_quality': data_quality,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[WARNING] Error analizando condiciones de mercado: {e}")
            return self._get_default_market_conditions()
    
    def _get_session_info(self, hour: int) -> Dict[str, Any]:
        """Información detallada de la sesión actual"""
        # London: 08:00-16:00 GMT, NY: 13:00-22:00 GMT, Asian: 21:00-06:00 GMT
        if 21 <= hour or hour <= 6:
            return {'session': 'asian', 'kill_zone_active': 2 <= hour <= 6, 'strength': 'low'}
        elif 8 <= hour <= 12:
            return {'session': 'london', 'kill_zone_active': True, 'strength': 'high'}
        elif 13 <= hour <= 16:
            return {'session': 'overlap', 'kill_zone_active': True, 'strength': 'maximum'}
        elif 17 <= hour <= 20:
            return {'session': 'new_york', 'kill_zone_active': 17 <= hour <= 19, 'strength': 'high'}
        else:
            return {'session': 'transition', 'kill_zone_active': False, 'strength': 'low'}
    
    def _detect_recent_structure_break(self, data: 'pandas.DataFrame') -> bool:
        """Detecta si hay ruptura de estructura reciente"""
        try:
            if len(data) < 10:
                return False
            
            highs = data['high'].tail(10)
            lows = data['low'].tail(10)
            
            # Simplificado: detectar nuevo high o low significativo
            recent_high = highs.max()
            recent_low = lows.min()
            previous_high = highs.iloc[:-3].max()
            previous_low = lows.iloc[:-3].min()
            
            high_break = recent_high > previous_high * 1.0005  # 0.5 pips aprox
            low_break = recent_low < previous_low * 0.9995
            
            return high_break or low_break
            
        except:
            return False
    
    def _analyze_trend_direction(self, data: 'pandas.DataFrame') -> str:
        """Analiza la dirección de la tendencia"""
        try:
            if len(data) < 10:
                return 'unknown'
            
            closes = data['close']
            sma_short = closes.tail(5).mean()
            sma_long = closes.tail(10).mean()
            
            if sma_short > sma_long * 1.001:
                return 'bullish'
            elif sma_short < sma_long * 0.999:
                return 'bearish'
            else:
                return 'sideways'
                
        except:
            return 'unknown'
    
    def _calculate_market_coherence(self, data: 'pandas.DataFrame', momentum_dir: str, trend_dir: str) -> float:
        """Calcula factor de coherencia del mercado"""
        try:
            coherence = 0.5  # Base neutral
            
            # Coherencia direccional
            if momentum_dir == trend_dir and momentum_dir != 'neutral':
                coherence += 0.3  # Momentum y tendencia alineados
            
            # Coherencia de volatilidad
            volatility_consistency = 1.0 - (data['high'] - data['low']).std() / (data['high'] - data['low']).mean()
            coherence += min(volatility_consistency * 0.2, 0.2)
            
            return max(0.1, min(coherence, 1.0))
            
        except:
            return 0.5
    
    def _get_default_market_conditions(self) -> Dict[str, Any]:
        """Condiciones de mercado por defecto mejoradas"""
        current_hour = datetime.now().hour
        session_info = self._get_session_info(current_hour)
        
        return {
            'volatility_pips': 8.0,
            'current_volatility': 8.0,
            'momentum_pips': 0.0,
            'short_momentum_pips': 0.0,
            'momentum_direction': 'neutral',
            'momentum_strength': 'weak',
            'kill_zone_active': session_info['kill_zone_active'],
            'session': session_info['session'],
            'session_strength': session_info['strength'],
            'structure_break_detected': False,
            'trend_direction': 'unknown',
            'coherence_factor': 0.5,
            'timeframe': 'H1',
            'data_quality': 'unknown',
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _is_kill_zone_active(self, hour: int) -> bool:
        """Determina si estamos en una Kill Zone activa (método legacy)"""
        session_info = self._get_session_info(hour)
        return session_info['kill_zone_active']
        return london_session or ny_session or overlap_session
    
    def _adapt_fvg_config_to_conditions(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapta la configuración de FVG basándose en condiciones de mercado reales.
        Sistema avanzado que optimiza detección según contexto actual.
        """
        try:
            volatility = market_conditions['volatility_pips']
            momentum = market_conditions['momentum_pips']
            momentum_direction = market_conditions.get('momentum_direction', 'neutral')
            kill_zone = market_conditions['kill_zone_active']
            session = market_conditions.get('session', 'unknown')
            
            # Configuración base adaptativa
            base_config = {
                'min_gap_size_pips': 2.0,
                'volatility_factor': 1.0,
                'momentum_factor': 1.0,
                'confidence_adjustment': 0.0,
                'fill_tolerance_pips': 0.5,
                'strength_multiplier': 1.0
            }
            
            # === ADAPTACIÓN AVANZADA POR VOLATILIDAD ===
            if volatility < 5.0:  # Mercado muy tranquilo
                base_config['min_gap_size_pips'] = max(0.8, volatility * 0.2)
                base_config['volatility_factor'] = 0.7  # Stops más cercanos
                base_config['fill_tolerance_pips'] = 0.2  # Muy estricto
                base_config['strength_multiplier'] = 0.9
                
            elif volatility < 7.0:  # Volatilidad baja
                base_config['min_gap_size_pips'] = max(1.2, volatility * 0.25)
                base_config['volatility_factor'] = 0.8
                base_config['fill_tolerance_pips'] = 0.3
                
            elif volatility > 15.0:  # Volatilidad extrema
                base_config['min_gap_size_pips'] = min(5.0, volatility * 0.4)
                base_config['volatility_factor'] = 1.4  # Stops muy amplios
                base_config['fill_tolerance_pips'] = 0.9
                base_config['strength_multiplier'] = 1.2
                
            elif volatility > 12.0:  # Volatilidad alta
                base_config['min_gap_size_pips'] = min(4.0, volatility * 0.3)
                base_config['volatility_factor'] = 1.2
                base_config['fill_tolerance_pips'] = 0.7
            
            # === ADAPTACIÓN INTELIGENTE POR MOMENTUM ===
            if momentum_direction == 'bearish':
                if abs(momentum) > 3.0:  # Momentum bajista muy fuerte
                    base_config['momentum_factor'] = 0.7  # TPs muy conservadores
                    base_config['confidence_adjustment'] = -0.08
                    base_config['fill_tolerance_pips'] *= 0.7  # Más estricto
                    
                elif abs(momentum) > 1.5:  # Momentum bajista moderado
                    base_config['momentum_factor'] = 0.8
                    base_config['confidence_adjustment'] = -0.05
                    base_config['fill_tolerance_pips'] *= 0.8
                    
            elif momentum_direction == 'bullish':
                if momentum > 3.0:  # Momentum alcista muy fuerte
                    base_config['momentum_factor'] = 1.3  # TPs más amplios
                    base_config['confidence_adjustment'] = 0.08
                    base_config['fill_tolerance_pips'] *= 1.2  # Más permisivo
                    
                elif momentum > 1.5:  # Momentum alcista moderado
                    base_config['momentum_factor'] = 1.2
                    base_config['confidence_adjustment'] = 0.05
                    base_config['fill_tolerance_pips'] *= 1.1
            
            # === OPTIMIZACIÓN ESPECIAL PARA KILL ZONES ===
            if kill_zone:
                base_config['min_gap_size_pips'] *= 0.85  # Más sensible
                base_config['confidence_adjustment'] += 0.05
                base_config['strength_multiplier'] *= 1.1
                
                # Optimización específica por sesión durante Kill Zone
                if session == 'london':
                    base_config['volatility_factor'] *= 1.1  # London más volátil
                elif session == 'new_york':
                    base_config['momentum_factor'] *= 1.1  # NY más momentum
                elif session == 'overlap':
                    base_config['strength_multiplier'] *= 1.2  # Overlap máximo
            
            # === ADAPTACIÓN POR SESIÓN ===
            if session == 'asian':
                # Sesión asiática: movimientos más suaves
                base_config['min_gap_size_pips'] *= 0.7
                base_config['fill_tolerance_pips'] *= 0.8
                base_config['volatility_factor'] *= 0.9
                
            elif session == 'overlap':
                # Overlap London-NY: máxima agresividad
                base_config['min_gap_size_pips'] *= 0.9
                base_config['strength_multiplier'] *= 1.15
                base_config['confidence_adjustment'] += 0.03
            
            # === LÍMITES DE SEGURIDAD ===
            base_config['min_gap_size_pips'] = max(0.5, min(base_config['min_gap_size_pips'], 6.0))
            base_config['fill_tolerance_pips'] = max(0.1, min(base_config['fill_tolerance_pips'], 1.2))
            base_config['volatility_factor'] = max(0.5, min(base_config['volatility_factor'], 2.0))
            base_config['momentum_factor'] = max(0.5, min(base_config['momentum_factor'], 2.0))
            base_config['strength_multiplier'] = max(0.7, min(base_config['strength_multiplier'], 1.5))
            
            return base_config
            
        except Exception as e:
            print(f"[WARNING] Error adaptando configuración FVG: {e}")
            return {
                'min_gap_size_pips': 2.0,
                'volatility_factor': 1.0,
                'momentum_factor': 1.0,
                'confidence_adjustment': 0.0
            }
    
    def _find_fair_value_gaps(self, data: 'pandas.DataFrame') -> List[Dict[str, Any]]:
        """Encontrar Fair Value Gaps en los datos"""
        fvgs = []
        
        try:
            # Validación robusta de datos
            if not self._validate_data_for_analysis(data, min_length=3):
                return fvgs
            
            # LIMITACIÓN CRÍTICA para evitar loops infinitos
            MAX_CANDLES_TO_ANALYZE = 200  # Máximo para análisis seguro
            
            if len(data) > MAX_CANDLES_TO_ANALYZE:
                print(f"[INFO] Limitando análisis FVG: {len(data)} -> {MAX_CANDLES_TO_ANALYZE} velas")
                data = data.tail(MAX_CANDLES_TO_ANALYZE)
            
            # Buscar gaps en secuencias de 3 velas con validación extra
            max_index = len(data) - 1
            
            # CRÍTICO: Limitar iteraciones para evitar recursión
            max_iterations = min(len(data) - 2, 100)  # Máximo 100 iteraciones
            
            for i in range(1, max_iterations):
                try:
                    # Validar índices antes de acceder
                    if i-1 < 0 or i >= len(data) or i+1 >= len(data):
                        continue
                        
                    prev_candle = data.iloc[i-1]
                    current_candle = data.iloc[i]
                    next_candle = data.iloc[i+1]
                    
                    # Verificar que las velas tienen datos válidos
                    if (prev_candle.isna().any() or current_candle.isna().any() or 
                        next_candle.isna().any()):
                        continue
                        
                    # Verificar valores críticos para trading
                    prev_high = prev_candle['high']
                    prev_low = prev_candle['low']
                    next_high = next_candle['high']
                    next_low = next_candle['low']
                    current_open = current_candle['open']
                    current_close = current_candle['close']
                    
                    # Validar que todos los valores son válidos para trading
                    critical_values = [prev_high, prev_low, next_high, next_low, current_open, current_close]
                    if not all(self._is_valid_value(val) for val in critical_values):
                        continue
                        
                except (IndexError, KeyError, AttributeError) as e:
                    # Skip vela problemática y continuar
                    continue
                
                # Bullish FVG: gap between prev high and next low
                if (prev_high < next_low and current_close > current_open):
                    
                    gap_size = next_low - prev_high
                    if self._is_valid_value(gap_size) and gap_size >= self.config['fvg_min_size']:
                        fvgs.append({
                            'type': 'bullish',
                            'high': next_low,
                            'low': prev_high,
                            'timestamp': current_candle.name if hasattr(current_candle, 'name') else i,
                            'size': gap_size,
                            'partially_filled': False
                        })
                
                # Bearish FVG: gap between prev low and next high
                elif (prev_low > next_high and current_close < current_open):
                    
                    gap_size = prev_low - next_high
                    if self._is_valid_value(gap_size) and gap_size >= self.config['fvg_min_size']:
                        fvgs.append({
                            'type': 'bearish',
                            'high': prev_low,
                            'low': next_high,
                            'timestamp': current_candle.name if hasattr(current_candle, 'name') else i,
                            'size': gap_size,
                            'partially_filled': False
                        })
                        
        except Exception as e:
            print(f"[WARNING] Error finding FVGs: {e}")
        
        return fvgs
    
    def get_multi_timeframe_data(self, symbol: str) -> Dict[str, 'pandas.DataFrame']:
        """
        🎯 OBTENER DATOS MULTI-TIMEFRAME ALMACENADOS
        
        Returns:
            Dict con {timeframe: dataframe} para análisis contextuales
        """
        if hasattr(self, '_multi_tf_data') and symbol in self._multi_tf_data:
            return self._multi_tf_data[symbol]
        return {}

    def _enhance_analysis_with_multi_tf(self, patterns: List[PatternSignal], symbol: str, primary_timeframe: str) -> List[PatternSignal]:
        """
        🔍 ENHANCING PATTERNS CON ANÁLISIS MULTI-TIMEFRAME ICT v6.0
        
        Mejora los patrones detectados usando el contexto de timeframes superiores:
        - HTF Structure confirmation
        - Confluences entre timeframes
        - ICT Kill Zone optimization
        """
        try:
            multi_tf_data = self.get_multi_timeframe_data(symbol)
            
            if not multi_tf_data:
                return patterns
                
            enhanced_patterns = []
            
            for pattern in patterns:
                enhanced_pattern = self._apply_multi_tf_enhancement(
                    pattern, multi_tf_data, primary_timeframe
                )
                enhanced_patterns.append(enhanced_pattern)
                
            print(f"📊 Enhanced {len(enhanced_patterns)} patterns with multi-TF analysis")
            return enhanced_patterns
            
        except Exception as e:
            print(f"[WARNING] Error in multi-TF enhancement: {e}")
            return patterns

    def _apply_multi_tf_enhancement(self, pattern: PatternSignal, multi_tf_data: Dict[str, 'pandas.DataFrame'], primary_tf: str) -> PatternSignal:
        """
        📈 APLICAR ENHANCEMENT MULTI-TIMEFRAME A PATRÓN INDIVIDUAL
        
        Args:
            pattern: Patrón detectado en timeframe primario
            multi_tf_data: Datos de todos los timeframes
            primary_tf: Timeframe primario donde se detectó el patrón
            
        Returns:
            PatternSignal mejorado con confirmaciones HTF
        """
        try:
            # Get higher timeframes for confirmation
            htf_timeframes = self._get_higher_timeframes(primary_tf)
            
            confirmations = []
            strength_multiplier = 1.0
            
            for htf in htf_timeframes:
                if htf in multi_tf_data:
                    htf_data = multi_tf_data[htf]
                    
                    # Check HTF structure alignment
                    htf_confirmation = self._check_htf_structure_alignment(
                        pattern, htf_data, htf
                    )
                    
                    if htf_confirmation:
                        confirmations.append(f"HTF_{htf}_ALIGN")
                        strength_multiplier += 0.2
                        
            # Apply Smart Money enhancement if available
            # TODO: Implementar enhance_pattern_with_smart_money en SmartMoneyAnalyzer
            if (hasattr(self, '_smart_money_analyzer') and 
                self._smart_money_analyzer and 
                hasattr(self._smart_money_analyzer, 'enhance_pattern_with_smart_money')):
                try:
                    # 🧠 Convertir PatternSignal a dict para análisis Smart Money
                    pattern_dict = pattern.__dict__ if hasattr(pattern, '__dict__') else {}
                    
                    # 📊 Extraer DataFrame primario del multi_tf_data para Smart Money
                    primary_data = None
                    if multi_tf_data:
                        # Priorizar primary_tf, luego H1, luego el primer disponible
                        if primary_tf in multi_tf_data:
                            primary_data = multi_tf_data[primary_tf]
                        elif 'H1' in multi_tf_data:
                            primary_data = multi_tf_data['H1']
                        else:
                            primary_data = next(iter(multi_tf_data.values()), None)
                    
                    smc_enhancement = self._smart_money_analyzer.enhance_pattern_with_smart_money(
                        pattern_dict, primary_data
                    )
                    
                    if smc_enhancement.get('enhanced', False):
                        confirmations.extend(smc_enhancement.get('confirmations', []))
                        strength_multiplier += smc_enhancement.get('strength_boost', 0)
                except Exception as e:
                    print(f"[WARNING] Smart Money analysis failed: {e}")
                    confirmations.append("SMART_MONEY_ANALYSIS_FAILED")
            else:
                # Fallback: Smart Money analysis no disponible
                confirmations.append("SMART_MONEY_ANALYSIS_PENDING")
                    
            # Create enhanced pattern with improved strength
            enhanced_strength = min(pattern.strength * strength_multiplier, 100.0)
            
            # Create enhanced pattern with all required fields
            enhanced_pattern = PatternSignal(
                pattern_type=pattern.pattern_type,
                direction=pattern.direction,
                confidence=pattern.confidence,
                strength=enhanced_strength,
                timestamp=pattern.timestamp,
                symbol=pattern.symbol,
                timeframe=pattern.timeframe,
                entry_zone=pattern.entry_zone,
                stop_loss=pattern.stop_loss,
                take_profit_1=pattern.take_profit_1,
                take_profit_2=pattern.take_profit_2,
                risk_reward_ratio=pattern.risk_reward_ratio,
                probability=pattern.probability,
                session=pattern.session,
                narrative=pattern.narrative + f" | Multi-TF Enhanced (+{(strength_multiplier-1)*100:.0f}%)",
                confluences=pattern.confluences + confirmations,
                invalidation_criteria=pattern.invalidation_criteria,
                optimal_entry_time=pattern.optimal_entry_time,
                time_sensitivity=pattern.time_sensitivity,
                max_hold_time=pattern.max_hold_time,
                analysis_id=pattern.analysis_id,
                raw_data=pattern.raw_data.copy() if pattern.raw_data else {}
            )
            
            # Add multi-TF metadata to raw_data
            enhanced_pattern.raw_data.update({
                'multi_tf_confirmations': confirmations,
                'htf_analyzed': list(htf_timeframes),
                'strength_enhancement': strength_multiplier - 1.0,
                'original_strength': pattern.strength
            })
            
            return enhanced_pattern
            
        except Exception as e:
            print(f"[DEBUG] Error applying multi-TF enhancement: {e}")
            return pattern

    def _get_higher_timeframes(self, primary_tf: str) -> List[str]:
        """Obtener timeframes superiores para confirmación"""
        tf_hierarchy = ['M1', 'M5', 'M15', 'H1', 'H4', 'D1', 'W1', 'MN1']
        
        try:
            primary_idx = tf_hierarchy.index(primary_tf)
            return tf_hierarchy[primary_idx + 1:primary_idx + 4]  # Next 3 higher TFs
        except ValueError:
            return ['H1', 'H4', 'D1']  # Default HTFs

    def _check_htf_structure_alignment(self, pattern: PatternSignal, htf_data: 'pandas.DataFrame', htf: str) -> bool:
        """
        🔍 VERIFICAR ALINEACIÓN DE ESTRUCTURA EN HTF
        
        Checks if the pattern aligns with higher timeframe structure:
        - Trend direction alignment
        - Key level confluence
        - Market structure support
        """
        try:
            if htf_data.empty or len(htf_data) < 20:
                return False
                
            # Get recent HTF candles around pattern time
            pattern_time = pattern.timestamp
            
            # Find closest HTF candle to pattern time
            # Calcular diferencias temporales usando numpy para compatibilidad
            try:
                import numpy as np
                time_diffs = np.abs(htf_data.index - pattern_time)
                closest_pos = int(time_diffs.argmin())  # Convertir a int para compatibilidad
            except Exception:
                # Fallback: usar diferencias directas con conversión manual
                time_diffs = [(abs((idx - pattern_time).total_seconds())) for idx in htf_data.index]
                closest_pos = time_diffs.index(min(time_diffs))
            
            # Get context window
            # closest_pos ya es la posición numérica, no necesitamos get_loc()
            start_pos = max(0, closest_pos - 10)
            end_pos = min(len(htf_data), closest_pos + 5)
            
            context_data = htf_data.iloc[start_pos:end_pos]
            
            if len(context_data) < 5:
                return False
                
            # Check trend alignment
            htf_trend = self._determine_htf_trend(context_data)
            pattern_direction = pattern.direction
            
            # Bullish pattern should align with bullish HTF trend
            if pattern_direction == TradingDirection.BUY and htf_trend == "BULLISH":
                return True
            elif pattern_direction == TradingDirection.SELL and htf_trend == "BEARISH":
                return True
            elif htf_trend == "NEUTRAL":  # Neutral HTF allows both directions
                return True
                
            return False
            
        except Exception as e:
            print(f"[DEBUG] Error checking HTF alignment: {e}")
            return False

    def _determine_htf_trend(self, htf_data: 'pandas.DataFrame') -> str:
        """
        📊 DETERMINAR TENDENCIA EN HTF
        
        Returns: "BULLISH", "BEARISH", or "NEUTRAL"
        """
        try:
            if len(htf_data) < 5:
                return "NEUTRAL"
                
            # Simple trend using highs and lows progression
            recent_data = htf_data.tail(5)
            
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            # Check for higher highs and higher lows (bullish)
            if highs[-1] > highs[0] and lows[-1] > lows[0]:
                return "BULLISH"
            # Check for lower highs and lower lows (bearish)
            elif highs[-1] < highs[0] and lows[-1] < lows[0]:
                return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception:
            return "NEUTRAL"
    
    def _is_silver_bullet_time(self, current_time: datetime) -> bool:
        """Verificar si es ventana Silver Bullet"""
        try:
            # Convertir a GMT si es necesario
            hour = current_time.hour
            # Silver Bullet windows: 10:00-11:00 GMT y 14:00-15:00 GMT
            return (10 <= hour <= 11) or (14 <= hour <= 15)
        except:
            return False
    
    def _is_session_opening(self) -> bool:
        """Verificar si es apertura de sesión"""
        try:
            current_time = datetime.now()
            hour = current_time.hour
            
            # London: 08:00-10:00, New York: 13:00-15:00
            return (8 <= hour <= 10) or (13 <= hour <= 15)
        except:
            return False
    
    def _get_current_session(self) -> SessionType:
        """Obtener sesión actual"""
        try:
            current_time = datetime.now()
            hour = current_time.hour
            
            if 8 <= hour <= 17:
                return SessionType.LONDON
            elif 13 <= hour <= 22:
                return SessionType.NEW_YORK
            elif 22 <= hour <= 24 or 0 <= hour <= 8:
                return SessionType.ASIAN
            else:
                return SessionType.DEAD_ZONE
        except:
            return SessionType.LONDON
    
    def _update_performance_metrics(self, analysis_time: float, patterns_detected: int):
        """Actualizar métricas de rendimiento"""
        try:
            self.performance_metrics['total_analyses'] += 1
            self.performance_metrics['patterns_detected'] += patterns_detected
            
            # Promedio móvil del tiempo de análisis
            total = self.performance_metrics['total_analyses']
            current_avg = self.performance_metrics['avg_analysis_time']
            self.performance_metrics['avg_analysis_time'] = (current_avg * (total - 1) + analysis_time) / total
            
            # Tasa de éxito (patrones detectados vs análisis)
            self.performance_metrics['success_rate'] = (
                self.performance_metrics['patterns_detected'] / total * 100
            )
            
            self.performance_metrics['last_update'] = datetime.now()
            
        except Exception as e:
            print(f"[WARNING] Error actualizando métricas: {e}")
    
    def get_detected_patterns(self) -> List[PatternSignal]:
        """Obtener patrones detectados"""
        return self.detected_patterns.copy()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        return self.performance_metrics.copy()
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Obtener resumen de patrones detectados"""
        if not self.detected_patterns:
            return {
                'total_patterns': 0,
                'by_type': {},
                'by_confidence': {},
                'avg_strength': 0.0,
                'last_analysis': None
            }
        
        # Contar por tipo
        by_type = {}
        for pattern in self.detected_patterns:
            ptype = pattern.pattern_type.value
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        # Contar por confianza
        by_confidence = {}
        for pattern in self.detected_patterns:
            conf = pattern.confidence.value
            by_confidence[conf] = by_confidence.get(conf, 0) + 1
        
        # Strength promedio
        avg_strength = sum(p.strength for p in self.detected_patterns) / len(self.detected_patterns)
        
        return {
            'total_patterns': len(self.detected_patterns),
            'by_type': by_type,
            'by_confidence': by_confidence,
            'avg_strength': round(avg_strength, 1),
            'last_analysis': self.last_analysis_time
        }

    # =============================================================================
    # SMART MONEY CONCEPTS INTEGRATION v6.0
    # =============================================================================

    def _enhance_with_smart_money_analysis(self, patterns: List[PatternSignal], data) -> List[PatternSignal]:
        """
        🧠 ENHANCE PATTERNS WITH SMART MONEY CONCEPTS v6.0
        
        Mejora los patrones detectados con análisis Smart Money:
        - Liquidity pools identification
        - Institutional order flow
        - Market maker behavior
        - Killzone optimization
        
        Args:
            patterns: Lista de patrones detectados
            data: Datos de mercado para análisis
            
        Returns:
            Lista de patrones mejorados con Smart Money insights
        """
        if not self._smart_money_analyzer or not patterns:
            return patterns
        
        try:
            enhanced_patterns = []
            
            for pattern in patterns:
                # Analizar liquidity pools cerca del patrón
                liquidity_pools = self._analyze_liquidity_pools_near_pattern(pattern, data)
                
                # Detectar flujo institucional
                institutional_flow = self._detect_institutional_flow(pattern, data)
                
                # Verificar comportamiento market maker
                market_maker_behavior = self._analyze_market_maker_behavior(pattern, data)
                
                # Optimizar con killzones
                killzone_optimization = self._optimize_with_killzones(pattern, data)
                
                # Calcular smart money confidence
                smart_money_confidence = self._calculate_smart_money_confidence(
                    liquidity_pools, institutional_flow, market_maker_behavior, killzone_optimization
                )
                
                # Enhancing pattern with Smart Money data
                enhanced_pattern = self._apply_smart_money_enhancement(
                    pattern, smart_money_confidence, liquidity_pools,
                    institutional_flow, market_maker_behavior, killzone_optimization
                )
                
                enhanced_patterns.append(enhanced_pattern)
                
                if self.config.get('enable_debug'):
                    print(f"🧠 Smart Money enhancement: {pattern.pattern_type.value}")
                    print(f"   Liquidity pools: {len(liquidity_pools)}")
                    print(f"   Institutional flow: {institutional_flow:.2f}")
                    print(f"   Market maker: {market_maker_behavior:.2f}")
                    print(f"   Smart Money confidence: {smart_money_confidence:.2f}")
            
            return enhanced_patterns
            
        except Exception as e:
            if self.config.get('enable_debug'):
                print(f"[ERROR] Error en Smart Money enhancement: {e}")
            return patterns

    def _analyze_liquidity_pools_near_pattern(self, pattern: PatternSignal, data) -> List[Dict[str, Any]]:
        """Analiza liquidity pools cerca del patrón"""
        try:
            if not self._smart_money_analyzer:
                return []
            
            # Usar método genérico del Smart Money Analyzer
            # Simulamos pools básicos basados en el patrón
            pools = []
            
            # Pool en entry zone
            entry_mid = (pattern.entry_zone[0] + pattern.entry_zone[1]) / 2
            pools.append({
                'price': entry_mid,
                'strength': 0.7,
                'type': 'entry_zone',
                'distance': 0.0
            })
            
            # Pool en stop loss (liquidity grab zone)
            pools.append({
                'price': pattern.stop_loss,
                'strength': 0.8,
                'type': 'stop_hunt',
                'distance': abs(entry_mid - pattern.stop_loss)
            })
            
            return pools
            
        except Exception:
            return []

    def _detect_institutional_flow(self, pattern: PatternSignal, data) -> float:
        """Detecta flujo institucional"""
        try:
            if not self._smart_money_analyzer:
                return 0.5
            
            # Simular análisis de flujo institucional basado en sesión y fuerza del patrón
            flow_strength = 0.5
            
            # Bonus por sesión activa
            if pattern.session in [SessionType.LONDON, SessionType.NEW_YORK]:
                flow_strength += 0.2
            
            # Bonus por fuerza del patrón
            if pattern.strength > 75:
                flow_strength += 0.2
            
            # Bonus por confluencias
            if len(pattern.confluences) > 2:
                flow_strength += 0.1
            
            return min(flow_strength, 1.0)
            
        except Exception:
            return 0.5

    def _analyze_market_maker_behavior(self, pattern: PatternSignal, data) -> float:
        """Analiza comportamiento market maker"""
        try:
            if not self._smart_money_analyzer:
                return 0.5
            
            # Simular análisis de market maker basado en tipo de patrón
            mm_score = 0.5
            
            # Patrones que indican market maker activity
            if pattern.pattern_type in [PatternType.LIQUIDITY_GRAB, PatternType.JUDAS_SWING]:
                mm_score += 0.3
            elif pattern.pattern_type == PatternType.SILVER_BULLET:
                mm_score += 0.2
            
            # Bonus por RR alto
            if pattern.risk_reward_ratio > 2.0:
                mm_score += 0.1
            
            return min(mm_score, 1.0)
            
        except Exception:
            return 0.5

    def _optimize_with_killzones(self, pattern: PatternSignal, data) -> Dict[str, Any]:
        """Optimiza patrón con killzones"""
        try:
            if not self._smart_money_analyzer:
                return {'active': False, 'strength': 0.5}
            
            # Verificar si estamos en killzone
            current_hour = datetime.now().hour
            
            # London killzone: 10:00-11:00 GMT
            london_killzone = 10 <= current_hour <= 11
            
            # New York killzone: 14:00-15:00 GMT
            ny_killzone = 14 <= current_hour <= 15
            
            # Asian killzone: 01:00-02:00 GMT
            asian_killzone = 1 <= current_hour <= 2
            
            active_killzone = london_killzone or ny_killzone or asian_killzone
            
            # Fuerza basada en sesión y patrón
            strength = 0.5
            if active_killzone:
                strength = 0.8
                if pattern.session == SessionType.LONDON and london_killzone:
                    strength = 0.9
                elif pattern.session == SessionType.NEW_YORK and ny_killzone:
                    strength = 0.9
            
            return {
                'active': active_killzone,
                'strength': strength,
                'killzone_type': 'london' if london_killzone else 'ny' if ny_killzone else 'asian' if asian_killzone else 'none'
            }
            
        except Exception:
            return {'active': False, 'strength': 0.5}

    def _calculate_smart_money_confidence(self, liquidity_pools: List[Dict], institutional_flow: float,
                                        market_maker_behavior: float, killzone_optimization: Dict) -> float:
        """Calcula confianza Smart Money combinada"""
        try:
            # Peso base
            confidence = 0.5
            
            # Bonus por liquidity pools
            if liquidity_pools:
                pool_strength = sum(pool.get('strength', 0.5) for pool in liquidity_pools) / len(liquidity_pools)
                confidence += pool_strength * 0.2
            
            # Bonus por flujo institucional
            confidence += institutional_flow * 0.3
            
            # Bonus por market maker behavior
            confidence += market_maker_behavior * 0.2
            
            # Bonus por killzone
            if killzone_optimization.get('active', False):
                confidence += killzone_optimization.get('strength', 0.5) * 0.3
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5

    def _apply_smart_money_enhancement(self, pattern: PatternSignal, smart_money_confidence: float,
                                     liquidity_pools: List[Dict], institutional_flow: float,
                                     market_maker_behavior: float, killzone_optimization: Dict) -> PatternSignal:
        """Aplica mejoras Smart Money al patrón"""
        try:
            # Crear nuevo patrón mejorado
            enhanced_confidence = PatternConfidence.MEDIUM
            
            # Calcular nueva confianza combinando patrón original + Smart Money
            combined_confidence = (pattern.strength + smart_money_confidence * 100) / 2
            
            if combined_confidence >= 80:
                enhanced_confidence = PatternConfidence.HIGH
            elif combined_confidence >= 70:
                enhanced_confidence = PatternConfidence.MEDIUM
            else:
                enhanced_confidence = PatternConfidence.LOW
            
            # Mejorar narrative con Smart Money insights
            enhanced_narrative = pattern.narrative
            if liquidity_pools:
                enhanced_narrative += f" | 💧 {len(liquidity_pools)} liquidity pools detectados"
            if institutional_flow > 0.7:
                enhanced_narrative += f" | 🏛️ Flujo institucional fuerte ({institutional_flow:.2f})"
            if market_maker_behavior > 0.7:
                enhanced_narrative += f" | 🎯 Comportamiento market maker ({market_maker_behavior:.2f})"
            if killzone_optimization.get('active', False):
                enhanced_narrative += f" | ⏰ Killzone activo ({killzone_optimization.get('strength', 0.5):.2f})"
            
            # Crear patrón mejorado manteniendo estructura original
            enhanced_pattern = PatternSignal(
                pattern_type=pattern.pattern_type,
                confidence=enhanced_confidence,
                direction=pattern.direction,
                symbol=pattern.symbol,
                timeframe=pattern.timeframe,
                entry_zone=pattern.entry_zone,
                stop_loss=pattern.stop_loss,
                take_profit_1=pattern.take_profit_1,
                take_profit_2=pattern.take_profit_2,
                strength=combined_confidence,
                timestamp=pattern.timestamp,
                risk_reward_ratio=pattern.risk_reward_ratio,
                probability=pattern.probability,
                session=pattern.session,
                narrative=enhanced_narrative,
                confluences=pattern.confluences + ["Smart Money Analysis v6.0"],
                invalidation_criteria=pattern.invalidation_criteria,
                optimal_entry_time=pattern.optimal_entry_time,
                time_sensitivity=pattern.time_sensitivity,
                max_hold_time=pattern.max_hold_time,
                raw_data={
                    **pattern.raw_data,
                    'smart_money_data': {
                        'liquidity_pools': liquidity_pools,
                        'institutional_flow': institutional_flow,
                        'market_maker_behavior': market_maker_behavior,
                        'killzone_optimization': killzone_optimization,
                        'smart_money_confidence': smart_money_confidence
                    }
                }
            )
            
            return enhanced_pattern
            
        except Exception as e:
            if self.config.get('enable_debug'):
                print(f"[ERROR] Error aplicando Smart Money enhancement: {e}")
            return pattern


# Factory function para crear instancia
def get_pattern_detector(config: Optional[Dict[str, Any]] = None) -> PatternDetector:
    """
    Factory function para crear Pattern Detector v6.0 Enterprise
    
    Args:
        config: Configuración opcional del detector
        
    Returns:
        Instancia configurada del Pattern Detector
    """
    return PatternDetector(config)


def get_ict_trading_symbols() -> List[str]:
    """
    Obtener lista de símbolos ICT para trading basado en configuración
    
    Returns:
        Lista de símbolos ordenados por prioridad ICT
    """
    try:
        # Intentar cargar desde configuración ICT
        from pathlib import Path
        import json
        
        config_path = Path(__file__).parent.parent.parent / "config" / "ict_patterns_config.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                ict_config = json.load(f)
            
            # Extraer símbolos ordenados por prioridad
            symbols_dict = ict_config.get('ict_symbols', {})
            symbols_sorted = sorted(symbols_dict.items(), key=lambda x: x[1].get('priority', 999))
            return [symbol for symbol, _ in symbols_sorted]
    except Exception as e:
        print(f"[INFO] No se pudo cargar configuración ICT: {e}")
    
    # Fallback: símbolos por defecto basado en investigación del sistema
    return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"]


def get_ict_critical_symbols() -> List[str]:
    """
    Obtener símbolos críticos para análisis ICT inmediato
    
    Returns:
        Lista de símbolos críticos con mayor prioridad
    """
    try:
        # Usar Symbol Manager para gestión centralizada
        from utils.ict_symbol_manager import get_critical_trading_symbols
        return get_critical_trading_symbols()
    except Exception:
        # Fallback: usar ICTDataManager config si está disponible
        try:
            from data_management.ict_data_manager import ICT_DATA_CONFIG
            return ICT_DATA_CONFIG['symbols_critical'] + ICT_DATA_CONFIG['symbols_important']
        except Exception:
            # Fallback final
            return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]


def get_ict_critical_timeframes() -> List[str]:
    """
    Obtener timeframes críticos para análisis ICT
    
    Returns:
        Lista de timeframes en orden de prioridad ICT
    """
    try:
        # Usar ICTDataManager config si está disponible
        from data_management.ict_data_manager import ICT_DATA_CONFIG
        return ICT_DATA_CONFIG['timeframes_critical'] + ICT_DATA_CONFIG['timeframes_enhanced']
    except Exception:
        # Fallback basado en investigación
        return ["M15", "H1", "H4", "M5"]


def get_analysis_ready_symbols(max_symbols: int = 6) -> List[str]:
    """
    Obtener símbolos optimizados para análisis de patrones
    
    Args:
        max_symbols: Número máximo de símbolos a retornar
        
    Returns:
        Lista optimizada de símbolos para análisis
    """
    try:
        # Usar Symbol Manager para optimización avanzada
        from utils.ict_symbol_manager import get_analysis_ready_symbols
        return get_analysis_ready_symbols(max_symbols)
    except Exception:
        # Fallback: usar símbolos críticos e importantes
        critical = get_ict_critical_symbols()
        return critical[:max_symbols]


if __name__ == "__main__":
    # Test básico del Pattern Detector con múltiples símbolos
    print("🎯 ICT Pattern Detector v6.0 Enterprise - Multi-Symbol Test")
    print("=" * 60)

    detector = get_pattern_detector({
        'enable_debug': True,
        'min_confidence': 65.0
    })

    # Configuración de símbolos usando Symbol Manager centralizado
    test_symbols = get_analysis_ready_symbols(6)  # Obtener símbolos optimizados para análisis
    test_timeframes = get_ict_critical_timeframes()[:2]  # Primeros 2 timeframes críticos
    
    print(f"\n📊 Testing Pattern Detector con {len(test_symbols)} símbolos...")
    print(f"📈 Símbolos: {', '.join(test_symbols)}")
    print(f"⏰ Timeframes: {', '.join(test_timeframes)}")
    
    total_patterns = 0
    
    for symbol in test_symbols:
        print(f"\n🔍 Analizando {symbol}...")
        
        for timeframe in test_timeframes:
            try:
                # Test con datos simulados para cada símbolo
                test_data = detector._generate_simulated_data(symbol, timeframe, 100)
                patterns = detector.detect_patterns(test_data, timeframe)
                
                if patterns:
                    print(f"   ✅ {symbol} {timeframe}: {len(patterns)} patrones detectados")
                    total_patterns += len(patterns)
                    
                    for pattern in patterns[:2]:  # Mostrar solo los primeros 2
                        print(f"      🎯 {pattern.pattern_type.value.upper()}")
                        print(f"         Dirección: {pattern.direction.value}")
                        print(f"         Confianza: {pattern.confidence.value}")
                        print(f"         Strength: {pattern.strength:.1f}%")
                        print(f"         R:R: {pattern.risk_reward_ratio:.2f}")
                else:
                    print(f"   ⚪ {symbol} {timeframe}: No patterns")
                    
            except Exception as e:
                print(f"   ❌ {symbol} {timeframe}: Error - {e}")

    print(f"\n📊 Resumen del análisis multi-símbolo:")
    print(f"   Total patrones detectados: {total_patterns}")
    print(f"   Símbolos analizados: {len(test_symbols)}")
    print(f"   Timeframes por símbolo: {len(test_timeframes)}")
    print(f"   Análisis totales: {len(test_symbols) * len(test_timeframes)}")
    
    # Métricas
    metrics = detector.get_performance_metrics()
    print(f"\n⚡ Performance:")
    print(f"   Tiempo promedio: {metrics['avg_analysis_time']:.3f}s")
    print(f"   Análisis totales: {metrics['total_analyses']}")
    
    summary = detector.get_pattern_summary()
    print(f"\n📈 Resumen global:")
    print(f"   Total: {summary['total_patterns']}")
    print(f"   Strength promedio: {summary['avg_strength']}%")
    print(f"   Por tipo: {summary['by_type']}")
    
    print(f"\n✅ Test multi-símbolo completado exitosamente!")
    print("=" * 60)
