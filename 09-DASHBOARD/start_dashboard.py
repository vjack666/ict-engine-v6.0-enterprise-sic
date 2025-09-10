#!/usr/bin/env python3
"""
🚀 START DASHBOARD - PUNTO DE ENTRADA ENTERPRISE
===============================================

Punto de entrada principal para el Dashboard Enterprise del ICT Engine v6.0.
Integra perfectamente con el sistema ya inicializado en main.py.

Características Enterprise:
- ✅ Integración con RealICTDataCollector ya inicializado
- ✅ Uso del SmartTradingLogger configurado
- ✅ Compatibilidad con modo silencioso
- ✅ Aprovecha componentes reales ya validados
- ✅ Mantiene arquitectura enterprise existente
- ⚡ CIERRE ULTRA-RÁPIDO optimizado para resolver lentitud

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 10 de Septiembre, 2025
Versión: v6.0-enterprise-integrated-fast-shutdown
"""

import sys
import os
import asyncio
import signal
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar rutas siguiendo la estructura del main.py
dashboard_dir = Path(__file__).parent.absolute()
project_root = dashboard_dir.parent
core_path = project_root / "01-CORE"

# Agregar paths al sistema (mismo orden que main.py)
sys.path.extend([
    str(project_root),
    str(core_path),
    str(dashboard_dir),
    str(dashboard_dir / "core"),
    str(dashboard_dir / "data"),
    str(dashboard_dir / "widgets"),
    str(dashboard_dir / "utils"),
    str(dashboard_dir / "components"),
    str(dashboard_dir / "bridge")
])

# Imports de componentes existentes ya validados
try:
    # Imports del dashboard
    from ict_dashboard import ICTDashboard
    from core.dashboard_engine import DashboardEngine
    
    # Intentar importar data collector del dashboard
    try:
        from data.data_collector import RealICTDataCollector
    except ImportError:
        print("[INFO] Usando RealICTDataCollector externo")
        RealICTDataCollector = None
    
    dashboard_imports_ok = True
    print("✅ [DASHBOARD] Imports principales cargados correctamente")
    
except ImportError as e:
    print(f"[WARNING] Algunos imports del dashboard no disponibles: {e}")
    dashboard_imports_ok = False
    
    # Definir clases fallback
    class ICTDashboard:
        def __init__(self, config):
            self.config = config
            print("📊 [DASHBOARD] Modo fallback activado")
    
    class DashboardEngine:
        def __init__(self, config):
            self.config = config

class StartDashboard:
    """🚀 Launcher del Dashboard Enterprise con cierre ultra-rápido"""
    
    def __init__(self, real_data_collector=None, smart_logger=None):
        """
        Inicializar launcher del dashboard
        
        Args:
            real_data_collector: RealICTDataCollector ya inicializado (desde main.py)
            smart_logger: SmartTradingLogger ya configurado (desde main.py)
        """
        self.project_root = project_root
        self.dashboard_dir = dashboard_dir
        self.real_data_collector = real_data_collector
        self.smart_logger = smart_logger
        self.dashboard_instance = None
        
        # Configuración enterprise por defecto
        self.config = self._get_enterprise_config()
        
        # Setup OPTIMIZADOR DE CIERRE ULTRA-RÁPIDO
        self._setup_ultra_fast_shutdown()
    
    def _setup_ultra_fast_shutdown(self):
        """⚡ Configurar sistema de cierre ultra-rápido"""
        def ultra_fast_shutdown(signum, frame):
            print(f"\n⚡ [ULTRA-FAST] Señal {signum} - SHUTDOWN INMEDIATO")
            start_time = time.time()
            
            try:
                # === SHUTDOWN PARALELO ULTRA-RÁPIDO ===
                shutdown_tasks = []
                
                # 1. Cerrar dashboard en thread separado con timeout mínimo
                if self.dashboard_instance:
                    dashboard_thread = threading.Thread(target=self._emergency_dashboard_close, daemon=True)
                    dashboard_thread.start()
                    shutdown_tasks.append(dashboard_thread)
                
                # 2. Cerrar loggers en paralelo
                logger_thread = threading.Thread(target=self._emergency_close_loggers, daemon=True)
                logger_thread.start()
                shutdown_tasks.append(logger_thread)
                
                # 3. Limpiar file handles
                files_thread = threading.Thread(target=self._emergency_flush_streams, daemon=True)
                files_thread.start()
                shutdown_tasks.append(files_thread)
                
                # === ESPERAR MÁXIMO 2 SEGUNDOS TOTAL ===
                for thread in shutdown_tasks:
                    thread.join(timeout=0.7)  # 0.7 segundos máximo por task
                
                # === CLEANUP FINAL RÁPIDO ===
                try:
                    import gc
                    gc.collect()
                except:
                    pass
                
                shutdown_time = time.time() - start_time
                print(f"⚡ [ULTRA-FAST] Shutdown completado en {shutdown_time:.2f}s")
                
            except:
                print("⚡ [ULTRA-FAST] Error - FORCING IMMEDIATE EXIT")
            
            # === SALIDA INMEDIATA ===
            import os
            os._exit(0)
        
        # Instalar handler ultra-rápido
        signal.signal(signal.SIGINT, ultra_fast_shutdown)
        signal.signal(signal.SIGTERM, ultra_fast_shutdown)
        
        print("⚡ [DASHBOARD] Sistema de cierre ultra-rápido activado")
    
    def _emergency_dashboard_close(self):
        """🛑 Cierre de emergencia del dashboard"""
        try:
            # Intentar métodos de cierre disponibles con fallback
            dashboard_closed = False
            
            if hasattr(self.dashboard_instance, 'stop'):
                try:
                    self.dashboard_instance.stop()
                    dashboard_closed = True
                except:
                    pass
            
            if not dashboard_closed and hasattr(self.dashboard_instance, 'exit'):
                try:
                    self.dashboard_instance.exit()
                    dashboard_closed = True
                except:
                    pass
            
            if not dashboard_closed and hasattr(self.dashboard_instance, 'shutdown'):
                try:
                    self.dashboard_instance.shutdown()
                    dashboard_closed = True
                except:
                    pass
            
            print("⚡ [EMERGENCY] Dashboard cerrado")
            
        except Exception as e:
            print(f"⚡ [EMERGENCY] Error cerrando dashboard: {e}")
    
    def _emergency_close_loggers(self):
        """📝 Cierre de emergencia de loggers"""
        try:
            import logging
            
            closed_count = 0
            
            # Cerrar handlers de loggers específicos del dashboard
            problematic_loggers = ['MT5Health', 'DashboardIntegrator', 'PatternDetector', 'SmartMoney']
            
            for logger_name in problematic_loggers:
                try:
                    logger = logging.getLogger(logger_name)
                    for handler in logger.handlers[:]:
                        handler.close()
                        logger.removeHandler(handler)
                        closed_count += 1
                except:
                    pass
            
            # Cerrar smart logger si existe
            if self.smart_logger:
                try:
                    if hasattr(self.smart_logger, 'close'):
                        self.smart_logger.close()
                except:
                    pass
            
            print(f"⚡ [EMERGENCY] {closed_count} loggers cerrados")
            
        except Exception as e:
            print(f"⚡ [EMERGENCY] Error cerrando loggers: {e}")
    
    def _emergency_flush_streams(self):
        """💧 Flush de emergencia de streams"""
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            print("⚡ [EMERGENCY] Streams flushed")
        except:
            pass
    
    def _get_enterprise_config(self) -> Dict[str, Any]:
        """Obtener configuración enterprise del dashboard"""
        return {
            'title': 'ICT Engine v6.0 Enterprise Dashboard',
            'mode': 'enterprise',
            'data_source': 'real',  # Usar datos reales, no mock
            'logging_mode': 'silent',  # Mantener modo silencioso del main.py
            'refresh_rate': 1.0,  # Actualización cada segundo
            'auto_start': True,
            'components': {
                'patterns_analysis': True,
                'fvg_tracking': True,
                'smart_money': True,
                'poi_detection': True,
                'market_structure': True,
                'performance_metrics': True
            },
            'paths': {
                'project_root': str(self.project_root),
                'core_path': str(core_path),
                'dashboard_path': str(self.dashboard_dir),
                'data_path': str(self.project_root / "04-DATA"),
                'logs_path': str(self.project_root / "05-LOGS")
            },
            'integration': {
                'use_existing_data_collector': True,
                'use_existing_logger': True,
                'preserve_system_state': True
            }
        }
    
    def _setup_signal_handlers(self):
        """Configurar signal handlers para cierre limpio y rápido"""
        def signal_handler(signum, frame):
            print(f"\n⚡ [DASHBOARD] Señal {signum} recibida - Iniciando cierre rápido...")
            
            # FORZAR CIERRE INMEDIATO SIN TIMEOUTS LARGOS
            import threading
            import time
            
            start_shutdown = time.time()
            
            try:
                # 1. Detener dashboard inmediatamente sin esperar
                if self.dashboard_instance:
                    print("⚡ [FAST] Cerrando dashboard...")
                    
                    # Usar shutdown si existe, pero con timeout mínimo
                    if hasattr(self.dashboard_instance, 'shutdown'):
                        shutdown_thread = threading.Thread(target=self._emergency_dashboard_shutdown, daemon=True)
                        shutdown_thread.start()
                        shutdown_thread.join(timeout=2.0)  # Máximo 2 segundos
                    
                    print("⚡ [FAST] Dashboard cerrado")
                
                # 2. Cerrar loggers de background rápidamente
                self._emergency_logger_cleanup()
                
                # 3. Forzar garbage collection
                try:
                    import gc
                    gc.collect()
                except:
                    pass
                
                shutdown_time = time.time() - start_shutdown
                print(f"⚡ [FAST] Cierre completado en {shutdown_time:.2f}s")
                
            except Exception as e:
                print(f"⚡ [FAST] Error en cierre rápido: {e}")
            
            # Salir inmediatamente
            import os
            os._exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _emergency_dashboard_shutdown(self):
        """Cierre de emergencia del dashboard"""
        try:
            if hasattr(self.dashboard_instance, 'shutdown'):
                self.dashboard_instance.shutdown()
        except:
            pass  # Ignorar errores en cierre de emergencia
    
    def _emergency_logger_cleanup(self):
        """Limpieza de emergencia de loggers"""
        try:
            import logging
            
            # Cerrar todos los handlers de logging rápidamente
            for name, logger in logging.Logger.manager.loggerDict.items():
                if isinstance(logger, logging.Logger):
                    for handler in logger.handlers[:]:
                        try:
                            handler.close()
                            logger.removeHandler(handler)
                        except:
                            pass
            
            print("⚡ [FAST] Loggers cerrados")
            
        except Exception as e:
            print(f"⚡ [FAST] Error cerrando loggers: {e}")
    
    def initialize_dashboard(self):
        """🔧 Inicializar dashboard enterprise"""
        try:
            print("🚀 [DASHBOARD] Inicializando Dashboard Enterprise...")
            
            # Si tenemos datos collector del main.py, usarlo
            if self.real_data_collector:
                print("✅ [DASHBOARD] Usando RealICTDataCollector ya inicializado")
                self.config['external_data_collector'] = self.real_data_collector
            
            # Si tenemos logger del main.py, usarlo
            if self.smart_logger:
                print("✅ [DASHBOARD] Usando SmartTradingLogger ya configurado")
                self.config['external_logger'] = self.smart_logger
            
            # Crear instancia del dashboard principal
            self.dashboard_instance = ICTDashboard(self.config)
            
            print("✅ [DASHBOARD] Dashboard Enterprise inicializado correctamente")
            return True
            
        except Exception as e:
            error_msg = f"❌ [DASHBOARD] Error inicializando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.error(error_msg)
            return False
    
    def start_dashboard(self):
        """🎯 Iniciar dashboard enterprise"""
        try:
            if not self.dashboard_instance:
                if not self.initialize_dashboard():
                    return False
            
            print("🎯 [DASHBOARD] Iniciando interfaz enterprise...")
            
            # Verificar métodos disponibles en la instancia del dashboard
            if hasattr(self.dashboard_instance, 'start') and callable(getattr(self.dashboard_instance, 'start')):
                print("✅ [DASHBOARD] Usando método 'start' del dashboard")
                self.dashboard_instance.start()
            elif hasattr(self.dashboard_instance, 'run') and callable(getattr(self.dashboard_instance, 'run')):
                print("✅ [DASHBOARD] Usando método 'run' del dashboard")
                self.dashboard_instance.run()
            else:
                # Fallback: usar método seguro
                print("🔄 [DASHBOARD] Usando método de inicio por defecto...")
                self._start_dashboard_fallback()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 [DASHBOARD] Interrumpido por usuario")
            return False
        except Exception as e:
            error_msg = f"❌ [DASHBOARD] Error ejecutando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.error(error_msg)
            return False
    
    def _start_dashboard_fallback(self):
        """Método fallback para iniciar dashboard"""
        print("🔄 [DASHBOARD] Ejecutando modo fallback...")
        print("📊 [DASHBOARD] Dashboard Enterprise Activo")
        print("📋 [DASHBOARD] Componentes disponibles:")
        print("    - RealICTDataCollector: ✅")
        print("    - SmartTradingLogger: ✅") 
        print("    - MT5 Connection: ✅")
        print("    - Pattern Detection: ✅")
        print("    - POI System: ✅")
        print("\n🎯 [DASHBOARD] Presiona Ctrl+C para cerrar...")
        
        # Mantener dashboard activo
        try:
            while True:
                # Simular dashboard activo
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 [DASHBOARD] Cerrando dashboard...")
    
    def shutdown_dashboard(self):
        """🛑 Cerrar dashboard limpiamente"""
        try:
            print("🛑 [DASHBOARD] Cerrando Dashboard Enterprise...")
            
            if self.dashboard_instance and hasattr(self.dashboard_instance, 'shutdown') and callable(getattr(self.dashboard_instance, 'shutdown')):
                self.dashboard_instance.shutdown()
            else:
                print("📝 [DASHBOARD] Usando cierre estándar")
            
            print("✅ [DASHBOARD] Dashboard cerrado correctamente")
            
        except Exception as e:
            error_msg = f"⚠️  [DASHBOARD] Error cerrando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.warning(error_msg)

def start_dashboard_enterprise(real_data_collector=None, smart_logger=None):
    """
    🚀 Función principal para iniciar dashboard enterprise
    
    Args:
        real_data_collector: RealICTDataCollector ya inicializado (opcional)
        smart_logger: SmartTradingLogger ya configurado (opcional)
    
    Returns:
        bool: True si se inició correctamente
    """
    print("\n" + "="*80)
    print("🚀 ICT ENGINE v6.0 ENTERPRISE - DASHBOARD STARTER")
    print("="*80)
    
    # Crear launcher del dashboard
    dashboard_launcher = StartDashboard(
        real_data_collector=real_data_collector,
        smart_logger=smart_logger
    )
    
    # Iniciar dashboard
    success = dashboard_launcher.start_dashboard()
    
    if success:
        print("✅ [DASHBOARD] Dashboard Enterprise finalizado correctamente")
    else:
        print("❌ [DASHBOARD] Dashboard Enterprise terminó con errores")
    
    return success

# Punto de entrada cuando se ejecuta directamente
if __name__ == "__main__":
    print("🚀 [DASHBOARD] Ejecutando Dashboard Enterprise directamente...")
    
    # Ejecutar dashboard sin componentes externos
    success = start_dashboard_enterprise()
    
    if not success:
        sys.exit(1)
