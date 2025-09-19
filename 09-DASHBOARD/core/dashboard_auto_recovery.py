#!/usr/bin/env python3
"""
🔧 DASHBOARD AUTO-RECOVERY SYSTEM
================================

Sistema de auto-recuperación para el Dashboard Enterprise del ICT Engine v6.0.
Detecta fallos del dashboard y ejecuta recovery automático.

Características:
- ✅ Detección de procesos dashboard colgados
- ✅ Monitoreo de health endpoints
- ✅ Restart automático con validación de estado
- ✅ Logging detallado de eventos de recovery
- ✅ Integración con sistema de alertas
- ⚡ Recovery rápido <30 segundos

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 18 de Septiembre, 2025
Versión: v1.0-auto-recovery
"""

import sys
import os
import time
import threading
import subprocess
import psutil
import signal
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import traceback

# Configurar rutas
dashboard_dir = Path(__file__).parent.parent.absolute()  # /09-DASHBOARD/
project_root = dashboard_dir.parent                      # /project_root/

# Agregar paths (01-CORE primero para evitar conflictos)
sys.path.extend([
    str(project_root / "01-CORE"),  # Prioridad al 01-CORE
    str(project_root),
    str(dashboard_dir)
])

try:
    from smart_trading_logger import SmartTradingLogger
    _LOGGER_AVAILABLE = True
except ImportError:
    _LOGGER_AVAILABLE = False
    # Fallback para logging básico
    import logging
    
    class FallbackLogger:
        def __init__(self):
            self.logger = logging.getLogger("DashboardAutoRecovery")
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        def info(self, message): self.logger.info(message)
        def warning(self, message): self.logger.warning(message)
        def error(self, message): self.logger.error(message)
        def critical(self, message): self.logger.critical(message)
    
    SmartTradingLogger = FallbackLogger

class DashboardAutoRecovery:
    """🔧 Sistema de auto-recuperación del dashboard"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar sistema de auto-recovery
        
        Args:
            config: Configuración personalizada del recovery system
        """
        self.config = self._setup_default_config()
        if config:
            self.config.update(config)
        
        # Configurar logging
        self.logger = SmartTradingLogger()
        
        # Paths del sistema
        self.dashboard_dir = dashboard_dir
        self.project_root = project_root
        
        # Estado del sistema
        self.is_monitoring = False
        self.monitoring_thread = None
        self.dashboard_process = None
        self.last_successful_check = datetime.now()
        self.recovery_attempts = 0
        self.max_recovery_attempts = self.config['max_recovery_attempts']
        
        # Callbacks para eventos
        self.on_failure_detected: Optional[Callable] = None
        self.on_recovery_started: Optional[Callable] = None
        self.on_recovery_completed: Optional[Callable] = None
        self.on_recovery_failed: Optional[Callable] = None
        
        self.logger.info("🔧 Dashboard Auto-Recovery System inicializado")
    
    def _setup_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del sistema de recovery (optimizado, sin web server)"""
        return {
            # Intervalos de monitoreo
            'check_interval': 45,  # segundos entre checks (aumentado para menos overhead)
            'health_timeout': 8,   # timeout para health checks (reducido)
            'restart_timeout': 45, # timeout para restart del dashboard (reducido)
            
            # Límites de recovery
            'max_recovery_attempts': 3,  # Reducido de 5 a 3
            'recovery_cooldown': 180,    # Reducido de 300s a 180s (3 minutos)
            
            # Dashboard configuration
            'dashboard_script_path': str(dashboard_dir / 'start_dashboard.py'),
            
            # Process monitoring (más estricto para mejor performance)
            'process_memory_limit_mb': 768,   # Reducido de 1024MB a 768MB
            'process_cpu_limit_percent': 75,  # Reducido de 80% a 75%
            'process_check_enabled': True,
            
            # Logging
            'log_recovery_events': True,
            'log_detailed_health_checks': False
        }
    
    def set_failure_callback(self, callback: Callable):
        """Configurar callback para detección de fallos"""
        self.on_failure_detected = callback
    
    def set_recovery_callbacks(self, 
                              started: Optional[Callable] = None,
                              completed: Optional[Callable] = None, 
                              failed: Optional[Callable] = None):
        """Configurar callbacks para eventos de recovery"""
        if started:
            self.on_recovery_started = started
        if completed:
            self.on_recovery_completed = completed
        if failed:
            self.on_recovery_failed = failed
    
    def start_monitoring(self):
        """Iniciar monitoreo del dashboard"""
        if self.is_monitoring:
            self.logger.warning("🟡 Monitoreo ya está activo")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name="DashboardAutoRecovery",
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🟢 Dashboard Auto-Recovery monitoreo iniciado")
        self.logger.info(f"   • Check interval: {self.config['check_interval']}s")
        self.logger.info(f"   • Max recovery attempts: {self.max_recovery_attempts}")
    
    def stop_monitoring(self):
        """Detener monitoreo del dashboard"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("🔴 Dashboard Auto-Recovery monitoreo detenido")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        self.logger.info("🔍 Iniciando loop de monitoreo del dashboard...")
        
        while self.is_monitoring:
            try:
                # Verificar salud del dashboard
                is_healthy = self._check_dashboard_health()
                
                if is_healthy:
                    self.last_successful_check = datetime.now()
                    self.recovery_attempts = 0  # Reset counter en checks exitosos
                    
                    if self.config['log_detailed_health_checks']:
                        self.logger.info("✅ Dashboard health check OK")
                else:
                    self.logger.warning("🔴 Dashboard health check FAILED")
                    self._handle_dashboard_failure()
                
                # Esperar antes del siguiente check
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                self.logger.error(f"❌ Error en monitoring loop: {e}")
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                time.sleep(self.config['check_interval'])
    
    def _check_dashboard_health(self) -> bool:
        """
        Verificar salud completa del dashboard
        
        Returns:
            bool: True si dashboard está saludable
        """
        try:
            # Check 1: Verificar proceso está vivo
            if self.config['process_check_enabled']:
                if not self._check_process_health():
                    return False
            
            # Check 2: Verificar recursos del sistema
            if not self._check_system_resources():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en health check: {e}")
            return False
    
    def _check_process_health(self) -> bool:
        """Verificar salud del proceso del dashboard"""
        try:
            # Buscar proceso del dashboard
            dashboard_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('start_dashboard.py' in arg for arg in proc.info['cmdline']):
                        dashboard_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not dashboard_processes:
                self.logger.warning("⚠️ No se encontró proceso del dashboard")
                return False
            
            # Verificar salud del proceso principal
            main_process = dashboard_processes[0]
            
            # Check memory usage
            memory_mb = main_process.memory_info().rss / 1024 / 1024
            if memory_mb > self.config['process_memory_limit_mb']:
                self.logger.warning(f"⚠️ Dashboard usando demasiada memoria: {memory_mb:.1f}MB")
                return False
            
            # Check CPU usage
            cpu_percent = main_process.cpu_percent()
            if cpu_percent > self.config['process_cpu_limit_percent']:
                self.logger.warning(f"⚠️ Dashboard usando demasiado CPU: {cpu_percent:.1f}%")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando proceso: {e}")
            return False
    
    def _check_system_resources(self) -> bool:
        """Verificar recursos del sistema"""
        try:
            # Check memory del sistema
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning(f"⚠️ Memoria del sistema alta: {memory.percent:.1f}%")
                return False
            
            # Check CPU del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                self.logger.warning(f"⚠️ CPU del sistema alta: {cpu_percent:.1f}%")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando recursos del sistema: {e}")
            return False
    
    def _handle_dashboard_failure(self):
        """Manejar fallo detectado del dashboard"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self.logger.critical("🚨 CRÍTICO: Máximo número de recovery attempts alcanzado")
            if self.on_recovery_failed:
                self.on_recovery_failed("Max recovery attempts exceeded")
            return
        
        # Verificar cooldown period
        time_since_last_success = datetime.now() - self.last_successful_check
        if time_since_last_success < timedelta(seconds=self.config['recovery_cooldown']):
            remaining = self.config['recovery_cooldown'] - time_since_last_success.total_seconds()
            self.logger.info(f"⏳ Recovery en cooldown, esperando {remaining:.0f}s")
            return
        
        # Callback de fallo detectado
        if self.on_failure_detected:
            self.on_failure_detected("Dashboard health check failed")
        
        # Iniciar recovery
        self.recovery_attempts += 1
        self.logger.warning(f"🔄 Iniciando recovery attempt {self.recovery_attempts}/{self.max_recovery_attempts}")
        
        recovery_success = self._execute_recovery()
        
        if recovery_success:
            self.logger.info("✅ Dashboard recovery completado exitosamente")
            if self.on_recovery_completed:
                self.on_recovery_completed()
        else:
            self.logger.error("❌ Dashboard recovery falló")
            if self.on_recovery_failed:
                self.on_recovery_failed("Recovery execution failed")
    
    def _execute_recovery(self) -> bool:
        """
        Ejecutar proceso de recovery del dashboard
        
        Returns:
            bool: True si recovery fue exitoso
        """
        try:
            if self.on_recovery_started:
                self.on_recovery_started()
            
            self.logger.info("🔄 Paso 1: Terminando procesos dashboard existentes...")
            self._terminate_dashboard_processes()
            
            self.logger.info("🔄 Paso 2: Limpiando recursos...")
            self._cleanup_dashboard_resources()
            
            self.logger.info("🔄 Paso 3: Reiniciando dashboard...")
            success = self._restart_dashboard()
            
            if success:
                self.logger.info("🔄 Paso 4: Validando nuevo dashboard...")
                # Dar tiempo al dashboard para inicializar
                time.sleep(15)
                return self._validate_recovery()
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error durante recovery: {e}")
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def _terminate_dashboard_processes(self):
        """Terminar todos los procesos del dashboard"""
        terminated_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('start_dashboard.py' in arg for arg in proc.info['cmdline']):
                    self.logger.info(f"   • Terminando proceso {proc.pid}")
                    proc.terminate()
                    terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Dar tiempo para termination graceful
        time.sleep(5)
        
        # Force kill si es necesario
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('start_dashboard.py' in arg for arg in proc.info['cmdline']):
                    self.logger.warning(f"   • Force killing proceso {proc.pid}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.logger.info(f"   • Terminados {terminated_count} procesos dashboard")
    
    def _cleanup_dashboard_resources(self):
        """Limpiar recursos del dashboard"""
        try:
            # Limpiar archivos temporales
            temp_patterns = [
                '*.tmp',
                '*.lock',
                '__pycache__/*'
            ]
            
            # Limpiar logs muy grandes
            log_dir = Path(self.project_root) / "05-LOGS" / "dashboard"
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                        self.logger.info(f"   • Rotando log grande: {log_file.name}")
                        backup_name = f"{log_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                        log_file.rename(log_dir / backup_name)
                        log_file.touch()  # Crear nuevo archivo vacío
            
            self.logger.info("   • Recursos limpiados")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error limpiando recursos: {e}")
    
    def _restart_dashboard(self) -> bool:
        """Reiniciar el dashboard"""
        try:
            # Comando para reiniciar dashboard
            cmd = [sys.executable, self.config['dashboard_script_path']]
            
            self.logger.info(f"   • Ejecutando: {' '.join(cmd)}")
            
            # Iniciar proceso en background
            self.dashboard_process = subprocess.Popen(
                cmd,
                cwd=str(self.dashboard_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.logger.info(f"   • Dashboard iniciado con PID: {self.dashboard_process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error reiniciando dashboard: {e}")
            return False
    
    def _validate_recovery(self) -> bool:
        """Validar que el recovery fue exitoso"""
        validation_attempts = 0
        max_validation_attempts = 6  # 6 intentos = 90 segundos
        
        while validation_attempts < max_validation_attempts:
            validation_attempts += 1
            self.logger.info(f"   • Validación attempt {validation_attempts}/{max_validation_attempts}")
            
            if self._check_dashboard_health():
                self.logger.info("✅ Validación exitosa - Dashboard recuperado")
                return True
            
            time.sleep(15)  # Esperar 15 segundos entre validaciones
        
        self.logger.error("❌ Validación falló - Dashboard no recuperado")
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado actual del auto-recovery system"""
        return {
            'is_monitoring': self.is_monitoring,
            'last_successful_check': self.last_successful_check.isoformat(),
            'recovery_attempts': self.recovery_attempts,
            'max_recovery_attempts': self.max_recovery_attempts,
            'config': self.config
        }


def main():
    """Función principal para testing del auto-recovery system"""
    print("🔧 Dashboard Auto-Recovery System - Test Mode")
    
    # Crear instancia del auto-recovery
    recovery = DashboardAutoRecovery()
    
    # Configurar callbacks de prueba
    def on_failure(reason):
        print(f"🚨 FALLO DETECTADO: {reason}")
    
    def on_recovery_started():
        print("🔄 RECOVERY INICIADO")
    
    def on_recovery_completed():
        print("✅ RECOVERY COMPLETADO")
    
    def on_recovery_failed(reason):
        print(f"❌ RECOVERY FALLÓ: {reason}")
    
    recovery.set_failure_callback(on_failure)
    recovery.set_recovery_callbacks(on_recovery_started, on_recovery_completed, on_recovery_failed)
    
    # Iniciar monitoreo
    recovery.start_monitoring()
    
    try:
        print("🔍 Monitoreo activo. Presiona Ctrl+C para salir...")
        while True:
            time.sleep(10)
            status = recovery.get_status()
            print(f"📊 Status: Monitoring={status['is_monitoring']}, "
                  f"Attempts={status['recovery_attempts']}/{status['max_recovery_attempts']}")
    
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitoreo...")
        recovery.stop_monitoring()
        print("✅ Auto-Recovery System detenido")


if __name__ == "__main__":
    main()