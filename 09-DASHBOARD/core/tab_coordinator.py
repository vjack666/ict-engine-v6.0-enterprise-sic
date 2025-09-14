#!/usr/bin/env python3
"""
🎛️ TAB COORDINATOR v6.0 ENTERPRISE - DASHBOARD ORCHESTRATION
===========================================================

OBJETIVO: Orchestrar navegación entre tabs y state sharing
PROBLEMA RESUELTO: Estado fragmentado entre tabs, navegación inconsistente
SOLUCIÓN: SharedState manager centralizado con event broadcasting

FUNCIONALIDADES:
✅ TabCoordinator class centralizada
✅ Cross-tab state management  
✅ Shared data caching entre tabs
✅ Navigation logic y routing
✅ Tab-specific configuration persistence
✅ Performance optimization compartido
✅ Event broadcasting entre tabs
✅ Memory-efficient state updates

Autor: ICT Engine v6.0 Enterprise Team  
Fecha: 13 Septiembre 2025
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable, Union, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from dashboard_core import DashboardCore  # noqa: F401
    from smart_trading_logger import SmartTradingLogger  # noqa: F401

# Core imports with safe loading
def _try_import_dashboard_core():
    try:
        from dashboard_core import DashboardCore, get_dashboard_core
        return DashboardCore, get_dashboard_core, True
    except ImportError as e:
        print(f"⚠️ Dashboard core not available: {e}")
        return None, None, False

def _try_import_smart_logger():
    try:
        current_dir = Path(__file__).parent.parent.parent / "01-CORE"
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        from smart_trading_logger import SmartTradingLogger
        return SmartTradingLogger, True
    except ImportError as e:
        print(f"⚠️ Core logging not available: {e}")
        return None, False

# Initialize imports
DashboardCore, get_dashboard_core, DASHBOARD_CORE_AVAILABLE = _try_import_dashboard_core()
SmartTradingLogger, CORE_LOGGING_AVAILABLE = _try_import_smart_logger()


class TabState(Enum):
    """🏷️ Estados de tabs del dashboard"""
    INACTIVE = "inactive"
    LOADING = "loading" 
    ACTIVE = "active"
    ERROR = "error"
    UPDATING = "updating"


class EventType(Enum):
    """📡 Tipos de eventos del sistema"""
    TAB_ACTIVATED = "tab_activated"
    TAB_DEACTIVATED = "tab_deactivated"
    DATA_UPDATED = "data_updated"
    STATE_CHANGED = "state_changed"
    ERROR_OCCURRED = "error_occurred"
    REFRESH_REQUESTED = "refresh_requested"
    CONFIG_CHANGED = "config_changed"


@dataclass
class TabInfo:
    """📋 Información de tab registrado"""
    id: str
    name: str
    component: Any
    state: TabState = TabState.INACTIVE
    last_updated: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)
    data_cache: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    update_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict"""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "last_updated": self.last_updated.isoformat(),
            "config": self.config,
            "error_message": self.error_message,
            "update_count": self.update_count
        }


@dataclass 
class DashboardEvent:
    """📡 Evento del sistema dashboard"""
    type: EventType
    source_tab: str
    target_tab: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict"""
        return {
            "type": self.type.value,
            "source_tab": self.source_tab,
            "target_tab": self.target_tab,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class SharedStateManager:
    """
    🔄 ADMINISTRADOR DE ESTADO COMPARTIDO
    ===================================
    
    Gestiona estado compartido entre tabs con persistencia y broadcasting.
    """
    
    def __init__(self):
        self.shared_data: Dict[str, Any] = {}
        self.tab_states: Dict[str, TabInfo] = {}
        self.event_history: List[DashboardEvent] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Performance tracking
        self.last_update = datetime.now()
        self.update_frequency = timedelta(milliseconds=100)  # Throttling
        
    def register_tab(self, tab_id: str, tab_name: str, component: Any, 
                    config: Optional[Dict[str, Any]] = None) -> bool:
        """📝 Registrar nuevo tab en el sistema"""
        try:
            self.tab_states[tab_id] = TabInfo(
                id=tab_id,
                name=tab_name,
                component=component,
                config=config or {}
            )
            
            # Broadcast registration event
            event = DashboardEvent(
                type=EventType.TAB_ACTIVATED,
                source_tab="coordinator",
                target_tab=tab_id,
                data={"action": "registered"}
            )
            self._broadcast_event(event)
            
            print(f"✅ Tab registered: {tab_name} ({tab_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error registering tab {tab_id}: {e}")
            return False
    
    def set_shared_data(self, key: str, value: Any, source_tab: str = "unknown") -> bool:
        """💾 Establecer datos compartidos"""
        if self._should_throttle_update():
            return False
            
        try:
            old_value = self.shared_data.get(key)
            self.shared_data[key] = value
            
            # Broadcast data change
            event = DashboardEvent(
                type=EventType.DATA_UPDATED,
                source_tab=source_tab,
                data={
                    "key": key,
                    "old_value": old_value,
                    "new_value": value
                }
            )
            self._broadcast_event(event)
            
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            print(f"❌ Error setting shared data {key}: {e}")
            return False
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """📖 Obtener datos compartidos"""
        return self.shared_data.get(key, default)
    
    def update_tab_state(self, tab_id: str, new_state: TabState, 
                        error_message: Optional[str] = None) -> bool:
        """🔄 Actualizar estado de tab"""
        if tab_id not in self.tab_states:
            return False
            
        try:
            tab_info = self.tab_states[tab_id]
            old_state = tab_info.state
            
            tab_info.state = new_state
            tab_info.last_updated = datetime.now()
            tab_info.update_count += 1
            
            if error_message:
                tab_info.error_message = error_message
            
            # Broadcast state change
            event = DashboardEvent(
                type=EventType.STATE_CHANGED,
                source_tab=tab_id,
                data={
                    "old_state": old_state.value,
                    "new_state": new_state.value,
                    "error_message": error_message
                }
            )
            self._broadcast_event(event)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating tab state {tab_id}: {e}")
            return False
    
    def subscribe_to_events(self, tab_id: str, callback: Callable[[DashboardEvent], None]):
        """📡 Suscribirse a eventos del sistema"""
        if tab_id not in self.subscribers:
            self.subscribers[tab_id] = []
        
        self.subscribers[tab_id].append(callback)
        print(f"📡 Tab {tab_id} subscribed to events")
    
    def _broadcast_event(self, event: DashboardEvent):
        """📡 Broadcast evento a subscribers"""
        try:
            self.event_history.append(event)
            
            # Limit event history size
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]
            
            # Notify subscribers
            for tab_id, callbacks in self.subscribers.items():
                if event.target_tab is None or event.target_tab == tab_id:
                    for callback in callbacks:
                        try:
                            callback(event)
                        except Exception as e:
                            print(f"❌ Error in event callback for {tab_id}: {e}")
                            
        except Exception as e:
            print(f"❌ Error broadcasting event: {e}")
    
    def _should_throttle_update(self) -> bool:
        """⏱️ Check if update should be throttled"""
        return datetime.now() - self.last_update < self.update_frequency
    
    def get_system_status(self) -> Dict[str, Any]:
        """📊 Obtener estado completo del sistema"""
        return {
            "tabs_registered": len(self.tab_states),
            "active_tabs": sum(1 for tab in self.tab_states.values() if tab.state == TabState.ACTIVE),
            "shared_data_keys": len(self.shared_data),
            "event_history_size": len(self.event_history),
            "subscribers": {tab_id: len(callbacks) for tab_id, callbacks in self.subscribers.items()},
            "last_update": self.last_update.isoformat(),
            "tabs": [tab.to_dict() for tab in self.tab_states.values()]
        }


class TabCoordinator:
    """
    🎛️ COORDINADOR PRINCIPAL DE TABS
    ===============================
    
    Orquesta la navegación, estado y comunicación entre todos los tabs del dashboard.
    """
    
    def __init__(self, dashboard_core: Optional[Any] = None):
        # Dashboard core integration
        if dashboard_core:
            self.core = dashboard_core
        elif DASHBOARD_CORE_AVAILABLE and get_dashboard_core:
            self.core = get_dashboard_core()
        else:
            self.core = None
            
        # State management
        self.state_manager = SharedStateManager()
        
        # Navigation
        self.active_tab = None
        self.tab_history: List[str] = []
        
        # Performance metrics
        self.performance_metrics = {
            "tab_switches": 0,
            "total_updates": 0,
            "average_switch_time": 0.0,
            "last_switch_time": 0.0
        }
        
        # Logger
        if CORE_LOGGING_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("TabCoordinator")
        else:
            self.logger = None
            
        print("🎛️ Tab Coordinator initialized")
    
    def register_tab(self, tab_id: str, tab_name: str, tab_component: Any,
                    config: Optional[Dict[str, Any]] = None) -> bool:
        """📝 Registrar tab en el coordinador"""
        
        if self.logger:
            self.logger.info(f"Registering tab: {tab_name}", "tab_registration")
        
        success = self.state_manager.register_tab(tab_id, tab_name, tab_component, config)
        
        if success:
            # Setup event subscription for the tab
            def tab_event_handler(event: DashboardEvent):
                self._handle_tab_event(tab_id, event)
            
            self.state_manager.subscribe_to_events(tab_id, tab_event_handler)
            
        return success
    
    def activate_tab(self, tab_id: str) -> bool:
        """🔄 Activar tab específico"""
        if tab_id not in self.state_manager.tab_states:
            print(f"❌ Tab {tab_id} not found")
            return False
        
        start_time = time.time()
        
        try:
            # Deactivate current tab
            if self.active_tab and self.active_tab != tab_id:
                self.state_manager.update_tab_state(self.active_tab, TabState.INACTIVE)
            
            # Activate new tab
            self.state_manager.update_tab_state(tab_id, TabState.ACTIVE)
            self.active_tab = tab_id
            
            # Update history
            if tab_id not in self.tab_history or self.tab_history[-1] != tab_id:
                self.tab_history.append(tab_id)
                if len(self.tab_history) > 50:  # Limit history
                    self.tab_history = self.tab_history[-25:]
            
            # Update performance metrics
            switch_time = (time.time() - start_time) * 1000  # ms
            self.performance_metrics["tab_switches"] += 1
            self.performance_metrics["last_switch_time"] = switch_time
            
            # Calculate average switch time
            total_switches = self.performance_metrics["tab_switches"]
            current_avg = self.performance_metrics["average_switch_time"]
            new_avg = ((current_avg * (total_switches - 1)) + switch_time) / total_switches
            self.performance_metrics["average_switch_time"] = new_avg
            
            if self.logger:
                self.logger.info(f"Tab activated: {tab_id}", "tab_activation")
            
            print(f"✅ Tab activated: {tab_id} ({switch_time:.2f}ms)")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error activating tab {tab_id}: {e}", "tab_activation")
            
            print(f"❌ Error activating tab {tab_id}: {e}")
            return False
    
    def get_tab_data(self, tab_id: str, key: str, default: Any = None) -> Any:
        """📖 Obtener datos específicos de tab"""
        if tab_id in self.state_manager.tab_states:
            tab_info = self.state_manager.tab_states[tab_id]
            return tab_info.data_cache.get(key, default)
        return default
    
    def set_tab_data(self, tab_id: str, key: str, value: Any) -> bool:
        """💾 Establecer datos específicos de tab"""
        if tab_id in self.state_manager.tab_states:
            tab_info = self.state_manager.tab_states[tab_id]
            tab_info.data_cache[key] = value
            tab_info.last_updated = datetime.now()
            return True
        return False
    
    def get_tab_config(self, tab_id: str, key: str, default: Any = None) -> Any:
        """⚙️ Obtener configuración de tab"""
        if tab_id in self.state_manager.tab_states:
            tab_info = self.state_manager.tab_states[tab_id]
            return tab_info.config.get(key, default)
        return default
    
    def set_tab_config(self, tab_id: str, key: str, value: Any) -> bool:
        """⚙️ Establecer configuración de tab"""
        if tab_id in self.state_manager.tab_states:
            tab_info = self.state_manager.tab_states[tab_id]
            tab_info.config[key] = value
            
            # Broadcast config change
            event = DashboardEvent(
                type=EventType.CONFIG_CHANGED,
                source_tab=tab_id,
                data={"key": key, "value": value}
            )
            self.state_manager._broadcast_event(event)
            return True
        return False
    
    def refresh_tab(self, tab_id: str) -> bool:
        """🔄 Refrescar tab específico"""
        if tab_id not in self.state_manager.tab_states:
            return False
        
        try:
            # Set updating state
            self.state_manager.update_tab_state(tab_id, TabState.UPDATING)
            
            # Broadcast refresh request
            event = DashboardEvent(
                type=EventType.REFRESH_REQUESTED,
                source_tab="coordinator",
                target_tab=tab_id
            )
            self.state_manager._broadcast_event(event)
            
            if self.logger:
                self.logger.info(f"Tab refresh requested: {tab_id}", "tab_refresh")
                
            return True
            
        except Exception as e:
            self.state_manager.update_tab_state(tab_id, TabState.ERROR, str(e))
            
            if self.logger:
                self.logger.error(f"Error refreshing tab {tab_id}: {e}", "tab_refresh")
            
            return False
    
    def refresh_all_tabs(self) -> Dict[str, bool]:
        """🔄 Refrescar todos los tabs registrados"""
        results = {}
        
        for tab_id in self.state_manager.tab_states.keys():
            results[tab_id] = self.refresh_tab(tab_id)
        
        return results
    
    def get_navigation_state(self) -> Dict[str, Any]:
        """🧭 Obtener estado de navegación actual"""
        return {
            "active_tab": self.active_tab,
            "tab_history": self.tab_history[-10:],  # Last 10
            "available_tabs": list(self.state_manager.tab_states.keys()),
            "tab_states": {tab_id: info.state.value for tab_id, info in self.state_manager.tab_states.items()}
        }
    
    def _handle_tab_event(self, tab_id: str, event: DashboardEvent):
        """🎯 Manejar eventos de tabs"""
        try:
            if event.type == EventType.ERROR_OCCURRED:
                error_msg = event.data.get("error_message", "Unknown error")
                self.state_manager.update_tab_state(tab_id, TabState.ERROR, error_msg)
                
                if self.logger:
                    self.logger.error(f"Tab {tab_id} error: {error_msg}", "tab_error")
                    
            elif event.type == EventType.DATA_UPDATED:
                self.performance_metrics["total_updates"] += 1
                
        except Exception as e:
            print(f"❌ Error handling tab event: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """📊 Obtener métricas de performance"""
        return {
            **self.performance_metrics,
            "system_status": self.state_manager.get_system_status(),
            "timestamp": datetime.now().isoformat()
        }
    
    def export_state(self) -> Dict[str, Any]:
        """💾 Exportar estado completo para persistencia"""
        return {
            "coordinator": {
                "active_tab": self.active_tab,
                "tab_history": self.tab_history,
                "performance_metrics": self.performance_metrics
            },
            "state_manager": self.state_manager.get_system_status(),
            "export_timestamp": datetime.now().isoformat()
        }


# Global coordinator instance
_tab_coordinator = None

def get_tab_coordinator(dashboard_core: Optional[Any] = None) -> TabCoordinator:
    """🌍 Obtener instancia global del coordinador (singleton pattern)"""
    global _tab_coordinator
    
    if _tab_coordinator is None:
        _tab_coordinator = TabCoordinator(dashboard_core)
        
    return _tab_coordinator


def register_default_tabs(coordinator: TabCoordinator) -> Dict[str, bool]:
    """📝 Registrar tabs por defecto del sistema"""
    default_tabs = [
        ("overview", "System Overview", "System overview and status"),
        ("metrics", "Performance Metrics", "System performance monitoring"),  
        ("trading", "Trading Status", "Real-time trading operations"),
        ("patterns", "Pattern Analysis", "ICT pattern detection"),
        ("market_structure", "Market Structure", "Market structure analysis"),
        ("order_blocks", "Order Blocks", "Order block identification"),
        ("fvg", "Fair Value Gaps", "FVG detection and analysis"),
        ("smart_money", "Smart Money", "Smart money concepts"),
    ]
    
    results = {}
    for tab_id, tab_name, description in default_tabs:
        # Create placeholder component
        component = type('PlaceholderTab', (), {
            'name': tab_name,
            'description': description,
            'tab_id': tab_id
        })()
        
        success = coordinator.register_tab(tab_id, tab_name, component)
        results[tab_id] = success
    
    return results


def get_coordinator_metrics() -> Dict[str, Any]:
    """📊 Obtener métricas del coordinador actual"""
    global _tab_coordinator
    
    if _tab_coordinator is None:
        return {"error": "TabCoordinator not initialized"}
    
    return _tab_coordinator.get_performance_metrics()


def initialize_tab_coordinator_integration(dashboard_core: Optional[Any] = None) -> bool:
    """🔧 Inicializar integración completa del TabCoordinator"""
    try:
        # Get coordinator instance
        coordinator = get_tab_coordinator(dashboard_core)
        
        # Register default tabs
        registration_results = register_default_tabs(coordinator)
        
        # Log results
        successful_registrations = sum(1 for success in registration_results.values() if success)
        total_tabs = len(registration_results)
        
        print(f"🎛️ Tab Coordinator integration initialized: {successful_registrations}/{total_tabs} tabs registered")
        
        if coordinator.logger:
            coordinator.logger.info(
                f"Tab Coordinator initialized with {successful_registrations} tabs",
                "tab_coordinator_init"
            )
        
        return successful_registrations > 0
        
    except Exception as e:
        print(f"❌ Error initializing TabCoordinator integration: {e}")
        return False


def setup_production_tabs_ecosystem():
    """🏭 Configurar ecosistema completo de tabs para producción"""
    try:
        # Obtener coordinador global
        coordinator = get_tab_coordinator()
        
        # Registrar tabs base del sistema
        registration_results = register_default_tabs(coordinator)
        
        # Cargar tabs reales desde el directorio
        from pathlib import Path
        tabs_dir = Path(__file__).parent / "tabs"
        
        real_tabs = {}
        
        # Intentar cargar tabs reales
        if tabs_dir.exists():
            for tab_file in tabs_dir.glob("*_tab*.py"):
                if "enterprise" in tab_file.stem:
                    try:
                        # Import dinámico del tab
                        tab_name = tab_file.stem
                        module_name = f"tabs.{tab_name}"
                        
                        import importlib
                        tab_module = importlib.import_module(module_name, package="core")
                        
                        # Buscar factory function o clase principal
                        if hasattr(tab_module, f"create_{tab_name}"):
                            factory_func = getattr(tab_module, f"create_{tab_name}")
                            tab_instance = factory_func()
                            real_tabs[tab_name] = tab_instance
                            
                            print(f"✅ Loaded real tab: {tab_name}")
                            
                    except Exception as e:
                        print(f"⚠️ Could not load tab {tab_file.stem}: {e}")
        
        # Persistir estado del coordinador
        state_dir = Path(__file__).parent.parent.parent / "04-DATA" / "coordinator_state"
        state_dir.mkdir(parents=True, exist_ok=True)
        
        export_data = coordinator.export_state()
        
        import json
        from datetime import datetime
        
        state_file = state_dir / "coordinator_export.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
            
        # Activar tab principal
        if coordinator.state_manager.tab_states:
            main_tab = list(coordinator.state_manager.tab_states.keys())[0]
            coordinator.activate_tab(main_tab)
        
        print(f"✅ Production tabs ecosystem ready")
        print(f"📊 Registered tabs: {len(registration_results)}")
        print(f"🔌 Real tabs loaded: {len(real_tabs)}")
        print(f"💾 State exported to: {state_file}")
        
        return coordinator, real_tabs, export_data
        
    except Exception as e:
        print(f"❌ Production tabs ecosystem setup failed: {e}")
        return None, {}, {}


if __name__ == "__main__":
    print("🏭 TabCoordinator - Production setup...")
    coordinator, real_tabs, state = setup_production_tabs_ecosystem()
    
    if coordinator:
        # Mostrar métricas del sistema
        metrics = coordinator.get_performance_metrics()
        print(f"📈 Performance metrics:")
        print(f"  - Tab switches: {metrics['tab_switches']}")
        print(f"  - Total updates: {metrics['total_updates']}")
        print(f"  - Average switch time: {metrics['average_switch_time']:.2f}ms")
        
        # Mostrar estado de navegación
        nav_state = coordinator.get_navigation_state()
        print(f"🧭 Navigation state:")
        print(f"  - Active tab: {nav_state['active_tab']}")
        print(f"  - Available tabs: {nav_state['available_tabs']}")
        
        print("✅ TabCoordinator production system ready")
    else:
        print("❌ TabCoordinator production setup failed")