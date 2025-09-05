#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SMART TRADING LOGGER - ICT ENGINE v6.0 ENTERPRISE
====================================================

Sistema de logging centralizado para ICT Engine v6.1.0.
Integrado con Enterprise System.

Autor: ICT Engine v6.1.0 Team
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class SmartTradingLogger:
    """🔧 Logger inteligente para ICT Engine v6.1.0"""
    
    def __init__(self, name: str = "ICT_Engine", level: str = "INFO"):
        """
        🏗️ Inicializar Smart Trading Logger
        
        Args:
            name: Nombre del logger
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Configurar nivel
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO))
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """🔧 Configurar handlers del logger"""
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # File handler (opcional) - ESTRUCTURA CORRECTA DE CARPETAS
        try:
            # Usar la estructura oficial 05-LOGS/application en lugar de raíz/logs
            project_root = Path(__file__).parent.parent.parent
            logs_dir = project_root / "05-LOGS" / "application"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = logs_dir / f"ict_engine_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
            
        except Exception:
            # Si no se puede crear archivo, continuar sin file logging
            pass
    
    def debug(self, message: str, component: str = "CORE", **kwargs):
        """🔍 Log debug message"""
        self.logger.debug(f"[{component}] {message}")
    
    def info(self, message: str, component: str = "CORE", **kwargs):
        """ℹ️ Log info message"""
        self.logger.info(f"[{component}] {message}")
    
    def warning(self, message: str, component: str = "CORE", **kwargs):
        """⚠️ Log warning message"""
        self.logger.warning(f"[{component}] {message}")
    
    def error(self, message: str, component: str = "CORE", **kwargs):
        """❌ Log error message"""
        self.logger.error(f"[{component}] {message}")
    
    def critical(self, message: str, component: str = "CORE", **kwargs):
        """🚨 Log critical message"""
        self.logger.critical(f"[{component}] {message}")

# Instancia global del logger
_smart_logger: Optional[SmartTradingLogger] = None

def get_smart_logger(name: str = "ICT_Engine", level: str = "INFO") -> SmartTradingLogger:
    """🔧 Obtener instancia del Smart Trading Logger"""
    global _smart_logger
    
    if _smart_logger is None:
        _smart_logger = SmartTradingLogger(name, level)
    
    return _smart_logger

# Funciones de conveniencia
def log_info(message: str, component: str = "CORE"):
    """ℹ️ Log info rápido"""
    get_smart_logger().info(message, component)

def log_warning(message: str, component: str = "CORE"):
    """⚠️ Log warning rápido"""
    get_smart_logger().warning(message, component)

def log_error(message: str, component: str = "CORE"):
    """❌ Log error rápido"""
    get_smart_logger().error(message, component)

def log_debug(message: str, component: str = "CORE"):
    """🔍 Log debug rápido"""
    get_smart_logger().debug(message, component)

# Alias para compatibilidad
SmartLogger = SmartTradingLogger
