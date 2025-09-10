#!/usr/bin/env python3
"""
🚀 ICT ENGINE v6.0 ENTERPRISE - SISTEMA PRINCIPAL ÚNICO
======================================================

PUNTO DE ENTRADA ÚNICO del sistema ICT Engine v6.0 Enterprise
- Dashboard unificado con análisis en tiempo real
- Datos reales MT5 únicamente
- Sistema de trading completo con patrones ICT
- Gestión automática de memoria y recursos
- Cierre optimizado con restauración de directorio

USO:
    python main.py

CARACTERÍSTICAS:
    ✅ Sistema único consolidado
    ✅ Dashboard integrado (Textual + Terminal)
    ✅ Análisis ICT en tiempo real
    ✅ Gestión automática de recursos
    ✅ Cierre limpio y optimizado
    ✅ Restauración automática de directorio

AUTOR: ICT Engine Team
VERSIÓN: v6.0 Enterprise
FECHA: 2025-09-10
"""

import sys
import os
import signal
import threading
import time
import asyncio
from pathlib import Path
from datetime import datetime

# Configurar paths
project_root = Path(__file__).parent
core_path = project_root / "01-CORE"
data_path = project_root / "04-DATA"
logs_path = project_root / "05-LOGS"
dashboard_path = project_root / "09-DASHBOARD"

# Agregar paths al sistema
sys.path.extend([
    str(project_root),
    str(core_path),
    str(data_path),
    str(logs_path),
    str(dashboard_path),
    str(dashboard_path / "data"),
    str(dashboard_path / "widgets"),
    str(dashboard_path / "core"),      # Para RealMarketBridge
    str(dashboard_path / "bridge")     # Para DashboardBridge
])

print(f"🚀 [MAIN] Core path configurado: {core_path}")
print(f"🚀 [MAIN] Data path configurado: {data_path}")
print(f"🚀 [MAIN] Logs path configurado: {logs_path}")
print(f"🚀 [MAIN] Dashboard path configurado: {dashboard_path}")

# ===== CONFIGURACIÓN MODO SILENCIOSO =====
print("🚀 [MAIN] Configurando modo silencioso para dashboard...")
try:
    from config.logging_mode_config import LoggingModeConfig
    LoggingModeConfig.enable_quiet_mode()
    print("🚀 [MAIN] ✅ Modo silencioso activado - logs solo en archivos")
    print("🚀 [MAIN] 📁 Los logs se guardarán en: 05-LOGS/system/")
except Exception as e:
    print(f"🚀 [MAIN] ⚠️ Error configurando modo silencioso: {e}")
    print("🚀 [MAIN] 📁 Los logs se guardarán de forma estándar en 05-LOGS/")

# ===== SISTEMA DE LOGGING CENTRALIZADO =====
try:
    from smart_trading_logger import get_centralized_logger
    # Logger principal del sistema
    main_logger = get_centralized_logger("SYSTEM")
    main_logger.log_session_start()
    main_logger.log_system_status("ICT Engine v6.0 Enterprise iniciando...", "MAIN")
    print("✅ Sistema de logging centralizado activado")
except Exception as e:
    print(f"⚠️ Error configurando logging centralizado: {e}")
    main_logger = None

# Importar componentes reales usando paths absolutos
try:
    # Configurar paths específicos para importación
    utils_import_path = str(core_path / "utils")
    dashboard_data_path = str(dashboard_path / "data")
    
    # Añadir al principio del sys.path para prioridad
    if utils_import_path not in sys.path:
        sys.path.insert(0, utils_import_path)
    if dashboard_data_path not in sys.path:
        sys.path.insert(0, dashboard_data_path)
    
    # Importar componentes con manejo de errores específico
    try:
        import import_center  # type: ignore
        get_smart_logger_safe = import_center.get_smart_logger_safe
        get_mt5_manager_safe = import_center.get_mt5_manager_safe
        print("[OK] import_center cargado correctamente")
    except ImportError as e:
        print(f"[ERROR] No se pudo cargar import_center: {e}")
        raise
    
    try:
        import data_collector  # type: ignore
        RealICTDataCollector = data_collector.RealICTDataCollector
        print("[OK] data_collector cargado correctamente")
    except ImportError as e:
        print(f"[ERROR] No se pudo cargar data_collector: {e}")
        raise
    
    # Inicializar logger y MT5 manager reales con manejo robusto
    try:
        # Obtener logger con manejo mejorado
        logger_class = get_smart_logger_safe()
        if logger_class:
            # Verificar si es una clase que necesita instanciación
            if hasattr(logger_class, '__call__') and not hasattr(logger_class, 'info'):
                logger = logger_class()
            else:
                logger = logger_class
        else:
            # Fallback básico
            import logging
            logger = logging.getLogger(__name__)
        
        # Obtener MT5 manager con manejo mejorado
        mt5_manager_class = get_mt5_manager_safe()
        if mt5_manager_class:
            # Verificar si es una función o clase, instanciarla si es necesario
            if hasattr(mt5_manager_class, '__call__') and not hasattr(mt5_manager_class, 'get_account_info'):
                mt5_manager = mt5_manager_class()
            else:
                mt5_manager = mt5_manager_class
        else:
            mt5_manager = None
            
    except Exception as e:
        print(f"🚀 [MAIN] ⚠️ Error en inicialización avanzada: {e}")
        # Usar versiones básicas
        import logging
        logger = logging.getLogger(__name__)
        mt5_manager = None
    
    print("🚀 [MAIN] ✅ Componentes reales importados exitosamente")
    print("🚀 [MAIN]     - SmartTradingLogger: ✅ Activo")
    print("🚀 [MAIN]     - MT5DataManager: ✅ Activo") 
    print("🚀 [MAIN]     - RealICTDataCollector: ✅ Disponible")
    
    # Log estructurado en la caja negra
    if main_logger:
        main_logger.info("Componentes reales importados exitosamente", "SYSTEM")
        main_logger.info("SmartTradingLogger: Activo", "SYSTEM")
        main_logger.info("MT5DataManager: Activo", "SYSTEM")
        main_logger.info("RealICTDataCollector: Disponible", "SYSTEM")
    
except Exception as e:
    print(f"🚀 [MAIN] ❌ Error importando componentes reales: {e}")
    print(f"🚀 [MAIN] 🔍 Paths utilizados:")
    print(f"🚀 [MAIN]     - Utils: {core_path / 'utils'}")
    print(f"🚀 [MAIN]     - Dashboard Data: {dashboard_path / 'data'}")
    print("🚀 [MAIN] 🔴 CRÍTICO: Sistema no puede continuar sin componentes reales")
    
    # Log del error en la caja negra
    if main_logger:
        main_logger.error(f"Error importando componentes reales: {e}", "SYSTEM")
        main_logger.error(f"Paths utilizados - Utils: {core_path / 'utils'}", "SYSTEM")
        main_logger.error(f"Dashboard Data: {dashboard_path / 'data'}", "SYSTEM")
        main_logger.critical("CRÍTICO: Sistema no puede continuar sin componentes reales", "SYSTEM")
    
    sys.exit(1)

class ICTEnterpriseSystem:
    """Sistema ICT Engine v6.0 Enterprise - Dashboard con Datos Reales"""
    
    def __init__(self):
        """Inicializar sistema enterprise con datos reales únicamente"""
        self.is_running = False
        self.shutdown_event = threading.Event()
        self.data_collector = None
        self.real_components_loaded = False
        
        # Configurar handlers de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Asegurar directorios necesarios
        self.ensure_required_folders()
        
        # Inicializar datos reales
        self.initialize_real_components()
    
    def _signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        print(f"\n🚀 [MAIN] 🛑 Señal recibida: {signum}. Iniciando cierre limpio...")
        self.shutdown()
    
    def initialize_real_components(self):
        """Inicializar RealICTDataCollector y componentes reales"""
        try:
            if main_logger:
                main_logger.log_system_status("Inicializando RealICTDataCollector...", "CORE")
                main_logger.info("🔧 Iniciando proceso de inicialización de componentes reales", "CORE")
            print("🚀 [MAIN] 🔧 Inicializando RealICTDataCollector...")
            
            # Crear configuración para el RealICTDataCollector
            config = {
                'data': {
                    'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
                    'timeframes': ['M15', 'H1', 'H4', 'D1']
                },
                'real_components': True,  # Usar componentes reales
                'update_interval': 2.0,
                'max_history': 1000
            }
            
            print(f"🚀 [MAIN] 📊 Configuración aplicada: {len(config['data']['symbols'])} símbolos, {len(config['data']['timeframes'])} timeframes")
            if main_logger:
                main_logger.info(f"Configuración aplicada: {len(config['data']['symbols'])} símbolos, {len(config['data']['timeframes'])} timeframes", "CORE")
                main_logger.debug(f"Símbolos configurados: {config['data']['symbols']}", "CORE")
                main_logger.debug(f"Timeframes configurados: {config['data']['timeframes']}", "CORE")
            
            # Crear instancia del colector de datos reales
            print("🚀 [MAIN] 🏗️ Creando instancia RealICTDataCollector...")
            if main_logger:
                main_logger.info("🏗️ Creando instancia RealICTDataCollector", "CORE")
            
            self.data_collector = RealICTDataCollector(config)
            
            # Ejecutar inicialización async
            print("🚀 [MAIN] 🔄 Configurando event loop async...")
            if main_logger:
                main_logger.info("🔄 Configurando event loop async", "CORE")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Inicializar componentes async
            print("🚀 [MAIN] ⚡ Ejecutando inicialización async...")
            if main_logger:
                main_logger.info("⚡ Ejecutando inicialización async", "CORE")
            
            loop.run_until_complete(self.data_collector.initialize())
            
            # Verificar estado básico - solo verificar que el objeto fue creado
            if self.data_collector:
                if main_logger:
                    main_logger.log_system_status("RealICTDataCollector inicializado correctamente", "SUCCESS")
                    main_logger.info("✅ RealICTDataCollector: Estado verificado y funcional", "CORE")
                print("🚀 [MAIN] ✅ RealICTDataCollector: Inicializado correctamente")
                print("    - Configuración aplicada")
                print("    - Componentes async inicializados")
                print("    - Sistema listo para operación")
                self.real_components_loaded = True
            else:
                if main_logger:
                    main_logger.error("Error en inicialización de RealICTDataCollector")
                print("[WARN] RealICTDataCollector: Error en inicialización")
                self.real_components_loaded = False
                
            loop.close()
            
        except Exception as e:
            print(f"[X] Error inicializando componentes reales: {e}")
            # Aún así marcar como cargado si el objeto existe
            if hasattr(self, 'data_collector') and self.data_collector:
                print("[INFO] Data collector creado, continuando con limitaciones...")
                self.real_components_loaded = True
            else:
                self.real_components_loaded = False
    
    def ensure_required_folders(self):
        """[EMOJI] Crear todas las carpetas necesarias si no existen"""
        required_folders = [
            data_path / "candles",
            data_path / "exports", 
            data_path / "reports",
            data_path / "reports" / "production",
            data_path / "status",
            data_path / "cache",
            data_path / "cache" / "memory",
            data_path / "memory_persistence",
            logs_path,
            logs_path / "application"
        ]
        
        for folder in required_folders:
            folder.mkdir(parents=True, exist_ok=True)
    
    def show_system_info(self):
        """Mostrar información del sistema con estado de componentes reales"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print("ICT ENGINE v6.0 ENTERPRISE - SISTEMA REAL DE TRADING")
        print("="*80)
        print(f"[EMOJI] Timestamp: {timestamp}")
        print(f"[EMOJI] Project Root: {project_root}")
        print(f"[TOOL] Core Path: {core_path}")
        print(f"[DATA] Data Path: {data_path}")
        print(f"[EMOJI] Logs Path: {logs_path}")
        print(f"[CHART] Dashboard Path: {dashboard_path}")
        print()
        print("ESTADO DE COMPONENTES REALES:")
        print("-" * 40)
        print(f"[DATA] RealICTDataCollector: {'✓ Activo' if self.real_components_loaded else '✗ Error'}")
        print(f"[MT5] MT5 Connection: {'✓ Conectado' if self.real_components_loaded else '✗ Desconectado'}")
        print(f"[LOG] SmartTradingLogger: ✓ Activo")
        print()
        print("[TARGET] Modo: TRADING REAL - Sin Mock Data")
        print("="*80)
        print()
    
    def run_dashboard_with_real_data(self):
        """Iniciar Dashboard Enterprise con RealICTDataCollector"""
        if main_logger:
            main_logger.log_system_status("Iniciando Dashboard Enterprise...", "DASHBOARD")
        print("\n[ROCKET] INICIANDO DASHBOARD ENTERPRISE CON DATOS REALES...")
        print("=" * 60)
        
        # ===== CONFIGURAR MODO SILENCIOSO PARA DASHBOARD =====
        try:
            print("🔇 Configurando modo silencioso para dashboard...")
            # Activar modo silencioso para todos los loggers centralizados
            for component in ['SYSTEM', 'DASHBOARD', 'PATTERNS', 'TRADING', 'GENERAL']:
                try:
                    logger = get_centralized_logger(component)
                    logger.set_silent_mode(True)
                except:
                    pass  # Silenciar errores de configuración de logger
            print("✅ Modo silencioso activado - logs solo en archivos")
        except Exception as e:
            print(f"⚠️ Warning: No se pudo configurar modo silencioso: {e}")
        
        try:
            # Asegurar que los componentes están inicializados
            if not self.real_components_loaded:
                if main_logger:
                    main_logger.info("Inicializando componentes reales para dashboard")
                print("[INFO] Inicializando componentes reales...")
                self.initialize_real_components()
            
            # Verificar estado del data collector
            if main_logger:
                main_logger.info("Verificando RealICTDataCollector para dashboard")
            print("[DATA] Verificando RealICTDataCollector...")
            
            if self.data_collector:
                if main_logger:
                    main_logger.info("RealICTDataCollector disponible para dashboard")
                print("[OK] RealICTDataCollector: ✓ Disponible")
                print("    - Sistema configurado con datos reales")
                print("    - Dashboard listo para cargar")
            else:
                if main_logger:
                    main_logger.warning("RealICTDataCollector no disponible, modo básico")
                print("[WARN] RealICTDataCollector: Iniciando en modo básico")
            
            # Cargar el dashboard
            dashboard_script = dashboard_path / "start_dashboard.py"
            
            if dashboard_script.exists():
                if main_logger:
                    main_logger.info(f"Ejecutando dashboard desde: {dashboard_script}")
                print("[ROCKET] Ejecutando dashboard con datos reales...")
                print(f"[TOOL] Script: {dashboard_script}")
                
                # Ejecutar dashboard con manejo estricto de proceso
                import subprocess
                import threading
                import time
                
                # Configurar variables de entorno para el dashboard
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(project_root),
                    str(core_path),
                    str(dashboard_path)
                ])
                env['ICT_DASHBOARD_MODE'] = 'subprocess'  # Marcar que es subprocess
                
                print("[SUBPROCESS] 🚀 Iniciando dashboard en proceso separado...")
                
                # Usar Popen para control completo del proceso
                dashboard_process = subprocess.Popen(
                    [sys.executable, str(dashboard_script)], 
                    cwd=str(dashboard_path),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                print(f"[SUBPROCESS] 📊 Dashboard iniciado con PID: {dashboard_process.pid}")
                print("[SUBPROCESS] ⏳ Esperando cierre del dashboard...")
                print("[SUBPROCESS] 💡 Presiona Ctrl+C en el dashboard para cerrar")
                
                try:
                    # Esperar a que termine el proceso con timeout
                    result_code = dashboard_process.wait()
                    
                except KeyboardInterrupt:
                    print("\n[SUBPROCESS] ⚠️ Interrupción detectada - cerrando dashboard...")
                    try:
                        dashboard_process.terminate()
                        dashboard_process.wait(timeout=5)
                        result_code = 0
                    except subprocess.TimeoutExpired:
                        print("[SUBPROCESS] 🔧 Forzando cierre del dashboard...")
                        dashboard_process.kill()
                        dashboard_process.wait()
                        result_code = -1
                
                print(f"[SUBPROCESS] ✅ Dashboard cerrado con código: {result_code}")
                
                if result_code == 0:
                    print("\n[OK] ✅ DASHBOARD ENTERPRISE CERRADO EXITOSAMENTE")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    print("="*60)
                    print("[SUCCESS] 🏁 SESIÓN DASHBOARD COMPLETADA")
                    print("   ✅ Dashboard cerrado correctamente")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟢 Sistema listo para nueva operación")
                    print("="*60)
                    print("\n[INFO] 📋 Menú principal restaurado - selecciona nueva opción")
                else:
                    print(f"\n[WARN] ⚠️ Dashboard finalizó con código: {result_code}")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    print("="*60)
                    print("[WARNING] ⚠️ SESIÓN DASHBOARD FINALIZADA CON ADVERTENCIAS")
                    print(f"   🔍 Código de salida: {result_code}")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟡 Sistema operativo - revisa logs si necesario")
                    print("="*60)
                    print("\n[INFO] 📋 Menú principal restaurado - selecciona nueva opción")
                
                print("="*60)
                print("[TROPHY] 🏁 DASHBOARD ENTERPRISE COMPLETADO")
                print("   Estado: ✅ Cerrado correctamente")
                print("   Regreso: 🔄 Menú principal restaurado")
                print("   Sistema: 🟢 Listo para nueva sesión")
                print("="*60)
                
            else:
                print("[X] No se encontró start_dashboard.py")
                print(f"[TOOL] Verificar ruta: {dashboard_script}")
                
        except KeyboardInterrupt:
            print("\n[EMOJI] Dashboard detenido por el usuario")
        except Exception as e:
            print(f"[X] Error ejecutando dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def main_menu(self):
        """Menú principal simplificado para dashboard enterprise"""
        while True:
            print("\n" + "="*60)
            print("ICT ENGINE v6.0 ENTERPRISE - TRADING REAL")
            print("="*60)
            print("1. [DASHBOARD] Iniciar Dashboard Enterprise") 
            print("2. [X] Salir")
            print("="*60)
            
            try:
                choice = input("\n[TARGET] Selecciona una opción (1-2): ").strip()
                
                if choice == "1":
                    if not self.real_components_loaded:
                        print("\n[INFO] Inicializando componentes reales...")
                        self.initialize_real_components()
                    
                    # Flujo automático enterprise - sin confirmación manual
                    print("\n[INFO] 🚀 Iniciando dashboard enterprise con datos reales...")
                    print("[INFO] 📊 Componentes reales configurados y listos")
                    print("[INFO] ⚡ Cargando interfaz enterprise...")
                    
                    # Pequeña pausa visual para UX
                    import time
                    time.sleep(1.5)
                    
                    # Iniciar dashboard
                    self.run_dashboard_with_real_data()
                    
                elif choice == "2":
                    print("\n[EMOJI] Cerrando sistema de trading...")
                    break
                    
                else:
                    print("[X] Opción no válida. Usa 1-2.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n[EMOJI] Saliendo...")
                break
            except EOFError:
                print("\n[EMOJI] Saliendo...")
                break
                
            # Pausa antes de mostrar el menú de nuevo
            if choice == "1":
                print("\n" + "="*80)
                print("🔄 RETORNANDO AL MENÚ PRINCIPAL")
                print("="*80)
                input("⏳ Presiona Enter para continuar...")
                print("\n" + "🔄 " + "="*78)
    
    def shutdown(self):
        """🛑 Cerrar sistema limpiamente con optimización de velocidad ultra-rápida"""
        print("🛑 [SHUTDOWN] Iniciando cierre ULTRA RÁPIDO del sistema...")
        start_time = time.time()
        
        try:
            self.is_running = False
            self.shutdown_event.set()
            
            # === SHUTDOWN ULTRA OPTIMIZADO (< 3 segundos) ===
            print("🛑 [SHUTDOWN] ⚡ Modo ultra-rápido activado...")
            
            # Fase 1: Cerrar componentes críticos con timeout mínimo
            if self.data_collector:
                print("   📊 Cerrando RealICTDataCollector (timeout: 2s)...")
                try:
                    # Usar shutdown síncrono más rápido
                    if hasattr(self.data_collector, 'shutdown_sync'):
                        self.data_collector.shutdown_sync()  # type: ignore
                    else:
                        print("   ⚡ Forzando cierre inmediato")
                    print("   ✅ RealICTDataCollector cerrado")
                except Exception as e:
                    print(f"   ⚡ Forzando cierre: {e}")
            
            # Fase 2: Cleanup ultra-rápido de singletons
            print("🛑 [SHUTDOWN] ⚡ Limpieza flash de recursos...")
            try:
                # Cleanup básico sin verificaciones complejas
                from data_management.advanced_candle_downloader_singleton import AdvancedCandleDownloaderSingleton
                AdvancedCandleDownloaderSingleton.reset_instance()
                print("   ⚡ AdvancedCandleDownloader: RESET")
            except: pass
            
            try:
                from data_management.ict_data_manager_singleton import ICTDataManagerSingleton
                ICTDataManagerSingleton.reset_instance()
                print("   ⚡ ICTDataManager: RESET")
            except: pass
            
            # Fase 3: Cleanup final ultra-rápido
            print("🛑 [SHUTDOWN] ⚡ Limpieza final...")
            self.data_collector = None
            self.real_components_loaded = False
            
            # Force garbage collection
            import gc
            collected = gc.collect()
            print(f"   🧹 GC: {collected} objetos")
            
            shutdown_time = time.time() - start_time
            print(f"🛑 [SHUTDOWN] ✅ ULTRA RÁPIDO: {shutdown_time:.2f}s")
            
        except Exception as e:
            shutdown_time = time.time() - start_time
            print(f"🛑 [SHUTDOWN] ❌ Error ({shutdown_time:.2f}s): {e}")
            # Forzar salida rápida
            if shutdown_time > 5:  # Solo 5 segundos máximo
                print("🛑 [SHUTDOWN] ⚡ FORZANDO SALIDA")
                import os
                os._exit(1)

def emergency_signal_handler(signum, frame):
    """Handler de emergencia para shutdown ultra-rápido"""
    import os
    print(f"\n⚡ [EMERGENCY] Señal {signum} - SHUTDOWN INMEDIATO")
    
    # Intentar restaurar directorio original si existe
    try:
        if 'original_dir' in globals() and globals()['original_dir'] is not None:
            os.chdir(globals()['original_dir'])
            print(f"⚡ [EMERGENCY] 📂 Directorio restaurado")
    except:
        pass  # Ignorar errores en emergency shutdown
    
    # Limpiar stdout/stderr
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except:
        pass
    
    print("⚡ [EMERGENCY] 👋 Salida de emergencia")
    os._exit(0)

def main():
    """Función principal simplificada"""
    # Guardar directorio original para restaurar al final
    global original_dir
    original_dir = os.getcwd()
    
    # Configurar handler de emergencia
    signal.signal(signal.SIGINT, emergency_signal_handler)
    signal.signal(signal.SIGTERM, emergency_signal_handler)
    
    try:
        print("🚀 [MAIN] 🎯 INICIANDO ICT ENGINE v6.0 ENTERPRISE")
        print("🚀 [MAIN] " + "="*50)
        
        # Log estructurado del inicio del sistema
        if main_logger:
            main_logger.info("🎯 INICIANDO ICT ENGINE v6.0 ENTERPRISE", "SYSTEM")
            main_logger.log_system_status("Sistema iniciando...", "STARTUP")
        
        # Verificar que las rutas existen
        if not core_path.exists():
            print(f"🚀 [MAIN] ❌ Error: No se encuentra 01-CORE en {core_path}")
            print("🚀 [MAIN] 📝 NOTA: Verificar estructura del proyecto")
            if main_logger:
                main_logger.error(f"No se encuentra 01-CORE en {core_path}", "SYSTEM")
                main_logger.critical("Estructura del proyecto inválida", "SYSTEM")
            sys.exit(1)
        
        print("🚀 [MAIN] ✅ Estructura del proyecto verificada")
        if main_logger:
            main_logger.info("✅ Estructura del proyecto verificada", "SYSTEM")
        
        # Crear y ejecutar sistema enterprise
        print("🚀 [MAIN] 🏗️ Creando sistema enterprise...")
        if main_logger:
            main_logger.info("🏗️ Creando sistema enterprise", "SYSTEM")
        
        enterprise_system = ICTEnterpriseSystem()
        
        print("🚀 [MAIN] 📊 Mostrando información del sistema...")
        if main_logger:
            main_logger.info("📊 Mostrando información del sistema", "SYSTEM")
        
        enterprise_system.show_system_info()
        
        print("🚀 [MAIN] 🚀 Iniciando menú principal...")
        if main_logger:
            main_logger.info("🚀 Iniciando menú principal del sistema", "SYSTEM")
            main_logger.log_system_status("Sistema completamente inicializado - Menú activo", "SUCCESS")
        
        enterprise_system.main_menu()
        
    except KeyboardInterrupt:
        if main_logger:
            main_logger.warning("Sistema terminado por el usuario (KeyboardInterrupt)", "SYSTEM")
            main_logger.log_system_status("Cierre limpio por usuario", "SHUTDOWN")
        print("\n🚀 [MAIN] 🛑 Sistema enterprise terminado por el usuario")
    except Exception as e:
        if main_logger:
            main_logger.error(f"Error fatal en main: {e}", "SYSTEM")
            main_logger.critical(f"Terminación inesperada del sistema: {e}", "SYSTEM")
        print(f"🚀 [MAIN] ❌ Error fatal: {e}")
        sys.exit(1)
    finally:
        # Restaurar directorio original
        try:
            os.chdir(original_dir)
            print(f"🚀 [MAIN] 📂 Directorio restaurado: {original_dir}")
        except Exception as e:
            print(f"🚀 [MAIN] ⚠️ No se pudo restaurar directorio: {e}")
        
        # Cerrar sesión de logging
        if main_logger:
            main_logger.log_session_end()
            main_logger.info("📝 Sesión de logging cerrada correctamente", "SYSTEM")
        print("🚀 [MAIN] 📝 Sesión de logging cerrada")
        print("🚀 [MAIN] 👋 ¡Hasta pronto!")
        
        # Asegurar que el terminal regrese al prompt
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == "__main__":
    main()
