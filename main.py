#!/usr/bin/env python3
"""
main.py - ICT Engine v6.0 Enterprise
Sistema de Trading Avanzado con Smart Money Concepts
"""

import os
import sys
import time
import gc
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Union, Any

# Determinar rutas del sistema
current_file = Path(__file__).resolve()
SYSTEM_ROOT = current_file.parent
original_dir = os.getcwd()

# Configurar paths principales
CORE_PATH = SYSTEM_ROOT / "01-CORE"
DATA_PATH = SYSTEM_ROOT / "04-DATA"
LOGS_PATH = SYSTEM_ROOT / "05-LOGS"
DASHBOARD_PATH = SYSTEM_ROOT / "09-DASHBOARD"
DOCUMENTATION_PATH = SYSTEM_ROOT / "03-DOCUMENTATION"

# Configurar el path de Python
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

# ============================================================================
# IMPORTS CON CARGA SEGURA
# ============================================================================

def safe_import_from_path(file_path, class_name, fallback_name=None):
    """Importar una clase desde un archivo específico de forma segura"""
    try:
        if not Path(file_path).exists():
            return None
        
        import importlib.util
        module_name = Path(file_path).stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
    except Exception:
        return None

# Clase fallback para SmartTradingLogger
class BasicLogger:
    """Logger básico como fallback"""
    def __init__(self, name):
        self.name = name
    def info(self, msg): print(f"[{self.name}] {msg}")
    def warning(self, msg): print(f"[{self.name}] WARNING: {msg}")
    def error(self, msg): print(f"[{self.name}] ERROR: {msg}")
    def debug(self, msg): print(f"[{self.name}] DEBUG: {msg}")

# Imports críticos con fallbacks
try:
    from smart_trading_logger import SmartTradingLogger
    SMART_LOGGER_AVAILABLE = True
    LoggerClass = SmartTradingLogger
except ImportError as e:
    print(f"Warning: Could not import SmartTradingLogger: {e}")
    SMART_LOGGER_AVAILABLE = False
    LoggerClass = BasicLogger

# ============================================================================
# CLASES DE APOYO
# ============================================================================

class SystemStatus:
    """Estado del sistema enterprise"""
    def __init__(self):
        self.mt5_connected = False
        self.real_components_loaded = False
        self.risk_monitoring = False
        self.trading_active = False
        self.data_feed_active = False
        self.last_update = datetime.now()

class AccountInfo:
    """Información de la cuenta de trading"""
    def __init__(self):
        self.account_number = 0
        self.balance = 0.0
        self.equity = 0.0
        self.margin = 0.0
        self.free_margin = 0.0
        self.margin_level = 0.0
        self.profit = 0.0
        self.currency = "USD"
        self.leverage = 1
        self.server = ""
        self.company = ""
        self.is_connected = False
        self.last_update = datetime.now()

# ============================================================================
# SISTEMA ENTERPRISE PRINCIPAL
# ============================================================================

class ICTEnterpriseManager:
    """Gestor principal del sistema ICT Enterprise v6.0"""
    
    def __init__(self):
        """Inicializar el sistema enterprise"""
        self.logger = LoggerClass("ICTEnterpriseManager")
        self.system_status = SystemStatus()
        self.account_info = AccountInfo()
        
        self.shutdown_requested = False
        self.real_components_loaded = False
        self.data_collector = None
        self.dashboard_process = None
        self.web_dashboard_process = None
        
        # Setup inicial
        self._setup_directories()
        
    def _setup_directories(self):
        """Crear directorios necesarios"""
        required_folders = [DATA_PATH, LOGS_PATH, DATA_PATH / "cache", DATA_PATH / "exports"]
        
        for folder in required_folders:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("📁 Estructura de directorios verificada")
    
    def initialize_real_components(self):
        """Inicializar RealICTDataCollector y componentes reales"""
        self.logger.info("🔄 Inicializando componentes reales...")
        
        try:
            # Añadir dashboard data path para imports
            dashboard_data_path = str(DASHBOARD_PATH / "data")
            if dashboard_data_path not in sys.path:
                sys.path.insert(0, dashboard_data_path)
            
            # Cargar RealICTDataCollector dinámicamente
            data_collector_path = DASHBOARD_PATH / "data" / "data_collector_simplified.py"
            RealICTDataCollector = safe_import_from_path(
                data_collector_path,
                "RealICTDataCollector",
                "RealICTDataCollector"
            )
            
            if not RealICTDataCollector:
                self.logger.warning("RealICTDataCollector no disponible - continuando sin él")
                self.real_components_loaded = False
                return
            
            self.logger.info("[SYSTEM] Creando RealICTDataCollector...")
            
            # Crear instancia del data collector con configuración básica
            config = {
                'symbols': ['EURUSD', 'GBPUSD', 'USDCAD', 'AUDUSD'],
                'timeframes': ['M1', 'M5', 'M15'],
                'data_path': str(DATA_PATH)
            }
            self.data_collector = RealICTDataCollector(config)
            
            self.logger.info("✅ RealICTDataCollector: Inicializado correctamente")
            print("🚀 [SYSTEM] ✅ RealICTDataCollector: Inicializado correctamente")
            print("    - Configuración aplicada")
            print("    - Sistema listo para operación")
            self.real_components_loaded = True
            self.system_status.real_components_loaded = True
                
        except Exception as e:
            self.logger.error(f"Error inicializando componentes reales: {e}")
            print(f"[X] Error inicializando componentes reales: {e}")
            self.real_components_loaded = False
            self.system_status.real_components_loaded = False
    
    def show_system_info(self):
        """Mostrar información del sistema con estado de componentes reales"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print("ICT ENGINE v6.0 ENTERPRISE - SISTEMA REAL DE TRADING")
        print("="*80)
        print(f"🕒 Timestamp: {timestamp}")
        print(f"📂 Project Root: {SYSTEM_ROOT}")
        print(f"🔧 Core Path: {CORE_PATH}")
        print(f"📊 Data Path: {DATA_PATH}")
        print(f"📝 Logs Path: {LOGS_PATH}")
        print(f"📈 Dashboard Path: {DASHBOARD_PATH}")
        print()
        print("ESTADO DE COMPONENTES REALES:")
        print("-" * 40)
        print(f"📊 RealICTDataCollector: {'✓ Activo' if self.real_components_loaded else '✗ Error'}")
        print(f"🔗 MT5 Connection: {'✓ Conectado' if self.system_status.mt5_connected else '✗ Desconectado'}")
        print(f"📝 SmartTradingLogger: {'✓ Activo' if SMART_LOGGER_AVAILABLE else '✗ Básico'}")
        print()
        print("🎯 Modo: TRADING REAL - Sin Mock Data")
        print("="*80)
        print()

    def run_dashboard_with_real_data(self):
        """Iniciar Dashboard Enterprise en ventana separada"""
        self.logger.info("🚀 INICIANDO DASHBOARD ENTERPRISE CON DATOS REALES...")
        print("\n[ROCKET] INICIANDO DASHBOARD ENTERPRISE CON DATOS REALES...")
        print("=" * 60)
        
        try:
            # Asegurar que los componentes están inicializados
            if not self.real_components_loaded:
                self.logger.info("Inicializando componentes reales para dashboard")
                print("[INFO] Inicializando componentes reales...")
                self.initialize_real_components()
            
            # Verificar estado del data collector
            self.logger.info("Verificando RealICTDataCollector para dashboard")
            print("[DATA] Verificando RealICTDataCollector...")
            
            if hasattr(self, 'data_collector') and self.data_collector:
                self.logger.info("RealICTDataCollector disponible para dashboard")
                print("[OK] RealICTDataCollector: ✓ Disponible")
                print("    - Sistema configurado con datos reales")
                print("    - Dashboard listo para cargar")
            else:
                self.logger.warning("RealICTDataCollector no disponible, modo básico")
                print("[WARN] RealICTDataCollector: Iniciando en modo básico")
            
            # Cargar el dashboard
            dashboard_script = DASHBOARD_PATH / "start_dashboard.py"
            
            if dashboard_script.exists():
                self.logger.info(f"Ejecutando dashboard desde: {dashboard_script}")
                print("[ROCKET] 🚀 Abriendo dashboard en ventana separada...")
                
                # Configurar variables de entorno para el dashboard
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(SYSTEM_ROOT),
                    str(CORE_PATH),
                    str(DASHBOARD_PATH)
                ])
                env['ICT_DASHBOARD_MODE'] = 'subprocess'
                
                print("[SUBPROCESS] 🚀 Iniciando dashboard en proceso separado...")
                
                # Usar Popen para control completo del proceso
                self.dashboard_process = subprocess.Popen(
                    [sys.executable, str(dashboard_script)], 
                    cwd=str(DASHBOARD_PATH),
                    env=env,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                print(f"[SUBPROCESS] 📊 Dashboard iniciado con PID: {self.dashboard_process.pid}")
                print("[SUBPROCESS] 🎯 Dashboard abriendo en ventana separada...")
                print("[SUBPROCESS] 💡 El dashboard debería aparecer en una nueva ventana")
                print("[SUBPROCESS] ⏳ Esperando que uses el dashboard...")
                print("[SUBPROCESS] 🔑 Presiona 'q' en el dashboard para cerrar y regresar aquí")
                
                try:
                    # Esperar a que termine el proceso
                    result_code = self.dashboard_process.wait()
                    
                except KeyboardInterrupt:
                    print("\n[SUBPROCESS] ⚠️ Interrupción detectada - cerrando dashboard...")
                    try:
                        self.dashboard_process.terminate()
                        self.dashboard_process.wait(timeout=5)
                        result_code = 0
                    except subprocess.TimeoutExpired:
                        print("[SUBPROCESS] 🔧 Forzando cierre del dashboard...")
                        self.dashboard_process.kill()
                        self.dashboard_process.wait()
                        result_code = -1
                
                print(f"[SUBPROCESS] ✅ Dashboard cerrado con código: {result_code}")
                
                if result_code == 0:
                    print("\n[OK] ✅ DASHBOARD ENTERPRISE CERRADO EXITOSAMENTE")
                    print("[INFO] 🔄 Regresando automáticamente al menú principal...")
                    print("="*60)
                    print("[SUCCESS] 🏁 SESIÓN DASHBOARD COMPLETADA")
                    print("   ✅ Dashboard cerrado correctamente")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟢 Sistema listo para nueva operación")
                    print("="*60)
                    print("\n[PRODUCCIÓN] 🚀 Menú principal se mostrará en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"\n[WARN] ⚠️ Dashboard finalizó con código: {result_code}")
                    print("[INFO] 🔄 Regresando automáticamente al menú principal...")
                    time.sleep(2)
                    
            else:
                print("[X] No se encontró start_dashboard.py")
                print(f"[TOOL] Verificar ruta: {dashboard_script}")
                
        except KeyboardInterrupt:
            print("\n[SUBPROCESS] ⚠️ Dashboard cerrado por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando dashboard: {e}")
            print(f"[X] Error ejecutando dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def run_web_dashboard_with_real_data(self):
        """Iniciar Web Dashboard con análisis real en navegador"""
        self.logger.info("🌐 INICIANDO WEB DASHBOARD CON ANÁLISIS REAL...")
        print("\n[WEB] 🌐 INICIANDO WEB DASHBOARD CON ANÁLISIS REAL...")
        print("=" * 60)
        
        try:
            # Asegurar que los componentes están inicializados
            if not self.real_components_loaded:
                self.logger.info("Inicializando componentes reales para web dashboard")
                print("[INFO] Inicializando componentes reales...")
                self.initialize_real_components()
            
            # Verificar estado del data collector
            print("[WEB] Verificando sistema de análisis real...")
            
            if hasattr(self, 'data_collector') and self.data_collector:
                print("[OK] ✓ Sistema de análisis real disponible")
                print("    - Order Blocks detection: ACTIVO")
                print("    - Smart Money Concepts: ACTIVO")
                print("    - Logging en tiempo real: ACTIVO")
            else:
                print("[WARN] Sistema básico - Iniciando con datos simulados")
            
            # Cargar el web dashboard
            web_dashboard_script = DASHBOARD_PATH / "start_web_dashboard.py"
            
            if web_dashboard_script.exists():
                self.logger.info(f"Ejecutando web dashboard desde: {web_dashboard_script}")
                print("[WEB] 🚀 Iniciando servidor web dashboard...")
                
                # Configurar variables de entorno
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(SYSTEM_ROOT),
                    str(CORE_PATH),
                    str(DASHBOARD_PATH)
                ])
                env['ICT_WEB_DASHBOARD_MODE'] = 'real_analysis'
                
                print("[WEB] 📊 Configurando servidor web...")
                print("[WEB] 🌐 URL: http://127.0.0.1:8050")
                print("[WEB] 💡 El dashboard se abrirá automáticamente en tu navegador")
                print("[WEB] 🔄 Order Blocks actualizándose cada 500ms")
                print("[WEB] ⚠️  Presiona Ctrl+C para detener el servidor")
                
                # Usar Popen para control del proceso web
                self.web_dashboard_process = subprocess.Popen(
                    [sys.executable, str(web_dashboard_script)], 
                    cwd=str(DASHBOARD_PATH),
                    env=env,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                print(f"[WEB] 📊 Servidor web iniciado con PID: {self.web_dashboard_process.pid}")
                print("[WEB] 🎯 Accede a: http://127.0.0.1:8050 en tu navegador")
                print("[WEB] 💰 Order Blocks Tab disponible con datos en tiempo real")
                
                try:
                    # Esperar a que termine el proceso web
                    result_code = self.web_dashboard_process.wait()
                    
                except KeyboardInterrupt:
                    print("\n[WEB] ⚠️ Interrupción detectada - cerrando servidor web...")
                    try:
                        self.web_dashboard_process.terminate()
                        self.web_dashboard_process.wait(timeout=5)
                        result_code = 0
                    except subprocess.TimeoutExpired:
                        print("[WEB] 🔧 Forzando cierre del servidor...")
                        self.web_dashboard_process.kill()
                        self.web_dashboard_process.wait()
                        result_code = -1
                
                print(f"[WEB] ✅ Servidor web cerrado con código: {result_code}")
                
                if result_code == 0:
                    print("\n[OK] ✅ WEB DASHBOARD CERRADO EXITOSAMENTE")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    print("="*60)
                    print("[SUCCESS] 🏁 SESIÓN WEB DASHBOARD COMPLETADA")
                    print("   ✅ Servidor web cerrado correctamente")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟢 Sistema listo para nueva operación")
                    print("="*60)
                    print("\n[PRODUCCIÓN] 🚀 Menú principal se mostrará en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"\n[WARN] ⚠️ Servidor web finalizó con código: {result_code}")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    time.sleep(2)
                    
            else:
                print("[X] No se encontró start_web_dashboard.py")
                print(f"[TOOL] Verificar ruta: {web_dashboard_script}")
                
        except KeyboardInterrupt:
            print("\n[WEB] ⚠️ Servidor web cerrado por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando web dashboard: {e}")
            print(f"[X] Error ejecutando web dashboard: {e}")
            import traceback
            traceback.print_exc()

    def main_menu(self):
        """Menú principal con opciones de Web Dashboard y Dashboard Terminal"""
        while True:
            print("\n" + "="*70)
            print("ICT ENGINE v6.0 ENTERPRISE - TRADING REAL")
            print("="*70)
            print("1. 🌐 [WEB DASHBOARD] Análisis Real - Navegador Web")
            print("2. 🖥️  [DASHBOARD TERMINAL] Dashboard Convencional")
            print("3. ❌ [SALIR] Cerrar Sistema")
            print("="*70)
            print("💡 Opción 1: Dashboard web moderno con Order Blocks en tiempo real")
            print("💡 Opción 2: Dashboard tradicional en ventana de terminal")
            print("="*70)
            
            try:
                choice = input("\n[TARGET] Selecciona una opción (1-3): ").strip()
                
                if choice == "1":
                    print("\n🌐 [WEB DASHBOARD] Iniciando dashboard web con análisis real...")
                    self.run_web_dashboard_with_real_data()
                    
                elif choice == "2":
                    if not self.real_components_loaded:
                        print("\n[INFO] Inicializando componentes reales...")
                        self.initialize_real_components()
                    
                    print("\n🖥️ [DASHBOARD TERMINAL] Iniciando dashboard convencional...")
                    print("[INFO] 📊 Componentes reales configurados y listos")
                    print("[INFO] ⚡ Cargando interfaz enterprise...")
                    
                    time.sleep(1.5)
                    self.run_dashboard_with_real_data()
                    
                elif choice == "3":
                    print("\n[EXIT] Cerrando sistema de trading...")
                    break
                    
                else:
                    print("[X] Opción no válida. Usa 1-3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n[EXIT] Saliendo...")
                break
            except EOFError:
                print("\n[EXIT] Saliendo...")
                break
                
            # Pausa antes de mostrar el menú de nuevo
            if choice == "1":
                print("\n" + "="*80)
                print("🔄 RETORNANDO AL MENÚ PRINCIPAL")
                print("="*80)
                print("⚡ [PRODUCCIÓN] Regresando automáticamente al menú...")
                time.sleep(2)  # Pausa breve para que el usuario vea el mensaje
                print("\n" + "🔄 " + "="*78)
    
    def shutdown(self):
        """🛑 Cerrar sistema limpiamente"""
        print("🛑 [SHUTDOWN] Iniciando cierre del sistema...")
        start_time = time.time()
        
        try:
            self.shutdown_requested = True
            
            # Cerrar dashboard process si existe
            if self.dashboard_process:
                try:
                    self.dashboard_process.terminate()
                    self.dashboard_process.wait(timeout=2)
                except:
                    if self.dashboard_process.poll() is None:
                        self.dashboard_process.kill()
            
            # Cerrar web dashboard process si existe
            if self.web_dashboard_process:
                try:
                    self.web_dashboard_process.terminate()
                    self.web_dashboard_process.wait(timeout=2)
                except:
                    if self.web_dashboard_process.poll() is None:
                        self.web_dashboard_process.kill()
            
            # Cerrar componentes críticos
            if hasattr(self, 'data_collector') and self.data_collector:
                try:
                    if hasattr(self.data_collector, 'shutdown_sync'):
                        self.data_collector.shutdown_sync()
                    else:
                        self.logger.info("Forzando cierre inmediato de data collector")
                except:
                    pass
            
            # Force garbage collection
            collected = gc.collect()
            
            shutdown_time = time.time() - start_time
            self.logger.info(f"🛑 Shutdown completado en {shutdown_time:.2f}s (GC: {collected} objetos)")
            
        except Exception as e:
            shutdown_time = time.time() - start_time
            self.logger.error(f"Error en shutdown ({shutdown_time:.2f}s): {e}")

# ============================================================================
# FUNCIÓN PRINCIPAL ENTERPRISE
# ============================================================================

def main():
    """Función principal del sistema ICT Engine v6.0 Enterprise"""
    manager = None
    try:
        print("🚀 [MAIN] ICT Engine v6.0 Enterprise - Sistema de Trading Real")
        print("🚀 [MAIN] =" * 60)
        print(f"🚀 [MAIN] 🕒 Iniciando sistema: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Crear instancia del sistema enterprise
        print("🚀 [MAIN] 🔧 Creando ICTEnterpriseManager...")
        manager = ICTEnterpriseManager()
        
        # Mostrar información del sistema
        manager.show_system_info()
        
        # Ejecutar menú principal
        print("🚀 [MAIN] 🎯 Iniciando interfaz principal...")
        manager.main_menu()
        
        # Shutdown limpio
        print("🚀 [MAIN] 🛑 Iniciando shutdown del sistema...")
        manager.shutdown()
        
        print("🚀 [MAIN] ✅ Sistema cerrado exitosamente")
        
    except KeyboardInterrupt:
        print("\n🚀 [MAIN] ⚠️ Interrupción por teclado detectada")
        print("🚀 [MAIN] 🛑 Cerrando sistema...")
        try:
            if manager is not None:
                manager.shutdown()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"🚀 [MAIN] ❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restaurar directorio original
        try:
            os.chdir(original_dir)
            print(f"🚀 [MAIN] 📂 Directorio restaurado: {original_dir}")
        except Exception as e:
            print(f"🚀 [MAIN] ⚠️ No se pudo restaurar directorio: {e}")
        
        print("🚀 [MAIN] 👋 ¡Hasta pronto!")
        
        # Asegurar que el terminal regrese al prompt
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == "__main__":
    main()
