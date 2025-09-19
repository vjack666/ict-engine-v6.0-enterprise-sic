#!/usr/bin/env python3
"""
🔧 DASHBOARD STABILITY FIX - Day 4 Post-Audit Task
==================================================

Script para corregir problemas de estabilidad en el dashboard identificados:

1. **PROBLEMA IDENTIFICADO:** 
   - Exit code 3221225786 (0xC000013A = STATUS_CONTROL_C_EXIT)
   - Doble configuración de signal handlers conflictiva
   - Líneas 225-226: ultra_fast_shutdown
   - Líneas 499-500: signal_handler

2. **CORRECCIONES IMPLEMENTADAS:**
   - Unificar signal handling en una sola función
   - Agregar logging detallado para debugging
   - Mejorar exception handling
   - Implementar logging de estados críticos antes de exits

3. **LOGGING ADICIONAL:**
   - Stack traces en excepciones
   - Estados antes de sys.exit()
   - Timeouts y threading issues
   - Signal handling flow

Autor: ICT Engine v6.0 Enterprise - Day 4 Post-Audit
Fecha: 18 Septiembre, 2025
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Configurar logging para debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [DASHBOARD_FIX] %(message)s',
    handlers=[
        logging.FileHandler('../05-LOGS/dashboard/dashboard_stability_fix.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def analyze_current_dashboard():
    """Analizar el código actual del dashboard para problemas"""
    logger.info("🔍 Analizando código actual del dashboard...")
    
    dashboard_file = Path("../09-DASHBOARD/start_dashboard.py")
    
    if not dashboard_file.exists():
        logger.error(f"❌ Archivo no encontrado: {dashboard_file}")
        return False
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar configuraciones de signal handlers
    signal_configs = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        if 'signal.signal' in line and 'SIGINT' in line:
            signal_configs.append((i, line.strip()))
    
    logger.info(f"📋 Encontradas {len(signal_configs)} configuraciones de signal handlers:")
    for line_num, line_content in signal_configs:
        logger.info(f"   Línea {line_num}: {line_content}")
    
    # Verificar problema de doble configuración
    if len(signal_configs) >= 4:  # 2 para SIGINT, 2 para SIGTERM
        logger.warning("⚠️  PROBLEMA CONFIRMADO: Múltiples configuraciones de signal handlers detectadas")
        return True
    
    return False

def create_unified_signal_handler():
    """Crear un signal handler unificado con logging mejorado"""
    logger.info("🔧 Creando signal handler unificado...")
    
    unified_handler = '''
    def _setup_unified_signal_handler(self):
        """🔧 Signal handler unificado con logging mejorado - Day 4 Fix"""
        def unified_shutdown_handler(signum, frame):
            """Handler unificado para señales con logging detallado"""
            import threading
            import time
            import traceback
            
            # === LOGGING CRÍTICO - INICIO SHUTDOWN ===
            self.logger.critical(f"🚨 [SIGNAL] Señal {signum} recibida - Iniciando shutdown unificado")
            self.logger.info(f"🔍 [DEBUG] Frame info: {frame.f_code.co_filename}:{frame.f_lineno}")
            
            start_shutdown = time.time()
            shutdown_success = False
            
            try:
                # === FASE 1: LOGGING DE ESTADO ACTUAL ===
                self.logger.info("📊 [SHUTDOWN] Logging estado actual del sistema...")
                try:
                    thread_count = threading.active_count()
                    self.logger.info(f"🧵 [DEBUG] Threads activos: {thread_count}")
                    
                    if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                        self.logger.info("📊 [DEBUG] Dashboard instance: ACTIVO")
                    else:
                        self.logger.info("📊 [DEBUG] Dashboard instance: INACTIVO")
                        
                except Exception as e:
                    self.logger.error(f"❌ [DEBUG] Error logging estado: {e}")
                
                # === FASE 2: SHUTDOWN COMPONENTES ===
                self.logger.info("🛑 [SHUTDOWN] Iniciando cierre de componentes...")
                
                shutdown_tasks = []
                
                # Dashboard shutdown
                if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                    self.logger.info("🌐 [SHUTDOWN] Cerrando dashboard...")
                    dashboard_thread = threading.Thread(
                        target=self._safe_dashboard_close, 
                        name="DashboardShutdown",
                        daemon=True
                    )
                    dashboard_thread.start()
                    shutdown_tasks.append(("Dashboard", dashboard_thread))
                
                # Logger cleanup
                self.logger.info("📝 [SHUTDOWN] Cerrando loggers...")
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
                    self.logger.info(f"⏳ [SHUTDOWN] Esperando {task_name} (timeout: {max_wait_per_task}s)...")
                    thread.join(timeout=max_wait_per_task)
                    
                    if thread.is_alive():
                        self.logger.warning(f"⚠️  [SHUTDOWN] {task_name} no terminó en {max_wait_per_task}s")
                    else:
                        self.logger.info(f"✅ [SHUTDOWN] {task_name} cerrado exitosamente")
                
                # === FASE 4: CLEANUP FINAL ===
                self.logger.info("🧹 [SHUTDOWN] Cleanup final...")
                try:
                    if hasattr(self, 'components') and self.components:
                        cleanup_func = self.components.get('cleanup_enterprise_components')
                        if cleanup_func:
                            cleanup_func()
                    
                    import gc
                    gc.collect()
                    self.logger.info("🧹 [SHUTDOWN] Garbage collection completado")
                except Exception as e:
                    self.logger.error(f"❌ [SHUTDOWN] Error en cleanup: {e}")
                
                shutdown_time = time.time() - start_shutdown
                self.logger.info(f"✅ [SHUTDOWN] Shutdown completado exitosamente en {shutdown_time:.2f}s")
                shutdown_success = True
                
            except Exception as e:
                # === LOGGING CRÍTICO DE ERRORES ===
                self.logger.critical(f"🚨 [SHUTDOWN] ERROR CRÍTICO durante shutdown: {e}")
                self.logger.critical(f"📋 [SHUTDOWN] Stack trace completo:\\n{traceback.format_exc()}")
                
                shutdown_time = time.time() - start_shutdown
                self.logger.critical(f"❌ [SHUTDOWN] Shutdown falló después de {shutdown_time:.2f}s")
            
            # === FASE 5: EXIT CON LOGGING ===
            try:
                if shutdown_success:
                    self.logger.info("🚀 [EXIT] Iniciando salida limpia con sys.exit(0)")
                    # Flush logs antes de exit
                    for handler in self.logger.handlers:
                        if hasattr(handler, 'flush'):
                            handler.flush()
                    sys.exit(0)
                else:
                    self.logger.critical("🚨 [EXIT] Shutdown falló - usando salida de emergencia")
                    # Flush logs antes de exit
                    for handler in self.logger.handlers:
                        if hasattr(handler, 'flush'):
                            handler.flush()
                    sys.exit(1)
                    
            except SystemExit:
                # Re-raise SystemExit para permitir salida normal
                raise
            except Exception as e:
                self.logger.critical(f"🚨 [EXIT] Error crítico en sys.exit(): {e}")
                self.logger.critical(f"📋 [EXIT] Usando os._exit() como último recurso")
                import os
                os._exit(1)
        
        # === CONFIGURACIÓN DE SIGNAL HANDLERS ===
        try:
            import signal
            
            self.logger.info("🔧 [SIGNAL] Configurando signal handlers unificados...")
            
            # Limpiar handlers previos si existen
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            
            # Configurar handler unificado
            signal.signal(signal.SIGINT, unified_shutdown_handler)
            signal.signal(signal.SIGTERM, unified_shutdown_handler)
            
            self.logger.info("✅ [SIGNAL] Signal handlers configurados exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ [SIGNAL] Error configurando signal handlers: {e}")
            self.logger.error(f"📋 [SIGNAL] Traceback: {traceback.format_exc()}")
    '''
    
    return unified_handler

def create_safe_shutdown_methods():
    """Crear métodos de shutdown seguros"""
    logger.info("🔧 Creando métodos de shutdown seguros...")
    
    safe_methods = '''
    def _safe_dashboard_close(self):
        """🛑 Cierre seguro del dashboard con logging"""
        try:
            self.logger.info("🌐 [SAFE_CLOSE] Iniciando cierre seguro dashboard...")
            
            if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                # Intentar diferentes métodos de cierre
                close_methods = ['stop', 'shutdown', 'close', 'quit']
                
                for method_name in close_methods:
                    if hasattr(self.dashboard_instance, method_name):
                        try:
                            self.logger.info(f"🔧 [SAFE_CLOSE] Intentando {method_name}()...")
                            method = getattr(self.dashboard_instance, method_name)
                            method()
                            self.logger.info(f"✅ [SAFE_CLOSE] {method_name}() ejecutado exitosamente")
                            break
                        except Exception as e:
                            self.logger.warning(f"⚠️  [SAFE_CLOSE] {method_name}() falló: {e}")
                            continue
                else:
                    self.logger.warning("⚠️  [SAFE_CLOSE] No se encontró método de cierre válido")
            
            self.logger.info("✅ [SAFE_CLOSE] Dashboard cerrado")
            
        except Exception as e:
            self.logger.error(f"❌ [SAFE_CLOSE] Error cerrando dashboard: {e}")
            self.logger.error(f"📋 [SAFE_CLOSE] Traceback: {traceback.format_exc()}")
    
    def _safe_logger_cleanup(self):
        """📝 Limpieza segura de loggers"""
        try:
            self.logger.info("📝 [SAFE_CLEANUP] Iniciando limpieza loggers...")
            
            # Flush todos los handlers
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
            
            self.logger.info("✅ [SAFE_CLEANUP] Loggers limpiados")
            
        except Exception as e:
            # Usar print como fallback si el logger falla
            print(f"❌ [SAFE_CLEANUP] Error limpiando loggers: {e}")
    '''
    
    return safe_methods

def apply_dashboard_fix():
    """Aplicar el fix al dashboard"""
    logger.info("🚀 Aplicando fix de estabilidad al dashboard...")
    
    try:
        dashboard_file = Path("../09-DASHBOARD/start_dashboard.py")
        backup_file = Path("../09-DASHBOARD/start_dashboard.py.backup")
        
        # Crear backup
        logger.info("💾 Creando backup del archivo original...")
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        logger.info(f"✅ Backup creado: {backup_file}")
        
        # Aplicar fix (por ahora solo crear el archivo de corrección)
        logger.info("📝 Generando archivo de correcciones...")
        
        fixes_content = f'''# === DASHBOARD STABILITY FIXES - Day 4 Post-Audit ===
# Aplicar estas correcciones al archivo start_dashboard.py

# 1. ELIMINAR configuraciones duplicadas de signal handlers:
#    - Líneas 225-226 (ultra_fast_shutdown)  
#    - Líneas 499-500 (signal_handler)

# 2. REEMPLAZAR con signal handler unificado:
{create_unified_signal_handler()}

# 3. AGREGAR métodos de shutdown seguros:
{create_safe_shutdown_methods()}

# 4. MODIFICAR __init__ para usar handler unificado:
#    - Reemplazar self._setup_ultra_fast_shutdown() 
#    - Reemplazar self._setup_signal_handlers()
#    - Agregar self._setup_unified_signal_handler()
'''
        
        fixes_file = Path("dashboard_stability_fixes.py")
        with open(fixes_file, 'w', encoding='utf-8') as f:
            f.write(fixes_content)
        
        logger.info(f"✅ Archivo de correcciones generado: {fixes_file}")
        logger.info("🎯 Review manual requerido antes de aplicar cambios automáticos")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error aplicando fix: {e}")
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 === DASHBOARD STABILITY FIX - Day 4 Post-Audit ===")
    
    try:
        # Paso 1: Analizar código actual
        if not analyze_current_dashboard():
            logger.error("❌ No se pudo analizar el dashboard actual")
            return False
        
        # Paso 2: Aplicar correcciones
        if not apply_dashboard_fix():
            logger.error("❌ No se pudo aplicar el fix")
            return False
        
        logger.info("✅ Dashboard stability fix completado exitosamente")
        logger.info("📋 Próximos pasos:")
        logger.info("   1. Revisar archivo dashboard_stability_fixes.py")
        logger.info("   2. Aplicar cambios manualmente al start_dashboard.py")  
        logger.info("   3. Probar nueva versión con logging mejorado")
        logger.info("   4. Monitorear logs en dashboard_stability_fix.log")
        
        return True
        
    except Exception as e:
        logger.critical(f"🚨 Error crítico en main: {e}")
        logger.critical(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)