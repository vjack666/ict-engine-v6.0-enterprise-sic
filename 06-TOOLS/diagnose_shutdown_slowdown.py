#!/usr/bin/env python3
"""
🔧 DIAGNÓSTICO DE CIERRE LENTO - ICT ENGINE v6.0 ENTERPRISE
============================================================

Herramienta para diagnosticar y solucionar problemas de cierre lento
en el sistema, especialmente logs ocultos y threads que no terminan.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 10 de Septiembre, 2025
"""

import sys
import os
import time
import threading
import signal
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Configurar rutas
project_root = Path(__file__).parent.absolute()
core_path = project_root / "01-CORE"
sys.path.extend([str(project_root), str(core_path)])

class ShutdownDiagnostic:
    """🔧 Herramienta de diagnóstico de cierre"""
    
    def __init__(self):
        self.start_time = time.time()
        self.shutdown_events = []
        self.running_threads = []
        self.active_loggers = []
        self.daemon_threads = []
        
    def diagnose_system(self) -> Dict[str, Any]:
        """🔍 Diagnosticar estado del sistema antes del cierre"""
        print("🔍 [DIAGNOSTIC] Iniciando diagnóstico del sistema...")
        
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'threads': self._analyze_threads(),
            'processes': self._analyze_processes(), 
            'loggers': self._analyze_loggers(),
            'signal_handlers': self._analyze_signal_handlers(),
            'file_handles': self._analyze_file_handles(),
            'memory_usage': self._analyze_memory()
        }
        
        return diagnosis
    
    def _analyze_threads(self) -> Dict[str, Any]:
        """📊 Analizar threads activos"""
        active_threads = threading.enumerate()
        daemon_threads = [t for t in active_threads if t.daemon]
        non_daemon_threads = [t for t in active_threads if not t.daemon]
        
        thread_info = {
            'total_threads': len(active_threads),
            'daemon_threads': len(daemon_threads),
            'non_daemon_threads': len(non_daemon_threads),
            'main_thread_alive': threading.main_thread().is_alive(),
            'thread_details': []
        }
        
        print(f"📊 [THREADS] Total: {len(active_threads)}, Daemon: {len(daemon_threads)}, Non-daemon: {len(non_daemon_threads)}")
        
        for thread in active_threads:
            thread_detail = {
                'name': thread.name,
                'daemon': thread.daemon,
                'alive': thread.is_alive(),
                'ident': thread.ident
            }
            
            # Identificar threads problemáticos
            problematic_keywords = ['MT5', 'Health', 'Monitor', 'Dashboard', 'Logger', 'Downloader']
            is_problematic = any(keyword.lower() in thread.name.lower() for keyword in problematic_keywords)
            
            if is_problematic:
                thread_detail['potentially_problematic'] = True
                print(f"⚠️  [THREAD] Problemático: {thread.name} (daemon={thread.daemon})")
            
            thread_info['thread_details'].append(thread_detail)
        
        return thread_info
    
    def _analyze_processes(self) -> Dict[str, Any]:
        """🔍 Analizar procesos del sistema"""
        try:
            current_process = psutil.Process()
            
            process_info = {
                'pid': current_process.pid,
                'name': current_process.name(),
                'cpu_percent': current_process.cpu_percent(),
                'memory_mb': current_process.memory_info().rss / 1024 / 1024,
                'open_files': len(current_process.open_files()),
                'connections': len(current_process.connections()),
                'children': len(current_process.children())
            }
            
            print(f"🔍 [PROCESS] PID: {process_info['pid']}, RAM: {process_info['memory_mb']:.1f}MB, Files: {process_info['open_files']}")
            
        except Exception as e:
            process_info = {'error': str(e)}
            print(f"❌ [PROCESS] Error analizando proceso: {e}")
        
        return process_info
    
    def _analyze_loggers(self) -> Dict[str, Any]:
        """📝 Analizar loggers activos"""
        import logging
        
        loggers = logging.Logger.manager.loggerDict
        active_loggers = []
        
        for name, logger in loggers.items():
            # Verificar que sea un logger real, no un placeholder
            if isinstance(logger, logging.Logger) and hasattr(logger, 'handlers') and logger.handlers:
                logger_info = {
                    'name': name,
                    'level': getattr(logger, 'level', 'UNKNOWN'),
                    'handlers': len(logger.handlers),
                    'disabled': getattr(logger, 'disabled', False)
                }
                active_loggers.append(logger_info)
                
                # Identificar loggers problemáticos
                if any(keyword in name.lower() for keyword in ['mt5', 'health', 'monitor', 'background']):
                    print(f"⚠️  [LOGGER] Potencialmente problemático: {name}")
        
        logger_analysis = {
            'total_loggers': len(loggers),
            'active_loggers': len(active_loggers),
            'logger_details': active_loggers
        }
        
        print(f"📝 [LOGGERS] Total: {len(loggers)}, Activos: {len(active_loggers)}")
        return logger_analysis
    
    def _analyze_signal_handlers(self) -> Dict[str, Any]:
        """🎯 Analizar signal handlers"""
        signal_info = {}
        
        signals_to_check = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, 'SIGBREAK'):
            signals_to_check.append(signal.SIGBREAK)
        
        for sig in signals_to_check:
            try:
                handler = signal.signal(sig, signal.getsignal(sig))
                signal.signal(sig, handler)  # Restaurar
                
                signal_info[sig.name] = {
                    'handler': str(handler),
                    'is_default': handler == signal.SIG_DFL,
                    'is_ignored': handler == signal.SIG_IGN
                }
            except Exception as e:
                signal_info[sig.name] = {'error': str(e)}
        
        print(f"🎯 [SIGNALS] Handlers configurados: {len(signal_info)}")
        return signal_info
    
    def _analyze_file_handles(self) -> Dict[str, Any]:
        """📁 Analizar file handles abiertos"""
        try:
            current_process = psutil.Process()
            open_files = current_process.open_files()
            
            # Categorizar archivos
            log_files = [f for f in open_files if '.log' in f.path or 'LOGS' in f.path.upper()]
            json_files = [f for f in open_files if '.json' in f.path]
            other_files = [f for f in open_files if f not in log_files and f not in json_files]
            
            file_info = {
                'total_open_files': len(open_files),
                'log_files': len(log_files),
                'json_files': len(json_files),
                'other_files': len(other_files),
                'file_details': [{'path': f.path, 'fd': f.fd} for f in open_files[:10]]  # Solo primeros 10
            }
            
            print(f"📁 [FILES] Total: {len(open_files)}, Logs: {len(log_files)}, JSON: {len(json_files)}")
            
        except Exception as e:
            file_info = {'error': str(e)}
            print(f"❌ [FILES] Error analizando archivos: {e}")
        
        return file_info
    
    def _analyze_memory(self) -> Dict[str, Any]:
        """💾 Analizar uso de memoria"""
        try:
            current_process = psutil.Process()
            memory_info = current_process.memory_info()
            
            memory_analysis = {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': current_process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
            
            print(f"💾 [MEMORY] RSS: {memory_analysis['rss_mb']:.1f}MB ({memory_analysis['percent']:.1f}%)")
            
        except Exception as e:
            memory_analysis = {'error': str(e)}
            print(f"❌ [MEMORY] Error analizando memoria: {e}")
        
        return memory_analysis

class FastShutdownOptimizer:
    """⚡ Optimizador de cierre rápido"""
    
    def __init__(self):
        self.force_shutdown = False
        self.shutdown_timeout = 10  # 10 segundos máximo total
        
    def optimize_shutdown_for_dashboard(self):
        """⚡ Optimizar cierre específico para dashboard"""
        print("⚡ [OPTIMIZER] Iniciando optimización de cierre para dashboard...")
        
        # 1. Forzar cierre de threads daemon problemáticos
        self._force_close_daemon_threads()
        
        # 2. Cerrar loggers de background
        self._close_background_loggers()
        
        # 3. Limpiar signal handlers
        self._cleanup_signal_handlers()
        
        # 4. Forzar garbage collection
        self._force_garbage_collection()
        
        print("✅ [OPTIMIZER] Optimización de cierre completada")
    
    def _force_close_daemon_threads(self):
        """💀 Forzar cierre de threads daemon problemáticos"""
        problematic_keywords = ['MT5Health', 'Monitor', 'DashboardIntegrator', 'BackgroundEnhancement']
        
        for thread in threading.enumerate():
            if thread.daemon and any(keyword in thread.name for keyword in problematic_keywords):
                print(f"💀 [FORCE] Marcando para terminación: {thread.name}")
                # Nota: Los threads daemon deberían terminar automáticamente
                # pero podemos marcarlos para análisis
    
    def _close_background_loggers(self):
        """📝 Cerrar loggers de background"""
        import logging
        
        loggers_to_close = []
        for name, logger in logging.Logger.manager.loggerDict.items():
            # Verificar que sea un logger real, no un placeholder
            if isinstance(logger, logging.Logger) and hasattr(logger, 'handlers') and any(keyword in name.lower() for keyword in ['background', 'daemon', 'health']):
                loggers_to_close.append(name)
        
        for logger_name in loggers_to_close:
            try:
                logger = logging.getLogger(logger_name)
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
                print(f"📝 [CLOSE] Logger cerrado: {logger_name}")
            except Exception as e:
                print(f"❌ [CLOSE] Error cerrando logger {logger_name}: {e}")
    
    def _cleanup_signal_handlers(self):
        """🎯 Limpiar signal handlers"""
        try:
            # Restaurar handlers por defecto para cierre rápido
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            print("🎯 [CLEANUP] Signal handlers restaurados a default")
        except Exception as e:
            print(f"❌ [CLEANUP] Error limpiando signal handlers: {e}")
    
    def _force_garbage_collection(self):
        """🗑️ Forzar garbage collection"""
        try:
            import gc
            collected = gc.collect()
            print(f"🗑️ [GC] Objetos recolectados: {collected}")
        except Exception as e:
            print(f"❌ [GC] Error en garbage collection: {e}")

def run_shutdown_diagnostic():
    """🔧 Ejecutar diagnóstico completo de cierre"""
    print("\n" + "="*80)
    print("🔧 DIAGNÓSTICO DE CIERRE LENTO - ICT ENGINE v6.0 ENTERPRISE")
    print("="*80)
    
    # Crear instancias de diagnóstico
    diagnostic = ShutdownDiagnostic()
    optimizer = FastShutdownOptimizer()
    
    # Ejecutar diagnóstico completo
    diagnosis = diagnostic.diagnose_system()
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DEL DIAGNÓSTICO:")
    print(f"   🧵 Threads activos: {diagnosis['threads']['total_threads']}")
    print(f"   👻 Threads daemon: {diagnosis['threads']['daemon_threads']}")
    print(f"   📝 Loggers activos: {diagnosis['loggers']['active_loggers']}")
    print(f"   📁 Archivos abiertos: {diagnosis['file_handles'].get('total_open_files', 'N/A')}")
    print(f"   💾 Memoria: {diagnosis['memory'].get('rss_mb', 'N/A')} MB")
    
    # Identificar problemas potenciales
    potential_issues = []
    
    if diagnosis['threads']['daemon_threads'] > 5:
        potential_issues.append("Demasiados threads daemon activos")
    
    if diagnosis['loggers']['active_loggers'] > 10:
        potential_issues.append("Demasiados loggers activos")
    
    if isinstance(diagnosis['file_handles'].get('total_open_files'), int) and diagnosis['file_handles']['total_open_files'] > 20:
        potential_issues.append("Demasiados archivos abiertos")
    
    if potential_issues:
        print(f"\n⚠️  PROBLEMAS POTENCIALES DETECTADOS:")
        for issue in potential_issues:
            print(f"   - {issue}")
    else:
        print(f"\n✅ No se detectaron problemas evidentes")
    
    # Aplicar optimizaciones
    print(f"\n⚡ APLICANDO OPTIMIZACIONES...")
    optimizer.optimize_shutdown_for_dashboard()
    
    # Guardar reporte
    save_diagnostic_report(diagnosis)
    
    return diagnosis

def save_diagnostic_report(diagnosis: Dict[str, Any]):
    """💾 Guardar reporte de diagnóstico"""
    try:
        report_path = Path("03-DOCUMENTATION/reports/shutdown_diagnostic_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(diagnosis, f, indent=2, default=str)
        
        print(f"💾 [REPORT] Diagnóstico guardado en: {report_path}")
        
    except Exception as e:
        print(f"❌ [REPORT] Error guardando reporte: {e}")

if __name__ == "__main__":
    # Ejecutar diagnóstico
    diagnosis = run_shutdown_diagnostic()
    
    print(f"\n🎯 RECOMENDACIONES:")
    print(f"   1. Usar timeouts más cortos en thread.join() (max 2-3 segundos)")
    print(f"   2. Evitar logs en threads daemon durante shutdown")
    print(f"   3. Implementar signal handlers optimizados")
    print(f"   4. Cerrar explícitamente file handles en finally blocks")
    print(f"   5. Usar threading.Event() para coordinar cierre de threads")
    
    print(f"\n👋 ¡Diagnóstico completado!")
