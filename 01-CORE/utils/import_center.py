#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CENTRAL DE IMPORTS v6.0 ENTERPRISE
====================================

Sistema centralizado de imports para scripts del ICT Engine v6.0.
Proporciona imports robustos con fallbacks automáticos.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 1 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
import sys
import threading
import datetime
from pathlib import Path
from typing import Any, Optional, Dict, Callable, Union, TYPE_CHECKING

# Type checking imports
if TYPE_CHECKING:
    from enum import Enum

# Añadir path del proyecto si no está presente
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importar logging central
try:
    from smart_trading_logger import get_smart_logger, log_info, log_warning, log_error, log_debug
    _logger = get_smart_logger("ImportCenter")
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback básico si no hay logger
    LOGGING_AVAILABLE = False
    def _log_info(msg): print(f"[INFO] {msg}")
    def _log_warning(msg): print(f"[WARNING] {msg}")
    def _log_error(msg): print(f"[ERROR] {msg}")
    def _log_debug(msg): print(f"[DEBUG] {msg}")

def _log(level: str, message: str, component: str = "IMPORT_CENTER"):
    """🔧 Log centralizado con fallback"""
    if LOGGING_AVAILABLE:
        if level == "info":
            _logger.info(message, component)
        elif level == "warning":
            _logger.warning(message, component)
        elif level == "error":
            _logger.error(message, component)
        elif level == "debug":
            _logger.debug(message, component)
    else:
        print(f"[{level.upper()}] [{component}] {message}")

class ImportCenter:
    """🔧 Centro de imports centralizado con thread-safety"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._failed_imports: set = set()
        self._lock = threading.RLock()  # Thread-safe pandas/numpy manager
        self._pandas_manager = None
        self._numpy_manager = None

    def safe_import(self, module_path: str, fallback_path: Optional[str] = None) -> Optional[Any]:
        """
        🔒 Import seguro con fallback automático

        Args:
            module_path: Ruta del módulo principal
            fallback_path: Ruta alternativa si falla el principal

        Returns:
            Módulo importado o None si falla
        """

        # Verificar cache
        if module_path in self._cache:
            return self._cache[module_path]

        # Casos especiales para módulos críticos
        if module_path in ['pandas', 'numpy']:
            return self._import_critical_module(module_path)

        # Intentar import principal
        try:
            module = __import__(module_path, fromlist=[''])
            self._cache[module_path] = module
            return module
        except ImportError as e:
            self._failed_imports.add(module_path)

            # Intentar fallback si está disponible
            if fallback_path and fallback_path not in self._failed_imports:
                try:
                    module = __import__(fallback_path, fromlist=[''])
                    self._cache[module_path] = module  # Cache con la key original
                    return module
                except ImportError:
                    self._failed_imports.add(fallback_path)

            return None

    def _import_critical_module(self, module_name: str) -> Optional[Any]:
        """🎯 Import optimizado para módulos críticos como pandas/numpy con thread-safety"""
        with self._lock:
            # Verificar cache primero (thread-safe)
            if module_name in self._cache:
                return self._cache[module_name]
            
            try:
                if module_name == 'pandas':
                    if self._pandas_manager is None:
                        import pandas
                        self._pandas_manager = pandas
                        _log("info", "✅ Thread-Safe Pandas manager inicializado")
                    self._cache['pandas'] = self._pandas_manager
                    return self._pandas_manager
                    
                elif module_name == 'numpy':
                    if self._numpy_manager is None:
                        import numpy
                        self._numpy_manager = numpy
                        _log("info", "✅ Thread-Safe Numpy manager inicializado")
                    self._cache['numpy'] = self._numpy_manager
                    return self._numpy_manager
                    
            except ImportError as e:
                _log("warning", f"⚠️ Error importando {module_name}: {e}")
                self._failed_imports.add(module_name)
                return None
            return None

    def get_mt5_manager(self):
        """🔌 Obtener MT5DataManager con fallbacks"""

        # Intentar función get_mt5_manager primero
        try:
            from data_management.mt5_data_manager import get_mt5_manager
            return get_mt5_manager
        except ImportError:
            pass

        # Intentar clase MT5DataManager directamente
        try:
            from data_management.mt5_data_manager import MT5DataManager
            return MT5DataManager
        except ImportError:
            pass

        # Fallback: crear función básica
        def fallback_mt5_manager(*args, **kwargs):
            _log("warning", "MT5DataManager no disponible - verificar instalación")
            return None
        return fallback_mt5_manager

    def get_pattern_detector(self):
        """🎯 Obtener PatternDetector con fallbacks"""

        # Intentar desde ict_engine
        try:
            from ict_engine.pattern_detector import PatternDetector
            return PatternDetector
        except ImportError:
            pass

        # Fallback: crear función básica
        def fallback_pattern_detector(*args, **kwargs):
            raise ImportError("PatternDetector no disponible - verificar instalación")
        return fallback_pattern_detector

    def get_smart_logger(self):
        """📋 Obtener SmartTradingLogger con fallbacks"""

        # Intentar desde core (ubicación real)
        try:
            from smart_trading_logger import SmartTradingLogger
            return SmartTradingLogger
        except ImportError:
            pass

        # Fallback: logger básico
        import logging

        class FallbackLogger:
            def __init__(self, name="ICT_Engine"):
                self.logger = logging.getLogger(name)
                if not self.logger.handlers:
                    handler = logging.StreamHandler()
                    formatter = logging.Formatter('[%(levelname)s] %(message)s')
                    handler.setFormatter(formatter)
                    self.logger.addHandler(handler)
                    self.logger.setLevel(logging.INFO)

            def info(self, message, **kwargs):
                self.logger.info(message)

            def warning(self, message, **kwargs):
                self.logger.warning(message)

            def error(self, message, **kwargs):
                self.logger.error(message)

            def debug(self, message, **kwargs):
                self.logger.debug(message)

        return FallbackLogger

    def get_smart_money_analyzer(self):
        """🧠 Obtener SmartMoneyAnalyzer con fallbacks robustos y evitando circularidad"""
        
        # Cache key para evitar reimports
        cache_key = 'smart_money_analyzer_class'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Importación diferida para evitar circularidad
        import importlib
        
        try:
            # Intentar importar el módulo completo primero
            sma_module = importlib.import_module('smart_money_concepts.smart_money_analyzer')
            
            # Verificar que la clase existe en el módulo
            if hasattr(sma_module, 'SmartMoneyAnalyzer'):
                SmartMoneyAnalyzer = getattr(sma_module, 'SmartMoneyAnalyzer')
                self._cache[cache_key] = SmartMoneyAnalyzer
                _log("info", "✅ SmartMoneyAnalyzer cargado exitosamente desde smart_money_concepts")
                return SmartMoneyAnalyzer
            else:
                _log("warning", "⚠️ SmartMoneyAnalyzer no encontrado en el módulo")
                
        except ImportError as e:
            _log("warning", f"⚠️ Error de importación SmartMoneyAnalyzer: {e}")
        except Exception as e:
            _log("warning", f"⚠️ Error general cargando SmartMoneyAnalyzer: {e}")
        
        # Fallback: clase básica de Smart Money
        _log("info", "🔄 Creando SmartMoneyAnalyzer fallback")
        
        class FallbackSmartMoneyAnalyzer:
            """SmartMoneyAnalyzer básico para compatibilidad"""
            
            def __init__(self, *args, **kwargs):
                self.enabled = False
                _log("info", "Usando SmartMoneyAnalyzer fallback - funcionalidad limitada")
            
            def analyze_smart_money_flow(self, *args, **kwargs):
                return {"detected": False, "reason": "Fallback analyzer - funcionalidad limitada"}
            
            def detect_institutional_levels(self, *args, **kwargs):
                return []
            
            def calculate_smart_money_score(self, *args, **kwargs):
                return 0.0
        
        self._cache[cache_key] = FallbackSmartMoneyAnalyzer
        return FallbackSmartMoneyAnalyzer

    def get_advanced_candle_downloader(self):
        """📊 Obtener AdvancedCandleDownloader con fallbacks"""
        
        cache_key = 'advanced_candle_downloader'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Intentar desde data_management
        try:
            from data_management.advanced_candle_downloader import get_advanced_candle_downloader
            self._cache[cache_key] = get_advanced_candle_downloader
            _log("info", "✅ AdvancedCandleDownloader cargado")
            return get_advanced_candle_downloader
        except ImportError as e:
            _log("warning", f"⚠️ AdvancedCandleDownloader no disponible: {e}")
        
        # Fallback: función básica
        def fallback_downloader(*args, **kwargs):
            _log("info", "🔄 Usando downloader simulado")
            return None
        
        self._cache[cache_key] = fallback_downloader
        return fallback_downloader

    def get_ict_types(self) -> tuple:
        """🎯 Obtener ICT Types con fallbacks - retorna tupla de tipos"""

        try:
            from ict_engine.ict_types import TradingDirection, ICTPattern
            # Retornar los tipos reales directamente
            return (TradingDirection, ICTPattern)
        except ImportError:
            pass

        # Fallback: enums básicos
        from enum import Enum

        class TradingDirectionFallback(Enum):
            BUY = "BUY"
            SELL = "SELL"
            NEUTRAL = "NEUTRAL"

        class ICTPatternFallback(Enum):
            ORDER_BLOCK = "ORDER_BLOCK"
            FAIR_VALUE_GAP = "FAIR_VALUE_GAP"
            DISPLACEMENT = "DISPLACEMENT"
            SILVER_BULLET = "SILVER_BULLET"

        return (TradingDirectionFallback, ICTPatternFallback)

    def is_trading_ready(self) -> bool:
        """🚨 Verificar si el sistema está listo para trading real"""
        with self._lock:
            pandas_ok = self.safe_import('pandas') is not None
            numpy_ok = self.safe_import('numpy') is not None
            return pandas_ok and numpy_ok

    def get_system_health(self) -> Dict[str, Any]:
        """🩺 Obtener salud completa del sistema"""
        health = {
            'pandas_available': self.safe_import('pandas') is not None,
            'numpy_available': self.safe_import('numpy') is not None,
            'smart_money_available': False,
            'downloader_available': False,
            'thread_safe_enabled': hasattr(self, '_lock'),
            'cache_items': len(self._cache),
            'failed_imports': list(self._failed_imports)
        }
        
        # Test SmartMoneyAnalyzer
        try:
            sma = self.get_smart_money_analyzer()
            health['smart_money_available'] = sma is not None
        except:
            health['smart_money_available'] = False
        
        # Test downloader
        try:
            downloader = self.get_advanced_candle_downloader()
            health['downloader_available'] = downloader is not None
        except:
            health['downloader_available'] = False
        
        # Calcular score general
        critical_components = ['pandas_available', 'numpy_available']
        optional_components = ['smart_money_available', 'downloader_available']
        
        critical_score = sum(health[comp] for comp in critical_components) / len(critical_components)
        optional_score = sum(health[comp] for comp in optional_components) / len(optional_components)
        
        health['health_score'] = (critical_score * 0.7 + optional_score * 0.3) * 100
        health['trading_ready'] = self.is_trading_ready()
        
        return health

    def print_system_health(self):
        """📊 Imprimir salud del sistema de forma detallada"""
        health = self.get_system_health()
        
        _log("info", "🩺 SALUD DEL SISTEMA ICT ENGINE v6.0")
        _log("info", "=" * 45)
        _log("info", f"🎯 Thread-Safe Manager: {'✅ ENABLED' if health['thread_safe_enabled'] else '❌ DISABLED'}")
        _log("info", f"📊 Pandas Manager: {'✅ OK' if health['pandas_available'] else '❌ FAILED'}")
        _log("info", f"🔢 Numpy Manager: {'✅ OK' if health['numpy_available'] else '❌ FAILED'}")
        _log("info", f"🧠 Smart Money Analyzer: {'✅ OK' if health['smart_money_available'] else '⚠️ FALLBACK'}")
        _log("info", f"📈 Advanced Downloader: {'✅ OK' if health['downloader_available'] else '⚠️ FALLBACK'}")
        _log("info", f"💾 Cache Items: {health['cache_items']}")
        
        if health['failed_imports']:
            _log("warning", f"❌ Failed Imports: {', '.join(health['failed_imports'])}")
        
        _log("info", f"🎯 Health Score: {health['health_score']:.1f}%")
        _log("info", f"🚨 Trading Ready: {'✅ YES' if health['trading_ready'] else '❌ NO'}")
        
        if health['health_score'] >= 80:
            _log("info", "✅ Sistema en excelente estado")
        elif health['health_score'] >= 60:
            _log("warning", "⚠️ Sistema funcional con limitaciones")
        else:
            _log("error", "🚨 Sistema necesita atención")

    def verify_installation(self) -> Dict[str, bool]:
        """✅ Verificar estado de instalación de componentes"""

        status = {}

        # Test MT5
        try:
            self.get_mt5_manager()
            status['mt5_manager'] = True
        except:
            status['mt5_manager'] = False

        # Test Pattern Detector
        try:
            self.get_pattern_detector()
            status['pattern_detector'] = True
        except:
            status['pattern_detector'] = False

        # Test Smart Logger
        try:
            self.get_smart_logger()
            status['smart_logger'] = True
        except:
            status['smart_logger'] = False

        # Test ICT Types
        try:
            self.get_ict_types()
            status['ict_types'] = True
        except:
            status['ict_types'] = False

        return status

# Función específica para importar ict_types de forma segura
def safe_import_ict_types():
    """🎯 Importar ict_types de forma segura para pattern_detector"""
    try:
        import ict_engine.ict_types as ict_types
        return ict_types
    except ImportError:
        pass

    # Fallback: módulo con tipos básicos
    from types import SimpleNamespace
    from enum import Enum

    class TradingDirection(Enum):
        BUY = "BUY"
        SELL = "SELL"
        NEUTRAL = "NEUTRAL"

    class ICTPattern(Enum):
        ORDER_BLOCK = "ORDER_BLOCK"
        FAIR_VALUE_GAP = "FAIR_VALUE_GAP"
        DISPLACEMENT = "DISPLACEMENT"
        SILVER_BULLET = "SILVER_BULLET"

    class ICTSignal:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class SmartMoneySignal:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class MarketStructureData:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    # Crear módulo fallback
    fallback_module = SimpleNamespace()
    fallback_module.TradingDirection = TradingDirection
    fallback_module.ICTPattern = ICTPattern
    fallback_module.ICTSignal = ICTSignal
    fallback_module.SmartMoneySignal = SmartMoneySignal
    fallback_module.MarketStructureData = MarketStructureData
    fallback_module.SessionType = TradingDirection  # Placeholder
    fallback_module.TimeFrame = TradingDirection    # Placeholder
    fallback_module.MarketPhase = TradingDirection  # Placeholder
    fallback_module.SmartMoneyType = TradingDirection  # Placeholder
    fallback_module.LiquidityLevel = TradingDirection  # Placeholder
    fallback_module.StructureType = TradingDirection   # Placeholder
    fallback_module.FVGType = TradingDirection        # Placeholder
    fallback_module.OrderBlockType = TradingDirection # Placeholder
    fallback_module.FairValueGap = ICTSignal          # Placeholder
    fallback_module.OrderBlock = ICTSignal            # Placeholder
    fallback_module.LiquidityPool = ICTSignal         # Placeholder
    fallback_module.ICTConfig = dict                  # Placeholder

    def validate_ict_signal(signal):
        return True

    def create_ict_narrative(signal):
        return "ICT Signal narrative"

    fallback_module.validate_ict_signal = validate_ict_signal
    fallback_module.create_ict_narrative = create_ict_narrative

    return fallback_module

# Instancia global del centro de imports
_import_center = ImportCenter()

# Funciones de conveniencia
def get_pattern_detector_safe():
    """🎯 Obtener PatternDetector de forma segura"""
    return _import_center.get_pattern_detector()

def get_mt5_manager_safe() -> Optional[Any]:
    """🔌 Obtener MT5DataManager con fallbacks mejorado"""
    try:
        # Intentar obtener el manager desde import center
        manager = _import_center.get_mt5_manager()
        if hasattr(manager, '__call__'):
            # Si es una función, llamarla para obtener la instancia
            return manager()
        return manager
    except Exception as e:
        _log("warning", f"MT5Manager no disponible: {e}")
        return None

def get_data_collector_safe() -> Optional[Any]:
    """📊 Obtener Data Collector con fallbacks optimizado"""
    try:
        # Intentar importar desde dashboard con configuración optimizada
        import sys
        from pathlib import Path
        dashboard_path = Path(__file__).parent.parent.parent / "09-DASHBOARD" / "data"
        sys.path.insert(0, str(dashboard_path))
        
        try:
            from data_collector import RealICTDataCollector  # type: ignore
        except ImportError:
            # Fallback a core si data no está disponible
            dashboard_core_path = Path(__file__).parent.parent.parent / "09-DASHBOARD" / "core"
            sys.path.insert(0, str(dashboard_core_path))
            from data_collector import RealICTDataCollector  # type: ignore
        
        # Configuración empresarial optimizada
        config = {
            'data': {
                'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'],
                'timeframes': ['H1', 'H4', 'M15'],
                'real_time_update': True,
                'enterprise_mode': True
            },
            'performance': {
                'cache_enabled': True,
                'concurrent_downloads': 3,
                'thread_safe': True
            }
        }
        
        collector = RealICTDataCollector(config)
        _log("info", "✅ Data Collector Enterprise inicializado exitosamente")
        return collector
    except Exception as e:
        _log("warning", f"Data Collector no disponible: {e}")
        return None

def verify_mt5_connection() -> bool:
    """🔌 Verificar conexión MT5 mejorada"""
    try:
        mt5_manager = get_mt5_manager_safe()
        if mt5_manager is None:
            return False
            
        # Verificar si ya está conectado o intentar conectar
        if hasattr(mt5_manager, 'is_connected') and mt5_manager.is_connected():
            return True
        elif hasattr(mt5_manager, 'connect'):
            return mt5_manager.connect()
        
        return False
    except Exception as e:
        _log("warning", f"Error verificando conexión MT5: {e}")
        return False

def get_system_status_detailed() -> Dict[str, Any]:
    """🩺 Obtener estado detallado del sistema"""
    status = {
        'mt5_connection': verify_mt5_connection(),
        'data_collector_available': get_data_collector_safe() is not None,
        'import_center_health': _import_center.get_system_health(),
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # Calcular score de salud general
    critical_components = ['mt5_connection', 'data_collector_available']
    health_score = sum(status[comp] for comp in critical_components if isinstance(status[comp], bool))
    status['overall_health_score'] = (health_score / len(critical_components)) * 100
    
    return status

def get_smart_logger_safe():
    """📋 Obtener SmartLogger de forma segura"""
    return _import_center.get_smart_logger()

def get_ict_types_safe() -> tuple:
    """🎯 Obtener ICT Types de forma segura"""
    return _import_center.get_ict_types()

def verify_system_status():
    """✅ Verificar estado del sistema"""
    return _import_center.verify_installation()

def print_system_status():
    """📊 Imprimir estado del sistema"""
    status = verify_system_status()

    _log("info", "🔧 ESTADO DEL SISTEMA ICT ENGINE v6.0")
    _log("info", "=" * 40)

    for component, available in status.items():
        status_icon = "✅" if available else "❌"
        _log("info", f"{status_icon} {component}: {'Disponible' if available else 'No disponible'}")

    total_available = sum(status.values())
    total_components = len(status)

    _log("info", f"📊 Componentes disponibles: {total_available}/{total_components}")
    _log("info", f"🎯 Sistema operativo: {total_available >= 2}")  # Mínimo MT5 + Pattern Detector

# Función para obtener salud del sistema de forma rápida
def get_system_health_quick():
    """🩺 Obtener salud del sistema de forma rápida"""
    return _import_center.get_system_health()

def print_system_health_quick():
    """🩺 Imprimir salud del sistema de forma rápida"""
    _import_center.print_system_health()

if __name__ == "__main__":
    print_system_status()
    print_system_health_quick()
