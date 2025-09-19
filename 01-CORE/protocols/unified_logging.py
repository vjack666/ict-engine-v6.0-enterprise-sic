#!/usr/bin/env python3
"""
🔧 UNIFIED LOGGING PROTOCOL - ICT ENGINE v6.0 ENTERPRISE
========================================================

Interfaz unificada de logging que estandariza el acceso a logging
en todo el sistema ICT Engine. Proporciona una capa de abstracción
que permite usar SmartTradingLogger cuando está disponible y fallback
robusto cuando no lo está.

OBJETIVOS:
- Interfaz consistente en todo el sistema
- Compatibilidad con SmartTradingLogger y logging estándar
- Fallbacks robustos sin fallos
- Performance optimizado para producción
- Configuración centralizada

USAGE:
```python
from protocols.unified_logging import get_unified_logger

logger = get_unified_logger("ComponentName")
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error crítico")
```
"""
from __future__ import annotations

import logging
import sys
import time
import os
from typing import Protocol, Any, Optional, Dict, Union
from pathlib import Path

# =============================================================================
# 1. PROTOCOLO UNIFICADO
# =============================================================================

class UnifiedLogger(Protocol):
    """🎯 Protocolo unificado para todos los loggers del sistema"""
    
    def info(self, message: str, component: str = "", **kwargs: Any) -> None:
        """Log información"""
        ...
    
    def warning(self, message: str, component: str = "", **kwargs: Any) -> None:
        """Log advertencia"""
        ...
    
    def error(self, message: str, component: str = "", **kwargs: Any) -> None:
        """Log error"""
        ...
    
    def debug(self, message: str, component: str = "", **kwargs: Any) -> None:
        """Log debug"""
        ...
    
    def critical(self, message: str, component: str = "", **kwargs: Any) -> None:
        """Log crítico"""
        ...

# =============================================================================
# 2. ADAPTADORES ESPECÍFICOS
# =============================================================================

class SmartTradingLoggerAdapter:
    """🧠 Adaptador para SmartTradingLogger"""
    
    def __init__(self, component_name: str, smart_logger_instance: Any):
        self.component_name = component_name
        self.smart_logger = smart_logger_instance
        self._methods_cache: Dict[str, bool] = {}
        # de-dup state
        self._last_sig: Optional[tuple[str, str, str]] = None
        self._last_ts: float = 0.0

    def _should_emit(self, method_name: str, message: str, component: str) -> bool:
        sig = (method_name, component or self.component_name, message.strip())
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return False
        self._last_sig = sig
        self._last_ts = now
        return True
    
    def _has_method(self, method_name: str) -> bool:
        """Cached method existence check"""
        if method_name not in self._methods_cache:
            self._methods_cache[method_name] = hasattr(self.smart_logger, method_name)
        return self._methods_cache[method_name]
    
    def _safe_call(self, method_name: str, message: str, component: str = "", **kwargs: Any) -> None:
        """Llamada segura a método de SmartTradingLogger"""
        try:
            # Filtro global anti-duplicados para mensajes de apagado
            if not _global_should_emit(method_name, component or self.component_name, message):
                return
            if not self._should_emit(method_name, message, component):
                return
            if self._has_method(method_name):
                method = getattr(self.smart_logger, method_name)
                method(message, component or self.component_name, **kwargs)
            else:
                # Fallback to print with proper formatting
                print(f"[{method_name.upper()}][{self.component_name}][{component}] {message}")
        except Exception:
            # Ultimate fallback
            print(f"[{method_name.upper()}][{self.component_name}][{component}] {message}")
    
    def info(self, message: str, component: str = "", **kwargs: Any) -> None:
        self._safe_call("info", message, component, **kwargs)
    
    def warning(self, message: str, component: str = "", **kwargs: Any) -> None:
        self._safe_call("warning", message, component, **kwargs)
    
    def error(self, message: str, component: str = "", **kwargs: Any) -> None:
        self._safe_call("error", message, component, **kwargs)
    
    def debug(self, message: str, component: str = "", **kwargs: Any) -> None:
        self._safe_call("debug", message, component, **kwargs)
    
    def critical(self, message: str, component: str = "", **kwargs: Any) -> None:
        self._safe_call("critical", message, component, **kwargs)


class StandardLoggerAdapter:
    """📝 Adaptador para logging estándar de Python"""
    
    def __init__(self, component_name: str, logger: Optional[logging.Logger] = None):
        self.component_name = component_name
        if logger is None:
            logger = logging.getLogger(component_name)
            if not logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
        self.logger = logger
        # de-dup state
        self._last_sig: Optional[tuple[str, str, str]] = None
        self._last_ts: float = 0.0
    
    def _format_message(self, message: str, component: str = "") -> str:
        """Formatear mensaje con componente"""
        if component:
            return f"[{component}] {message}"
        return message
    
    def info(self, message: str, component: str = "", **kwargs: Any) -> None:
        formatted = self._format_message(message, component)
        if not _global_should_emit("info", component or self.component_name, formatted):
            return
        sig = ("info", component or self.component_name, formatted)
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return
        self._last_sig = sig
        self._last_ts = now
        self.logger.info(formatted)
    
    def warning(self, message: str, component: str = "", **kwargs: Any) -> None:
        formatted = self._format_message(message, component)
        if not _global_should_emit("warning", component or self.component_name, formatted):
            return
        sig = ("warning", component or self.component_name, formatted)
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return
        self._last_sig = sig
        self._last_ts = now
        self.logger.warning(formatted)
    
    def error(self, message: str, component: str = "", **kwargs: Any) -> None:
        formatted = self._format_message(message, component)
        if not _global_should_emit("error", component or self.component_name, formatted):
            return
        sig = ("error", component or self.component_name, formatted)
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return
        self._last_sig = sig
        self._last_ts = now
        self.logger.error(formatted)
    
    def debug(self, message: str, component: str = "", **kwargs: Any) -> None:
        formatted = self._format_message(message, component)
        if not _global_should_emit("debug", component or self.component_name, formatted):
            return
        sig = ("debug", component or self.component_name, formatted)
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return
        self._last_sig = sig
        self._last_ts = now
        self.logger.debug(formatted)
    
    def critical(self, message: str, component: str = "", **kwargs: Any) -> None:
        formatted = self._format_message(message, component)
        if not _global_should_emit("critical", component or self.component_name, formatted):
            return
        sig = ("critical", component or self.component_name, formatted)
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return
        self._last_sig = sig
        self._last_ts = now
        self.logger.critical(formatted)


class MinimalLoggerAdapter:
    """⚡ Adaptador mínimo para máximo rendimiento"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self._last_sig: Optional[tuple[str, str, str]] = None
        self._last_ts: float = 0.0

    def _should_emit(self, level: str, message: str, component: str) -> bool:
        sig = (level, component or self.component_name, message.strip())
        now = time.monotonic()
        if self._last_sig == sig and (now - self._last_ts) < 1.0:
            return False
        self._last_sig = sig
        self._last_ts = now
        return True
    
    def info(self, message: str, component: str = "", **kwargs: Any) -> None:
        if not _global_should_emit("info", component or self.component_name, message):
            return
        if not self._should_emit("info", message, component):
            return
        print(f"[INFO][{self.component_name}][{component}] {message}")
    
    def warning(self, message: str, component: str = "", **kwargs: Any) -> None:
        if not _global_should_emit("warning", component or self.component_name, message):
            return
        if not self._should_emit("warning", message, component):
            return
        print(f"[WARNING][{self.component_name}][{component}] {message}")
    
    def error(self, message: str, component: str = "", **kwargs: Any) -> None:
        if not _global_should_emit("error", component or self.component_name, message):
            return
        if not self._should_emit("error", message, component):
            return
        print(f"[ERROR][{self.component_name}][{component}] {message}")
    
    def debug(self, message: str, component: str = "", **kwargs: Any) -> None:
        # Debug messages are typically suppressed in minimal mode
        if not _global_should_emit("debug", component or self.component_name, message):
            return
        if not self._should_emit("debug", message, component):
            return
        # usually suppressed; keep noop
    
    def critical(self, message: str, component: str = "", **kwargs: Any) -> None:
        if not _global_should_emit("critical", component or self.component_name, message):
            return
        if not self._should_emit("critical", message, component):
            return
        print(f"[CRITICAL][{self.component_name}][{component}] {message}")

# =============================================================================
# Global de-dup solo para mensajes de apagado/parada
# =============================================================================

_DEDUP_WINDOW_SEC = float(os.getenv('ICT_LOG_DEDUP_WINDOW_SEC', '1.0'))
# clave: (nivel, componente, mensaje_normalizado)
_DEDUP_CACHE: Dict[tuple[str, str, str], float] = {}
_DEDUP_KEYWORDS = (
    'shutdown',
    'stopped',
    'shutting down',
    'shutdown completado',
    'system monitoring stopped',
    'desconectado de mt5',
    'forzando cierre inmediato',
    'real-time data processing stopped',
    'alert integration system stopped',
    'production system shutdown complete',
    'shutdown successfully'
)

def _global_should_emit(level: str, component: str, message: str) -> bool:
    try:
        msg = (message or '').strip()
        low = msg.lower()
        # Solo activar de-dup para mensajes de cierre/parada
        if not any(k in low for k in _DEDUP_KEYWORDS):
            return True
        key = (level, (component or '').strip(), low)
        now = time.monotonic()
        last = _DEDUP_CACHE.get(key)
        if last is not None and (now - last) < _DEDUP_WINDOW_SEC:
            return False
        _DEDUP_CACHE[key] = now
        # poda simple para evitar crecimiento
        if len(_DEDUP_CACHE) > 512:
            cutoff = now - max(_DEDUP_WINDOW_SEC, 1.0)
            for k in list(_DEDUP_CACHE.keys())[:256]:
                if _DEDUP_CACHE.get(k, 0.0) < cutoff:
                    _DEDUP_CACHE.pop(k, None)
        return True
    except Exception:
        return True


# =============================================================================
# 3. FACTORY Y GESTIÓN CENTRALIZADA
# =============================================================================

class UnifiedLoggingFactory:
    """🏭 Factory centralizada para loggers unificados"""
    
    _instance: Optional['UnifiedLoggingFactory'] = None
    _loggers_cache: Dict[str, UnifiedLogger] = {}
    _smart_logger_available: Optional[bool] = None
    _smart_logger_class: Optional[Any] = None
    _logging_config: Dict[str, Any] = {
        'prefer_smart_logger': True,
        'fallback_to_standard': True,
        'enable_debug': False,
        'minimal_mode': False
    }
    
    def __new__(cls) -> 'UnifiedLoggingFactory':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def configure(cls, **config: Any) -> None:
        """Configurar factory globalmente"""
        if cls._instance is None:
            cls._instance = cls()
        cls._instance._logging_config.update(config)
        cls._instance._clear_cache()
    
    def _clear_cache(self) -> None:
        """Limpiar cache de loggers"""
        self._loggers_cache.clear()
    
    def _check_smart_logger(self) -> bool:
        """Verificar disponibilidad de SmartTradingLogger (con cache)"""
        if self._smart_logger_available is None:
            try:
                from smart_trading_logger import SmartTradingLogger
                self._smart_logger_class = SmartTradingLogger
                self._smart_logger_available = True
            except ImportError:
                self._smart_logger_available = False
                self._smart_logger_class = None
        return self._smart_logger_available
    
    def create_logger(self, component_name: str, **kwargs: Any) -> UnifiedLogger:
        """Crear logger unificado"""
        # Check cache
        if component_name in self._loggers_cache:
            return self._loggers_cache[component_name]
        
        # Override config per component if needed
        config = {**self._logging_config, **kwargs}
        
        # Determine strategy
        if config.get('minimal_mode', False):
            logger = MinimalLoggerAdapter(component_name)
        elif config.get('prefer_smart_logger', True) and self._check_smart_logger() and self._smart_logger_class:
            try:
                smart_instance = self._smart_logger_class(component_name)
                logger = SmartTradingLoggerAdapter(component_name, smart_instance)
            except Exception:
                # Fallback if SmartTradingLogger fails to initialize
                if config.get('fallback_to_standard', True):
                    logger = StandardLoggerAdapter(component_name)
                else:
                    logger = MinimalLoggerAdapter(component_name)
        elif config.get('fallback_to_standard', True):
            logger = StandardLoggerAdapter(component_name)
        else:
            logger = MinimalLoggerAdapter(component_name)
        
        # Cache and return
        self._loggers_cache[component_name] = logger
        return logger


# =============================================================================
# 4. API PÚBLICA SIMPLIFICADA
# =============================================================================

# Global factory instance
_factory = UnifiedLoggingFactory()

def get_unified_logger(component_name: str, **config: Any) -> UnifiedLogger:
    """
    🎯 Función principal para obtener logger unificado
    
    Args:
        component_name: Nombre del componente
        **config: Configuración específica (override global)
        
    Returns:
        Logger unificado que cumple UnifiedLogger protocol
        
    Example:
        ```python
        logger = get_unified_logger("TradingEngine")
        logger.info("Sistema iniciado", "CORE")
        ```
    """
    return _factory.create_logger(component_name, **config)

def configure_unified_logging(**config: Any) -> None:
    """
    ⚙️ Configurar logging unificado globalmente
    
    Args:
        prefer_smart_logger: bool = True - Preferir SmartTradingLogger
        fallback_to_standard: bool = True - Fallback a logging estándar
        enable_debug: bool = False - Habilitar mensajes debug
        minimal_mode: bool = False - Modo mínimo (solo print)
        
    Example:
        ```python
        configure_unified_logging(
            prefer_smart_logger=True,
            minimal_mode=False,
            enable_debug=True
        )
        ```
    """
    UnifiedLoggingFactory.configure(**config)

def clear_logging_cache() -> None:
    """🧹 Limpiar cache de loggers (útil para tests o reconfiguración)"""
    _factory._clear_cache()

# =============================================================================
# 5. UTILIDADES DE CONVENIENCIA
# =============================================================================

def log_system_startup(component_name: str, details: Optional[Dict[str, Any]] = None) -> None:
    """🚀 Log estandarizado de inicio de sistema"""
    logger = get_unified_logger(component_name)
    message = f"✅ {component_name} inicializado"
    if details:
        message += f" - {details}"
    logger.info(message, "STARTUP")

def log_error_with_context(component_name: str, error: Exception, 
                          context: Optional[Dict[str, Any]] = None) -> None:
    """❌ Log estandarizado de errores con contexto"""
    logger = get_unified_logger(component_name)
    message = f"Error: {type(error).__name__}: {error}"
    if context:
        message += f" | Context: {context}"
    logger.error(message, "ERROR")

def log_performance_metric(component_name: str, metric_name: str, 
                          value: Union[int, float], unit: str = "") -> None:
    """📊 Log estandarizado de métricas"""
    logger = get_unified_logger(component_name)
    message = f"📊 {metric_name}: {value}"
    if unit:
        message += f" {unit}"
    logger.info(message, "METRICS")

# =============================================================================
# 6. COMPATIBILITY LAYER
# =============================================================================

def create_safe_logger(name: str, **kwargs: Any) -> UnifiedLogger:
    """🔄 Función de compatibilidad con create_safe_logger existente"""
    return get_unified_logger(name, **kwargs)

# Export all for easy imports
__all__ = [
    'UnifiedLogger',
    'get_unified_logger', 
    'configure_unified_logging',
    'clear_logging_cache',
    'log_system_startup',
    'log_error_with_context', 
    'log_performance_metric',
    'create_safe_logger'
]