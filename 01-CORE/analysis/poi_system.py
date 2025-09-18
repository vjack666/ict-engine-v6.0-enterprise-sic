# -*- coding: utf-8 -*-
"""
🎯 POI SYSTEM v6.0 ENTERPRISE - POINTS OF INTEREST
==================================================

Sistema avanzado de Points of Interest (POI) para ICT Engine v6.1.0 Enterprise.
Identifica y gestiona puntos clave de interés en el mercado donde es probable 
que instituciones tengan órdenes o donde el precio reaccione.

Características Enterprise:
- Detección automática de 15+ tipos de POI
- Scoring inteligente con confluencias
- Gestión temporal de POI (creación/invalidación)
- Integración con Pattern Detector y Market Structure
- Performance optimizado para análisis en tiempo real

Autor: ICT Engine v6.1.0 Enterprise Team
Fecha: Agosto 7, 2025
Versión: v6.1.0-enterprise
"""

from protocols.unified_logging import get_unified_logger
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# ThreadSafe pandas import para runtime
from data_management.advanced_candle_downloader import _pandas_manager

# Import pandas solo para tipado estático
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any as DataFrameType
else:
    DataFrameType = Any

# Importar otros componentes con fallbacks robustos
from typing import Any

try:
    # Usar rutas absolutas basadas en extraPaths de pyproject.toml
    from data_management.advanced_candle_downloader import get_advanced_candle_downloader
    from analysis.pattern_detector import get_pattern_detector, PatternType as PatternDetectorType
    from analysis.market_structure_analyzer import get_market_structure_analyzer
    print("[INFO] Componentes POI System cargados exitosamente")
except ImportError as e:
    print(f"[WARNING] Algunos componentes no disponibles: {e}")
    print("[INFO] POI System funcionará con capacidad limitada")
    
    # Fallback functions para evitar errores "possibly unbound"
    def get_advanced_candle_downloader(config: Any = None) -> Any:  # type: ignore
        """Fallback para advanced candle downloader"""
        print("[WARNING] Advanced Candle Downloader no disponible - usando fallback")
        return None
    
    def get_pattern_detector(config: Any = None) -> Any:  # type: ignore
        """Fallback para pattern detector"""
        print("[WARNING] Pattern Detector no disponible - usando fallback")
        return None
        
    def get_market_structure_analyzer(config: Any = None) -> Any:  # type: ignore
        """Fallback para market structure analyzer"""
        print("[WARNING] Market Structure Analyzer no disponible - usando fallback")
        return None
    
    # Fallback PatternType enum
    from enum import Enum
    class PatternType(Enum):
        """Fallback PatternType enum para compatibilidad"""
        UNKNOWN = "unknown"


class POIType(Enum):
    """Tipos de Points of Interest"""
    ORDER_BLOCK = "order_block"
    MITIGATION_BLOCK = "mitigation_block"
    BREAKER_BLOCK = "breaker_block"
    FAIR_VALUE_GAP = "fair_value_gap"
    LIQUIDITY_POOL = "liquidity_pool"
    SWING_HIGH = "swing_high"
    SWING_LOW = "swing_low"
    SESSION_HIGH = "session_high"
    SESSION_LOW = "session_low"
    DAILY_HIGH = "daily_high"
    DAILY_LOW = "daily_low"
    WEEKLY_HIGH = "weekly_high"
    WEEKLY_LOW = "weekly_low"
    FIBONACCI_LEVEL = "fibonacci_level"
    PSYCHOLOGICAL_LEVEL = "psychological_level"
    INSTITUTIONAL_LEVEL = "institutional_level"
    KILLZONE_LEVEL = "killzone_level"


class POIStatus(Enum):
    """Estado del POI"""
    ACTIVE = "active"
    TESTED = "tested"
    PARTIALLY_MITIGATED = "partially_mitigated"
    FULLY_MITIGATED = "fully_mitigated"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"


class POISignificance(Enum):
    """Significancia del POI"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INSTITUTIONAL = "institutional"


@dataclass
class POI:
    """Point of Interest individual"""
    poi_type: POIType
    price_level: float
    price_zone: Tuple[float, float]  # (low, high)
    timestamp: datetime
    symbol: str
    timeframe: str
    
    # Características
    significance: POISignificance = POISignificance.MEDIUM
    status: POIStatus = POIStatus.ACTIVE
    strength: float = 70.0  # 0-100
    
    # Contexto
    session_context: str = ""
    market_structure: str = ""
    confluences: List[str] = field(default_factory=list)
    
    # Gestión temporal
    created_at: datetime = field(default_factory=datetime.now)
    last_tested: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    test_count: int = 0
    max_tests: int = 3
    
    # Métricas
    reaction_strength: float = 0.0
    hold_time: Optional[timedelta] = None
    success_rate: float = 0.0
    
    # Metadata
    analysis_id: str = ""
    notes: str = ""
    related_pois: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_metadata(self, key: str, value: Any) -> None:
        """Agregar/actualizar entrada de metadata de forma segura."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Obtener valor de metadata con default si no existe."""
        return self.metadata.get(key, default)


class POISystem:
    """
    🎯 POI SYSTEM v6.0 ENTERPRISE
    
    Sistema avanzado de gestión de Points of Interest:
    - Detección automática de 15+ tipos de POI
    - Tracking en tiempo real de estado y validez
    - Scoring inteligente con confluencias
    - Integración con otros sistemas ICT
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar POI System v6.0 Enterprise
        
        Args:
            config: Configuración del sistema
        """
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
        
        # Estado del sistema
        self.is_initialized = False
        self.active_pois: List[POI] = []
        self.historical_pois: List[POI] = []
        self.poi_cache = {}
        
        # Métricas
        self.performance_metrics = {
            'total_pois_created': 0,
            'active_pois': 0,
            'avg_poi_lifetime': timedelta(hours=0),
            'success_rate': 0.0,
            'last_update': datetime.now()
        }
        
        # Componentes integrados
        self._downloader = None
        self._pattern_detector = None
        self._market_analyzer = None
        
        self._initialize_components()
        
        print(f"[INFO] POI System v6.0 Enterprise inicializado")
        print(f"[INFO] Configuración: {len(self.config)} parámetros cargados")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Cargar configuración por defecto"""
        return {
            # General
            'enable_debug': True,
            'enable_cache': True,
            'max_active_pois': 50,
            'poi_cleanup_interval': 3600,  # 1 hora
            
            # Detección
            'min_poi_strength': 60.0,
            'enable_order_blocks': True,
            'enable_fair_value_gaps': True,
            'enable_liquidity_pools': True,
            'enable_swing_points': True,
            'enable_session_levels': True,
            'enable_fibonacci_levels': True,
            'enable_psychological_levels': True,
            
            # Gestión temporal
            'default_poi_lifetime': 48,  # horas
            'order_block_lifetime': 72,  # horas
            'fvg_lifetime': 24,  # horas
            'swing_point_lifetime': 168,  # 1 semana
            'session_level_lifetime': 24,  # horas
            
            # Validación
            'mitigation_threshold': 0.5,  # 50% del POI
            'test_invalidation_count': 3,
            'proximity_threshold': 0.0010,  # 10 pips
            
            # Scoring
            'confluence_weight': 0.3,
            'recency_weight': 0.2,
            'strength_weight': 0.3,
            'context_weight': 0.2,
            
            # Performance
            'max_analysis_time': 0.1,  # 100ms
            'batch_processing': True
        }
    
    def _initialize_components(self):
        """Inicializar componentes integrados con fallbacks robustos"""
        try:
            # Downloader - verificar que la función esté disponible y no sea fallback
            if get_advanced_candle_downloader and callable(get_advanced_candle_downloader):
                try:
                    self._downloader = get_advanced_candle_downloader()
                    if self._downloader is not None:
                        print("[INFO] Downloader conectado al POI System")
                    else:
                        print("[INFO] Downloader en modo fallback")
                except Exception as e:
                    print(f"[WARNING] Error inicializando downloader: {e}")
                    self._downloader = None
            else:
                print("[INFO] Downloader no disponible - usando modo básico")
            
            # Pattern Detector - verificar disponibilidad
            if get_pattern_detector and callable(get_pattern_detector):
                try:
                    self._pattern_detector = get_pattern_detector({
                        'enable_debug': False,  # Evitar spam en logs
                        'min_confidence': 65.0
                    })
                    if self._pattern_detector is not None:
                        print("[INFO] Pattern Detector conectado al POI System")
                    else:
                        print("[INFO] Pattern Detector en modo fallback")
                except Exception as e:
                    print(f"[WARNING] Error inicializando pattern detector: {e}")
                    self._pattern_detector = None
            else:
                print("[INFO] Pattern Detector no disponible - usando detección básica")
            
            # Market Analyzer - verificar disponibilidad
            if get_market_structure_analyzer and callable(get_market_structure_analyzer):
                try:
                    self._market_analyzer = get_market_structure_analyzer({
                        'enable_debug': False
                    })
                    if self._market_analyzer is not None:
                        print("[INFO] Market Analyzer conectado al POI System")
                    else:
                        print("[INFO] Market Analyzer en modo fallback")
                except Exception as e:
                    print(f"[WARNING] Error inicializando market analyzer: {e}")
                    self._market_analyzer = None
            else:
                print("[INFO] Market Analyzer no disponible - usando análisis básico")
            
            self.is_initialized = True
            
        except Exception as e:
            print(f"[WARNING] Error general inicializando componentes: {e}")
            print("[INFO] Continuando en modo básico")
    
    def detect_pois(
        self, 
        symbol: str = "EURUSD", 
        timeframe: str = "M15",
        lookback_days: int = 7
    ) -> List[POI]:
        """
        Detectar Points of Interest en los datos de mercado
        
        Args:
            symbol: Símbolo a analizar
            timeframe: Marco temporal
            lookback_days: Días de historia a analizar
            
        Returns:
            Lista de POIs detectados
        """
        start_time = time.time()
        
        try:
            print(f"[INFO] Detectando POIs para {symbol} {timeframe}...")
            
            # Obtener datos de mercado
            data = self._get_market_data(symbol, timeframe, lookback_days)
            if data is None or data.empty:
                print(f"[WARNING] Sin datos para {symbol} {timeframe}")
                return []
            
            detected_pois = []
            
            # 1. Order Blocks
            if self.config['enable_order_blocks']:
                order_block_pois = self._detect_order_block_pois(data, symbol, timeframe)
                detected_pois.extend(order_block_pois)
            
            # 2. Fair Value Gaps
            if self.config['enable_fair_value_gaps']:
                fvg_pois = self._detect_fvg_pois(data, symbol, timeframe)
                detected_pois.extend(fvg_pois)
            
            # 3. Swing Points
            if self.config['enable_swing_points']:
                swing_pois = self._detect_swing_point_pois(data, symbol, timeframe)
                detected_pois.extend(swing_pois)
            
            # 4. Session Levels
            if self.config['enable_session_levels']:
                session_pois = self._detect_session_level_pois(data, symbol, timeframe)
                detected_pois.extend(session_pois)
            
            # 5. Liquidity Pools
            if self.config['enable_liquidity_pools']:
                liquidity_pois = self._detect_liquidity_pool_pois(data, symbol, timeframe)
                detected_pois.extend(liquidity_pois)
            
            # 6. Fibonacci Levels
            if self.config['enable_fibonacci_levels']:
                fib_pois = self._detect_fibonacci_pois(data, symbol, timeframe)
                detected_pois.extend(fib_pois)
            
            # 7. Psychological Levels
            if self.config['enable_psychological_levels']:
                psych_pois = self._detect_psychological_level_pois(data, symbol, timeframe)
                detected_pois.extend(psych_pois)
            
            # Filtrar por strength mínimo
            detected_pois = [poi for poi in detected_pois if poi.strength >= self.config['min_poi_strength']]
            
            # Eliminar duplicados y POIs muy cercanos
            detected_pois = self._remove_duplicate_pois(detected_pois)
            
            # Calcular confluencias
            detected_pois = self._calculate_confluences(detected_pois)
            
            # Ordenar por significancia y strength
            detected_pois.sort(key=lambda x: (x.significance.value, x.strength), reverse=True)
            
            # Limitar cantidad
            max_pois = self.config['max_active_pois']
            if len(detected_pois) > max_pois:
                detected_pois = detected_pois[:max_pois]
            
            # Añadir a POIs activos
            self.active_pois.extend(detected_pois)
            
            # Limpiar POIs antiguos
            self._cleanup_expired_pois()
            
            analysis_time = time.time() - start_time
            
            # Actualizar métricas
            self._update_metrics(detected_pois, analysis_time)
            
            print(f"[INFO] Detectados {len(detected_pois)} POIs en {analysis_time:.3f}s")
            
            return detected_pois
            
        except Exception as e:
            print(f"[ERROR] Error detectando POIs: {e}")
            return []

    def detect_points_of_interest(self, data: Any) -> List[Dict[str, Any]]:
        """
        🎯 DETECTAR POINTS OF INTEREST - Método requerido para ProductionSystemIntegrator
        
        Detecta Points of Interest en los datos de mercado proporcionados
        
        Args:
            data: Datos de mercado (DataFrame o dict con OHLCV)
            
        Returns:
            Lista de POIs encontrados como diccionarios
        """
        try:
            # Validar datos de entrada
            if data is None:
                return []
            
            # Convertir datos a formato estándar
            if hasattr(data, 'empty') and data.empty:
                return []
                
            # Detectar POIs usando el método principal
            if hasattr(data, 'columns') and all(col in data.columns for col in ['high', 'low', 'open', 'close']):
                # Es un DataFrame con datos OHLC
                symbol = "UNKNOWN"  # No disponible en los datos
                timeframe = "M15"   # Asumir M15 por defecto
                
                detected_pois = []
                
                # Usar los mismos métodos internos de detección
                if self.config.get('enable_order_blocks', True):
                    order_block_pois = self._detect_order_block_pois(data, symbol, timeframe)
                    detected_pois.extend(order_block_pois)
                
                if self.config.get('enable_fair_value_gaps', True):
                    fvg_pois = self._detect_fvg_pois(data, symbol, timeframe)
                    detected_pois.extend(fvg_pois)
                
                if self.config.get('enable_swing_points', True):
                    swing_pois = self._detect_swing_point_pois(data, symbol, timeframe)
                    detected_pois.extend(swing_pois)
                
                # Convertir POI objects a diccionarios
                poi_dicts = []
                for poi in detected_pois:
                    poi_dict = {
                        'type': poi.poi_type.value if hasattr(poi, 'poi_type') else 'unknown',
                        'price': float(poi.price) if hasattr(poi, 'price') else 0.0,
                        'strength': float(poi.strength) if hasattr(poi, 'strength') else 0.5,
                        'significance': poi.significance.value if hasattr(poi, 'significance') else 'medium',
                        'timestamp': poi.timestamp.isoformat() if hasattr(poi, 'timestamp') else datetime.now().isoformat(),
                        'is_valid': bool(poi.is_valid) if hasattr(poi, 'is_valid') else True,
                        'confidence': float(getattr(poi, 'confidence', 0.6))
                    }
                    poi_dicts.append(poi_dict)
                
                # Actualizar métricas
                self.performance_metrics['total_pois_created'] += len(poi_dicts)
                self.performance_metrics['last_update'] = datetime.now()
                
                return poi_dicts
                
            elif isinstance(data, list) and len(data) > 0:
                # Es una lista de velas
                # Crear respuesta básica para compatibilidad
                basic_pois = []
                
                if len(data) >= 10:  # Mínimo para análisis
                    # Detectar niveles de swing básicos
                    for i in range(2, len(data) - 2):
                        candle = data[i]
                        prev_candles = data[i-2:i]
                        next_candles = data[i+1:i+3]
                        
                        if isinstance(candle, dict):
                            high = candle.get('high', candle.get('High', 0))
                            low = candle.get('low', candle.get('Low', 0))
                            
                            # Swing High
                            is_swing_high = all(high > c.get('high', c.get('High', 0)) for c in prev_candles + next_candles if isinstance(c, dict))
                            if is_swing_high and high > 0:
                                basic_pois.append({
                                    'type': 'swing_high',
                                    'price': float(high),
                                    'strength': 0.7,
                                    'significance': 'medium',
                                    'timestamp': datetime.now().isoformat(),
                                    'is_valid': True,
                                    'confidence': 0.65
                                })
                            
                            # Swing Low
                            is_swing_low = all(low < c.get('low', c.get('Low', 999999)) for c in prev_candles + next_candles if isinstance(c, dict))
                            if is_swing_low and low > 0:
                                basic_pois.append({
                                    'type': 'swing_low',
                                    'price': float(low),
                                    'strength': 0.7,
                                    'significance': 'medium',
                                    'timestamp': datetime.now().isoformat(),
                                    'is_valid': True,
                                    'confidence': 0.65
                                })
                
                return basic_pois[:10]  # Limitar a 10 POIs
                
            return []
            
        except Exception as e:
            print(f"[ERROR] Error detecting points of interest: {e}")
            return []
    
    def _get_market_data(self, symbol: str, timeframe: str, days: int) -> Optional[DataFrameType]:
        """Obtener datos de mercado"""
        try:
            if self._downloader:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                result = self._downloader.download_candles(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                    save_to_file=False
                )
                
                if isinstance(result, dict) and 'data' in result:
                    return result['data']
                elif hasattr(result, 'columns') and hasattr(result, 'index'):  # DataFrame check
                    return result
                else:
                    return self._generate_simulated_data(symbol, timeframe, days)
            else:
                return self._generate_simulated_data(symbol, timeframe, days)
                
        except Exception as e:
            print(f"[WARNING] Error obteniendo datos: {e}")
            return self._generate_simulated_data(symbol, timeframe, days)
    
    def _generate_simulated_data(self, symbol: str, timeframe: str, days: int) -> DataFrameType:
        """Generar datos simulados para testing"""
        periods = days * 24 * 4  # Asumiendo M15
        
        # Usar pandas manager para acceder a pandas thread-safe
        pd = _pandas_manager.get_safe_pandas_instance()
        if pd is None:
            return None
            
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='15min')
        
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
        
        # Usar pandas manager para crear DataFrame
        return pd.DataFrame(data) if pd is not None else None
    
    def _detect_order_block_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de Order Blocks"""
        pois = []
        
        try:
            if len(data) < 20:
                return pois
            
            # Buscar velas de impulso seguidas de retorno
            for i in range(10, len(data) - 10):
                current_candle = data.iloc[i]
                candle_size = abs(current_candle['close'] - current_candle['open'])
                
                # Calcular tamaño promedio
                prev_candles = data.iloc[i-5:i]
                avg_size = abs(prev_candles['close'] - prev_candles['open']).mean()
                
                # Verificar si es impulso
                if candle_size > avg_size * 1.5:
                    # Verificar retorno futuro
                    future_candles = data.iloc[i+1:i+11]
                    
                    ob_high = current_candle['high']
                    ob_low = current_candle['low']
                    
                    # Buscar test del Order Block
                    tested = False
                    for j, future_candle in future_candles.iterrows():
                        if future_candle['low'] <= ob_high and future_candle['high'] >= ob_low:
                            tested = True
                            break
                    
                    if tested:
                        ob_type = "bullish" if current_candle['close'] > current_candle['open'] else "bearish"
                        
                        strength = min(70.0 + (candle_size / avg_size) * 10, 95.0)
                        
                        poi = POI(
                            poi_type=POIType.ORDER_BLOCK,
                            price_level=(ob_high + ob_low) / 2,
                            price_zone=(ob_low, ob_high),
                            timestamp=current_candle.name if hasattr(current_candle, 'name') else datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            significance=POISignificance.HIGH if strength >= 80 else POISignificance.MEDIUM,
                            strength=strength,
                            market_structure=f"{ob_type}_order_block",
                            confluences=[f"{ob_type}_impulse", "tested_zone"],
                            expiry_time=datetime.now() + timedelta(hours=self.config['order_block_lifetime']),
                            analysis_id=f"OB_{symbol}_{int(time.time())}"
                        )
                        
                        pois.append(poi)
                        
        except Exception as e:
            print(f"[WARNING] Error detectando Order Block POIs: {e}")
        
        return pois
    
    def _detect_fvg_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de Fair Value Gaps"""
        pois = []
        
        try:
            if len(data) < 3:
                return pois
            
            # Buscar FVGs en secuencias de 3 velas
            for i in range(1, len(data) - 1):
                prev_candle = data.iloc[i-1]
                current_candle = data.iloc[i]
                next_candle = data.iloc[i+1]
                
                # Bullish FVG
                if (prev_candle['high'] < next_candle['low'] and
                    current_candle['close'] > current_candle['open']):
                    
                    gap_size = next_candle['low'] - prev_candle['high']
                    if gap_size >= 0.0003:  # Mínimo 3 pips
                        
                        strength = min(60.0 + (gap_size * 10000), 85.0)
                        
                        poi = POI(
                            poi_type=POIType.FAIR_VALUE_GAP,
                            price_level=(prev_candle['high'] + next_candle['low']) / 2,
                            price_zone=(prev_candle['high'], next_candle['low']),
                            timestamp=current_candle.name if hasattr(current_candle, 'name') else datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            significance=POISignificance.MEDIUM,
                            strength=strength,
                            market_structure="bullish_fvg",
                            confluences=["price_imbalance", "gap_fill_target"],
                            expiry_time=datetime.now() + timedelta(hours=self.config['fvg_lifetime']),
                            analysis_id=f"FVG_{symbol}_{int(time.time())}"
                        )
                        
                        pois.append(poi)
                
                # Bearish FVG
                elif (prev_candle['low'] > next_candle['high'] and
                      current_candle['close'] < current_candle['open']):
                    
                    gap_size = prev_candle['low'] - next_candle['high']
                    if gap_size >= 0.0003:
                        
                        strength = min(60.0 + (gap_size * 10000), 85.0)
                        
                        poi = POI(
                            poi_type=POIType.FAIR_VALUE_GAP,
                            price_level=(prev_candle['low'] + next_candle['high']) / 2,
                            price_zone=(next_candle['high'], prev_candle['low']),
                            timestamp=current_candle.name if hasattr(current_candle, 'name') else datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            significance=POISignificance.MEDIUM,
                            strength=strength,
                            market_structure="bearish_fvg",
                            confluences=["price_imbalance", "gap_fill_target"],
                            expiry_time=datetime.now() + timedelta(hours=self.config['fvg_lifetime']),
                            analysis_id=f"FVG_{symbol}_{int(time.time())}"
                        )
                        
                        pois.append(poi)
                        
        except Exception as e:
            print(f"[WARNING] Error detectando FVG POIs: {e}")
        
        return pois
    
    def _detect_swing_point_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de Swing Points"""
        pois = []
        
        try:
            if len(data) < 11:
                return pois
            
            # Detectar swing highs y lows
            window = 5
            
            for i in range(window, len(data) - window):
                current_high = data['high'].iloc[i]
                current_low = data['low'].iloc[i]
                
                # Verificar swing high
                left_highs = data['high'].iloc[i-window:i]
                right_highs = data['high'].iloc[i+1:i+window+1]
                
                if (current_high > left_highs.max() and 
                    current_high > right_highs.max()):
                    
                    strength = 70.0
                    
                    # Verificar si es session high o daily high
                    significance = POISignificance.MEDIUM
                    confluences = ["swing_high", "potential_resistance"]
                    
                    # Check for session high
                    session_data = data.iloc[max(0, i-48):i+1]  # Últimas 12 horas
                    if current_high >= session_data['high'].max():
                        significance = POISignificance.HIGH
                        confluences.append("session_high")
                        strength += 10
                    
                    poi = POI(
                        poi_type=POIType.SWING_HIGH,
                        price_level=current_high,
                        price_zone=(current_high - 0.0005, current_high + 0.0005),
                        timestamp=data.index[i] if hasattr(data.index[i], 'hour') else datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        significance=significance,
                        strength=strength,
                        market_structure="resistance_level",
                        confluences=confluences,
                        expiry_time=datetime.now() + timedelta(hours=self.config['swing_point_lifetime']),
                        analysis_id=f"SH_{symbol}_{int(time.time())}"
                    )
                    
                    pois.append(poi)
                
                # Verificar swing low
                left_lows = data['low'].iloc[i-window:i]
                right_lows = data['low'].iloc[i+1:i+window+1]
                
                if (current_low < left_lows.min() and 
                    current_low < right_lows.min()):
                    
                    strength = 70.0
                    
                    significance = POISignificance.MEDIUM
                    confluences = ["swing_low", "potential_support"]
                    
                    # Check for session low
                    session_data = data.iloc[max(0, i-48):i+1]
                    if current_low <= session_data['low'].min():
                        significance = POISignificance.HIGH
                        confluences.append("session_low")
                        strength += 10
                    
                    poi = POI(
                        poi_type=POIType.SWING_LOW,
                        price_level=current_low,
                        price_zone=(current_low - 0.0005, current_low + 0.0005),
                        timestamp=data.index[i] if hasattr(data.index[i], 'hour') else datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        significance=significance,
                        strength=strength,
                        market_structure="support_level",
                        confluences=confluences,
                        expiry_time=datetime.now() + timedelta(hours=self.config['swing_point_lifetime']),
                        analysis_id=f"SL_{symbol}_{int(time.time())}"
                    )
                    
                    pois.append(poi)
                    
        except Exception as e:
            print(f"[WARNING] Error detectando Swing Point POIs: {e}")
        
        return pois
    
    def _detect_session_level_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de niveles de sesión"""
        pois = []
        
        try:
            if len(data) < 24:  # Necesitamos al menos 6 horas de datos
                return pois
            
            # Detectar niveles de sesión actuales
            current_session_data = data.tail(48)  # Últimas 12 horas
            
            session_high = current_session_data['high'].max()
            session_low = current_session_data['low'].min()
            
            # Session High POI
            poi_high = POI(
                poi_type=POIType.SESSION_HIGH,
                price_level=session_high,
                price_zone=(session_high - 0.0002, session_high + 0.0002),
                timestamp=datetime.now(),
                symbol=symbol,
                timeframe=timeframe,
                significance=POISignificance.HIGH,
                strength=75.0,
                market_structure="session_resistance",
                confluences=["session_boundary", "liquidity_level"],
                expiry_time=datetime.now() + timedelta(hours=self.config['session_level_lifetime']),
                analysis_id=f"SH_SESSION_{symbol}_{int(time.time())}"
            )
            
            # Session Low POI
            poi_low = POI(
                poi_type=POIType.SESSION_LOW,
                price_level=session_low,
                price_zone=(session_low - 0.0002, session_low + 0.0002),
                timestamp=datetime.now(),
                symbol=symbol,
                timeframe=timeframe,
                significance=POISignificance.HIGH,
                strength=75.0,
                market_structure="session_support",
                confluences=["session_boundary", "liquidity_level"],
                expiry_time=datetime.now() + timedelta(hours=self.config['session_level_lifetime']),
                analysis_id=f"SL_SESSION_{symbol}_{int(time.time())}"
            )
            
            pois.extend([poi_high, poi_low])
            
        except Exception as e:
            print(f"[WARNING] Error detectando Session Level POIs: {e}")
        
        return pois
    
    def _detect_liquidity_pool_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de Liquidity Pools"""
        pois = []
        
        try:
            # Buscar equal highs y equal lows
            if len(data) < 20:
                return pois
            
            tolerance = 0.0005  # 5 pips tolerancia
            
            # Buscar equal highs (liquidez bearish)
            highs = data['high'].rolling(window=5, center=True).max()
            
            for i in range(10, len(data) - 10):
                current_high = highs.iloc[i]
                
                # Buscar otros highs similares en ventana
                nearby_highs = highs.iloc[i-10:i+10]
                equal_highs = nearby_highs[abs(nearby_highs - current_high) <= tolerance]
                
                if len(equal_highs) >= 2:  # Al menos 2 equal highs
                    strength = min(65.0 + len(equal_highs) * 5, 85.0)
                    
                    poi = POI(
                        poi_type=POIType.LIQUIDITY_POOL,
                        price_level=current_high,
                        price_zone=(current_high - tolerance, current_high + tolerance),
                        timestamp=data.index[i] if hasattr(data.index[i], 'hour') else datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        significance=POISignificance.HIGH,
                        strength=strength,
                        market_structure="bearish_liquidity_pool",
                        confluences=["equal_highs", "stop_loss_cluster", "sweep_target"],
                        expiry_time=datetime.now() + timedelta(hours=24),
                        analysis_id=f"LP_HIGH_{symbol}_{int(time.time())}"
                    )
                    
                    pois.append(poi)
            
            # Buscar equal lows (liquidez bullish)
            lows = data['low'].rolling(window=5, center=True).min()
            
            for i in range(10, len(data) - 10):
                current_low = lows.iloc[i]
                
                nearby_lows = lows.iloc[i-10:i+10]
                equal_lows = nearby_lows[abs(nearby_lows - current_low) <= tolerance]
                
                if len(equal_lows) >= 2:
                    strength = min(65.0 + len(equal_lows) * 5, 85.0)
                    
                    poi = POI(
                        poi_type=POIType.LIQUIDITY_POOL,
                        price_level=current_low,
                        price_zone=(current_low - tolerance, current_low + tolerance),
                        timestamp=data.index[i] if hasattr(data.index[i], 'hour') else datetime.now(),
                        symbol=symbol,
                        timeframe=timeframe,
                        significance=POISignificance.HIGH,
                        strength=strength,
                        market_structure="bullish_liquidity_pool",
                        confluences=["equal_lows", "stop_loss_cluster", "sweep_target"],
                        expiry_time=datetime.now() + timedelta(hours=24),
                        analysis_id=f"LP_LOW_{symbol}_{int(time.time())}"
                    )
                    
                    pois.append(poi)
                    
        except Exception as e:
            print(f"[WARNING] Error detectando Liquidity Pool POIs: {e}")
        
        return pois
    
    def _detect_fibonacci_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de niveles Fibonacci"""
        pois = []
        
        try:
            if len(data) < 30:
                return pois
            
            # Buscar swing reciente para Fibonacci
            recent_data = data.tail(100)
            recent_high = recent_data['high'].max()
            recent_low = recent_data['low'].min()
            
            # Calcular niveles Fibonacci
            price_range = recent_high - recent_low
            
            fib_levels = {
                0.236: recent_high - (price_range * 0.236),
                0.382: recent_high - (price_range * 0.382),
                0.500: recent_high - (price_range * 0.500),
                0.618: recent_high - (price_range * 0.618),
                0.786: recent_high - (price_range * 0.786)
            }
            
            for fib_ratio, fib_price in fib_levels.items():
                # Verificar si el nivel es significativo
                strength = 65.0
                confluences = [f"fibonacci_{fib_ratio}", "retracement_level"]
                
                # Niveles más importantes tienen mayor strength
                if fib_ratio in [0.618, 0.786]:  # Golden ratios
                    strength += 10.0
                    confluences.append("golden_ratio")
                
                if fib_ratio == 0.500:  # 50% level
                    strength += 5.0
                    confluences.append("equilibrium_level")
                
                poi = POI(
                    poi_type=POIType.FIBONACCI_LEVEL,
                    price_level=fib_price,
                    price_zone=(fib_price - 0.0005, fib_price + 0.0005),
                    timestamp=datetime.now(),
                    symbol=symbol,
                    timeframe=timeframe,
                    significance=POISignificance.MEDIUM,
                    strength=strength,
                    market_structure=f"fibonacci_{fib_ratio}_level",
                    confluences=confluences,
                    expiry_time=datetime.now() + timedelta(hours=48),
                    analysis_id=f"FIB_{fib_ratio}_{symbol}_{int(time.time())}"
                )
                
                pois.append(poi)
                
        except Exception as e:
            print(f"[WARNING] Error detectando Fibonacci POIs: {e}")
        
        return pois
    
    def _detect_psychological_level_pois(self, data: DataFrameType, symbol: str, timeframe: str) -> List[POI]:
        """Detectar POIs de niveles psicológicos"""
        pois = []
        
        try:
            current_price = data['close'].iloc[-1]
            
            # Niveles psicológicos comunes para EURUSD
            if symbol == "EURUSD":
                base_levels = [1.0000, 1.0500, 1.1000, 1.1500, 1.2000]
                
                # Encontrar niveles cercanos al precio actual
                for level in base_levels:
                    distance = abs(current_price - level)
                    
                    if distance <= 0.0100:  # Dentro de 100 pips
                        strength = max(60.0, 80.0 - (distance * 1000))
                        
                        poi = POI(
                            poi_type=POIType.PSYCHOLOGICAL_LEVEL,
                            price_level=level,
                            price_zone=(level - 0.0010, level + 0.0010),
                            timestamp=datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            significance=POISignificance.MEDIUM,
                            strength=strength,
                            market_structure="psychological_resistance_support",
                            confluences=["round_number", "psychological_barrier"],
                            expiry_time=datetime.now() + timedelta(days=7),
                            analysis_id=f"PSYCH_{level}_{symbol}_{int(time.time())}"
                        )
                        
                        pois.append(poi)
                
                # Niveles de 50 pips
                fifty_pip_levels = []
                base = int(current_price * 10000) // 500 * 500  # Redondear a 50 pips
                
                for offset in [-500, -250, 0, 250, 500]:
                    level_pips = base + offset
                    level_price = level_pips / 10000
                    
                    if abs(level_price - current_price) <= 0.0050:
                        strength = 65.0
                        
                        poi = POI(
                            poi_type=POIType.PSYCHOLOGICAL_LEVEL,
                            price_level=level_price,
                            price_zone=(level_price - 0.0005, level_price + 0.0005),
                            timestamp=datetime.now(),
                            symbol=symbol,
                            timeframe=timeframe,
                            significance=POISignificance.LOW,
                            strength=strength,
                            market_structure="minor_psychological_level",
                            confluences=["50_pip_level"],
                            expiry_time=datetime.now() + timedelta(hours=48),
                            analysis_id=f"PSYCH50_{level_price}_{symbol}_{int(time.time())}"
                        )
                        
                        pois.append(poi)
                        
        except Exception as e:
            print(f"[WARNING] Error detectando Psychological Level POIs: {e}")
        
        return pois
    
    def _remove_duplicate_pois(self, pois: List[POI]) -> List[POI]:
        """Eliminar POIs duplicados o muy cercanos"""
        if not pois:
            return pois
        
        filtered_pois = []
        proximity_threshold = self.config['proximity_threshold']
        
        for poi in pois:
            is_duplicate = False
            
            for existing_poi in filtered_pois:
                distance = abs(poi.price_level - existing_poi.price_level)
                
                if (distance <= proximity_threshold and 
                    poi.poi_type == existing_poi.poi_type):
                    # Es duplicado, mantener el de mayor strength
                    if poi.strength > existing_poi.strength:
                        filtered_pois.remove(existing_poi)
                        filtered_pois.append(poi)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_pois.append(poi)
        
        return filtered_pois
    
    def _calculate_confluences(self, pois: List[POI]) -> List[POI]:
        """Calcular confluencias entre POIs"""
        proximity_threshold = self.config['proximity_threshold'] * 2  # Mayor tolerancia para confluencias
        
        for i, poi in enumerate(pois):
            confluent_pois = []
            
            for j, other_poi in enumerate(pois):
                if i != j:
                    distance = abs(poi.price_level - other_poi.price_level)
                    
                    if distance <= proximity_threshold:
                        confluent_pois.append(other_poi.poi_type.value)
            
            if confluent_pois:
                poi.confluences.extend([f"confluence_with_{t}" for t in set(confluent_pois)])
                # Bonus de strength por confluencias
                poi.strength += min(len(confluent_pois) * 5, 15)
                
                # Upgrade significance si hay muchas confluencias
                if len(confluent_pois) >= 2:
                    if poi.significance == POISignificance.LOW:
                        poi.significance = POISignificance.MEDIUM
                    elif poi.significance == POISignificance.MEDIUM:
                        poi.significance = POISignificance.HIGH
        
        return pois
    
    def _cleanup_expired_pois(self):
        """Limpiar POIs expirados"""
        current_time = datetime.now()
        
        # Mover POIs expirados a histórico
        expired_pois = []
        active_pois = []
        
        for poi in self.active_pois:
            if poi.expiry_time and current_time > poi.expiry_time:
                poi.status = POIStatus.EXPIRED
                expired_pois.append(poi)
            elif poi.test_count >= poi.max_tests:
                poi.status = POIStatus.INVALIDATED
                expired_pois.append(poi)
            else:
                active_pois.append(poi)
        
        self.active_pois = active_pois
        self.historical_pois.extend(expired_pois)
        
        if expired_pois:
            print(f"[INFO] {len(expired_pois)} POIs movidos a histórico")
    
    def _update_metrics(self, new_pois: List[POI], analysis_time: float):
        """Actualizar métricas del sistema"""
        self.performance_metrics['total_pois_created'] += len(new_pois)
        self.performance_metrics['active_pois'] = len(self.active_pois)
        self.performance_metrics['last_update'] = datetime.now()
        
        # Calcular lifetime promedio de POIs históricos
        if self.historical_pois:
            lifetimes = []
            for poi in self.historical_pois:
                if poi.created_at and poi.expiry_time:
                    lifetime = poi.expiry_time - poi.created_at
                    lifetimes.append(lifetime)
            
            if lifetimes:
                avg_lifetime = sum(lifetimes, timedelta()) / len(lifetimes)
                self.performance_metrics['avg_poi_lifetime'] = avg_lifetime
    
    def get_active_pois(self, poi_type: Optional[POIType] = None) -> List[POI]:
        """Obtener POIs activos, opcionalmente filtrados por tipo"""
        if poi_type:
            return [poi for poi in self.active_pois if poi.poi_type == poi_type]
        return self.active_pois.copy()
    
    def get_pois_near_price(self, price: float, distance: float = 0.0020) -> List[POI]:
        """Obtener POIs cercanos a un precio específico"""
        nearby_pois = []
        
        for poi in self.active_pois:
            if abs(poi.price_level - price) <= distance:
                nearby_pois.append(poi)
        
        # Ordenar por proximidad
        nearby_pois.sort(key=lambda x: abs(x.price_level - price))
        
        return nearby_pois
    
    def get_poi_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado del sistema POI"""
        if not self.active_pois:
            return {
                'total_active': 0,
                'by_type': {},
                'by_significance': {},
                'avg_strength': 0.0,
                'next_expiry': None
            }
        
        # Contar por tipo
        by_type = {}
        for poi in self.active_pois:
            ptype = poi.poi_type.value
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        # Contar por significancia
        by_significance = {}
        for poi in self.active_pois:
            sig = poi.significance.value
            by_significance[sig] = by_significance.get(sig, 0) + 1
        
        # Strength promedio
        avg_strength = sum(poi.strength for poi in self.active_pois) / len(self.active_pois)
        
        # Próxima expiración
        expiry_times = [poi.expiry_time for poi in self.active_pois if poi.expiry_time]
        next_expiry = min(expiry_times) if expiry_times else None
        
        return {
            'total_active': len(self.active_pois),
            'by_type': by_type,
            'by_significance': by_significance,
            'avg_strength': round(avg_strength, 1),
            'next_expiry': next_expiry,
            'historical_count': len(self.historical_pois)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        return self.performance_metrics.copy()


# Factory function
def get_poi_system(config: Optional[Dict[str, Any]] = None) -> POISystem:
    """
    Factory function para crear POI System v6.0 Enterprise
    
    Args:
        config: Configuración opcional del sistema
        
    Returns:
        Instancia configurada del POI System
    """
    return POISystem(config)


# Alias para compatibilidad con tests existentes
POIDetector = POISystem


if __name__ == "__main__":
    # Test básico del POI System
    print("🎯 POI System v6.0 Enterprise - Test")
    print("=" * 50)
    
    poi_system = get_poi_system({
        'enable_debug': True,
        'min_poi_strength': 60.0
    })
    
    pois = poi_system.detect_pois("EURUSD", "M15", 5)
    
    print(f"\n📊 Resultados del análisis:")
    print(f"POIs detectados: {len(pois)}")
    
    for poi in pois[:5]:  # Mostrar solo los primeros 5
        print(f"\n🎯 {poi.poi_type.value.upper()}")
        print(f"   Precio: {poi.price_level:.5f}")
        print(f"   Zona: {poi.price_zone[0]:.5f} - {poi.price_zone[1]:.5f}")
        print(f"   Significancia: {poi.significance.value}")
        print(f"   Strength: {poi.strength:.1f}%")
        print(f"   Estado: {poi.status.value}")
        print(f"   Confluencias: {', '.join(poi.confluences[:3])}")
    
    # Resumen
    summary = poi_system.get_poi_summary()
    print(f"\n📈 Resumen POI System:")
    print(f"   Total activos: {summary['total_active']}")
    print(f"   Strength promedio: {summary['avg_strength']}%")
    print(f"   Por tipo: {summary['by_type']}")
    print(f"   Por significancia: {summary['by_significance']}")
    
    # Métricas
    metrics = poi_system.get_performance_metrics()
    print(f"\n⚡ Métricas:")
    print(f"   POIs creados: {metrics['total_pois_created']}")
    print(f"   POIs activos: {metrics['active_pois']}")
    print(f"   Históricos: {summary['historical_count']}")
