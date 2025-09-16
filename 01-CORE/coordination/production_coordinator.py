#!/usr/bin/env python3
"""
Production Coordinator - ICT Engine v6.0 Enterprise
==================================================

Coordinador central para el sistema de trading en producción.
Gestiona la inicialización, estado y sincronización de todos los módulos críticos.

Características:
✅ Inicialización ordenada de componentes
✅ Monitoreo de salud del sistema
✅ Coordinación de recursos compartidos
✅ Recuperación automática de fallos
✅ Métricas centralizadas de producción

Autor: ICT Engine v6.0 Team
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Protocol
import json

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("ProductionCoordinator", LogLevel.INFO)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ProductionCoordinator")

# System State Management
class SystemState(Enum):
    """Estados del sistema de producción"""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    EMERGENCY_STOP = "emergency_stop"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"

class HealthStatus(Enum):
    """Estados de salud de componentes"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"

@dataclass
class ComponentHealth:
    """Información de salud de un componente"""
    component_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    last_check: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3

class ComponentProtocol(Protocol):
    """Protocolo que deben implementar todos los componentes gestionados"""
    
    def initialize(self) -> bool:
        """Inicializar componente"""
        ...
    
    def start(self) -> bool:
        """Iniciar componente"""
        ...
    
    def stop(self) -> bool:
        """Detener componente"""
        ...
    
    def health_check(self) -> ComponentHealth:
        """Verificar salud del componente"""
        ...

@dataclass
class ProductionMetrics:
    """Métricas centralizadas de producción"""
    uptime_seconds: float = 0.0
    total_trades_executed: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    system_errors: int = 0
    recovery_events: int = 0
    last_heartbeat: Optional[datetime] = None
    
    # Performance metrics
    avg_execution_time_ms: float = 0.0
    peak_memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Trading metrics
    current_drawdown_percent: float = 0.0
    max_drawdown_percent: float = 0.0
    profit_factor: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para persistencia"""
        return {
            'uptime_seconds': self.uptime_seconds,
            'total_trades_executed': self.total_trades_executed,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'system_errors': self.system_errors,
            'recovery_events': self.recovery_events,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'peak_memory_usage_mb': self.peak_memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'current_drawdown_percent': self.current_drawdown_percent,
            'max_drawdown_percent': self.max_drawdown_percent,
            'profit_factor': self.profit_factor,
        }

class ProductionCoordinator:
    """
    Coordinador central del sistema de trading en producción
    
    Responsabilidades:
    - Gestión del ciclo de vida de componentes
    - Monitoreo de salud del sistema
    - Coordinación de recursos compartidos
    - Recuperación automática de fallos
    - Métricas centralizadas
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.state = SystemState.STOPPED
        self.start_time: Optional[datetime] = None
        
        # Component management
        self.components: Dict[str, ComponentProtocol] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        self.initialization_order: List[str] = []
        
        # Threading and sync
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ProdCoord")
        self._shutdown_event = threading.Event()
        
        # Monitoring
        self._monitor_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        
        # Metrics
        self.metrics = ProductionMetrics()
        self._metrics_lock = threading.Lock()
        
        # Callbacks
        self._state_callbacks: List[Callable[[SystemState, SystemState], None]] = []
        self._health_callbacks: List[Callable[[str, ComponentHealth], None]] = []
        
        # Persistence
        self._setup_persistence()
        
        logger.info("ProductionCoordinator initialized", "INIT")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'monitoring_interval_seconds': 10.0,
            'heartbeat_interval_seconds': 5.0,
            'health_check_timeout_seconds': 30.0,
            'auto_recovery_enabled': True,
            'max_recovery_attempts': 3,
            'shutdown_timeout_seconds': 30.0,
            'metrics_persistence_interval': 60.0,
            'emergency_stop_on_critical_failure': True,
            'component_startup_timeout_seconds': 120.0,
        }
    
    def _setup_persistence(self):
        """Configurar persistencia de métricas y estado"""
        self.metrics_file = Path("data/system_metrics.json")
        self.state_file = Path("data/system_status.json")
        
        # Crear directorios si no existen
        for file_path in [self.metrics_file, self.state_file]:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar métricas anteriores si existen
        self._load_previous_metrics()
    
    def _load_previous_metrics(self):
        """Cargar métricas de ejecución anterior"""
        try:
            if self.metrics_file.exists():
                data = json.loads(self.metrics_file.read_text(encoding='utf-8'))
                # Solo cargar métricas acumulativas
                self.metrics.max_drawdown_percent = data.get('max_drawdown_percent', 0.0)
                logger.info("Previous metrics loaded successfully", "METRICS")
        except Exception as e:
            logger.warning(f"Could not load previous metrics: {e}", "METRICS")
    
    # Component Registration and Management
    def register_component(self, name: str, component: ComponentProtocol, 
                          initialization_priority: int = 100) -> bool:
        """
        Registrar componente en el coordinador
        
        Args:
            name: Nombre único del componente
            component: Instancia del componente
            initialization_priority: Prioridad de inicialización (menor = antes)
            
        Returns:
            bool: True si se registró exitosamente
        """
        with self._lock:
            if name in self.components:
                logger.warning(f"Component {name} already registered", "REGISTER")
                return False
            
            self.components[name] = component
            self.component_health[name] = ComponentHealth(
                component_name=name,
                max_recovery_attempts=self.config['max_recovery_attempts']
            )
            
            # Insertar en orden de prioridad
            inserted = False
            for i, existing_name in enumerate(self.initialization_order):
                existing_priority = getattr(self.components[existing_name], 'priority', 100)
                if initialization_priority < existing_priority:
                    self.initialization_order.insert(i, name)
                    inserted = True
                    break
            
            if not inserted:
                self.initialization_order.append(name)
            
            logger.info(f"Component {name} registered with priority {initialization_priority}", "REGISTER")
            return True
    
    def unregister_component(self, name: str) -> bool:
        """Desregistrar componente"""
        with self._lock:
            if name not in self.components:
                return False
            
            # Stop component if running
            try:
                self.components[name].stop()
            except Exception as e:
                logger.warning(f"Error stopping component {name}: {e}", "UNREGISTER")
            
            del self.components[name]
            del self.component_health[name]
            if name in self.initialization_order:
                self.initialization_order.remove(name)
            
            logger.info(f"Component {name} unregistered", "UNREGISTER")
            return True
    
    # System Lifecycle Management
    def start_system(self) -> bool:
        """
        Iniciar todo el sistema de producción
        
        Returns:
            bool: True si se inició exitosamente
        """
        with self._lock:
            if self.state != SystemState.STOPPED:
                logger.warning(f"System already in state: {self.state}", "START")
                return False
            
            logger.info("Starting production system...", "START")
            self._transition_state(SystemState.INITIALIZING)
            
            try:
                # Phase 1: Initialize all components
                self._transition_state(SystemState.INITIALIZING)
                if not self._initialize_components():
                    self._transition_state(SystemState.ERROR)
                    return False
                
                # Phase 2: Start components
                self._transition_state(SystemState.STARTING)
                if not self._start_components():
                    self._transition_state(SystemState.ERROR)
                    return False
                
                # Phase 3: Start monitoring
                self._start_monitoring()
                
                # Phase 4: System operational
                self.start_time = datetime.now()
                self._transition_state(SystemState.RUNNING)
                
                logger.info("Production system started successfully", "START")
                self._persist_state()
                return True
                
            except Exception as e:
                logger.error(f"System startup failed: {e}", "START")
                self._transition_state(SystemState.ERROR)
                return False
    
    def stop_system(self, emergency: bool = False) -> bool:
        """
        Detener el sistema de producción
        
        Args:
            emergency: Si es parada de emergencia
            
        Returns:
            bool: True si se detuvo exitosamente
        """
        with self._lock:
            if self.state == SystemState.STOPPED:
                logger.info("System already stopped", "STOP")
                return True
            
            if emergency:
                logger.warning("EMERGENCY STOP initiated", "STOP")
                self._transition_state(SystemState.EMERGENCY_STOP)
            else:
                logger.info("Graceful system shutdown initiated", "STOP")
                self._transition_state(SystemState.SHUTTING_DOWN)
            
            try:
                # Stop monitoring first
                self._shutdown_event.set()
                self._stop_monitoring()
                
                # Stop components in reverse order
                self._stop_components(emergency)
                
                # Final cleanup
                # ThreadPoolExecutor.shutdown in stdlib does not accept 'timeout'; emulate timed wait for emergency
                if emergency:
                    self._executor.shutdown(wait=False)
                    # Emulate a bounded wait loop for up to 5 seconds
                    import time as _t
                    end = _t.time() + 5.0
                    while _t.time() < end and len(getattr(self._executor, '_threads', [])) > 0:
                        _t.sleep(0.05)
                else:
                    # Graceful full wait
                    self._executor.shutdown(wait=True)
                
                self._transition_state(SystemState.STOPPED)
                
                # Persist final metrics
                self._persist_metrics()
                self._persist_state()
                
                logger.info("System stopped successfully", "STOP")
                return True
                
            except Exception as e:
                logger.error(f"System shutdown error: {e}", "STOP")
                self._transition_state(SystemState.ERROR)
                return False
    
    def _initialize_components(self) -> bool:
        """Inicializar componentes en orden de prioridad"""
        timeout = self.config['component_startup_timeout_seconds']
        
        for component_name in self.initialization_order:
            try:
                logger.info(f"Initializing component: {component_name}", "INIT")
                
                component = self.components[component_name]
                
                # Inicializar con timeout
                future = self._executor.submit(component.initialize)
                if future.result(timeout=timeout):
                    logger.info(f"Component {component_name} initialized successfully", "INIT")
                else:
                    logger.error(f"Component {component_name} initialization failed", "INIT")
                    return False
                    
            except Exception as e:
                logger.error(f"Error initializing component {component_name}: {e}", "INIT")
                return False
        
        return True
    
    def _start_components(self) -> bool:
        """Iniciar componentes en orden"""
        for component_name in self.initialization_order:
            try:
                logger.info(f"Starting component: {component_name}", "START")
                
                component = self.components[component_name]
                if component.start():
                    logger.info(f"Component {component_name} started successfully", "START")
                else:
                    logger.error(f"Component {component_name} start failed", "START")
                    return False
                    
            except Exception as e:
                logger.error(f"Error starting component {component_name}: {e}", "START")
                return False
        
        return True
    
    def _stop_components(self, emergency: bool = False) -> None:
        """Detener componentes en orden inverso"""
        for component_name in reversed(self.initialization_order):
            try:
                logger.info(f"Stopping component: {component_name}", "STOP")
                
                component = self.components[component_name]
                component.stop()
                
                logger.info(f"Component {component_name} stopped", "STOP")
                
            except Exception as e:
                logger.warning(f"Error stopping component {component_name}: {e}", "STOP")
                if not emergency:  # En emergencia, continuar sin esperar
                    time.sleep(0.1)
    
    # State Management
    def _transition_state(self, new_state: SystemState) -> None:
        """Transición de estado con callbacks"""
        old_state = self.state
        self.state = new_state
        
        logger.info(f"State transition: {old_state.value} -> {new_state.value}", "STATE")
        
        # Ejecutar callbacks de estado
        for callback in self._state_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.warning(f"State callback error: {e}", "STATE")
    
    def add_state_callback(self, callback: Callable[[SystemState, SystemState], None]) -> None:
        """Agregar callback para cambios de estado"""
        self._state_callbacks.append(callback)
    
    def add_health_callback(self, callback: Callable[[str, ComponentHealth], None]) -> None:
        """Agregar callback para cambios de salud"""
        self._health_callbacks.append(callback)
    
    # Monitoring
    def _start_monitoring(self) -> None:
        """Iniciar hilos de monitoreo"""
        self._shutdown_event.clear()
        
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="SystemMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name="SystemHeartbeat", 
            daemon=True
        )
        self._heartbeat_thread.start()
        
        logger.info("Monitoring threads started", "MONITOR")
    
    def _stop_monitoring(self) -> None:
        """Detener hilos de monitoreo"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5.0)
        
        logger.info("Monitoring threads stopped", "MONITOR")
    
    def _monitoring_loop(self) -> None:
        """Bucle principal de monitoreo"""
        interval = self.config['monitoring_interval_seconds']
        
        while not self._shutdown_event.is_set():
            try:
                self._perform_health_checks()
                self._check_system_health()
                self._update_metrics()
                self._persist_metrics_if_needed()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}", "MONITOR")
                time.sleep(interval)
    
    def _heartbeat_loop(self) -> None:
        """Bucle de heartbeat del sistema"""
        interval = self.config['heartbeat_interval_seconds']
        
        while not self._shutdown_event.is_set():
            try:
                with self._metrics_lock:
                    self.metrics.last_heartbeat = datetime.now()
                    if self.start_time:
                        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", "HEARTBEAT")
                time.sleep(interval)
    
    def _perform_health_checks(self) -> None:
        """Realizar chequeos de salud de todos los componentes"""
        timeout = self.config['health_check_timeout_seconds']
        
        for component_name, component in self.components.items():
            try:
                future = self._executor.submit(component.health_check)
                health = future.result(timeout=timeout)
                
                old_health = self.component_health.get(component_name)
                self.component_health[component_name] = health
                
                # Trigger callbacks if health changed
                if old_health and old_health.status != health.status:
                    for callback in self._health_callbacks:
                        try:
                            callback(component_name, health)
                        except Exception as e:
                            logger.warning(f"Health callback error: {e}", "HEALTH")
                
            except Exception as e:
                # Component health check failed
                health = ComponentHealth(
                    component_name=component_name,
                    status=HealthStatus.UNAVAILABLE,
                    error_message=str(e)
                )
                self.component_health[component_name] = health
                logger.warning(f"Health check failed for {component_name}: {e}", "HEALTH")
    
    def _check_system_health(self) -> None:
        """Evaluar salud general del sistema"""
        critical_count = sum(1 for h in self.component_health.values() 
                           if h.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for h in self.component_health.values() 
                          if h.status == HealthStatus.WARNING)
        unavailable_count = sum(1 for h in self.component_health.values() 
                              if h.status == HealthStatus.UNAVAILABLE)
        
        # Decidir si cambiar estado del sistema
        if critical_count > 0 or unavailable_count > len(self.components) // 2:
            if self.state == SystemState.RUNNING:
                logger.warning(f"System degraded: {critical_count} critical, {unavailable_count} unavailable", "HEALTH")
                self._transition_state(SystemState.DEGRADED)
                
                if self.config['emergency_stop_on_critical_failure'] and critical_count > 1:
                    logger.error("Multiple critical failures - initiating emergency stop", "HEALTH")
                    self.stop_system(emergency=True)
        
        elif warning_count > 0:
            if self.state == SystemState.RUNNING:
                logger.info(f"System has warnings: {warning_count} components", "HEALTH")
        
        elif self.state == SystemState.DEGRADED:
            # System recovered
            logger.info("System health recovered", "HEALTH")
            self._transition_state(SystemState.RUNNING)
    
    def _update_metrics(self) -> None:
        """Actualizar métricas del sistema"""
        try:
            import psutil
            
            with self._metrics_lock:
                # System metrics
                self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.metrics.peak_memory_usage_mb = max(
                    self.metrics.peak_memory_usage_mb, 
                    memory.used / 1024 / 1024
                )
                
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.warning(f"Error updating system metrics: {e}", "METRICS")
    
    # Persistence
    def _persist_metrics_if_needed(self) -> None:
        """Persistir métricas si es necesario"""
        now = time.time()
        if hasattr(self, '_last_metrics_persist'):
            if now - self._last_metrics_persist < self.config['metrics_persistence_interval']:
                return
        
        self._persist_metrics()
        self._last_metrics_persist = now
    
    def _persist_metrics(self) -> None:
        """Persistir métricas actuales"""
        try:
            with self._metrics_lock:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'system_state': self.state.value,
                    'metrics': self.metrics.to_dict(),
                    'component_health': {
                        name: {
                            'status': health.status.value,
                            'last_check': health.last_check.isoformat(),
                            'metrics': health.metrics,
                            'error_message': health.error_message,
                            'recovery_attempts': health.recovery_attempts
                        }
                        for name, health in self.component_health.items()
                    }
                }
            
            # Atomic write
            temp_file = self.metrics_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
            temp_file.replace(self.metrics_file)
            
        except Exception as e:
            logger.warning(f"Error persisting metrics: {e}", "METRICS")
    
    def _persist_state(self) -> None:
        """Persistir estado actual del sistema"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'system_state': self.state.value,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'component_count': len(self.components),
                'healthy_components': sum(1 for h in self.component_health.values() 
                                        if h.status == HealthStatus.HEALTHY)
            }
            
            # Atomic write
            temp_file = self.state_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
            temp_file.replace(self.state_file)
            
        except Exception as e:
            logger.warning(f"Error persisting state: {e}", "STATE")
    
    # Public API
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        with self._metrics_lock:
            return {
                'system_state': self.state.value,
                'uptime_seconds': self.metrics.uptime_seconds,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'component_count': len(self.components),
                'healthy_components': sum(1 for h in self.component_health.values() 
                                        if h.status == HealthStatus.HEALTHY),
                'warning_components': sum(1 for h in self.component_health.values() 
                                        if h.status == HealthStatus.WARNING),
                'critical_components': sum(1 for h in self.component_health.values() 
                                         if h.status == HealthStatus.CRITICAL),
                'metrics': self.metrics.to_dict(),
                'last_heartbeat': self.metrics.last_heartbeat.isoformat() if self.metrics.last_heartbeat else None
            }
    
    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Obtener salud de un componente específico"""
        return self.component_health.get(component_name)
    
    def emergency_stop(self) -> bool:
        """Parada de emergencia del sistema"""
        logger.error("EMERGENCY STOP TRIGGERED", "EMERGENCY")
        return self.stop_system(emergency=True)
    
    @contextmanager
    def production_context(self):
        """Context manager para operación en producción"""
        try:
            if not self.start_system():
                raise RuntimeError("Failed to start production system")
            yield self
        finally:
            self.stop_system()

# Global instance management
_global_coordinator: Optional[ProductionCoordinator] = None

def get_production_coordinator() -> ProductionCoordinator:
    """Obtener instancia global del coordinador de producción"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = ProductionCoordinator()
    return _global_coordinator

def set_production_coordinator(coordinator: ProductionCoordinator) -> None:
    """Establecer instancia global del coordinador"""
    global _global_coordinator
    _global_coordinator = coordinator

__all__ = [
    'ProductionCoordinator',
    'SystemState',
    'HealthStatus', 
    'ComponentHealth',
    'ComponentProtocol',
    'ProductionMetrics',
    'get_production_coordinator',
    'set_production_coordinator'
]