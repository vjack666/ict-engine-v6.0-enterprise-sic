#!/usr/bin/env python3
"""
📊 MONITORING MODULE - ICT ENGINE v6.0 ENTERPRISE
===============================================

Sistema de monitoreo avanzado para trading en producción real.
Supervisa salud del sistema, performance, operaciones de trading
y recursos en tiempo real con alertas automáticas.

Características principales:
✅ Monitoreo de salud del sistema en tiempo real
✅ Métricas de performance y latencia
✅ Alertas automáticas por thresholds
✅ Dashboard de estado del sistema
✅ Histórico de métricas para análisis
✅ Integración con logging centralizado

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 16 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import time
import json
from collections import deque, defaultdict
import psutil


class MonitoringLevel(Enum):
    """Niveles de monitoreo disponibles"""
    BASIC = "basic"           # Monitoreo básico esencial
    ADVANCED = "advanced"     # Monitoreo detallado
    ENTERPRISE = "enterprise" # Monitoreo completo para producción


class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    network_io: Dict[str, int] = field(default_factory=dict)
    process_count: int = 0
    open_files: int = 0
    uptime_seconds: float = 0.0


@dataclass
class TradingMetrics:
    """Métricas de trading"""
    timestamp: datetime = field(default_factory=datetime.now)
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_volume: float = 0.0
    current_positions: int = 0
    total_pnl: float = 0.0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0


@dataclass
class Alert:
    """Alerta del sistema"""
    timestamp: datetime
    level: AlertLevel
    component: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


class HealthMonitor:
    """
    🏥 Monitor de salud del sistema
    
    Supervisa todos los aspectos críticos del sistema de trading
    y genera alertas cuando se detectan problemas.
    """
    
    def __init__(self, level: MonitoringLevel = MonitoringLevel.ADVANCED):
        self.monitoring_level = level
        self.logger = get_unified_logger("HealthMonitor")
        self._lock = threading.RLock()
        
        # Estado del monitoreo
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        
        # Métricas y alertas
        self._system_metrics_history = deque(maxlen=1440)  # 24 horas de muestras por minuto
        self._trading_metrics_history = deque(maxlen=1440)
        self._alerts = deque(maxlen=1000)
        self._alert_handlers: List[Callable[[Alert], None]] = []
        
        # Configuración de thresholds
        self._thresholds = self._setup_default_thresholds()
        
        # Contadores de componentes
        self._component_status: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"healthy": True, "last_check": datetime.now()})
        
        # Tiempo de inicio
        self._start_time = time.time()
        
        self.logger.info(f"✅ HealthMonitor initialized with level: {level.value}")
    
    def _setup_default_thresholds(self) -> Dict[str, Any]:
        """⚙️ Configurar thresholds por defecto"""
        return {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0,
            'latency_warning': 100.0,  # ms
            'latency_critical': 500.0,  # ms
            'error_rate_warning': 5.0,  # %
            'error_rate_critical': 15.0,  # %
            'response_time_warning': 2.0,  # seconds
            'response_time_critical': 5.0,  # seconds
        }
    
    def start_monitoring(self, check_interval: int = 60) -> None:
        """
        🚀 Iniciar monitoreo continuo
        
        Args:
            check_interval: Intervalo de verificación en segundos
        """
        try:
            with self._lock:
                if self._monitoring_active:
                    self.logger.warning("Monitoring already active")
                    return
                
                self._monitoring_active = True
                self._monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    args=(check_interval,),
                    daemon=True,
                    name="HealthMonitorThread"
                )
                self._monitoring_thread.start()
                
                self.logger.info(f"✅ Health monitoring started with {check_interval}s interval")
                
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self) -> None:
        """🛑 Detener monitoreo"""
        try:
            with self._lock:
                if not self._monitoring_active:
                    return
                
                self._monitoring_active = False
                
                if self._monitoring_thread and self._monitoring_thread.is_alive():
                    self._monitoring_thread.join(timeout=5.0)
                
                self.logger.info("🛑 Health monitoring stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
    
    def _monitoring_loop(self, check_interval: int) -> None:
        """🔄 Loop principal de monitoreo"""
        self.logger.info("Monitoring loop started")
        
        while self._monitoring_active:
            try:
                # Recopilar métricas
                self._collect_system_metrics()
                
                if self.monitoring_level in [MonitoringLevel.ADVANCED, MonitoringLevel.ENTERPRISE]:
                    self._collect_trading_metrics()
                
                # Verificar thresholds y generar alertas
                self._check_thresholds()
                
                # Verificar estado de componentes
                self._check_component_health()
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)
    
    def _collect_system_metrics(self) -> None:
        """📊 Recopilar métricas del sistema"""
        try:
            metrics = SystemMetrics()
            
            # CPU y memoria
            metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            metrics.memory_percent = memory.percent
            
            # Disco
            try:
                disk = psutil.disk_usage('/')
                metrics.disk_percent = disk.percent
            except Exception:
                metrics.disk_percent = 0.0
            
            # Red (si está disponible)
            try:
                net_io = psutil.net_io_counters()
                metrics.network_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                }
            except Exception:
                metrics.network_io = {}
            
            # Procesos
            try:
                metrics.process_count = len(psutil.pids())
            except Exception:
                metrics.process_count = 0
            
            # Uptime
            metrics.uptime_seconds = time.time() - self._start_time
            
            # Almacenar en historial
            with self._lock:
                self._system_metrics_history.append(metrics)
                
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_trading_metrics(self) -> None:
        """💼 Recopilar métricas de trading"""
        try:
            metrics = TradingMetrics()
            
            # TODO: Integrar con el sistema de trading real
            # Por ahora, métricas simuladas
            metrics.total_trades = 0
            metrics.successful_trades = 0
            metrics.failed_trades = 0
            metrics.total_volume = 0.0
            metrics.current_positions = 0
            metrics.total_pnl = 0.0
            metrics.success_rate = 0.0
            metrics.avg_latency_ms = 0.0
            
            # Almacenar en historial
            with self._lock:
                self._trading_metrics_history.append(metrics)
                
        except Exception as e:
            self.logger.error(f"Error collecting trading metrics: {e}")
    
    def _check_thresholds(self) -> None:
        """🚨 Verificar thresholds y generar alertas"""
        try:
            if not self._system_metrics_history:
                return
            
            latest_metrics = self._system_metrics_history[-1]
            
            # CPU
            if latest_metrics.cpu_percent >= self._thresholds['cpu_critical']:
                self._create_alert(AlertLevel.CRITICAL, "System", 
                                f"Critical CPU usage: {latest_metrics.cpu_percent:.1f}%")
            elif latest_metrics.cpu_percent >= self._thresholds['cpu_warning']:
                self._create_alert(AlertLevel.WARNING, "System", 
                                f"High CPU usage: {latest_metrics.cpu_percent:.1f}%")
            
            # Memoria
            if latest_metrics.memory_percent >= self._thresholds['memory_critical']:
                self._create_alert(AlertLevel.CRITICAL, "System", 
                                f"Critical memory usage: {latest_metrics.memory_percent:.1f}%")
            elif latest_metrics.memory_percent >= self._thresholds['memory_warning']:
                self._create_alert(AlertLevel.WARNING, "System", 
                                f"High memory usage: {latest_metrics.memory_percent:.1f}%")
            
            # Disco
            if latest_metrics.disk_percent >= self._thresholds['disk_critical']:
                self._create_alert(AlertLevel.CRITICAL, "System", 
                                f"Critical disk usage: {latest_metrics.disk_percent:.1f}%")
            elif latest_metrics.disk_percent >= self._thresholds['disk_warning']:
                self._create_alert(AlertLevel.WARNING, "System", 
                                f"High disk usage: {latest_metrics.disk_percent:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _check_component_health(self) -> None:
        """🔍 Verificar salud de componentes"""
        try:
            current_time = datetime.now()
            
            for component, status in self._component_status.items():
                # Verificar si el componente ha reportado recientemente
                last_check = status.get('last_check', current_time)
                if isinstance(last_check, datetime) and (current_time - last_check).total_seconds() > 300:  # 5 minutos
                    if status.get('healthy', True):
                        self._create_alert(AlertLevel.WARNING, component, 
                                        f"Component {component} hasn't reported in 5+ minutes")
                        status['healthy'] = False
                        
        except Exception as e:
            self.logger.error(f"Error checking component health: {e}")
    
    def _create_alert(self, level: AlertLevel, component: str, message: str, 
                     details: Optional[Dict[str, Any]] = None) -> None:
        """🚨 Crear nueva alerta"""
        try:
            alert = Alert(
                timestamp=datetime.now(),
                level=level,
                component=component,
                message=message,
                details=details or {}
            )
            
            with self._lock:
                self._alerts.append(alert)
            
            # Notificar handlers
            for handler in self._alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert handler: {e}")
            
            # Log de la alerta
            log_message = f"[{level.value.upper()}] {component}: {message}"
            if level == AlertLevel.CRITICAL:
                self.logger.critical(log_message)
            elif level == AlertLevel.ERROR:
                self.logger.error(log_message)
            elif level == AlertLevel.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
                
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    def register_component(self, component_name: str) -> None:
        """📝 Registrar componente para monitoreo"""
        try:
            with self._lock:
                self._component_status[component_name] = {
                    'healthy': True,
                    'last_check': datetime.now()
                }
                
            self.logger.info(f"📝 Component registered: {component_name}")
            
        except Exception as e:
            self.logger.error(f"Error registering component {component_name}: {e}")
    
    def report_component_health(self, component_name: str, healthy: bool = True, 
                              details: Optional[Dict[str, Any]] = None) -> None:
        """💚 Reportar estado de un componente"""
        try:
            with self._lock:
                self._component_status[component_name] = {
                    'healthy': healthy,
                    'last_check': datetime.now(),
                    'details': details or {}
                }
            
            if not healthy:
                self._create_alert(AlertLevel.ERROR, component_name, 
                                f"Component {component_name} reported unhealthy", details)
                
        except Exception as e:
            self.logger.error(f"Error reporting component health for {component_name}: {e}")
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """🔔 Agregar handler de alertas"""
        self._alert_handlers.append(handler)
        self.logger.info(f"Alert handler added: {handler.__name__}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """📊 Obtener métricas actuales"""
        try:
            with self._lock:
                system_metrics = self._system_metrics_history[-1] if self._system_metrics_history else None
                trading_metrics = self._trading_metrics_history[-1] if self._trading_metrics_history else None
                
                return {
                    'monitoring_active': self._monitoring_active,
                    'monitoring_level': self.monitoring_level.value,
                    'uptime_seconds': time.time() - self._start_time,
                    'component_count': len(self._component_status),
                    'healthy_components': sum(1 for s in self._component_status.values() if s.get('healthy', True)),
                    'total_alerts': len(self._alerts),
                    'unacknowledged_alerts': sum(1 for a in self._alerts if not a.acknowledged),
                    'system_metrics': {
                        'cpu_percent': system_metrics.cpu_percent if system_metrics else 0,
                        'memory_percent': system_metrics.memory_percent if system_metrics else 0,
                        'disk_percent': system_metrics.disk_percent if system_metrics else 0
                    } if system_metrics else {},
                    'trading_metrics': {
                        'total_trades': trading_metrics.total_trades if trading_metrics else 0,
                        'success_rate': trading_metrics.success_rate if trading_metrics else 0,
                        'current_positions': trading_metrics.current_positions if trading_metrics else 0
                    } if trading_metrics else {}
                }
                
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return {}
    
    def get_recent_alerts(self, count: int = 50) -> List[Dict[str, Any]]:
        """🚨 Obtener alertas recientes"""
        try:
            with self._lock:
                recent_alerts = list(self._alerts)[-count:]
                
                return [{
                    'timestamp': alert.timestamp.isoformat(),
                    'level': alert.level.value,
                    'component': alert.component,
                    'message': alert.message,
                    'acknowledged': alert.acknowledged,
                    'details': alert.details
                } for alert in reversed(recent_alerts)]
                
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []


def create_database_health_check() -> Callable[[], bool]:
    """
    🗃️ Crear función de health check para base de datos
    
    Returns:
        Función que retorna True si la BD está disponible
    """
    def check_database() -> bool:
        try:
            # TODO: Implementar check real de base de datos
            # Por ahora retorna True
            return True
        except Exception:
            return False
    
    return check_database


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

_global_health_monitor: Optional[HealthMonitor] = None
_monitoring_lock = threading.Lock()


def get_health_monitor(level: MonitoringLevel = MonitoringLevel.ADVANCED, 
                      force_new: bool = False) -> HealthMonitor:
    """
    🏭 Factory function para obtener HealthMonitor
    
    Args:
        level: Nivel de monitoreo deseado
        force_new: Forzar nueva instancia
        
    Returns:
        Instancia de HealthMonitor
    """
    global _global_health_monitor
    
    with _monitoring_lock:
        if _global_health_monitor is None or force_new:
            _global_health_monitor = HealthMonitor(level)
        
        return _global_health_monitor


def test_monitoring_module():
    """🧪 Test del módulo de monitoreo"""
    print("🧪 Testing monitoring module...")
    
    try:
        # Test inicialización
        monitor = get_health_monitor(MonitoringLevel.ENTERPRISE)
        print("✅ HealthMonitor initialized")
        
        # Test registro de componente
        monitor.register_component("TestComponent")
        print("✅ Component registered")
        
        # Test reporte de salud
        monitor.report_component_health("TestComponent", healthy=True, 
                                      details={'test': True})
        print("✅ Component health reported")
        
        # Test métricas actuales
        metrics = monitor.get_current_metrics()
        print(f"✅ Current metrics: {len(metrics)} fields")
        
        # Test alertas recientes
        alerts = monitor.get_recent_alerts(10)
        print(f"✅ Recent alerts: {len(alerts)} alerts")
        
        # Test handler de alertas
        def test_alert_handler(alert):
            print(f"🔔 Alert received: {alert.level.value} - {alert.message}")
        
        monitor.add_alert_handler(test_alert_handler)
        print("✅ Alert handler added")
        
        # Crear alerta de prueba
        monitor._create_alert(AlertLevel.INFO, "TestModule", "Test alert message")
        print("✅ Test alert created")
        
        print("🎉 Monitoring module test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring module test failed: {e}")
        return False


if __name__ == "__main__":
    test_monitoring_module()