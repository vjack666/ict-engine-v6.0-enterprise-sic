#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DATA MANAGEMENT MODULE - ICT ENGINE v6.0 ENTERPRISE
=====================================================

Módulo de gestión de datos enterprise integrado con protocolos de logging central.
Contiene herramientas avanzadas para descarga, procesamiento y almacenamiento 
de datos financieros optimizado para cuentas reales.

Características Enterprise:
✅ Descarga inteligente de velas (AdvancedCandleDownloader)
✅ Gestión MT5 optimizada (MT5DataManager)  
✅ Coordinación de descargas avanzada
✅ Procesamiento de datos en tiempo real
✅ Cache predictivo enterprise
✅ Logging centralizado con protocolos

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

__version__ = "6.0.0-enterprise"
__author__ = "ICT Engine v6.0 Enterprise Team"

# Importar protocolos de logging central
try:
    from ..protocols import setup_module_logging, LogLevel
    _PROTOCOLS_AVAILABLE = True
    module_logger = setup_module_logging("DataManagement", LogLevel.INFO)
except ImportError:
    _PROTOCOLS_AVAILABLE = False
    import logging
    logging.basicConfig(level=logging.INFO)
    module_logger = logging.getLogger("DataManagement")

def _safe_log(level: str, message: str):
    """Logging seguro para el módulo data_management"""
    try:
        if _PROTOCOLS_AVAILABLE:
            getattr(module_logger, level)(message, "DataManagement")
        else:
            getattr(module_logger, level)(f"[DataManagement] {message}")
    except Exception:
        print(f"[{level.upper()}] [DataManagement] {message}")

# Inicializar variables de estado
_ADVANCED_CANDLE_DOWNLOADER_AVAILABLE = False
_MT5_DATA_MANAGER_AVAILABLE = False
_IMPORT_ERRORS = []

# AdvancedCandleDownloader - Componente crítico para cuenta real
try:
    from .advanced_candle_downloader import (
        AdvancedCandleDownloader,
        get_advanced_candle_downloader,
        create_download_request,
        DownloadStats,
        DownloadRequest,
        DownloadStatus
    )
    _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE = True
    _safe_log("info", "✅ AdvancedCandleDownloader cargado exitosamente")
    
except ImportError as e:
    _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE = False
    _IMPORT_ERRORS.append(f"AdvancedCandleDownloader: {str(e)}")
    _safe_log("warning", f"⚠️ AdvancedCandleDownloader no disponible: {e}")
    
    # Crear stubs para evitar errores de importación
    class _AdvancedCandleDownloaderStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "AdvancedCandleDownloader no disponible - usando stub")
            raise ImportError("AdvancedCandleDownloader no está disponible")
    
    AdvancedCandleDownloader = _AdvancedCandleDownloaderStub
    get_advanced_candle_downloader = lambda: None
    create_download_request = lambda: None
    DownloadStats = None
    DownloadRequest = None
    DownloadStatus = None

# MT5DataManager - Componente crítico para operaciones reales
try:
    from .mt5_data_manager import MT5DataManager
    _MT5_DATA_MANAGER_AVAILABLE = True
    _safe_log("info", "✅ MT5DataManager cargado exitosamente")
    
except ImportError as e:
    MT5DataManager = None
    _MT5_DATA_MANAGER_AVAILABLE = False
    _IMPORT_ERRORS.append(f"MT5DataManager: {str(e)}")
    _safe_log("warning", f"⚠️ MT5DataManager no disponible: {e}")
    
    # Crear stub para MT5DataManager
    class _MT5DataManagerStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "MT5DataManager no disponible - usando stub")
            raise ImportError("MT5DataManager no está disponible")
    
    MT5DataManager = _MT5DataManagerStub

# RealTradingBridge - Bridge crítico para cuenta real
try:
    from .real_trading_bridge import RealTradingBridge
    _REAL_TRADING_BRIDGE_AVAILABLE = True
    _safe_log("info", "✅ RealTradingBridge cargado exitosamente")
except ImportError as e:
    _REAL_TRADING_BRIDGE_AVAILABLE = False
    _IMPORT_ERRORS.append(f"RealTradingBridge: {str(e)}")
    _safe_log("warning", f"⚠️ RealTradingBridge no disponible: {e}")
    
    class _RealTradingBridgeStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "RealTradingBridge no disponible - usando stub")
            raise ImportError("RealTradingBridge no está disponible")
    
    RealTradingBridge = _RealTradingBridgeStub

# DataValidatorRealTrading - Validador crítico para datos reales
try:
    from .data_validator_real_trading import RealTradingDataValidator
    _DATA_VALIDATOR_AVAILABLE = True
    _safe_log("info", "✅ RealTradingDataValidator cargado exitosamente")
except ImportError as e:
    _DATA_VALIDATOR_AVAILABLE = False
    _IMPORT_ERRORS.append(f"RealTradingDataValidator: {str(e)}")
    _safe_log("warning", f"⚠️ RealTradingDataValidator no disponible: {e}")
    
    class _RealTradingDataValidatorStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "RealTradingDataValidator no disponible - usando stub")
            raise ImportError("RealTradingDataValidator no está disponible")
    
    RealTradingDataValidator = _RealTradingDataValidatorStub

# ICTDataManager - Gestor avanzado de datos ICT
try:
    from .ict_data_manager import ICTDataManager
    _ICT_DATA_MANAGER_AVAILABLE = True  
    _safe_log("info", "✅ ICTDataManager cargado exitosamente")
except ImportError as e:
    _ICT_DATA_MANAGER_AVAILABLE = False
    _IMPORT_ERRORS.append(f"ICTDataManager: {str(e)}")
    _safe_log("warning", f"⚠️ ICTDataManager no disponible: {e}")
    
    class _ICTDataManagerStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "ICTDataManager no disponible - usando stub")
            raise ImportError("ICTDataManager no está disponible")
    
    ICTDataManager = _ICTDataManagerStub

# MT5ConnectionManager - Gestión de conexión robusta
try:
    from .mt5_connection_manager import MT5ConnectionManager
    _MT5_CONNECTION_MANAGER_AVAILABLE = True
    _safe_log("info", "✅ MT5ConnectionManager cargado exitosamente")
except ImportError as e:
    _MT5_CONNECTION_MANAGER_AVAILABLE = False
    _IMPORT_ERRORS.append(f"MT5ConnectionManager: {str(e)}")
    _safe_log("warning", f"⚠️ MT5ConnectionManager no disponible: {e}")
    
    class _MT5ConnectionManagerStub:
        def __init__(self, *args, **kwargs):
            _safe_log("error", "MT5ConnectionManager no disponible - usando stub")
            raise ImportError("MT5ConnectionManager no está disponible")
    
    MT5ConnectionManager = _MT5ConnectionManagerStub

# Exports principales - Garantizados para funcionar con cuenta real
__all__ = [
    # AdvancedCandleDownloader exports
    'AdvancedCandleDownloader',
    'get_advanced_candle_downloader', 
    'create_download_request',
    'DownloadStats',
    'DownloadRequest',
    'DownloadStatus',
    
    # Core data management
    'MT5DataManager',
    'ICTDataManager',
    'MT5ConnectionManager',
    
    # Real trading components
    'RealTradingBridge',
    'RealTradingDataValidator',
    
    # Utility functions
    'get_module_status',
    'validate_enterprise_requirements',
    'get_enterprise_data_collector'
]

# Información del módulo enterprise
MODULE_INFO = {
    'name': 'data_management',
    'version': __version__,
    'description': 'Advanced data management enterprise optimizado para cuenta real',
    'components': {
        'advanced_candle_downloader': _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE,
        'mt5_data_manager': _MT5_DATA_MANAGER_AVAILABLE,
        'real_trading_bridge': _REAL_TRADING_BRIDGE_AVAILABLE,
        'data_validator': _DATA_VALIDATOR_AVAILABLE,
        'ict_data_manager': _ICT_DATA_MANAGER_AVAILABLE,
        'mt5_connection_manager': _MT5_CONNECTION_MANAGER_AVAILABLE
    },
    'enterprise_features': [
        'Real-time data processing',
        'Predictive caching',
        'Enterprise logging protocols',
        'Robust error handling',
        'Live account optimization',
        'Data validation for real trading',
        'MT5 connection management',
        'ICT pattern data optimization'
    ],
    'protocols_integration': _PROTOCOLS_AVAILABLE,
    'import_errors': _IMPORT_ERRORS if _IMPORT_ERRORS else None
}

def get_module_status():
    """Obtiene el estado completo del módulo data_management enterprise"""
    status = {
        'version': __version__,
        'advanced_candle_downloader': _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE,
        'mt5_data_manager': _MT5_DATA_MANAGER_AVAILABLE,
        'real_trading_bridge': _REAL_TRADING_BRIDGE_AVAILABLE,
        'data_validator': _DATA_VALIDATOR_AVAILABLE,
        'ict_data_manager': _ICT_DATA_MANAGER_AVAILABLE,
        'mt5_connection_manager': _MT5_CONNECTION_MANAGER_AVAILABLE,
        'protocols_available': _PROTOCOLS_AVAILABLE,
        'import_errors': _IMPORT_ERRORS if _IMPORT_ERRORS else None,
        'enterprise_ready': all([
            _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE,
            _MT5_DATA_MANAGER_AVAILABLE,
            _REAL_TRADING_BRIDGE_AVAILABLE,
            _DATA_VALIDATOR_AVAILABLE
        ]),
        'components_loaded': sum([
            _ADVANCED_CANDLE_DOWNLOADER_AVAILABLE,
            _MT5_DATA_MANAGER_AVAILABLE,
            _REAL_TRADING_BRIDGE_AVAILABLE,
            _DATA_VALIDATOR_AVAILABLE,
            _ICT_DATA_MANAGER_AVAILABLE,
            _MT5_CONNECTION_MANAGER_AVAILABLE
        ])
    }
    
    _safe_log("info", f"Module status: {status['components_loaded']}/6 components loaded")
    return status

def validate_enterprise_requirements():
    """Valida que los componentes enterprise críticos estén disponibles"""
    critical_components = [
        (_ADVANCED_CANDLE_DOWNLOADER_AVAILABLE, 'AdvancedCandleDownloader'),
        (_MT5_DATA_MANAGER_AVAILABLE, 'MT5DataManager'),
        (_REAL_TRADING_BRIDGE_AVAILABLE, 'RealTradingBridge'), 
        (_DATA_VALIDATOR_AVAILABLE, 'RealTradingDataValidator')
    ]
    
    missing_components = [name for available, name in critical_components if not available]
    
    if missing_components:
        _safe_log("warning", f"Componentes críticos faltantes para cuenta real: {missing_components}")
        return False, missing_components
    else:
        _safe_log("info", "✅ Todos los componentes críticos enterprise disponibles")
        return True, []

def get_enterprise_data_collector():
    """Factory function para obtener el collector de datos enterprise óptimo"""
    if _REAL_TRADING_BRIDGE_AVAILABLE:
        try:
            # Solo crear instancia si realmente está disponible
            from .real_trading_bridge import RealTradingBridge as _RealBridge
            bridge = _RealBridge()
            if hasattr(bridge, 'initialize') and bridge.initialize():
                _safe_log("info", "🚀 RealTradingBridge inicializado exitosamente")
                return bridge
        except Exception as e:
            _safe_log("error", f"Error inicializando RealTradingBridge: {e}")
    
    if _MT5_DATA_MANAGER_AVAILABLE:
        try:
            # Solo crear instancia si realmente está disponible
            from .mt5_data_manager import MT5DataManager as _MT5Manager
            manager = _MT5Manager()
            _safe_log("info", "📊 MT5DataManager como fallback")
            return manager
        except Exception as e:
            _safe_log("error", f"Error inicializando MT5DataManager: {e}")
    
    _safe_log("warning", "⚠️ No hay collector de datos enterprise disponible")
    return None

# Inicialización del módulo
_safe_log("info", f"DataManagement v{__version__} inicializado")
_is_enterprise_ready, _missing_components = validate_enterprise_requirements()

if _is_enterprise_ready:
    _safe_log("info", "🚀 Módulo data_management listo para cuenta real")
else:
    _safe_log("warning", f"⚠️ Módulo parcialmente disponible - Faltan: {_missing_components}")

# Validar variables para evitar "possibly unbound"
if '_REAL_TRADING_BRIDGE_AVAILABLE' not in globals():
    _REAL_TRADING_BRIDGE_AVAILABLE = False
if '_DATA_VALIDATOR_AVAILABLE' not in globals():
    _DATA_VALIDATOR_AVAILABLE = False
if '_ICT_DATA_MANAGER_AVAILABLE' not in globals():
    _ICT_DATA_MANAGER_AVAILABLE = False
if '_MT5_CONNECTION_MANAGER_AVAILABLE' not in globals():
    _MT5_CONNECTION_MANAGER_AVAILABLE = False
