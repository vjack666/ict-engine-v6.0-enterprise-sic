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
                mode = os.environ.get('ICT_LOGGING_MODE', 'silent').strip().lower()
                if mode == 'silent':
                    # In silent mode, avoid console handlers entirely
                    try:
                        logger.addHandler(logging.NullHandler())
                    except Exception:
                        pass
                    logger.setLevel(logging.WARNING)
                else:
                    handler = logging.StreamHandler(sys.stdout)
                    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
                    handler.setFormatter(formatter)
                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
            # Avoid duplicate emission via root handlers
            try:
                logger.propagate = False
            except Exception:
                pass
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
        if not _global_should_emit("info", component or self.component_name, message):
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
        if not _global_should_emit("warning", component or self.component_name, message):
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
        if not _global_should_emit("error", component or self.component_name, message):
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
        if not _global_should_emit("debug", component or self.component_name, message):
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
        if not _global_should_emit("critical", component or self.component_name, message):
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
# clave: mensaje_normalizado (global)
_DEDUP_CACHE: Dict[str, float] = {}
_DEDUP_KEYWORDS = (
    # English
    'shutdown',
    'stopped',
    'stopping alert integration system',
    'shutting down',
    'shutting down production system',
    'system monitoring stopped',
    'real-time data processing stopped',
    'alert integration system stopped',
    'production system shutdown complete',
    'shutdown successfully',
    # Spanish
    'shutdown completado',
    'iniciando cierre del sistema',
    'monitoreo del sistema detenido',
    'desconectado de mt5',
    'forzando cierre inmediato',
)

def _global_should_emit(level: str, component: str, message: str) -> bool:
    try:
        msg = (message or '').strip()
        low = msg.lower()
        # Solo activar de-dup para mensajes de cierre/parada
        if not any(k in low for k in _DEDUP_KEYWORDS):
            return True
        # clave global: solo por mensaje normalizado (independiente de componente/level)
        key = low
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
# Root logging filter for external emitters
# =============================================================================
class _ShutdownDedupFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            low = (msg or '').strip().lower()
            if not any(k in low for k in _DEDUP_KEYWORDS):
                return True
            now = time.monotonic()
            last = _DEDUP_CACHE.get(low)
            if last is not None and (now - last) < _DEDUP_WINDOW_SEC:
                return False
            _DEDUP_CACHE[low] = now
            return True
        except Exception:
            return True

_ROOT_FILTER_INSTALLED = False

def _ensure_root_filter_installed() -> None:
    global _ROOT_FILTER_INSTALLED
    if _ROOT_FILTER_INSTALLED:
        return
    try:
        root = logging.getLogger()
        # Avoid adding duplicates
        for f in getattr(root, 'filters', []):
            if isinstance(f, _ShutdownDedupFilter):
                _ROOT_FILTER_INSTALLED = True
                return
        root.addFilter(_ShutdownDedupFilter())
        _ROOT_FILTER_INSTALLED = True
    except Exception:
        pass


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
        # Ensure root filter is installed to catch external emitters
        _ensure_root_filter_installed()
        
        # Override config per component if needed
        config = {**self._logging_config, **kwargs}
        # Honor global silent mode: avoid SmartTradingLogger which may emit to console
        try:
            mode = os.environ.get('ICT_LOGGING_MODE', 'silent').strip().lower()
            if mode == 'silent':
                config['prefer_smart_logger'] = False
        except Exception:
            pass
        
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
# 5.1. CARGA DE CONFIGURACIÓN CENTRAL (JSON)
# =============================================================================

_CONFIG_LOADED = False

def _apply_root_and_module_levels(config: Dict[str, Any]) -> None:
    try:
        import logging as _logging
        modes = config.get('modes', {})
        mode = os.environ.get('ICT_LOGGING_MODE', 'silent').strip().lower()
        mode_cfg: Dict[str, Any] = modes.get(mode, {})
        root_level = getattr(_logging, str(mode_cfg.get('root_level', 'WARNING')).upper(), _logging.WARNING)
        _logging.getLogger().setLevel(root_level)
        module_levels: Dict[str, str] = mode_cfg.get('module_levels', {})
        for name, level_str in module_levels.items():
            try:
                lvl = getattr(_logging, str(level_str).upper(), _logging.WARNING)
                lg = _logging.getLogger(name)
                lg.setLevel(lvl)
                # avoid console propagation in silent mode
                if mode == 'silent':
                    lg.propagate = False
            except Exception:
                pass
    except Exception:
        pass

def load_unified_logging_config() -> None:
    """Cargar configuración central de logging desde 01-CORE/config/logging.config.json.

    Aplica niveles root y por módulo, y ajusta la factory para el modo activo.
    Respeta overrides por ENV.
    """
    global _CONFIG_LOADED
    if _CONFIG_LOADED:
        return
    try:
        # Resolver ruta del repo: este archivo está en 01-CORE/protocols
        repo_root = Path(__file__).resolve().parent.parent.parent
        cfg_path = repo_root / '01-CORE' / 'config' / 'logging.config.json'
        if not cfg_path.exists():
            _CONFIG_LOADED = True
            return
        import json as _json
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = _json.load(f)
        # Determinar modo
        mode = os.environ.get('ICT_LOGGING_MODE', 'silent').strip().lower()
        mode_cfg: Dict[str, Any] = (cfg.get('modes') or {}).get(mode, {})
        # Overrides por ENV simples
        # ICT_LOGGING_ROOT_LEVEL=INFO
        env_root = os.environ.get('ICT_LOGGING_ROOT_LEVEL')
        if env_root:
            cfg.setdefault('modes', {})
            mode_cfg = cfg['modes'].setdefault(mode, {})
            mode_cfg['root_level'] = env_root
        # ICT_LOGGING_MODULE_LEVELS='loggerA=ERROR,loggerB=INFO'
        env_mods = os.environ.get('ICT_LOGGING_MODULE_LEVELS')
        if env_mods:
            mode_cfg = cfg['modes'].setdefault(mode, {})
            mods = mode_cfg.setdefault('module_levels', {})
            for pair in env_mods.split(','):
                if '=' in pair:
                    name, lvl = pair.split('=', 1)
                    mods[name.strip()] = lvl.strip()
        # Aplicar niveles root/módulo
        _apply_root_and_module_levels(cfg)
        # Configurar factory defaults
        defaults = {
            'prefer_smart_logger': bool(mode_cfg.get('prefer_smart_logger', True)),
            'fallback_to_standard': bool(mode_cfg.get('fallback_to_standard', True)),
            'enable_debug': bool(mode_cfg.get('enable_debug', False)),
            'minimal_mode': bool(mode_cfg.get('minimal_mode', False)),
        }
        # En modo silent, forzar a no preferir smart logger
        if mode == 'silent':
            defaults['prefer_smart_logger'] = False
        UnifiedLoggingFactory.configure(**defaults)
    except Exception:
        # no bloquear start-up
        pass
    finally:
        _CONFIG_LOADED = True

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