#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 PRODUCTION PERFORMANCE MONITOR - ICT ENGINE v6.0 ENTERPRISE
=============================================================

Monitor especializado de performance para trading en cuenta real.
Supervisa latencia, throughput, errores y métricas críticas.

Características:
✅ Monitoreo de latencia en tiempo real
✅ Seguimiento de throughput y rendimiento
✅ Detección automática de anomalías
✅ Métricas específicas de trading
✅ Integración con central de logging
✅ Alertas por degradación de performance

Autor: ICT Engine v6.0 Team - Production Module
Fecha: 15 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Deque
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import json
from pathlib import Path
import sys

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
CORE_PATH = CURRENT_DIR.parent
sys.path.insert(0, str(CORE_PATH))

# Importar central de logging
try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    logger = setup_module_logging("ProductionPerformanceMonitor", LogLevel.INFO)
    LOGGING_AVAILABLE = True
except ImportError:
    logger = None
    LOGGING_AVAILABLE = False
    print("[ProductionPerformanceMonitor] Warning: Central logging not available")

class PerformanceStatus(Enum):
    """Estados de performance"""
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """Tipos de métricas"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"
    CONNECTION_COUNT = "connection_count"

@dataclass
class PerformanceMetric:
    """Métrica individual de performance"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    component: str
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceSnapshot:
    """Snapshot completo de performance"""
    timestamp: datetime
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_ops_sec: float
    error_rate_percent: float
    active_connections: int
    queue_depth: int
    status: PerformanceStatus = PerformanceStatus.UNKNOWN
    
@dataclass
class PerformanceAlert:
    """Alerta de performance"""
    timestamp: datetime
    severity: str
    component: str
    metric_type: MetricType
    threshold_value: float
    actual_value: float
    message: str
    
class ComponentPerformanceTracker:
    """Tracker de performance por componente"""
    
    def __init__(self, component_name: str, window_size: int = 100):
        self.component_name = component_name
        self.window_size = window_size
        
        # Ventanas deslizantes para métricas
        self.latency_samples: Deque[float] = deque(maxlen=window_size)
        self.response_times: Deque[float] = deque(maxlen=window_size)
        self.operation_counts: defaultdict[str, int] = defaultdict(int)
        self.error_counts: defaultdict[str, int] = defaultdict(int)
        
        # Estadísticas
        self.total_operations = 0
        self.total_errors = 0
        self.start_time = datetime.now()
        
    def record_operation(self, operation: str, latency_ms: float, success: bool = True):
        """Registrar operación"""
        self.latency_samples.append(latency_ms)
        self.response_times.append(latency_ms)
        self.operation_counts[operation] += 1
        self.total_operations += 1
        
        if not success:
            self.error_counts[operation] += 1
            self.total_errors += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del componente"""
        if not self.latency_samples:
            return {'status': 'no_data'}
        
        latencies = list(self.latency_samples)
        
        return {
            'component': self.component_name,
            'avg_latency_ms': statistics.mean(latencies),
            'median_latency_ms': statistics.median(latencies),
            'p95_latency_ms': self._percentile(latencies, 95),
            'p99_latency_ms': self._percentile(latencies, 99),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'total_operations': self.total_operations,
            'total_errors': self.total_errors,
            'error_rate_percent': (self.total_errors / self.total_operations * 100) if self.total_operations > 0 else 0,
            'operations_per_second': self._calculate_ops_per_second(),
            'sample_count': len(latencies)
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcular percentil"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f == len(sorted_data) - 1:
            return sorted_data[f]
        return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
    
    def _calculate_ops_per_second(self) -> float:
        """Calcular operaciones por segundo"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed <= 0:
            return 0.0
        return self.total_operations / elapsed

class ProductionPerformanceMonitor:
    """📊 Monitor de performance de producción para ICT Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.is_running = False
        self.start_time = datetime.now()
        
        # Trackers por componente
        self.component_trackers: Dict[str, ComponentPerformanceTracker] = {}
        
        # Métricas y snapshots
        self.current_snapshot: Optional[PerformanceSnapshot] = None
        self.snapshots_history: List[PerformanceSnapshot] = []
        self.alerts: List[PerformanceAlert] = []
        
        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self.snapshot_callbacks: List[Callable[[PerformanceSnapshot], None]] = []
        
        # Persistencia
        self.metrics_file = Path(self.config.get('performance_file', 'data/performance_metrics.json'))
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Production Performance Monitor inicializado", "PerformanceMonitor")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'snapshot_interval': 10.0,  # segundos
            'history_size': 500,
            'component_window_size': 1000,
            'thresholds': {
                'latency_warning_ms': 100.0,
                'latency_critical_ms': 500.0,
                'error_rate_warning': 1.0,  # %
                'error_rate_critical': 5.0,  # %
                'throughput_min_ops_sec': 10.0,
                'response_time_p95_ms': 200.0,
            },
            'auto_create_components': True,
            'persist_snapshots': True,
            'max_alerts': 200
        }
    
    def start_monitoring(self):
        """Iniciar monitoreo de performance"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Monitoreo de performance iniciado", "PerformanceMonitor")
    
    def stop_monitoring(self):
        """Detener monitoreo de performance"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Monitoreo de performance detenido", "PerformanceMonitor")
    
    def _monitor_loop(self):
        """Loop principal de monitoreo"""
        while not self.stop_event.is_set():
            try:
                # Generar snapshot de performance
                self.current_snapshot = self._create_performance_snapshot()
                
                # Evaluar performance
                self._evaluate_performance()
                
                # Verificar umbrales
                self._check_performance_thresholds()
                
                # Actualizar historial
                self._update_snapshot_history()
                
                # Ejecutar callbacks
                self._execute_snapshot_callbacks()
                
                # Persistir si está habilitado
                if self.config.get('persist_snapshots', True):
                    self._persist_snapshot()
                
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error en loop de performance: {e}", "PerformanceMonitor")
            
            # Esperar intervalo
            self.stop_event.wait(self.config.get('snapshot_interval', 10.0))
    
    def _create_performance_snapshot(self) -> PerformanceSnapshot:
        """Crear snapshot actual de performance"""
        if not self.component_trackers:
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                avg_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                throughput_ops_sec=0.0,
                error_rate_percent=0.0,
                active_connections=0,
                queue_depth=0
            )
        
        # Agregar estadísticas de todos los componentes
        all_latencies = []
        total_ops = 0
        total_errors = 0
        total_throughput = 0.0
        
        for tracker in self.component_trackers.values():
            stats = tracker.get_statistics()
            if stats.get('status') != 'no_data':
                all_latencies.extend(tracker.latency_samples)
                total_ops += stats['total_operations']
                total_errors += stats['total_errors']
                total_throughput += stats['operations_per_second']
        
        # Calcular métricas agregadas
        if all_latencies:
            avg_latency = statistics.mean(all_latencies)
            p95_latency = self._percentile(all_latencies, 95)
            p99_latency = self._percentile(all_latencies, 99)
        else:
            avg_latency = p95_latency = p99_latency = 0.0
        
        error_rate = (total_errors / total_ops * 100) if total_ops > 0 else 0.0
        
        return PerformanceSnapshot(
            timestamp=datetime.now(),
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            throughput_ops_sec=total_throughput,
            error_rate_percent=error_rate,
            active_connections=len(self.component_trackers),
            queue_depth=0  # Calculado por componentes específicos
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcular percentil"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f == len(sorted_data) - 1:
            return sorted_data[f]
        return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
    
    def _evaluate_performance(self):
        """Evaluar estado general de performance"""
        if not self.current_snapshot:
            return
        
        thresholds = self.config.get('thresholds', {})
        
        # Puntuación de performance
        score = 100
        
        # Latencia
        if self.current_snapshot.p95_latency_ms > thresholds.get('latency_critical_ms', 500):
            score -= 40
        elif self.current_snapshot.p95_latency_ms > thresholds.get('latency_warning_ms', 100):
            score -= 20
        
        # Tasa de error
        if self.current_snapshot.error_rate_percent > thresholds.get('error_rate_critical', 5):
            score -= 30
        elif self.current_snapshot.error_rate_percent > thresholds.get('error_rate_warning', 1):
            score -= 15
        
        # Throughput
        if self.current_snapshot.throughput_ops_sec < thresholds.get('throughput_min_ops_sec', 10):
            score -= 15
        
        # Determinar estado
        if score >= 90:
            self.current_snapshot.status = PerformanceStatus.OPTIMAL
        elif score >= 70:
            self.current_snapshot.status = PerformanceStatus.GOOD
        elif score >= 40:
            self.current_snapshot.status = PerformanceStatus.DEGRADED
        else:
            self.current_snapshot.status = PerformanceStatus.CRITICAL
    
    def _check_performance_thresholds(self):
        """Verificar umbrales de performance"""
        if not self.current_snapshot:
            return
        
        thresholds = self.config.get('thresholds', {})
        
        # Latencia P95
        if self.current_snapshot.p95_latency_ms > thresholds.get('latency_critical_ms', 500):
            self._create_performance_alert(
                'critical', 'System', MetricType.LATENCY,
                thresholds.get('latency_critical_ms', 500),
                self.current_snapshot.p95_latency_ms,
                f"Latencia P95 crítica: {self.current_snapshot.p95_latency_ms:.1f}ms"
            )
        elif self.current_snapshot.p95_latency_ms > thresholds.get('latency_warning_ms', 100):
            self._create_performance_alert(
                'warning', 'System', MetricType.LATENCY,
                thresholds.get('latency_warning_ms', 100),
                self.current_snapshot.p95_latency_ms,
                f"Latencia P95 elevada: {self.current_snapshot.p95_latency_ms:.1f}ms"
            )
        
        # Tasa de error
        if self.current_snapshot.error_rate_percent > thresholds.get('error_rate_critical', 5):
            self._create_performance_alert(
                'critical', 'System', MetricType.ERROR_RATE,
                thresholds.get('error_rate_critical', 5),
                self.current_snapshot.error_rate_percent,
                f"Tasa de error crítica: {self.current_snapshot.error_rate_percent:.2f}%"
            )
    
    def _create_performance_alert(self, severity: str, component: str, 
                                metric_type: MetricType, threshold: float, 
                                actual: float, message: str):
        """Crear alerta de performance"""
        alert = PerformanceAlert(
            timestamp=datetime.now(),
            severity=severity,
            component=component,
            metric_type=metric_type,
            threshold_value=threshold,
            actual_value=actual,
            message=message
        )
        
        self.alerts.append(alert)
        
        # Limitar alertas
        max_alerts = self.config.get('max_alerts', 200)
        if len(self.alerts) > max_alerts:
            self.alerts = self.alerts[-max_alerts:]
        
        # Logging
        if LOGGING_AVAILABLE and logger:
            if severity == 'critical':
                logger.error(f"PERFORMANCE ALERT: {message}", component)
            elif severity == 'warning':
                logger.warning(f"PERFORMANCE ALERT: {message}", component)
        
        # Ejecutar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error ejecutando callback de alerta: {e}", "PerformanceMonitor")
    
    def _update_snapshot_history(self):
        """Actualizar historial de snapshots"""
        if not self.current_snapshot:
            return
        
        self.snapshots_history.append(self.current_snapshot)
        
        # Limitar tamaño
        max_size = self.config.get('history_size', 500)
        if len(self.snapshots_history) > max_size:
            self.snapshots_history = self.snapshots_history[-max_size:]
    
    def _execute_snapshot_callbacks(self):
        """Ejecutar callbacks de snapshot"""
        if not self.current_snapshot:
            return
        
        for callback in self.snapshot_callbacks:
            try:
                callback(self.current_snapshot)
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error ejecutando callback de snapshot: {e}", "PerformanceMonitor")
    
    def _persist_snapshot(self):
        """Persistir snapshot actual"""
        try:
            if self.current_snapshot:
                snapshot_data = {
                    'timestamp': self.current_snapshot.timestamp.isoformat(),
                    'avg_latency_ms': self.current_snapshot.avg_latency_ms,
                    'p95_latency_ms': self.current_snapshot.p95_latency_ms,
                    'p99_latency_ms': self.current_snapshot.p99_latency_ms,
                    'throughput_ops_sec': self.current_snapshot.throughput_ops_sec,
                    'error_rate_percent': self.current_snapshot.error_rate_percent,
                    'active_connections': self.current_snapshot.active_connections,
                    'queue_depth': self.current_snapshot.queue_depth,
                    'status': self.current_snapshot.status.value
                }
                
                with open(self.metrics_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(snapshot_data) + '\n')
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error persistiendo snapshot: {e}", "PerformanceMonitor")
    
    # API Pública
    def record_operation(self, component: str, operation: str, latency_ms: float, success: bool = True):
        """Registrar operación de un componente"""
        # Crear tracker si no existe
        if component not in self.component_trackers and self.config.get('auto_create_components', True):
            self.component_trackers[component] = ComponentPerformanceTracker(
                component, self.config.get('component_window_size', 1000)
            )
        
        if component in self.component_trackers:
            self.component_trackers[component].record_operation(operation, latency_ms, success)
    
    def get_component_tracker(self, component: str) -> Optional[ComponentPerformanceTracker]:
        """Obtener tracker de componente"""
        return self.component_trackers.get(component)
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Agregar callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def add_snapshot_callback(self, callback: Callable[[PerformanceSnapshot], None]):
        """Agregar callback para snapshots"""
        self.snapshot_callbacks.append(callback)
    
    def get_current_performance(self) -> Dict[str, Any]:
        """Obtener performance actual"""
        if not self.current_snapshot:
            return {'status': 'no_data'}
        
        return {
            'status': self.current_snapshot.status.value,
            'avg_latency_ms': round(self.current_snapshot.avg_latency_ms, 2),
            'p95_latency_ms': round(self.current_snapshot.p95_latency_ms, 2),
            'throughput_ops_sec': round(self.current_snapshot.throughput_ops_sec, 2),
            'error_rate_percent': round(self.current_snapshot.error_rate_percent, 3),
            'active_components': len(self.component_trackers),
            'recent_alerts': len([a for a in self.alerts[-10:] if a.severity != 'info'])
        }
    
    def get_component_summary(self) -> Dict[str, Any]:
        """Obtener resumen por componente"""
        summary = {}
        for name, tracker in self.component_trackers.items():
            stats = tracker.get_statistics()
            if stats.get('status') != 'no_data':
                summary[name] = {
                    'avg_latency_ms': round(stats['avg_latency_ms'], 2),
                    'operations_per_second': round(stats['operations_per_second'], 2),
                    'error_rate_percent': round(stats['error_rate_percent'], 3),
                    'total_operations': stats['total_operations']
                }
        return summary

# Funciones de utilidad
def create_performance_monitor(config: Optional[Dict[str, Any]] = None) -> ProductionPerformanceMonitor:
    """Crear monitor de performance con configuración"""
    return ProductionPerformanceMonitor(config)

def time_operation(monitor: ProductionPerformanceMonitor, component: str, operation: str):
    """Decorador para medir tiempo de operaciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                monitor.record_operation(component, operation, elapsed_ms, success)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test básico
    monitor = create_performance_monitor()
    
    def test_alert_callback(alert: PerformanceAlert):
        print(f"🚨 [{alert.severity.upper()}] {alert.component}: {alert.message}")
    
    def test_snapshot_callback(snapshot: PerformanceSnapshot):
        print(f"📊 Status: {snapshot.status.value} | Latency P95: {snapshot.p95_latency_ms:.1f}ms | Throughput: {snapshot.throughput_ops_sec:.1f} ops/s")
    
    monitor.add_alert_callback(test_alert_callback)
    monitor.add_snapshot_callback(test_snapshot_callback)
    
    try:
        monitor.start_monitoring()
        print("📊 Monitor de performance iniciado - Presiona Ctrl+C para detener")
        
        # Simular algunas operaciones
        import random
        for i in range(100):
            latency = random.uniform(10, 200)
            success = random.random() > 0.05  # 95% success rate
            monitor.record_operation("TestComponent", "test_operation", latency, success)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor detenido")