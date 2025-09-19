#!/usr/bin/env python3
"""
DASHBOARD STABILITY FIXES - Day 4 Post-Audit Task
=================================================

PROBLEMA IDENTIFICADO:
- Exit code 3221225786 (0xC000013A = STATUS_CONTROL_C_EXIT)  
- Doble configuracion de signal handlers conflictiva:
  * Linea 225: signal.signal(signal.SIGINT, ultra_fast_shutdown)
  * Linea 499: signal.signal(signal.SIGINT, signal_handler)

SOLUCION IMPLEMENTADA:
- Signal handler unificado con logging detallado
- Metodos de shutdown seguros
- Exception handling mejorado

INSTRUCCIONES DE APLICACION:
1. Hacer backup de start_dashboard.py
2. Reemplazar las dos configuraciones de signal handlers
3. Agregar los nuevos metodos
4. Probar con logging detallado

Autor: ICT Engine v6.0 Enterprise - Day 4 Post-Audit
"""

import sys
import signal
import threading
import time
import traceback
import logging

# === NUEVOS METODOS PARA AGREGAR AL DASHBOARD ===

def _setup_unified_signal_handler(self):
    """Signal handler unificado con logging mejorado - Day 4 Fix"""
    def unified_shutdown_handler(signum, frame):
        """Handler unificado para senales con logging detallado"""
        import threading
        import time
        import traceback
        
        # === LOGGING CRITICO - INICIO SHUTDOWN ===
        self.logger.critical(f"[SIGNAL] Senal {signum} recibida - Iniciando shutdown unificado")
        self.logger.info(f"[DEBUG] Frame info: {frame.f_code.co_filename}:{frame.f_lineno}")
        
        start_shutdown = time.time()
        shutdown_success = False
        
        try:
            # === FASE 1: LOGGING DE ESTADO ACTUAL ===
            self.logger.info("[SHUTDOWN] Logging estado actual del sistema...")
            try:
                thread_count = threading.active_count()
                self.logger.info(f"[DEBUG] Threads activos: {thread_count}")
                
                if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                    self.logger.info("[DEBUG] Dashboard instance: ACTIVO")
                else:
                    self.logger.info("[DEBUG] Dashboard instance: INACTIVO")
                    
            except Exception as e:
                self.logger.error(f"[DEBUG] Error logging estado: {e}")
            
            # === FASE 2: SHUTDOWN COMPONENTES ===
            self.logger.info("[SHUTDOWN] Iniciando cierre de componentes...")
            
            shutdown_tasks = []
            
            # Dashboard shutdown
            if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                self.logger.info("[SHUTDOWN] Cerrando dashboard...")
                dashboard_thread = threading.Thread(
                    target=self._safe_dashboard_close, 
                    name="DashboardShutdown",
                    daemon=True
                )
                dashboard_thread.start()
                shutdown_tasks.append(("Dashboard", dashboard_thread))
            
            # Logger cleanup
            self.logger.info("[SHUTDOWN] Cerrando loggers...")
            logger_thread = threading.Thread(
                target=self._safe_logger_cleanup,
                name="LoggerShutdown", 
                daemon=True
            )
            logger_thread.start()
            shutdown_tasks.append(("Logger", logger_thread))
            
            # === FASE 3: ESPERAR THREADS CON TIMEOUT ===
            max_wait_per_task = 2.0
            for task_name, thread in shutdown_tasks:
                self.logger.info(f"[SHUTDOWN] Esperando {task_name} (timeout: {max_wait_per_task}s)...")
                thread.join(timeout=max_wait_per_task)
                
                if thread.is_alive():
                    self.logger.warning(f"[SHUTDOWN] {task_name} no termino en {max_wait_per_task}s")
                else:
                    self.logger.info(f"[SHUTDOWN] {task_name} cerrado exitosamente")
            
            # === FASE 4: CLEANUP FINAL ===
            self.logger.info("[SHUTDOWN] Cleanup final...")
            try:
                if hasattr(self, 'components') and self.components:
                    cleanup_func = self.components.get('cleanup_enterprise_components')
                    if cleanup_func:
                        cleanup_func()
                
                import gc
                gc.collect()
                self.logger.info("[SHUTDOWN] Garbage collection completado")
            except Exception as e:
                self.logger.error(f"[SHUTDOWN] Error en cleanup: {e}")
            
            shutdown_time = time.time() - start_shutdown
            self.logger.info(f"[SHUTDOWN] Shutdown completado exitosamente en {shutdown_time:.2f}s")
            shutdown_success = True
            
        except Exception as e:
            # === LOGGING CRITICO DE ERRORES ===
            self.logger.critical(f"[SHUTDOWN] ERROR CRITICO durante shutdown: {e}")
            self.logger.critical(f"[SHUTDOWN] Stack trace completo:\n{traceback.format_exc()}")
            
            shutdown_time = time.time() - start_shutdown
            self.logger.critical(f"[SHUTDOWN] Shutdown fallo despues de {shutdown_time:.2f}s")
        
        # === FASE 5: EXIT CON LOGGING ===
        try:
            if shutdown_success:
                self.logger.info("[EXIT] Iniciando salida limpia con sys.exit(0)")
                # Flush logs antes de exit
                for handler in self.logger.handlers:
                    if hasattr(handler, 'flush'):
                        handler.flush()
                sys.exit(0)
            else:
                self.logger.critical("[EXIT] Shutdown fallo - usando salida de emergencia")
                # Flush logs antes de exit
                for handler in self.logger.handlers:
                    if hasattr(handler, 'flush'):
                        handler.flush()
                sys.exit(1)
                
        except SystemExit:
            # Re-raise SystemExit para permitir salida normal
            raise
        except Exception as e:
            self.logger.critical(f"[EXIT] Error critico en sys.exit(): {e}")
            self.logger.critical("[EXIT] Usando os._exit() como ultimo recurso")
            import os
            os._exit(1)
    
    # === CONFIGURACION DE SIGNAL HANDLERS ===
    try:
        import signal
        
        self.logger.info("[SIGNAL] Configurando signal handlers unificados...")
        
        # Limpiar handlers previos si existen
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        
        # Configurar handler unificado
        signal.signal(signal.SIGINT, unified_shutdown_handler)
        signal.signal(signal.SIGTERM, unified_shutdown_handler)
        
        self.logger.info("[SIGNAL] Signal handlers configurados exitosamente")
        
    except Exception as e:
        self.logger.error(f"[SIGNAL] Error configurando signal handlers: {e}")
        self.logger.error(f"[SIGNAL] Traceback: {traceback.format_exc()}")


def _safe_dashboard_close(self):
    """Cierre seguro del dashboard con logging"""
    try:
        self.logger.info("[SAFE_CLOSE] Iniciando cierre seguro dashboard...")
        
        if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
            # Intentar diferentes metodos de cierre
            close_methods = ['stop', 'shutdown', 'close', 'quit']
            
            for method_name in close_methods:
                if hasattr(self.dashboard_instance, method_name):
                    try:
                        self.logger.info(f"[SAFE_CLOSE] Intentando {method_name}()...")
                        method = getattr(self.dashboard_instance, method_name)
                        method()
                        self.logger.info(f"[SAFE_CLOSE] {method_name}() ejecutado exitosamente")
                        break
                    except Exception as e:
                        self.logger.warning(f"[SAFE_CLOSE] {method_name}() fallo: {e}")
                        continue
            else:
                self.logger.warning("[SAFE_CLOSE] No se encontro metodo de cierre valido")
        
        self.logger.info("[SAFE_CLOSE] Dashboard cerrado")
        
    except Exception as e:
        self.logger.error(f"[SAFE_CLOSE] Error cerrando dashboard: {e}")
        self.logger.error(f"[SAFE_CLOSE] Traceback: {traceback.format_exc()}")


def _safe_logger_cleanup(self):
    """Limpieza segura de loggers"""
    try:
        self.logger.info("[SAFE_CLEANUP] Iniciando limpieza loggers...")
        
        # Flush todos los handlers
        import logging
        for handler in logging.root.handlers[:]:
            try:
                handler.flush()
                if hasattr(handler, 'close'):
                    handler.close()
            except:
                pass
        
        # Flush el logger actual
        for handler in self.logger.handlers[:]:
            try:
                handler.flush()
            except:
                pass
        
        self.logger.info("[SAFE_CLEANUP] Loggers limpiados")
        
    except Exception as e:
        # Usar print como fallback si el logger falla
        print(f"[SAFE_CLEANUP] Error limpiando loggers: {e}")


# === MODIFICACIONES AL __init__ DE DashboardRunner ===
"""
CAMBIOS A REALIZAR EN start_dashboard.py:

1. ELIMINAR estas lineas:
   - Linea ~166: self._setup_ultra_fast_shutdown()
   - Linea ~225-226: signal.signal(signal.SIGINT, ultra_fast_shutdown), signal.signal(signal.SIGTERM, ultra_fast_shutdown)
   - Linea ~499-500: signal.signal(signal.SIGINT, signal_handler), signal.signal(signal.SIGTERM, signal_handler)

2. AGREGAR en el __init__ de DashboardRunner:
   self._setup_unified_signal_handler()

3. AGREGAR los tres metodos nuevos a la clase DashboardRunner:
   - _setup_unified_signal_handler
   - _safe_dashboard_close  
   - _safe_logger_cleanup

4. ASEGURAR que self.logger este disponible en __init__:
   if not hasattr(self, 'logger'):
       self.logger = logging.getLogger('DashboardRunner')
"""

print("=== DASHBOARD STABILITY FIXES ===")
print("Problema identificado: Doble configuracion signal handlers")
print("Solucion: Handler unificado con logging detallado")
print("Aplicar cambios manualmente siguiendo las instrucciones")