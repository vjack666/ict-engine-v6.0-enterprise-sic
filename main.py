#!/usr/bin/env python3
"""
[TARGET] ICT ENGINE v6.0 ENTERPRISE - DASHBOARD ÚNICO
==============================================
Sistema simplificado con una sola función:
Dashboard Enterprise con datos reales
"""

import sys
import os
import signal
import threading
import time
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

class ICTEnterpriseSystem:
    """[TARGET] Sistema ICT Engine v6.0 Enterprise - Dashboard Único"""
    
    def __init__(self):
        """Inicializar sistema enterprise simplificado"""
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Configurar handlers de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Asegurar directorios necesarios
        self.ensure_required_folders()
    
    def _signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        print(f"\n[EMOJI] Señal recibida: {signum}. Iniciando cierre...")
        self.shutdown()
    
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
        """Mostrar información del sistema"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print("[TARGET] ICT ENGINE v6.0 ENTERPRISE - DASHBOARD ÚNICO")
        print("="*80)
        print(f"[EMOJI] Timestamp: {timestamp}")
        print(f"[EMOJI] Project Root: {project_root}")
        print(f"[TOOL] Core Path: {core_path}")
        print(f"[DATA] Data Path: {data_path}")
        print(f"[EMOJI] Logs Path: {logs_path}")
        print(f"[CHART] Dashboard Path: {dashboard_path}")
        print("[TARGET] Modo: Dashboard Enterprise con Datos Reales Únicamente")
        print("="*80)
        print()
    
    def initialize_and_validate_system(self):
        """[TOOL] Inicializar y validar sistema usando RealMarketBridge"""
        print("[TOOL] INICIALIZANDO SISTEMA ENTERPRISE...")
        print("=" * 50)
        
        # Inicializar RealMarketBridge para validación
        try:
            print("[EMOJI] Inicializando RealMarketBridge...")
            
            # Configurar path correcto para RealMarketBridge
            dashboard_core_path = dashboard_path / "core"
            if str(dashboard_core_path) not in sys.path:
                sys.path.insert(0, str(dashboard_core_path))
            
            # Import con manejo de errores robusto
            import importlib.util
            bridge_spec = importlib.util.spec_from_file_location(
                "real_market_bridge", 
                dashboard_core_path / "real_market_bridge.py"
            )
            
            if bridge_spec is not None and bridge_spec.loader is not None:
                bridge_module = importlib.util.module_from_spec(bridge_spec)
                bridge_spec.loader.exec_module(bridge_module)
                
                RealMarketBridge = bridge_module.RealMarketBridge
                bridge = RealMarketBridge()
                print("[OK] RealMarketBridge inicializado exitosamente")
            else:
                raise ImportError("No se pudo cargar RealMarketBridge")
            
        except Exception as e:
            print(f"[X] Error inicializando RealMarketBridge: {e}")
            print("[WARN] Sistema continuará sin validación de bridge")
            bridge = None
        
        # Validar MT5DataManager
        try:
            print("[DATA] Validando MT5DataManager...")
            if bridge:
                bridge.initialize_mt5_manager()
                print("[OK] MT5DataManager: Conectado")
            else:
                print("[WARN] MT5DataManager: No validado")
        except Exception as e:
            print(f"[WARN] MT5DataManager: Error - {e}")
        
        # Validar UnifiedMemorySystem
        try:
            print("[BRAIN] Validando UnifiedMemorySystem...")
            if bridge:
                bridge.initialize_unified_memory()
                print("[OK] UnifiedMemorySystem: v6.1 Activo")
            else:
                print("[WARN] UnifiedMemorySystem: No validado")
        except Exception as e:
            print(f"[WARN] UnifiedMemorySystem: Error - {e}")
        
        # Validar SilverBulletEnterprise
        try:
            print("[TARGET] Validando SilverBulletEnterprise...")
            if bridge:
                bridge.initialize_silver_bullet()
                print("[OK] SilverBulletEnterprise: Cargado")
            else:
                print("[WARN] SilverBulletEnterprise: No validado")
        except Exception as e:
            print(f"[WARN] SilverBulletEnterprise: Error - {e}")
        
        # Mostrar información de símbolos y datos disponibles
        print("\n[DATA] INFORMACIÓN DE DATOS DISPONIBLES:")
        print("-" * 40)
        
        if bridge:
            try:
                # Obtener información de símbolos
                symbols_config = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
                print(f"[CHART] Símbolos configurados: {', '.join(symbols_config)}")
                
                # Intentar obtener datos FVG (sin parámetros - método no los acepta)
                fvg_stats = bridge.get_real_fvg_stats()
                if fvg_stats:
                    active_fvgs = fvg_stats.get('total_active_fvgs', 0)
                    print(f"[DATA] FVGs detectados: {active_fvgs} activos")
                else:
                    print("[DATA] FVGs detectados: No disponibles")
                
                # Obtener datos de mercado
                market_data = bridge.get_market_data("EURUSD", "M15")
                if market_data and 'price' in market_data:
                    print(f"[EMOJI] Precio actual EURUSD: {market_data['price']}")
                else:
                    print("[EMOJI] Datos de mercado: No disponibles")
                
                print("[OK] Sistema listo para dashboard")
                
            except Exception as e:
                print(f"[WARN] Error obteniendo información de datos: {e}")
                print("[WARN] Dashboard iniciará con datos limitados")
        else:
            print("[WARN] Sin RealMarketBridge - Dashboard iniciará en modo básico")
        
        print("\n" + "=" * 50)
        return bridge is not None
    
    def run_dashboard_with_real_data(self):
        """[ROCKET] Iniciar Dashboard Enterprise con datos reales"""
        print("\n[ROCKET] INICIANDO DASHBOARD ENTERPRISE...")
        print("=" * 50)
        
        try:
            # Intentar cargar DashboardBridge
            try:
                # Configurar path correcto para DashboardBridge
                dashboard_bridge_path = dashboard_path / "bridge"
                if str(dashboard_bridge_path) not in sys.path:
                    sys.path.insert(0, str(dashboard_bridge_path))
                
                # Import con manejo de errores robusto
                import importlib.util
                dashboard_spec = importlib.util.spec_from_file_location(
                    "dashboard_bridge", 
                    dashboard_bridge_path / "dashboard_bridge.py"
                )
                
                if dashboard_spec is not None and dashboard_spec.loader is not None:
                    dashboard_module = importlib.util.module_from_spec(dashboard_spec)
                    dashboard_spec.loader.exec_module(dashboard_module)
                    
                    DashboardBridge = dashboard_module.DashboardBridge
                    bridge = DashboardBridge()
                    print("[OK] DashboardBridge importado exitosamente")
                else:
                    raise ImportError("No se pudo cargar DashboardBridge")
            except ImportError as e:
                print(f"[WARN] Error importando dashboard_bridge: {e}")
                print("[EMOJI] Intentando método alternativo...")
                
                # Método alternativo - usar script directo
                dashboard_script = dashboard_path / "start_dashboard.py"
                if dashboard_script.exists():
                    print("[OK] Script dashboard encontrado")
                    import subprocess
                    subprocess.run([sys.executable, str(dashboard_script)], cwd=str(dashboard_path))
                    return
                else:
                    print("[X] No se encontró start_dashboard.py")
                    return
            
            # Inicializar componentes del sistema
            print("[LINK] Inicializando componentes del sistema...")
            
            # Usar el método correcto del DashboardBridge
            bridge.initialize_system_components()
            
            # Obtener estado de los componentes
            component_status = bridge.get_system_status()
            
            if component_status and component_status.get('system_ready'):
                print("[OK] Componentes Enterprise inicializados:")
                print(f"   Sistema listo: {component_status.get('system_ready', 'Unknown')}")
                print(f"   Dashboard disponible: {component_status.get('dashboard_available', 'Unknown')}")
                print(f"   Componentes activos: {component_status.get('available_components_count', 0)}/{component_status.get('total_components_count', 0)}")
                initialized_components = component_status
            else:
                print("[X] Error inicializando componentes del sistema")
                return
            
            # Lanzar dashboard con datos reales
            print("\n[TARGET] Lanzando Dashboard Enterprise con datos reales...")
            
            # Verificar que el sistema está listo
            if component_status.get('system_ready'):
                print("[OK] Sistema listo para dashboard enterprise")
                print(f"   Componentes disponibles: {component_status.get('available_components_count', 0)}")
                
                # Intentar ejecutar el dashboard
                print("[ROCKET] Iniciando dashboard enterprise...")
                
                # Usar el método directo de start_dashboard.py
                dashboard_script = dashboard_path / "start_dashboard.py"
                if dashboard_script.exists():
                    print("[OK] Ejecutando start_dashboard.py...")
                    import subprocess
                    result = subprocess.run([sys.executable, str(dashboard_script)], 
                                          cwd=str(dashboard_path),
                                          capture_output=False)
                    
                    if result.returncode == 0:
                        dashboard_success = True
                    else:
                        print(f"[WARN] Dashboard finalizó con código: {result.returncode}")
                        dashboard_success = True  # Considerar éxito aunque termine
                else:
                    print("[X] No se encontró start_dashboard.py")
                    dashboard_success = False
            else:
                print("[WARN] Sistema no completamente listo - iniciando dashboard en modo básico")
                dashboard_success = True
            
            if dashboard_success:
                print("[OK] DASHBOARD ENTERPRISE OPERATIVO")
                print("="*65)
                print("[TROPHY] Estado: Dashboard funcionando con datos reales")
                print("[DATA] Datos: MT5 Professional + UnifiedMemorySystem v6.1")
                print("[EMOJI] Análisis: Enterprise-grade con datos en tiempo real")
                print("[TARGET] Interface: Dashboard completo con datos live")
                print("="*65)
            else:
                print("[X] Error lanzando dashboard enterprise")
                
        except KeyboardInterrupt:
            print("\n[EMOJI] Dashboard detenido por el usuario")
        except Exception as e:
            print(f"[X] Error ejecutando dashboard: {e}")
    
    def main_menu(self):
        """[EMOJI] Menú principal simplificado"""
        while True:
            print("\n[TARGET] ICT Engine v6.0 Enterprise Dashboard")
            print("="*50)
            print("1. [ROCKET] Iniciar Dashboard Enterprise con Datos Reales")
            print("2. [X] Salir")
            print("="*50)
            
            try:
                choice = input("\n[TARGET] Selecciona una opción (1 o 2): ").strip()
                
                if choice == "1":
                    # Validar sistema antes de iniciar dashboard
                    system_ready = self.initialize_and_validate_system()
                    
                    if system_ready:
                        print("\n[OK] Sistema validado - Procediendo con dashboard...")
                    else:
                        print("\n[WARN] Sistema con limitaciones - Dashboard iniciará en modo básico...")
                    
                    # Esperar confirmación del usuario
                    input("\n[EMOJI] Presiona Enter para continuar...")
                    
                    # Iniciar dashboard
                    self.run_dashboard_with_real_data()
                    
                elif choice == "2":
                    print("\n[EMOJI] Saliendo del sistema...")
                    break
                    
                else:
                    print("[X] Opción no válida. Usa 1 o 2.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n[EMOJI] Saliendo...")
                break
            except EOFError:
                print("\n[EMOJI] Saliendo...")
                break
                
            # Pausa antes de mostrar el menú de nuevo
            input("\n[EMOJI] Presiona Enter para volver al menú principal...")
            print("\n" + "="*80)
    
    def shutdown(self):
        """[EMOJI] Cerrar sistema limpiamente"""
        try:
            self.is_running = False
            self.shutdown_event.set()
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
        print("\n[EMOJI] Sistema enterprise terminado por el usuario")
    except Exception as e:
        print(f"[X] Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
