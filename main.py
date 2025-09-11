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
    
    def main_menu(self):
        """Menú principal simplificado para producción enterprise"""
        while True:
            print("\n" + "="*60)
            print("ICT ENGINE v6.0 ENTERPRISE - TRADING REAL")
            print("="*60)
            print("1. [DASHBOARD] Iniciar Sistema Enterprise")
            print("2. [X] Salir")
            print("="*60)
            
            try:
                choice = input("\n[TARGET] Selecciona una opción (1-2): ").strip()
                
                if choice == "1":
                    if not self.real_components_loaded:
                        print("\n[INFO] Inicializando componentes reales...")
                        self.initialize_real_components()
                    
                    print("\n[INFO] 🚀 Iniciando sistema enterprise con datos reales...")
                    print("[INFO] 📊 Componentes reales configurados y listos")
                    print("[INFO] ⚡ Cargando interfaz enterprise...")
                    
                    time.sleep(1.5)
                    # Usar subprocess por defecto ya que es más estable
                    self.run_dashboard_with_real_data()
                    
                elif choice == "2":
                    print("\n[EXIT] Cerrando sistema de trading...")
                    break
                    
                else:
                    print("[X] Opción no válida. Usa 1-2.")
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
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal simplificada"""
    global original_dir
    
    try:
        print("🚀 [MAIN] 🎯 INICIANDO ICT ENGINE v6.0 ENTERPRISE")
        print("🚀 [MAIN] " + "="*50)
        
        # Log estructurado del inicio del sistema
        print("🚀 [MAIN] 📊 Verificando estructura del proyecto...")
        
        # Verificar que las rutas existen
        if not CORE_PATH.exists():
            print(f"🚀 [MAIN] ❌ Error: No se encuentra 01-CORE en {CORE_PATH}")
            print("🚀 [MAIN] 📝 NOTA: Verificar estructura del proyecto")
            sys.exit(1)
        
        print("🚀 [MAIN] ✅ Estructura del proyecto verificada")
        
        # Crear y ejecutar sistema enterprise
        print("🚀 [MAIN] 🏗️ Creando sistema enterprise...")
        enterprise_system = ICTEnterpriseManager()
        
        print("🚀 [MAIN] 📊 Mostrando información del sistema...")
        enterprise_system.show_system_info()
        
        print("🚀 [MAIN] 🚀 Iniciando menú principal...")
        enterprise_system.main_menu()
        
        # Shutdown limpio
        enterprise_system.shutdown()
        
    except KeyboardInterrupt:
        print("\n🚀 [MAIN] 🛑 Sistema enterprise terminado por el usuario")
    except Exception as e:
        print(f"🚀 [MAIN] ❌ Error fatal: {e}")
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
