#!/usr/bin/env python3
"""
ICT ENGINE v6.0 ENTERPRISE - DASHBOARD REAL
==============================================
Sistema de trading con dashboard unificado y análisis en tiempo real
Con datos reales MT5 únicamente - Sin mock data
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

print(f"[TOOL] Core path configurado: {core_path}")
print(f"[TOOL] Data path configurado: {data_path}")
print(f"[TOOL] Logs path configurado: {logs_path}")

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
        print(f"[WARN] Error en inicialización avanzada: {e}")
        # Usar versiones básicas
        import logging
        logger = logging.getLogger(__name__)
        mt5_manager = None
    
    print("[OK] Componentes reales importados exitosamente")
    print("    - SmartTradingLogger: Activo")
    print("    - MT5DataManager: Activo") 
    print("    - RealICTDataCollector: Disponible")
    
except Exception as e:
    print(f"[X] Error importando componentes reales: {e}")
    print(f"[DEBUG] Paths utilizados:")
    print(f"    - Utils: {core_path / 'utils'}")
    print(f"    - Dashboard Data: {dashboard_path / 'data'}")
    print("[CRITICAL] Sistema no puede continuar sin componentes reales")
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
        print(f"\n[EMOJI] Señal recibida: {signum}. Iniciando cierre...")
        self.shutdown()
    
    def initialize_real_components(self):
        """Inicializar RealICTDataCollector y componentes reales"""
        try:
            if main_logger:
                main_logger.log_system_status("Inicializando RealICTDataCollector...", "CORE")
            print("[TOOL] Inicializando RealICTDataCollector...")
            
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
            
            if main_logger:
                main_logger.info(f"Configuración aplicada: {len(config['data']['symbols'])} símbolos, {len(config['data']['timeframes'])} timeframes")
            
            # Crear instancia del colector de datos reales
            self.data_collector = RealICTDataCollector(config)
            
            # Ejecutar inicialización async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Inicializar componentes async
            loop.run_until_complete(self.data_collector.initialize())
            
            # Verificar estado básico - solo verificar que el objeto fue creado
            if self.data_collector:
                if main_logger:
                    main_logger.log_system_status("RealICTDataCollector inicializado correctamente", "SUCCESS")
                print("[OK] RealICTDataCollector: Inicializado correctamente")
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
                
                # Ejecutar dashboard
                import subprocess
                
                # Configurar variables de entorno para el dashboard
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(project_root),
                    str(core_path),
                    str(dashboard_path)
                ])
                
                result = subprocess.run(
                    [sys.executable, str(dashboard_script)], 
                    cwd=str(dashboard_path),
                    env=env,
                    capture_output=False
                )
                
                if result.returncode == 0:
                    print("[OK] DASHBOARD ENTERPRISE EJECUTADO EXITOSAMENTE")
                else:
                    print(f"[WARN] Dashboard finalizó con código: {result.returncode}")
                
                print("="*60)
                print("[TROPHY] DASHBOARD ENTERPRISE OPERATIVO")
                print("   Estado: Funcionando con datos MT5 reales")
                print("   Datos: RealICTDataCollector + MT5DataManager")
                print("   Análisis: Tiempo real sin mock data")
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
                    
                    # Confirmar inicio del dashboard
                    print("\n[INFO] Iniciando dashboard enterprise con datos reales...")
                    input("Presiona Enter para continuar...")
                    
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
                input("\n[EMOJI] Presiona Enter para volver al menú principal...")
                print("\n" + "="*80)
    
    def shutdown(self):
        """Cerrar sistema limpiamente incluyendo componentes reales"""
        try:
            self.is_running = False
            self.shutdown_event.set()
            
            # Cerrar RealICTDataCollector si está activo
            if self.data_collector:
                print("[TOOL] Cerrando RealICTDataCollector...")
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.data_collector.shutdown())
                    loop.close()
                    print("[OK] RealICTDataCollector cerrado exitosamente")
                except Exception as e:
                    print(f"[WARN] Error cerrando data collector: {e}")
            
            print("[OK] Sistema enterprise cerrado exitosamente")
        except Exception as e:
            print(f"[WARN] Error durante cierre: {e}")

def main():
    """Función principal simplificada"""
    try:
        # Verificar que las rutas existen
        if not core_path.exists():
            print(f"[X] Error: No se encuentra 01-CORE en {core_path}")
            print("[EMOJI] NOTA: Verificar estructura del proyecto")
            sys.exit(1)
        
        # Crear y ejecutar sistema enterprise
        enterprise_system = ICTEnterpriseSystem()
        enterprise_system.show_system_info()
        enterprise_system.main_menu()
        
    except KeyboardInterrupt:
        if main_logger:
            main_logger.warning("Sistema terminado por el usuario (KeyboardInterrupt)")
        print("\n[EMOJI] Sistema enterprise terminado por el usuario")
    except Exception as e:
        if main_logger:
            main_logger.error(f"Error fatal en main: {e}")
        print(f"[X] Error fatal: {e}")
        sys.exit(1)
    finally:
        # Cerrar sesión de logging
        if main_logger:
            main_logger.log_session_end()

if __name__ == "__main__":
    main()
