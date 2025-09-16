#!/usr/bin/env python3
"""
🎯 DASHBOARD ENGINE ENTERPRISE BRIDGE
====================================

Puente entre el sistema de validación (01-CORE) y el dashboard engine (09-DASHBOARD).
Este módulo permite a los sistemas core acceder al DashboardEngine sin duplicar código.

Optimizado para cuentas reales sin type: ignore.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Agregar path al dashboard
dashboard_path = Path(__file__).parent.parent.parent / "09-DASHBOARD"
if str(dashboard_path) not in sys.path:
    sys.path.insert(0, str(dashboard_path))

# Logger enterprise
from protocols.unified_logging import get_unified_logger

logger = get_unified_logger("dashboard_bridge")

try:
    # Import del DashboardEngine real del dashboard
    from core.dashboard_engine import DashboardEngine as _DashboardEngine, DashboardState
    DASHBOARD_ENGINE_AVAILABLE = True
    logger.info("✅ DashboardEngine importado exitosamente", "dashboard_bridge")
    
except ImportError as e:
    logger.warning(f"⚠️ DashboardEngine no disponible: {e}", "dashboard_bridge")
    DASHBOARD_ENGINE_AVAILABLE = False
    _DashboardEngine = None
    DashboardState = None

class DashboardEngine:
    """🎯 Proxy Enterprise del Dashboard Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializar DashboardEngine enterprise"""
        self.config = config
        self.logger = get_unified_logger("dashboard_engine_proxy")
        
        if DASHBOARD_ENGINE_AVAILABLE and _DashboardEngine:
            try:
                # Usar el DashboardEngine real
                self._engine = _DashboardEngine(config)
                self.logger.info("✅ DashboardEngine real inicializado", "dashboard_engine_proxy")
                
                # Exponer métodos principales
                self.state = getattr(self._engine, 'state', None)
                self.start = getattr(self._engine, 'start', self._no_op)
                self.stop = getattr(self._engine, 'stop', self._no_op)
                self.update = getattr(self._engine, 'update', self._no_op)
                self.get_state = getattr(self._engine, 'get_state', self._get_default_state)
                
            except Exception as e:
                self.logger.error(f"❌ Error inicializando DashboardEngine real: {e}", "dashboard_engine_proxy")
                self._engine = None
                self._initialize_enterprise_fallback()
        else:
            self.logger.warning("⚠️ DashboardEngine no disponible, usando enterprise fallback", "dashboard_engine_proxy")
            self._engine = None
            self._initialize_enterprise_fallback()
    
    def _initialize_enterprise_fallback(self):
        """Inicializar fallback enterprise (sin mocks)"""
        self.logger.info("🚀 Inicializando DashboardEngine Enterprise Fallback", "dashboard_engine_proxy")
        
        # Estado enterprise mínimo
        self.state = self._create_enterprise_state()
        self.start = self._start_enterprise
        self.stop = self._stop_enterprise
        self.update = self._update_enterprise
        self.get_state = self._get_enterprise_state
        
        # Componentes enterprise
        self.components = {}
        self.event_handlers = {}
        self.is_running = False
        
        self.logger.info("✅ DashboardEngine Enterprise Fallback listo", "dashboard_engine_proxy")
    
    def _create_enterprise_state(self) -> Dict[str, Any]:
        """Crear estado enterprise básico"""
        return {
            'is_running': False,
            'last_update': None,
            'error_count': 0,
            'update_count': 0,
            'active_alerts': [],
            'performance_metrics': {},
            'engine_type': 'enterprise_fallback',
            'initialized_at': datetime.now().isoformat()
        }
    
    def _start_enterprise(self) -> bool:
        """Iniciar engine enterprise"""
        try:
            self.is_running = True
            if self.state:
                self.state['is_running'] = True
                self.state['last_update'] = datetime.now().isoformat()
            self.logger.info("🚀 DashboardEngine Enterprise iniciado", "dashboard_engine_proxy")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error iniciando engine: {e}", "dashboard_engine_proxy")
            return False
    
    def _stop_enterprise(self) -> bool:
        """Detener engine enterprise"""
        try:
            self.is_running = False
            if self.state:
                self.state['is_running'] = False
            self.logger.info("🛑 DashboardEngine Enterprise detenido", "dashboard_engine_proxy")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error deteniendo engine: {e}", "dashboard_engine_proxy")
            return False
    
    def _update_enterprise(self, data: Optional[Dict[str, Any]] = None) -> bool:
        """Actualizar estado enterprise"""
        try:
            if self.state:
                self.state['update_count'] += 1
                self.state['last_update'] = datetime.now().isoformat()
                
                if data:
                    self.state['performance_metrics'].update(data)
                
                self.logger.debug(f"📊 Estado actualizado: update #{self.state['update_count']}", 
                                "dashboard_engine_proxy")
            return True
        except Exception as e:
            if self.state:
                self.state['error_count'] += 1
            self.logger.error(f"❌ Error actualizando estado: {e}", "dashboard_engine_proxy")
            return False
    
    def _get_enterprise_state(self) -> Dict[str, Any]:
        """Obtener estado enterprise"""
        if not self.state:
            self.state = self._get_default_state()
        
        return self.state.copy() if self.state else {}
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Estado por defecto"""
        return {
            'is_running': False,
            'components': {},
            'performance_metrics': {}
        }
    
    def _no_op(self, *args, **kwargs) -> bool:
        """No operation"""
        return True
    
    def add_component(self, name: str, component: Any) -> bool:
        """Agregar componente al engine"""
        try:
            if not hasattr(self, 'components') or not self.components:
                self.components = {}
            
            self.components[name] = component
            self.logger.info(f"✅ Componente '{name}' agregado", "dashboard_engine_proxy")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error agregando componente '{name}': {e}", "dashboard_engine_proxy")
            return False
    
    def get_component(self, name: str) -> Optional[Any]:
        """Obtener componente del engine"""
        if not hasattr(self, 'components') or not self.components:
            return None
        return self.components.get(name)
    
    def is_healthy(self) -> bool:
        """Verificar si el engine está saludable"""
        return (
            hasattr(self, 'state') and
            isinstance(self.state, dict) and
            self.state.get('error_count', 0) < 10
        )

# Factory function enterprise
def create_dashboard_engine(config: Dict[str, Any]) -> DashboardEngine:
    """Factory para crear DashboardEngine enterprise"""
    return DashboardEngine(config)

# Exportar para compatibilidad
__all__ = ['DashboardEngine', 'DashboardState', 'create_dashboard_engine']