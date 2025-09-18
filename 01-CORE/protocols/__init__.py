#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ PROTOCOLS MODULE INITIALIZATION - ICT ENGINE v6.0 ENTERPRISE
================================================================

Punto de entrada único del paquete `protocols`.
Re-exporta las APIs de logging unificado y enterprise para resolver imports
de forma más amigable en editores (Pylance) y mantener compatibilidad.

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

# ---------------------------------------------------------------------------
# Logging central protocols (clásico)
# ---------------------------------------------------------------------------
from .logging_central_protocols import (
    LoggingProtocols,
    LoggingConfig,
    LogLevel as LogLevel,  # Mantener nombre histórico
    EnterpriseLoggerProtocol,
    FallbackLogger,
    PrintLogger,
    ProtocolValidator,
    setup_module_logging,
    create_safe_logger as create_safe_logger_central,
    with_enterprise_logging,
)

# ---------------------------------------------------------------------------
# Enterprise logging protocol (optimizado producción)
# ---------------------------------------------------------------------------
from .logging_protocol import (
    CentralLogger,
    LogLevel as EnterpriseLogLevel,
    LogCategory,
    EnterpriseLoggingConfig,
    create_enterprise_logger,
    create_safe_logger as create_safe_logger_enterprise,
    create_central_logger,
    get_central_logger,
    get_logger,
    EnterpriseLoggerFactory,
    initialize_enterprise_logging_system,
)

# ---------------------------------------------------------------------------
# Unified logging facade (adaptador unificado)
# ---------------------------------------------------------------------------
from .unified_logging import (
    get_unified_logger,
    configure_unified_logging,
    clear_logging_cache,
    log_system_startup,
    log_error_with_context,
    log_performance_metric,
    create_safe_logger as create_safe_logger_unified,
)

__all__ = [
    # Central protocols (clásico)
    'LoggingProtocols',
    'LoggingConfig',
    'LogLevel',
    'EnterpriseLoggerProtocol',
    'FallbackLogger',
    'PrintLogger',
    'ProtocolValidator',
    'setup_module_logging',
    'create_safe_logger_central',
    'with_enterprise_logging',
    # Enterprise logging (producción)
    'CentralLogger',
    'EnterpriseLogLevel',
    'LogCategory',
    'EnterpriseLoggingConfig',
    'create_enterprise_logger',
    'create_safe_logger_enterprise',
    'create_central_logger',
    'get_central_logger',
    'get_logger',
    'EnterpriseLoggerFactory',
    'initialize_enterprise_logging_system',
    # Unified facade
    'get_unified_logger',
    'configure_unified_logging',
    'clear_logging_cache',
    'log_system_startup',
    'log_error_with_context',
    'log_performance_metric',
    'create_safe_logger_unified',
]