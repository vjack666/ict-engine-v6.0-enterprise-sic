#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 LOGGING MODE CONFIGURATION - ICT ENGINE v6.0 ENTERPRISE
===========================================================

Configuración centralizada para controlar el modo silencioso del sistema de logging.
Permite suprimir logs de consola manteniendo el guardado en archivos.

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-09
"""

from protocols.unified_logging import get_unified_logger
import os
from typing import Dict, List

class LoggingModeConfig:
    """🔧 Configuración centralizada para modos de logging"""
    
    # CONFIGURACIÓN PRINCIPAL DE MODO SILENCIOSO
    DASHBOARD_QUIET_MODE = True  # Modo silencioso para dashboard por defecto
    
    # Componentes que deben estar siempre en modo silencioso durante dashboard
    QUIET_COMPONENTS = [
        'FVG_Memory',
        'UnifiedMemorySystem', 
        'PatternDetector',
        'ICT_Engine',
        'OrderBlocksDetector',
        'MarketContext',
        'HistoricalAnalyzer',
        'FractalAnalyzer'
    ]
    
    # Componentes que pueden mostrar logs críticos en consola
    ALLOWED_CONSOLE_COMPONENTS = [
        'DASHBOARD',
        'SYSTEM',
        'ICT_Emergency'
    ]
    
    # Niveles de logging por modo
    LOGGING_LEVELS = {
        'console_silent': 'ERROR',    # Solo errores en consola cuando silencioso
        'console_verbose': 'INFO',    # Modo verbose normal
        'file_always': 'INFO'        # Siempre INFO en archivos
    }
    
    @classmethod
    def should_be_silent(cls, component_name: str) -> bool:
        """
        🤫 Determinar si un componente debe estar en modo silencioso
        
        Args:
            component_name: Nombre del componente
            
        Returns:
            bool: True si debe estar silencioso
        """
        
        # Verificar variable de entorno para override
        env_quiet = os.environ.get('ICT_QUIET_MODE', '').lower()
        if env_quiet == 'false':
            return False
        
        # Verificar si está en modo dashboard silencioso
        if cls.DASHBOARD_QUIET_MODE:
            # Permitir consola para componentes específicos
            if component_name in cls.ALLOWED_CONSOLE_COMPONENTS:
                return False
            # Permitir si el nombre contiene 'dashboard' (case insensitive)
            if 'dashboard' in component_name.lower():
                return False
            # Silenciar componentes ruidosos
            if component_name in cls.QUIET_COMPONENTS:
                return True
            # Por defecto, silencioso durante dashboard para otros componentes
            return True
        
        return False
    
    @classmethod
    def get_console_level(cls, component_name: str, is_silent: bool) -> str:
        """
        📊 Obtener nivel de logging para consola
        
        Args:
            component_name: Nombre del componente
            is_silent: Si está en modo silencioso
            
        Returns:
            str: Nivel de logging
        """
        if is_silent:
            return cls.LOGGING_LEVELS['console_silent']
        else:
            return cls.LOGGING_LEVELS['console_verbose']
    
    @classmethod
    def enable_quiet_mode(cls):
        """🤫 Activar modo silencioso globalmente"""
        os.environ['ICT_QUIET_MODE'] = 'true'
        cls.DASHBOARD_QUIET_MODE = True
    
    @classmethod
    def disable_quiet_mode(cls):
        """🔊 Desactivar modo silencioso globalmente"""
        os.environ['ICT_QUIET_MODE'] = 'false'
        cls.DASHBOARD_QUIET_MODE = False
    
    @classmethod
    def is_dashboard_mode(cls) -> bool:
        """📊 Verificar si está en modo dashboard"""
        return cls.DASHBOARD_QUIET_MODE
    
    @classmethod
    def set_environment_quiet(cls, quiet: bool = True):
        """🌍 Configurar variable de entorno para modo silencioso"""
        if quiet:
            os.environ['ICT_QUIET_MODE'] = 'true'
        else:
            os.environ.pop('ICT_QUIET_MODE', None)

# CONFIGURACIÓN POR DEFECTO AL IMPORTAR
LoggingModeConfig.set_environment_quiet(True)  # Activar modo silencioso por defecto

# CONSTANTES DE CONVENIENCIA
DASHBOARD_QUIET = LoggingModeConfig.DASHBOARD_QUIET_MODE
QUIET_COMPONENTS = LoggingModeConfig.QUIET_COMPONENTS
