#!/usr/bin/env python3
"""
🏭 ENTERPRISE TABS MANAGER v6.0 - PRODUCTION ORCHESTRATOR
=========================================================

Gestor centralizado para todos los tabs enterprise del dashboard.
Reemplaza las funciones de test con funcionalidad de producción real.

Funcionalidades:
✅ Carga automática de todos los tabs enterprise
✅ Integración con TabCoordinator
✅ Persistencia de estado y configuración
✅ Métricas de rendimiento de tabs
✅ Auto-registro y activación
✅ Health monitoring de tabs

Autor: ICT Engine v6.0 Enterprise Team  
Fecha: 14 Septiembre 2025
"""

import sys
import json
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import traceback

# Core imports
try:
    from tab_coordinator import get_tab_coordinator, TabState, TabCoordinator
    from dashboard_core import get_dashboard_core
    TAB_COORDINATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TabCoordinator not available: {e}")
    TAB_COORDINATOR_AVAILABLE = False
    get_tab_coordinator = None
    get_dashboard_core = None

# Core system integration
try:
    core_path = Path(__file__).parent.parent.parent.parent / "01-CORE"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
        
    from smart_trading_logger import SmartTradingLogger
    CORE_LOGGING_AVAILABLE = True
except ImportError:
    CORE_LOGGING_AVAILABLE = False
    SmartTradingLogger = None


class EnterpriseTabsManager:
    """
    🏭 GESTOR DE TABS ENTERPRISE
    ===========================
    
    Orquesta la carga, configuración y monitoreo de todos los tabs enterprise.
    """
    
    def __init__(self):
        self.tabs_directory = Path(__file__).parent
        self.coordinator = get_tab_coordinator() if (TAB_COORDINATOR_AVAILABLE and get_tab_coordinator) else None
        self.dashboard_core = get_dashboard_core() if (TAB_COORDINATOR_AVAILABLE and get_dashboard_core) else None
        
        # Logger
        if CORE_LOGGING_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("EnterpriseTabsManager")
        else:
            self.logger = None
            
        # State
        self.loaded_tabs = {}
        self.tab_configs = {}
        self.tab_metrics = {}
        
        # Persistence directories
        self.state_dir = Path(__file__).parent.parent.parent.parent / "04-DATA" / "tabs_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        print("🏭 EnterpriseTabsManager initialized")
        
    def discover_enterprise_tabs(self) -> List[str]:
        """🔍 Descubrir todos los tabs enterprise disponibles"""
        enterprise_tabs = []
        
        for tab_file in self.tabs_directory.glob("*_tab_enterprise.py"):
            tab_name = tab_file.stem
            enterprise_tabs.append(tab_name)
            
        if self.logger:
            self.logger.info(f"Discovered {len(enterprise_tabs)} enterprise tabs", "tab_discovery")
            
        print(f"🔍 Discovered enterprise tabs: {enterprise_tabs}")
        return enterprise_tabs
        
    def load_tab_module(self, tab_name: str) -> Optional[Any]:
        """📥 Cargar módulo de tab específico"""
        try:
            module_name = f"tabs.{tab_name}"
            tab_module = importlib.import_module(module_name, package="core")
            
            # Buscar factory function o clase principal
            factory_candidates = [
                f"create_{tab_name}",
                f"{tab_name.title().replace('_', '')}",
                f"{tab_name.title().replace('_', '')}Tab"
            ]
            
            for candidate in factory_candidates:
                if hasattr(tab_module, candidate):
                    factory_func = getattr(tab_module, candidate)
                    return factory_func
                    
            print(f"⚠️ No factory function found for {tab_name}")
            return tab_module
            
        except Exception as e:
            print(f"❌ Error loading {tab_name}: {e}")
            if self.logger:
                self.logger.error(f"Tab loading failed: {tab_name} - {e}")
            return None
            
    def create_tab_instance(self, tab_name: str, factory_func: Any) -> Optional[Any]:
        """🏗️ Crear instancia del tab"""
        try:
            # Intentar diferentes formas de crear la instancia
            if callable(factory_func):
                if "create_" in tab_name:
                    # Factory function
                    instance = factory_func()
                else:
                    # Class constructor
                    instance = factory_func()
            else:
                # Módulo directo
                instance = factory_func
                
            return instance
            
        except Exception as e:
            print(f"❌ Error creating instance for {tab_name}: {e}")
            return None
            
    def get_tab_configuration(self, tab_name: str) -> Dict[str, Any]:
        """⚙️ Obtener configuración del tab"""
        default_configs = {
            "fvg_tab_enterprise": {
                "refresh_interval": 1000,
                "default_symbol": "EURUSD",
                "timeframes": ["M15", "H1", "H4"],
                "detection_threshold": 0.6
            },
            "smart_money_tab_enterprise": {
                "refresh_interval": 500,
                "killzones": ["London", "New York", "Asia"],
                "liquidity_levels": 5,
                "institutional_analysis": True
            },
            "system_status_tab_enterprise": {
                "refresh_interval": 2000,
                "monitor_components": ["MT5", "Data", "Analysis", "Trading"],
                "health_checks": True
            },
            "order_blocks_tab_enterprise": {
                "refresh_interval": 500,
                "min_confidence": 0.5,
                "block_types": ["bullish", "bearish"],
                "volume_analysis": True
            },
            "market_structure_tab_enterprise": {
                "refresh_interval": 1000,
                "structure_types": ["BOS", "CHoCH", "Trend"],
                "multi_timeframe": True
            }
        }
        
        return default_configs.get(tab_name, {
            "refresh_interval": 1000,
            "enabled": True
        })
        
    def register_tab_with_coordinator(self, tab_name: str, tab_instance: Any) -> bool:
        """🎯 Registrar tab con el coordinador"""
        if not self.coordinator:
            return False
            
        try:
            # Obtener configuración
            config = self.get_tab_configuration(tab_name)
            
            # Formatear nombre para mostrar
            display_name = tab_name.replace("_tab_enterprise", "").replace("_", " ").title()
            
            # Registrar con coordinador
            success = self.coordinator.register_tab(
                tab_name,
                display_name,
                tab_instance,
                config
            )
            
            if success:
                self.loaded_tabs[tab_name] = tab_instance
                self.tab_configs[tab_name] = config
                
                # Activar tab si es el primero
                if len(self.loaded_tabs) == 1:
                    self.coordinator.activate_tab(tab_name)
                    
                print(f"✅ Registered: {display_name}")
                return True
            else:
                print(f"❌ Failed to register: {display_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering {tab_name}: {e}")
            return False
            
    def load_all_enterprise_tabs(self) -> Dict[str, bool]:
        """🔄 Cargar todos los tabs enterprise"""
        enterprise_tabs = self.discover_enterprise_tabs()
        results = {}
        
        for tab_name in enterprise_tabs:
            print(f"📥 Loading {tab_name}...")
            
            # Cargar módulo
            factory_func = self.load_tab_module(tab_name)
            if not factory_func:
                results[tab_name] = False
                continue
                
            # Crear instancia
            tab_instance = self.create_tab_instance(tab_name, factory_func)
            if not tab_instance:
                results[tab_name] = False
                continue
                
            # Registrar con coordinador
            success = self.register_tab_with_coordinator(tab_name, tab_instance)
            results[tab_name] = success
            
        return results
        
    def save_tabs_state(self) -> str:
        """💾 Guardar estado de tabs"""
        try:
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "loaded_tabs": list(self.loaded_tabs.keys()),
                "tab_configs": self.tab_configs,
                "coordinator_state": self.coordinator.export_state() if self.coordinator else None,
                "metrics": {
                    "total_tabs": len(self.loaded_tabs),
                    "successful_loads": sum(1 for success in self.loaded_tabs.values() if success),
                    "manager_initialized": True
                }
            }
            
            state_file = self.state_dir / "enterprise_tabs_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
                
            return str(state_file)
            
        except Exception as e:
            print(f"❌ Error saving tabs state: {e}")
            return ""
            
    def get_tabs_health_report(self) -> Dict[str, Any]:
        """🏥 Obtener reporte de salud de tabs"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "manager_status": "active",
            "coordinator_available": self.coordinator is not None,
            "dashboard_core_available": self.dashboard_core is not None,
            "total_tabs_loaded": len(self.loaded_tabs),
            "tabs_status": {}
        }
        
        # Estado individual de tabs
        for tab_name, tab_instance in self.loaded_tabs.items():
            try:
                # Verificar si el tab tiene método de health check
                if hasattr(tab_instance, 'get_health_status'):
                    status = tab_instance.get_health_status()
                else:
                    status = "active"
                    
                report["tabs_status"][tab_name] = {
                    "status": status,
                    "instance_type": type(tab_instance).__name__,
                    "config": self.tab_configs.get(tab_name, {})
                }
                
            except Exception as e:
                report["tabs_status"][tab_name] = {
                    "status": "error",
                    "error": str(e)
                }
                
        return report


def setup_enterprise_production_system() -> Tuple[Optional[EnterpriseTabsManager], Dict[str, Any]]:
    """🏭 Configurar sistema completo de producción enterprise"""
    print("🏭 Setting up Enterprise Production System...")
    
    try:
        # Inicializar gestor
        manager = EnterpriseTabsManager()
        
        # Cargar todos los tabs
        load_results = manager.load_all_enterprise_tabs()
        
        # Guardar estado
        state_file = manager.save_tabs_state()
        
        # Generar reporte de salud
        health_report = manager.get_tabs_health_report()
        
        # Mostrar resultados
        successful = sum(1 for success in load_results.values() if success)
        total = len(load_results)
        
        print(f"✅ Enterprise Production System ready:")
        print(f"  - Tabs loaded: {successful}/{total}")
        print(f"  - State saved: {state_file}")
        print(f"  - Coordinator active: {manager.coordinator is not None}")
        print(f"  - Dashboard core active: {manager.dashboard_core is not None}")
        
        if manager.logger:
            manager.logger.info(
                f"Enterprise system initialized: {successful}/{total} tabs loaded",
                "production_init"
            )
            
        return manager, {
            "load_results": load_results,
            "health_report": health_report,
            "state_file": state_file
        }
        
    except Exception as e:
        print(f"❌ Enterprise Production System setup failed: {e}")
        traceback.print_exc()
        return None, {"error": str(e)}


if __name__ == "__main__":
    print("🚀 Enterprise Tabs Manager - Production Mode")
    manager, results = setup_enterprise_production_system()
    
    if manager:
        print("\n📊 System Status:")
        health = manager.get_tabs_health_report()
        
        print(f"  - Manager: {health['manager_status']}")
        print(f"  - Total tabs: {health['total_tabs_loaded']}")
        print(f"  - Coordinator: {'✅' if health['coordinator_available'] else '❌'}")
        print(f"  - Dashboard Core: {'✅' if health['dashboard_core_available'] else '❌'}")
        
        if manager.coordinator:
            metrics = manager.coordinator.get_performance_metrics()
            print(f"\n⚡ Performance:")
            print(f"  - Tab switches: {metrics['tab_switches']}")
            print(f"  - Updates: {metrics['total_updates']}")
            print(f"  - Avg switch time: {metrics['average_switch_time']:.2f}ms")
            
        print("\n🎉 Enterprise Tabs Manager ready for production!")
    else:
        print("❌ Enterprise Tabs Manager initialization failed")