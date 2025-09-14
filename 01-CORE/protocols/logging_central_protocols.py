#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ LOGGING CENTRAL PROTOCOLS - ICT ENGINE v6.0 ENTERPRISE
=========================================================

Protocolos y estándares para logging centralizado en todo el sistema.
Define patrones, configuraciones y mejores prácticas para logging consistente.

Características:
✅ Protocolos estándar de logging
✅ Configuraciones centralizadas 
✅ Patrones de manejo de errores
✅ Fallbacks robustos
✅ Integración con SmartTradingLogger

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

from typing import Dict, Any, Optional, Callable, Protocol
from dataclasses import dataclass
from enum import Enum
import logging
import os
import sys
from datetime import datetime

# Protocolo para logger enterprise
class EnterpriseLoggerProtocol(Protocol):
    """Protocolo que define interfaz de logger enterprise"""
    def info(self, message: str, component: str) -> None:
        """Log info message with component"""
        ...
    
    def warning(self, message: str, component: str) -> None:
        """Log warning message with component"""
        ...
        
    def error(self, message: str, component: str) -> None:
        """Log error message with component"""
        ...
        
    def debug(self, message: str, component: str) -> None:
        """Log debug message with component"""
        ...

class LogLevel(Enum):
    """Niveles de logging estándar"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LoggingConfig:
    """Configuración de logging centralizada"""
    component_name: str
    log_level: LogLevel = LogLevel.INFO
    use_smart_logger: bool = True
    fallback_enabled: bool = True
    format_string: str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    date_format: str = "%H:%M:%S"

class LoggingProtocols:
    """
    🛡️ Protocolos de Logging Central Enterprise
    
    Define estándares y patrones para logging consistente
    en todo el sistema ICT Engine v6.0
    """
    
    # Configuración central de SmartTradingLogger
    SMART_LOGGER_AVAILABLE = None
    SMART_LOGGER_CLASS = None
    
    @classmethod
    def initialize_smart_logger_system(cls):
        """Inicializar sistema SmartTradingLogger centralizado"""
        if cls.SMART_LOGGER_AVAILABLE is None:
            try:
                # Intentar importación directa
                from smart_trading_logger import SmartTradingLogger
                cls.SMART_LOGGER_CLASS = SmartTradingLogger
                cls.SMART_LOGGER_AVAILABLE = True
                print("[PROTOCOL] ✅ SmartTradingLogger disponible (import directo)")
            except ImportError:
                try:
                    # Intentar importación relativa desde 01-CORE
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from smart_trading_logger import SmartTradingLogger
                    cls.SMART_LOGGER_CLASS = SmartTradingLogger
                    cls.SMART_LOGGER_AVAILABLE = True
                    print("[PROTOCOL] ✅ SmartTradingLogger disponible (import relativo)")
                except ImportError:
                    cls.SMART_LOGGER_CLASS = None
                    cls.SMART_LOGGER_AVAILABLE = False
                    print("[PROTOCOL] ⚠️ SmartTradingLogger no disponible")
    
    @classmethod
    def create_enterprise_logger(cls, config: LoggingConfig) -> EnterpriseLoggerProtocol:
        """
        Crear logger enterprise siguiendo protocolos establecidos
        
        Args:
            config: Configuración del logger
            
        Returns:
            EnterpriseLoggerProtocol: Logger configurado
        """
        cls.initialize_smart_logger_system()
        
        if config.use_smart_logger and cls.SMART_LOGGER_AVAILABLE and cls.SMART_LOGGER_CLASS:
            # Usar SmartTradingLogger
            return cls.SMART_LOGGER_CLASS(config.component_name)
        else:
            # Usar fallback logger estándar
            return cls._create_fallback_logger(config)
    
    @classmethod
    def _create_fallback_logger(cls, config: LoggingConfig) -> 'FallbackLogger':
        """Crear logger fallback estándar"""
        logger = logging.getLogger(config.component_name)
        
        # Configurar nivel
        log_levels = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        logger.setLevel(log_levels.get(config.log_level, logging.INFO))
        
        # Configurar handler si no existe
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(config.format_string, config.date_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return FallbackLogger(logger)
    
    @classmethod
    def get_standard_config(cls, component_name: str, **kwargs) -> LoggingConfig:
        """Obtener configuración estándar para un componente"""
        return LoggingConfig(
            component_name=component_name,
            **kwargs
        )

class FallbackLogger:
    """Logger fallback que implementa EnterpriseLoggerProtocol"""
    
    def __init__(self, standard_logger: logging.Logger):
        self.logger = standard_logger
    
    def info(self, message: str, component: str) -> None:
        self.logger.info(f"[{component}] {message}")
    
    def warning(self, message: str, component: str) -> None:
        self.logger.warning(f"[{component}] {message}")
    
    def error(self, message: str, component: str) -> None:
        self.logger.error(f"[{component}] {message}")
    
    def debug(self, message: str, component: str) -> None:
        self.logger.debug(f"[{component}] {message}")

# Decorador para logging automático
def with_enterprise_logging(component_name: str):
    """
    Decorador para agregar logging enterprise automáticamente
    
    Args:
        component_name: Nombre del componente
    """
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Crear logger usando protocolos
            config = LoggingProtocols.get_standard_config(component_name)
            self.logger = LoggingProtocols.create_enterprise_logger(config)
            
            # Llamar al init original
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator

# Funciones de utilidad para protocolos
def setup_module_logging(component_name: str, 
                        log_level: LogLevel = LogLevel.INFO) -> EnterpriseLoggerProtocol:
    """
    Configurar logging para un módulo siguiendo protocolos
    
    Args:
        component_name: Nombre del componente
        log_level: Nivel de logging
        
    Returns:
        EnterpriseLoggerProtocol: Logger configurado
    """
    config = LoggingProtocols.get_standard_config(
        component_name, 
        log_level=log_level
    )
    return LoggingProtocols.create_enterprise_logger(config)

def create_safe_logger(component_name: str, 
                      fallback_to_print: bool = True) -> EnterpriseLoggerProtocol:
    """
    Crear logger con máximo nivel de seguridad
    
    Args:
        component_name: Nombre del componente
        fallback_to_print: Si usar print como último recurso
        
    Returns:
        EnterpriseLoggerProtocol: Logger ultra-seguro
    """
    try:
        config = LoggingProtocols.get_standard_config(component_name)
        return LoggingProtocols.create_enterprise_logger(config)
    except Exception as e:
        if fallback_to_print:
            print(f"[PROTOCOL_ERROR] No se pudo crear logger para {component_name}: {e}")
            return PrintLogger(component_name)
        else:
            raise

class PrintLogger:
    """Logger de emergencia que usa print()"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
    
    def info(self, message: str, component: str) -> None:
        print(f"[INFO] [{component}] {message}")
    
    def warning(self, message: str, component: str) -> None:
        print(f"[WARNING] [{component}] {message}")
    
    def error(self, message: str, component: str) -> None:
        print(f"[ERROR] [{component}] {message}")
    
    def debug(self, message: str, component: str) -> None:
        print(f"[DEBUG] [{component}] {message}")

# Validación de protocolos
class ProtocolValidator:
    """Validador de cumplimiento de protocolos"""
    
    @staticmethod
    def validate_logger_implementation(logger: Any) -> bool:
        """Validar que un logger cumple con los protocolos"""
        required_methods = ['info', 'warning', 'error', 'debug']
        
        for method_name in required_methods:
            if not hasattr(logger, method_name):
                return False
            method = getattr(logger, method_name)
            if not callable(method):
                return False
        
        return True
    
    @staticmethod
    def get_protocol_compliance_report(logger: Any) -> Dict[str, Any]:
        """Obtener reporte de cumplimiento de protocolos"""
        report = {
            'compliant': False,
            'logger_type': type(logger).__name__,
            'missing_methods': [],
            'timestamp': datetime.now()
        }
        
        required_methods = ['info', 'warning', 'error', 'debug']
        
        for method_name in required_methods:
            if not hasattr(logger, method_name):
                report['missing_methods'].append(method_name)
        
        report['compliant'] = len(report['missing_methods']) == 0
        
        return report

# Exportaciones del protocolo
__all__ = [
    'LoggingProtocols',
    'LoggingConfig', 
    'LogLevel',
    'EnterpriseLoggerProtocol',
    'FallbackLogger',
    'PrintLogger',
    'ProtocolValidator',
    'setup_module_logging',
    'create_safe_logger',
    'with_enterprise_logging'
]