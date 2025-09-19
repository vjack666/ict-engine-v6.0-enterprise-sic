#!/usr/bin/env python3
"""
🔧 DASHBOARD LOGGER - Sistema de logging para dashboard
=====================================================

Manejo centralizado de logs para el dashboard ICT Engine.
Incluye rotación de archivos, niveles configurables y formato consistente.

Versión: v6.1.0-enterprise
"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional

class DashboardLogger:
    """📝 Logger configurado para el dashboard ICT"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializar logger con configuración"""
        self.config = config
        self.logger = logging.getLogger('ICTDashboard')
        self._setup_logger()
    
    def _setup_logger(self):
        """Configurar logger con handlers apropriados"""
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar nivel
        level = self.config.get('level', 'INFO').upper()
        self.logger.setLevel(getattr(logging, level, logging.INFO))
        
        # Formato de logs
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
        self.logger.addHandler(console_handler)
        
        # Handler para archivo (si está configurado)
        log_file = self.config.get('file')
        if log_file:
            try:
                # Crear logs en 05-LOGS/application/dashboard/
                project_root = Path(__file__).parent.parent.parent
                log_path = project_root / "05-LOGS" / "application" / "dashboard" / log_file
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                max_size = self.config.get('max_size_mb', 10) * 1024 * 1024
                backup_count = self.config.get('backup_count', 5)
                
                if os.getenv('ICT_DISABLE_LOG_ROTATION') == '1':
                    file_handler = logging.FileHandler(log_path, encoding='utf-8')
                else:
                    file_handler = RotatingFileHandler(
                        log_path,
                        maxBytes=max_size,
                        backupCount=backup_count,
                        encoding='utf-8'
                    )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                
            except Exception as e:
                print(f"⚠️ No se pudo configurar logging a archivo: {e}")
    
    def debug(self, message: str):
        """Log debug"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical"""
        self.logger.critical(message)
    
    def dashboard_event(self, event_type: str, details: Dict[str, Any]):
        """Log evento específico del dashboard"""
        message = f"[{event_type}] {details}"
        self.info(message)
    
    def performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log métrica de rendimiento"""
        message = f"[PERFORMANCE] {metric_name}: {value:.2f}{unit}"
        self.info(message)
    
    def fvg_event(self, action: str, symbol: str, details: Dict[str, Any]):
        """Log evento FVG específico"""
        message = f"[FVG] {action} {symbol}: {details}"
        self.info(message)
