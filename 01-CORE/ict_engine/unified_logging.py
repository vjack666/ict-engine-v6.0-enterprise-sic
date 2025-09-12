#!/usr/bin/env python3
"""
🔧 UNIFIED LOGGING SYSTEM - ICT ENGINE v6.0 ENTERPRISE
======================================================

Sistema de logging unificado con fallbacks robustos para patrones avanzados.
Soluciona los errores de Pylance "possibly unbound" con imports seguros.

Características:
✅ Fallbacks múltiples para imports
✅ Funciones de logging siempre disponibles
✅ Compatible con Pylance
✅ Integración con SmartTradingLogger
✅ Rate limiting automático
✅ Deduplicación inteligente

Autor: ICT Engine v6.0 Team
Fecha: 12 Septiembre 2025
"""

import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# ===========================================
# 🛡️ FALLBACK LOGGING FUNCTIONS
# ===========================================

def _create_fallback_logger(name: str = "ICT_FALLBACK") -> logging.Logger:
    """Crear logger básico como fallback"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Logger fallback global
_fallback_logger = _create_fallback_logger()

def _fallback_log_info(message: str, component: str = "CORE"):
    """Función fallback para log_info"""
    _fallback_logger.info(f"[{component}] {message}")

def _fallback_log_warning(message: str, component: str = "CORE"):
    """Función fallback para log_warning"""
    _fallback_logger.warning(f"[{component}] {message}")

def _fallback_log_error(message: str, component: str = "CORE"):
    """Función fallback para log_error"""
    _fallback_logger.error(f"[{component}] {message}")

def _fallback_log_debug(message: str, component: str = "CORE"):
    """Función fallback para log_debug"""
    _fallback_logger.debug(f"[{component}] {message}")

# ===========================================
# 🔄 SMART LOGGING IMPORTS CON FALLBACKS
# ===========================================

# Variables para logging functions - siempre inicializadas
log_info = _fallback_log_info
log_warning = _fallback_log_warning
log_error = _fallback_log_error
log_debug = _fallback_log_debug

# Smart Trading Logger instance
SmartTradingLogger: Optional[Any] = None

# Intentar importar el sistema principal de logging con múltiples fallbacks
try:
    # Intento 1: Import relativo desde parent directory
    from ..smart_trading_logger import SmartTradingLogger as STL
    from ..smart_trading_logger import log_info as _log_info
    from ..smart_trading_logger import log_warning as _log_warning
    from ..smart_trading_logger import log_error as _log_error
    from ..smart_trading_logger import log_debug as _log_debug
    
    SmartTradingLogger = STL
    log_info = _log_info
    log_warning = _log_warning
    log_error = _log_error
    log_debug = _log_debug
    
    _fallback_logger.info("✅ SmartTradingLogger importado exitosamente (import relativo)")
    
except ImportError:
    try:
        # Intento 2: Import absoluto
        from smart_trading_logger import SmartTradingLogger as STL
        from smart_trading_logger import log_info as _log_info
        from smart_trading_logger import log_warning as _log_warning
        from smart_trading_logger import log_error as _log_error
        from smart_trading_logger import log_debug as _log_debug
        
        SmartTradingLogger = STL
        log_info = _log_info
        log_warning = _log_warning
        log_error = _log_error
        log_debug = _log_debug
        
        _fallback_logger.info("✅ SmartTradingLogger importado exitosamente (import absoluto)")
        
    except ImportError:
        try:
            # Intento 3: Import desde parent directory
            import sys
            from pathlib import Path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            from smart_trading_logger import SmartTradingLogger as STL
            from smart_trading_logger import log_info as _log_info
            from smart_trading_logger import log_warning as _log_warning
            from smart_trading_logger import log_error as _log_error
            from smart_trading_logger import log_debug as _log_debug
            
            SmartTradingLogger = STL
            log_info = _log_info
            log_warning = _log_warning
            log_error = _log_error
            log_debug = _log_debug
            
            _fallback_logger.info("✅ SmartTradingLogger importado exitosamente (path manipulation)")
            
        except ImportError:
            # Usar fallbacks - las funciones ya están asignadas
            _fallback_logger.warning("⚠️ SmartTradingLogger no disponible - usando sistema fallback")

# ===========================================
# 🎯 UNIFIED LOGGING INTERFACE
# ===========================================

class UnifiedLoggingSystem:
    """
    🎯 Sistema de logging unificado para patrones avanzados
    
    Proporciona una interfaz consistente para logging con fallbacks automáticos
    """
    
    def __init__(self, component_name: str = "ADVANCED_PATTERNS"):
        self.component_name = component_name
        self.smart_logger = None
        
        # Intentar crear instancia de SmartTradingLogger
        if SmartTradingLogger:
            try:
                self.smart_logger = SmartTradingLogger(
                    name=f"ICT_{component_name}", 
                    level="INFO",
                    silent_mode=False
                )
            except Exception as e:
                _fallback_logger.warning(f"⚠️ Error creando SmartTradingLogger: {e}")
    
    def info(self, message: str, component: Optional[str] = None):
        """Log info message"""
        comp = component or self.component_name
        log_info(message, comp)
    
    def warning(self, message: str, component: Optional[str] = None):
        """Log warning message"""
        comp = component or self.component_name
        log_warning(message, comp)
    
    def error(self, message: str, component: Optional[str] = None):
        """Log error message"""
        comp = component or self.component_name
        log_error(message, comp)
    
    def debug(self, message: str, component: Optional[str] = None):
        """Log debug message"""
        comp = component or self.component_name
        log_debug(message, comp)

# ===========================================
# 🚀 CONVENIENCE FUNCTIONS
# ===========================================

def create_unified_logger(component_name: str) -> UnifiedLoggingSystem:
    """
    🚀 Crear logger unificado para un componente específico
    
    Args:
        component_name: Nombre del componente (ej: "JUDAS_SWING", "LIQUIDITY_GRAB")
        
    Returns:
        UnifiedLoggingSystem instance
    """
    return UnifiedLoggingSystem(component_name)

def test_unified_logging():
    """🧪 Test del sistema de logging unificado"""
    print("\n🧪 TESTING UNIFIED LOGGING SYSTEM")
    print("=" * 50)
    
    # Test funciones globales
    log_info("Test info message - global function", "TEST")
    log_warning("Test warning message - global function", "TEST")
    log_error("Test error message - global function", "TEST")
    log_debug("Test debug message - global function", "TEST")
    
    # Test logger unificado
    logger = create_unified_logger("TEST_COMPONENT")
    logger.info("Test info message - unified logger")
    logger.warning("Test warning message - unified logger")
    logger.error("Test error message - unified logger")
    logger.debug("Test debug message - unified logger")
    
    print("✅ Unified logging system test completed")

# ===========================================
# 🔍 DIAGNOSTIC FUNCTIONS
# ===========================================

def get_logging_status() -> Dict[str, Any]:
    """Obtener estado del sistema de logging"""
    return {
        "smart_trading_logger_available": SmartTradingLogger is not None,
        "fallback_mode": SmartTradingLogger is None,
        "functions_available": {
            "log_info": log_info is not None,
            "log_warning": log_warning is not None,
            "log_error": log_error is not None,
            "log_debug": log_debug is not None
        },
        "timestamp": datetime.now().isoformat()
    }

def print_logging_status():
    """Imprimir estado del sistema de logging"""
    status = get_logging_status()
    print("\n🔍 UNIFIED LOGGING SYSTEM STATUS")
    print("=" * 40)
    print(f"SmartTradingLogger Available: {'✅' if status['smart_trading_logger_available'] else '❌'}")
    print(f"Fallback Mode: {'⚠️ YES' if status['fallback_mode'] else '✅ NO'}")
    print(f"Logging Functions:")
    for func_name, available in status['functions_available'].items():
        print(f"  {func_name}: {'✅' if available else '❌'}")
    print(f"Timestamp: {status['timestamp']}")

# ===========================================
# 🧪 MAIN TESTING
# ===========================================

if __name__ == "__main__":
    print_logging_status()
    test_unified_logging()