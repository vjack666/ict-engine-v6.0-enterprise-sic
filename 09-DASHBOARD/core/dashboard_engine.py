#!/usr/bin/env python3
"""
🎯 DASHBOARD ENGINE - MOTOR PRINCIPAL DEL DASHBOARD
=================================================

Motor principal que coordina todos los componentes del dashboard ICT.
Basado en funcionalidades de los tests existentes.

Funcionalidades:
- ✅ Gestión de estado del dashboard
- ✅ Coordinación de componentes
- ✅ Manejo de eventos
- ✅ Actualización de datos
- ✅ Gestión de alertas

Versión: v6.1.0-enterprise
"""

import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque

@dataclass
class DashboardState:
    """Estado del dashboard"""
    is_running: bool = False
    last_update: Optional[datetime] = None
    error_count: int = 0
    update_count: int = 0
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class DashboardEngine:
    """🎯 Motor principal del dashboard"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar motor del dashboard
        
        Args:
            config: Configuración del dashboard
        """
        self.config = config
        self.state = DashboardState()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.update_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Métricas de rendimiento
        self.performance_history = deque(maxlen=100)
        self.error_history = deque(maxlen=50)
        
        # Alertas del sistema
        self.alert_queue = deque(maxlen=100)
        
    def initialize(self):
        """🔧 Inicializar motor del dashboard"""
        try:
            print("🔧 Inicializando Dashboard Engine...")
            
            # Configurar evento handlers por defecto
            self._setup_default_handlers()
            
            # Iniciar métricas de rendimiento
            self._start_performance_monitoring()
            
            self.state.is_running = True
            print("✅ Dashboard Engine inicializado correctamente")
            
        except Exception as e:
            self._handle_error(f"Error inicializando dashboard engine: {e}")
            raise
    
    def _setup_default_handlers(self):
        """Configurar handlers por defecto"""
        self.register_event_handler('data_update', self._on_data_update)
        self.register_event_handler('error', self._on_error)
        self.register_event_handler('alert', self._on_alert)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Registrar handler para eventos
        
        Args:
            event_type: Tipo de evento
            handler: Función handler
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, data: Any = None):
        """
        Emitir evento
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self._handle_error(f"Error en handler {event_type}: {e}")
    
    def _on_data_update(self, data):
        """Handler para actualización de datos"""
        self.state.last_update = datetime.now(timezone.utc)
        self.state.update_count += 1
        
        # Calcular métricas de rendimiento
        self._update_performance_metrics()
    
    def _on_error(self, error_data):
        """Handler para errores"""
        self.state.error_count += 1
        self.error_history.append({
            'timestamp': datetime.now(timezone.utc),
            'error': error_data,
            'context': 'dashboard_engine'
        })
    
    def _on_alert(self, alert_data):
        """Handler para alertas"""
        alert = {
            'timestamp': datetime.now(timezone.utc),
            'type': alert_data.get('type', 'info'),
            'message': alert_data.get('message', ''),
            'severity': alert_data.get('severity', 'low'),
            'source': alert_data.get('source', 'system')
        }
        
        self.alert_queue.append(alert)
        self.state.active_alerts.append(alert)
        
        # Limpiar alertas antiguas (más de 1 hora)
        self._cleanup_old_alerts()
    
    def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas"""
        now = datetime.now(timezone.utc)
        self.state.active_alerts = [
            alert for alert in self.state.active_alerts
            if (now - alert['timestamp']).total_seconds() < 3600
        ]
    
    def _start_performance_monitoring(self):
        """Iniciar monitoreo de rendimiento"""
        self.performance_start_time = time.time()
        
    def _update_performance_metrics(self):
        """Actualizar métricas de rendimiento"""
        current_time = time.time()
        
        # Actualizar métricas de rendimiento individualmente para evitar errores de tipo
        self.state.performance_metrics['uptime_seconds'] = current_time - self.performance_start_time
        self.state.performance_metrics['updates_per_minute'] = self.state.update_count / max(1, (current_time - self.performance_start_time) / 60)
        self.state.performance_metrics['error_rate'] = self.state.error_count / max(1, self.state.update_count)
        self.state.performance_metrics['memory_usage_mb'] = self._get_memory_usage()
        self.state.performance_metrics['last_update_timestamp'] = self.state.last_update.isoformat() if self.state.last_update else None
        
        # Agregar a historial
        self.performance_history.append({
            'timestamp': datetime.now(timezone.utc),
            'metrics': self.state.performance_metrics.copy()
        })
    
    def _get_memory_usage(self) -> float:
        """Obtener uso de memoria"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0
    
    def _handle_error(self, error_message: str):
        """Manejar errores del motor"""
        print(f"❌ {error_message}")
        self.emit_event('error', error_message)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            'state': {
                'is_running': self.state.is_running,
                'last_update': self.state.last_update.isoformat() if self.state.last_update else None,
                'update_count': self.state.update_count,
                'error_count': self.state.error_count
            },
            'performance': self.state.performance_metrics,
            'alerts': {
                'active_count': len(self.state.active_alerts),
                'recent_alerts': list(self.alert_queue)[-10:] if self.alert_queue else []
            },
            'config': self.config
        }
    
    def create_alert(self, alert_type: str, message: str, severity: str = 'info', source: str = 'system'):
        """
        Crear nueva alerta
        
        Args:
            alert_type: Tipo de alerta
            message: Mensaje de la alerta
            severity: Severidad (low/medium/high/critical)
            source: Fuente de la alerta
        """
        self.emit_event('alert', {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'source': source
        })
    
    def cleanup(self):
        """🧹 Limpiar recursos del motor"""
        try:
            self.state.is_running = False
            self.stop_event.set()
            
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=5)
            
            print("✅ Dashboard Engine limpiado correctamente")
            
        except Exception as e:
            print(f"⚠️ Error limpiando dashboard engine: {e}")
