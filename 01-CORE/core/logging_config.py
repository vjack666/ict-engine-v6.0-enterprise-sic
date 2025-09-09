#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 LOGGING CENTRALIZADO DIARIO - ICT ENGINE v6.0 ENTERPRISE
============================================================

Sistema de logging centralizado que agrupa todos los logs del día
en archivos únicos por componente, evitando proliferación de archivos.

✅ CARACTERÍSTICAS:
- Un archivo por día por componente  
- Múltiples sesiones en el mismo archivo diario
- Separadores de sesión para identificar ejecuciones
- Rotación automática de logs antiguos
- Viewer integrado para logs diarios

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 2025-09-09
"""

import logging
import os
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class CentralizedLogger:
    """📋 Logger centralizado con archivos diarios consolidados"""
    
    def __init__(self, component_name: str, auto_cleanup_days: int = 30):
        """
        🏗️ Inicializar logger centralizado diario
        
        Args:
            component_name: Nombre del componente (SYSTEM, DASHBOARD, PATTERNS, etc.)
            auto_cleanup_days: Días para mantener logs (default: 30)
        """
        self.component = component_name.upper()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.session_id = datetime.now().strftime('%H:%M:%S')
        self.auto_cleanup_days = auto_cleanup_days
        
        # Configurar logger diario
        self.setup_daily_logger()
        
        # Limpiar logs antiguos automáticamente
        self.cleanup_old_logs()
    
    def setup_daily_logger(self):
        """📅 Configurar logger con UN archivo por día por componente"""
        
        # Crear estructura de directorios
        log_dir = Path("05-LOGS") / self.component.lower()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # ARCHIVO ÚNICO por día
        self.log_file = log_dir / f"{self.component.lower()}_{self.today}.log"
        
        # Logger único por componente y día
        logger_name = f"ICT_{self.component}_{self.today}"
        self.logger = logging.getLogger(logger_name)
        
        # VERIFICAR si ya está configurado para evitar duplicados
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # HANDLER con modo append para agregar al archivo diario
            file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
            
            # FORMATO con timestamp detallado
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # TAMBIÉN mantener output en consola
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def log_session_start(self):
        """🚀 Marcar inicio de nueva sesión en archivo diario"""
        separator = "=" * 80
        
        self.logger.info(f"\n{separator}")
        self.logger.info(f"🚀 NUEVA SESIÓN INICIADA - {self.session_id}")
        self.logger.info(f"📅 Fecha: {self.today}")
        self.logger.info(f"🎯 Componente: {self.component}")
        self.logger.info(f"{separator}")
        
        # También imprimir en consola para seguimiento inmediato
        print(f"\n📋 [{self.component}] Sesión iniciada - {self.session_id}")
    
    def log_session_end(self):
        """⏹️ Marcar fin de sesión en archivo diario"""
        end_time = datetime.now().strftime('%H:%M:%S')
        self.logger.info(f"⏹️ SESIÓN TERMINADA - {end_time}")
        self.logger.info("=" * 40 + "\n")
        
        print(f"📋 [{self.component}] Sesión terminada - {end_time}")
    
    def log_info(self, message: str):
        """ℹ️ Log información"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """❌ Log error"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """⚠️ Log warning"""
        self.logger.warning(message)
    
    def log_debug(self, message: str):
        """🔍 Log debug"""
        self.logger.debug(message)
    
    def log_critical(self, message: str):
        """🚨 Log crítico"""
        self.logger.critical(message)
    
    def log_trading_action(self, action: str, symbol: str = "UNKNOWN", details: Dict[str, Any] = None):
        """💰 Log específico para acciones de trading"""
        details_str = ""
        if details:
            details_str = f" | {details}"
        
        trading_msg = f"💰 TRADING: {action} [{symbol}]{details_str}"
        self.logger.info(trading_msg)
    
    def log_pattern_detection(self, pattern: str, symbol: str = "UNKNOWN", confidence: float = 0.0):
        """🎯 Log específico para detección de patrones"""
        pattern_msg = f"🎯 PATTERN: {pattern} [{symbol}] | Confidence: {confidence:.2f}"
        self.logger.info(pattern_msg)
    
    def log_system_status(self, status: str, component: str = "SYSTEM"):
        """🔧 Log específico para estado del sistema"""
        status_msg = f"🔧 STATUS: {component} | {status}"
        self.logger.info(status_msg)
    
    def cleanup_old_logs(self):
        """🗑️ Eliminar logs más antiguos que X días automáticamente"""
        try:
            log_base_dir = Path("05-LOGS")
            if not log_base_dir.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=self.auto_cleanup_days)
            
            for log_file in log_base_dir.rglob("*.log"):
                try:
                    # EXTRAER fecha del nombre del archivo (formato: component_YYYY-MM-DD.log)
                    filename_parts = log_file.stem.split('_')
                    if len(filename_parts) >= 2:
                        date_str = filename_parts[-1]  # Última parte debería ser YYYY-MM-DD
                        
                        try:
                            file_date = datetime.strptime(date_str, '%Y-%m-%d')
                            
                            if file_date < cutoff_date:
                                log_file.unlink()  # ELIMINAR archivo antiguo
                                print(f"🗑️ [{self.component}] Eliminado log antiguo: {log_file.name}")
                        except ValueError:
                            # Si no se puede parsear la fecha, ignorar el archivo
                            continue
                            
                except (ValueError, IndexError, OSError):
                    # Ignorar archivos que no siguen el formato esperado
                    continue
                    
        except Exception as e:
            # No interrumpir el sistema si falla la limpieza
            print(f"⚠️ [{self.component}] Error en limpieza de logs: {e}")
    
    def compress_old_logs(self, days_old: int = 7):
        """📦 Comprimir logs de más de X días (opcional)"""
        try:
            log_base_dir = Path("05-LOGS")
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            for log_file in log_base_dir.rglob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    # COMPRIMIR archivo
                    compressed_file = f"{log_file}.gz"
                    
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    log_file.unlink()  # ELIMINAR original
                    print(f"📦 [{self.component}] Comprimido: {log_file.name} -> {Path(compressed_file).name}")
                    
        except Exception as e:
            print(f"⚠️ [{self.component}] Error en compresión de logs: {e}")
    
    def get_log_file_path(self) -> Path:
        """📁 Obtener ruta del archivo de log actual"""
        return self.log_file
    
    def get_log_stats(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas del archivo de log actual"""
        try:
            if self.log_file.exists():
                stat = self.log_file.stat()
                
                return {
                    'file_path': str(self.log_file),
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'component': self.component,
                    'date': self.today
                }
            else:
                return {
                    'file_path': str(self.log_file),
                    'status': 'not_created_yet',
                    'component': self.component,
                    'date': self.today
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'component': self.component,
                'date': self.today
            }

# ===== FUNCIONES DE UTILIDAD =====

def get_centralized_logger(component: str) -> CentralizedLogger:
    """🎯 Función helper para obtener logger centralizado"""
    return CentralizedLogger(component)

def list_log_files() -> Dict[str, Any]:
    """📋 Listar todos los archivos de log actuales"""
    log_base_dir = Path("05-LOGS")
    
    if not log_base_dir.exists():
        return {'status': 'logs_directory_not_found', 'files': []}
    
    log_files = []
    for log_file in log_base_dir.rglob("*.log"):
        try:
            stat = log_file.stat()
            log_files.append({
                'name': log_file.name,
                'path': str(log_file),
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'component': log_file.parent.name.upper()
            })
        except Exception:
            continue
    
    return {
        'status': 'success',
        'total_files': len(log_files),
        'files': sorted(log_files, key=lambda x: x['modified'], reverse=True)
    }

# ===== TESTING Y VALIDACIÓN =====

def test_centralized_logging():
    """🧪 Test básico del sistema de logging centralizado"""
    print("🧪 Probando sistema de logging centralizado...")
    
    # Test con diferentes componentes
    components = ['SYSTEM', 'DASHBOARD', 'PATTERNS', 'TRADING']
    
    for component in components:
        logger = CentralizedLogger(component)
        logger.log_session_start()
        
        logger.log_info(f"Prueba de logging para {component}")
        logger.log_warning(f"Prueba de warning para {component}")
        logger.log_error(f"Prueba de error para {component}")
        
        if component == 'TRADING':
            logger.log_trading_action("BUY", "EURUSD", {"volume": 0.01, "price": 1.0850})
            
        if component == 'PATTERNS':
            logger.log_pattern_detection("Fair Value Gap", "GBPUSD", 0.85)
        
        logger.log_session_end()
        
        # Mostrar estadísticas
        stats = logger.get_log_stats()
        print(f"📊 {component}: {stats.get('size_mb', 0)} MB")
    
    # Listar archivos creados
    files_info = list_log_files()
    print(f"\n📋 Archivos de log creados: {files_info['total_files']}")
    for file_info in files_info['files']:
        print(f"  - {file_info['name']} ({file_info['size_mb']} MB)")

if __name__ == "__main__":
    test_centralized_logging()
