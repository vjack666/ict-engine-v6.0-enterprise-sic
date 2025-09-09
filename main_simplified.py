#!/usr/bin/env python3
"""
🎯 ICT ENGINE v6.0 ENTERPRISE - DASHBOARD ÚNICO
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
    str(dashboard_path / "widgets")
])

print(f"🔧 Core path configurado: {core_path}")
print(f"🔧 Data path configurado: {data_path}")
print(f"🔧 Logs path configurado: {logs_path}")

class ICTEnterpriseSystem:
    """🎯 Sistema ICT Engine v6.0 Enterprise - Dashboard Único"""
    
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
        print(f"\n📡 Señal recibida: {signum}. Iniciando cierre...")
        self.shutdown()
    
    def ensure_required_folders(self):
        """📁 Crear todas las carpetas necesarias si no existen"""
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
        print("🎯 ICT ENGINE v6.0 ENTERPRISE - DASHBOARD ÚNICO")
        print("="*80)
        print(f"📅 Timestamp: {timestamp}")
        print(f"📁 Project Root: {project_root}")
        print(f"🔧 Core Path: {core_path}")
        print(f"📊 Data Path: {data_path}")
        print(f"📋 Logs Path: {logs_path}")
        print(f"📈 Dashboard Path: {dashboard_path}")
        print("🎯 Modo: Dashboard Enterprise con Datos Reales Únicamente")
        print("="*80)
        print()
    
    def initialize_and_validate_system(self):
        """🔧 Inicializar y validar sistema usando RealMarketBridge"""
        print("🔧 INICIALIZANDO SISTEMA ENTERPRISE...")
        print("=" * 50)
        
        # Inicializar RealMarketBridge para validación
        try:
            print("📡 Inicializando RealMarketBridge...")
            sys.path.insert(0, str(dashboard_path))
            from core.real_market_bridge import RealMarketBridge
            
            bridge = RealMarketBridge()
            print("✅ RealMarketBridge inicializado exitosamente")
            
        except Exception as e:
            print(f"❌ Error inicializando RealMarketBridge: {e}")
            print("⚠️ Sistema continuará sin validación de bridge")
            bridge = None
        
        # Validar MT5DataManager
        try:
            print("📊 Validando MT5DataManager...")
            if bridge:
                bridge.initialize_mt5_manager()
                print("✅ MT5DataManager: Conectado")
            else:
                print("⚠️ MT5DataManager: No validado")
        except Exception as e:
            print(f"⚠️ MT5DataManager: Error - {e}")
        
        # Validar UnifiedMemorySystem
        try:
            print("🧠 Validando UnifiedMemorySystem...")
            if bridge:
                bridge.initialize_unified_memory()
                print("✅ UnifiedMemorySystem: v6.1 Activo")
            else:
                print("⚠️ UnifiedMemorySystem: No validado")
        except Exception as e:
            print(f"⚠️ UnifiedMemorySystem: Error - {e}")
        
        # Validar SilverBulletEnterprise
        try:
            print("🎯 Validando SilverBulletEnterprise...")
            if bridge:
                bridge.initialize_silver_bullet()
                print("✅ SilverBulletEnterprise: Cargado")
            else:
                print("⚠️ SilverBulletEnterprise: No validado")
        except Exception as e:
            print(f"⚠️ SilverBulletEnterprise: Error - {e}")
        
        # Mostrar información de símbolos y datos disponibles
        print("\n📊 INFORMACIÓN DE DATOS DISPONIBLES:")
        print("-" * 40)
        
        if bridge:
            try:
                # Obtener información de símbolos
                symbols_config = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
                print(f"📈 Símbolos configurados: {', '.join(symbols_config)}")
                
                # Intentar obtener datos FVG
                fvg_stats = bridge.get_real_fvg_stats("EURUSD", "M15")
                if fvg_stats:
                    active_fvgs = fvg_stats.get('active_fvgs', 0)
                    print(f"📊 FVGs detectados: {active_fvgs} activos")
                else:
                    print("📊 FVGs detectados: No disponibles")
                
                # Obtener datos de mercado
                market_data = bridge.get_market_data("EURUSD", "M15")
                if market_data and 'price' in market_data:
                    print(f"💰 Precio actual EURUSD: {market_data['price']}")
                else:
                    print("💰 Datos de mercado: No disponibles")
                
                print("✅ Sistema listo para dashboard")
                
            except Exception as e:
                print(f"⚠️ Error obteniendo información de datos: {e}")
                print("⚠️ Dashboard iniciará con datos limitados")
        else:
            print("⚠️ Sin RealMarketBridge - Dashboard iniciará en modo básico")
        
        print("\n" + "=" * 50)
        return bridge is not None
    
    def run_dashboard_with_real_data(self):
        """🚀 Iniciar Dashboard Enterprise con datos reales"""
        print("\n🚀 INICIANDO DASHBOARD ENTERPRISE...")
        print("=" * 50)
        
        try:
            # Intentar cargar DashboardBridge
            try:
                from dashboard_bridge import DashboardBridge
                bridge = DashboardBridge()
                print("✅ DashboardBridge importado exitosamente")
            except ImportError as e:
                print(f"⚠️ Error importando dashboard_bridge: {e}")
                print("🔄 Intentando método alternativo...")
                
                # Método alternativo - usar script directo
                dashboard_script = dashboard_path / "start_dashboard.py"
                if dashboard_script.exists():
                    print("✅ Script dashboard encontrado")
                    import subprocess
                    subprocess.run([sys.executable, str(dashboard_script)], cwd=str(dashboard_path))
                    return
                else:
                    print("❌ No se encontró start_dashboard.py")
                    return
            
            # Inicializar componentes del sistema
            print("🔗 Inicializando componentes del sistema...")
            initialized_components = bridge.initialize_system_components()
            
            if not initialized_components:
                print("❌ Error inicializando componentes del sistema")
                return
            
            print("✅ Componentes Enterprise inicializados:")
            for component, status in initialized_components.items():
                print(f"   {component}: {status}")
            
            # Lanzar dashboard con datos reales
            print("\n🎯 Lanzando Dashboard Enterprise con datos reales...")
            
            dashboard_success = bridge.launch_dashboard_with_real_data(initialized_components)
            
            if dashboard_success:
                print("✅ DASHBOARD ENTERPRISE OPERATIVO")
                print("="*65)
                print("🏆 Estado: Dashboard funcionando con datos reales")
                print("📊 Datos: MT5 Professional + UnifiedMemorySystem v6.1")
                print("💰 Análisis: Enterprise-grade con datos en tiempo real")
                print("🎯 Interface: Dashboard completo con datos live")
                print("="*65)
            else:
                print("❌ Error lanzando dashboard enterprise")
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard detenido por el usuario")
        except Exception as e:
            print(f"❌ Error ejecutando dashboard: {e}")
    
    def main_menu(self):
        """📋 Menú principal simplificado"""
        while True:
            print("\n🎯 ICT Engine v6.0 Enterprise Dashboard")
            print("="*50)
            print("1. 🚀 Iniciar Dashboard Enterprise con Datos Reales")
            print("2. ❌ Salir")
            print("="*50)
            
            try:
                choice = input("\n🎯 Selecciona una opción (1 o 2): ").strip()
                
                if choice == "1":
                    # Validar sistema antes de iniciar dashboard
                    system_ready = self.initialize_and_validate_system()
                    
                    if system_ready:
                        print("\n✅ Sistema validado - Procediendo con dashboard...")
                    else:
                        print("\n⚠️ Sistema con limitaciones - Dashboard iniciará en modo básico...")
                    
                    # Esperar confirmación del usuario
                    input("\n🔄 Presiona Enter para continuar...")
                    
                    # Iniciar dashboard
                    self.run_dashboard_with_real_data()
                    
                elif choice == "2":
                    print("\n👋 Saliendo del sistema...")
                    break
                    
                else:
                    print("❌ Opción no válida. Usa 1 o 2.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except EOFError:
                print("\n👋 Saliendo...")
                break
                
            # Pausa antes de mostrar el menú de nuevo
            input("\n🔄 Presiona Enter para volver al menú principal...")
            print("\n" + "="*80)
    
    def shutdown(self):
        """🔄 Cerrar sistema limpiamente"""
        try:
            self.is_running = False
            self.shutdown_event.set()
            print("✅ Sistema enterprise cerrado exitosamente")
        except Exception as e:
            print(f"⚠️ Error durante cierre: {e}")

def main():
    """Función principal simplificada"""
    try:
        # Verificar que las rutas existen
        if not core_path.exists():
            print(f"❌ Error: No se encuentra 01-CORE en {core_path}")
            print("📋 NOTA: Verificar estructura del proyecto")
            sys.exit(1)
        
        # Crear y ejecutar sistema enterprise
        enterprise_system = ICTEnterpriseSystem()
        enterprise_system.show_system_info()
        enterprise_system.main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Sistema enterprise terminado por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
