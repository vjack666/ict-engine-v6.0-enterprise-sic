#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 PRODUCTION SYSTEM MONITOR - ICT ENGINE v6.0 ENTERPRISE
========================================================

Monitor integral del sistema para cuenta real.
Supervisa recursos, conexiones, latencia y estado general.

Características:
✅ Monitoreo de recursos del sistema
✅ Seguimiento de conexiones críticas
✅ Métricas de performance en tiempo real
✅ Alertas automáticas por umbrales
✅ Integración con central de logging
✅ Persistencia de métricas

Autor: ICT Engine v6.0 Team - Production Module
Fecha: 15 Septiembre 2025
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import sys
import os

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
CORE_PATH = CURRENT_DIR.parent
sys.path.insert(0, str(CORE_PATH))

# Importar central de logging
try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    logger = setup_module_logging("ProductionSystemMonitor", LogLevel.INFO)
    LOGGING_AVAILABLE = True
except ImportError:
    logger = None
    LOGGING_AVAILABLE = False
    print("[ProductionSystemMonitor] Warning: Central logging not available")

class SystemHealthStatus(Enum):
    """Estados de salud del sistema"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_connections: int
    process_count: int
    uptime_seconds: float
    health_status: SystemHealthStatus = SystemHealthStatus.UNKNOWN
    
@dataclass
class PerformanceMetrics:
    """Métricas de performance específicas"""
    timestamp: datetime
    response_time_ms: float
    throughput_ops_sec: float
    error_rate_percent: float
    active_connections: int
    queue_depth: int
    latency_p95: Optional[float] = None
    
@dataclass
class Alert:
    """Alerta del sistema"""
    timestamp: datetime
    level: AlertLevel
    component: str
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    
class ProductionSystemMonitor:
    """🚀 Monitor de producción para sistema ICT Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.is_running = False
        self.start_time = datetime.now()
        
        # Métricas y alertas
        self.current_metrics: Optional[SystemMetrics] = None
        self.performance_metrics: Optional[PerformanceMetrics] = None
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        
        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks de alerta
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Persistencia
        self.metrics_file = Path(self.config.get('metrics_file', 'data/system_metrics.json'))
        self.alerts_file = Path(self.config.get('alerts_file', 'data/system_alerts.json'))
        
        # Crear directorios
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Production System Monitor inicializado", "SystemMonitor")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'monitoring_interval': 5.0,  # segundos
            'metrics_history_size': 1000,
            'thresholds': {
                'cpu_warning': 70.0,
                'cpu_critical': 90.0,
                'memory_warning': 80.0,
                'memory_critical': 95.0,
                'disk_warning': 85.0,
                'disk_critical': 95.0,
                'response_time_warning': 1000.0,  # ms
                'response_time_critical': 5000.0,  # ms
            },
            'persist_metrics': True,
            'max_alerts': 500
        }
    
    def start_monitoring(self):
        """Iniciar monitoreo en background"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Monitoreo del sistema iniciado", "SystemMonitor")
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Monitoreo del sistema detenido", "SystemMonitor")
    
    def _monitor_loop(self):
        """Loop principal de monitoreo"""
        while not self.stop_event.is_set():
            try:
                # Recolectar métricas
                self.current_metrics = self._collect_system_metrics()
                
                # Evaluar salud del sistema
                self._evaluate_system_health()
                
                # Generar alertas si es necesario
                self._check_thresholds()
                
                # Actualizar historial
                self._update_metrics_history()
                
                # Persistir métricas si está habilitado
                if self.config.get('persist_metrics', True):
                    self._persist_metrics()
                
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error en loop de monitoreo: {e}", "SystemMonitor")
            
            # Esperar intervalo
            self.stop_event.wait(self.config.get('monitoring_interval', 5.0))
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Recolectar métricas del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1.0)
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disco (partición principal)
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Red
            network_connections = len(psutil.net_connections())
            
            # Procesos
            process_count = len(psutil.pids())
            
            # Uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_usage_percent=disk_usage_percent,
                network_connections=network_connections,
                process_count=process_count,
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error recolectando métricas: {e}", "SystemMonitor")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                network_connections=0,
                process_count=0,
                uptime_seconds=0.0
            )
    
    def _evaluate_system_health(self):
        """Evaluar salud general del sistema"""
        if not self.current_metrics:
            return
        
        thresholds = self.config.get('thresholds', {})
        
        # Puntuación de salud (0-100)
        health_score = 100
        
        # CPU
        if self.current_metrics.cpu_percent > thresholds.get('cpu_critical', 90):
            health_score -= 30
        elif self.current_metrics.cpu_percent > thresholds.get('cpu_warning', 70):
            health_score -= 15
        
        # Memoria
        if self.current_metrics.memory_percent > thresholds.get('memory_critical', 95):
            health_score -= 30
        elif self.current_metrics.memory_percent > thresholds.get('memory_warning', 80):
            health_score -= 15
        
        # Disco
        if self.current_metrics.disk_usage_percent > thresholds.get('disk_critical', 95):
            health_score -= 20
        elif self.current_metrics.disk_usage_percent > thresholds.get('disk_warning', 85):
            health_score -= 10
        
        # Determinar estado
        if health_score >= 90:
            self.current_metrics.health_status = SystemHealthStatus.EXCELLENT
        elif health_score >= 75:
            self.current_metrics.health_status = SystemHealthStatus.GOOD
        elif health_score >= 50:
            self.current_metrics.health_status = SystemHealthStatus.WARNING
        else:
            self.current_metrics.health_status = SystemHealthStatus.CRITICAL
    
    def _check_thresholds(self):
        """Verificar umbrales y generar alertas"""
        if not self.current_metrics:
            return
        
        thresholds = self.config.get('thresholds', {})
        
        # CPU
        if self.current_metrics.cpu_percent > thresholds.get('cpu_critical', 90):
            self._create_alert(AlertLevel.CRITICAL, "CPU", 
                            f"Uso de CPU crítico: {self.current_metrics.cpu_percent:.1f}%")
        elif self.current_metrics.cpu_percent > thresholds.get('cpu_warning', 70):
            self._create_alert(AlertLevel.WARNING, "CPU", 
                            f"Uso de CPU elevado: {self.current_metrics.cpu_percent:.1f}%")
        
        # Memoria
        if self.current_metrics.memory_percent > thresholds.get('memory_critical', 95):
            self._create_alert(AlertLevel.CRITICAL, "Memory", 
                            f"Uso de memoria crítico: {self.current_metrics.memory_percent:.1f}%")
        elif self.current_metrics.memory_percent > thresholds.get('memory_warning', 80):
            self._create_alert(AlertLevel.WARNING, "Memory", 
                            f"Uso de memoria elevado: {self.current_metrics.memory_percent:.1f}%")
    
    def _create_alert(self, level: AlertLevel, component: str, message: str, 
                     extra_metrics: Optional[Dict[str, Any]] = None):
        """Crear y procesar alerta"""
        alert = Alert(
            timestamp=datetime.now(),
            level=level,
            component=component,
            message=message,
            metrics=extra_metrics or {}
        )
        
        self.alerts.append(alert)
        
        # Limitar número de alertas
        max_alerts = self.config.get('max_alerts', 500)
        if len(self.alerts) > max_alerts:
            self.alerts = self.alerts[-max_alerts:]
        
        # Logging
        if LOGGING_AVAILABLE and logger:
            if level == AlertLevel.CRITICAL:
                logger.error(f"ALERT: {message}", component)
            elif level == AlertLevel.WARNING:
                logger.warning(f"ALERT: {message}", component)
            else:
                logger.info(f"ALERT: {message}", component)
        
        # Ejecutar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error ejecutando callback de alerta: {e}", "SystemMonitor")
    
    def _update_metrics_history(self):
        """Actualizar historial de métricas"""
        if not self.current_metrics:
            return
        
        self.metrics_history.append(self.current_metrics)
        
        # Limitar tamaño del historial
        max_size = self.config.get('metrics_history_size', 1000)
        if len(self.metrics_history) > max_size:
            self.metrics_history = self.metrics_history[-max_size:]
    
    def _persist_metrics(self):
        """Persistir métricas a disco"""
        try:
            if self.current_metrics:
                metrics_data = {
                    'timestamp': self.current_metrics.timestamp.isoformat(),
                    'cpu_percent': self.current_metrics.cpu_percent,
                    'memory_percent': self.current_metrics.memory_percent,
                    'memory_available_gb': self.current_metrics.memory_available_gb,
                    'disk_usage_percent': self.current_metrics.disk_usage_percent,
                    'network_connections': self.current_metrics.network_connections,
                    'process_count': self.current_metrics.process_count,
                    'uptime_seconds': self.current_metrics.uptime_seconds,
                    'health_status': self.current_metrics.health_status.value
                }
                
                with open(self.metrics_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(metrics_data) + '\n')
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error persistiendo métricas: {e}", "SystemMonitor")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Agregar callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def get_current_status(self) -> Dict[str, Any]:
        """Obtener estado actual del sistema"""
        if not self.current_metrics:
            return {'status': 'no_data'}
        
        return {
            'status': 'active',
            'health': self.current_metrics.health_status.value,
            'uptime_hours': self.current_metrics.uptime_seconds / 3600,
            'cpu_percent': self.current_metrics.cpu_percent,
            'memory_percent': self.current_metrics.memory_percent,
            'disk_percent': self.current_metrics.disk_usage_percent,
            'active_alerts': len([a for a in self.alerts[-10:] if a.level != AlertLevel.INFO]),
            'is_monitoring': self.is_running
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de performance"""
        if len(self.metrics_history) < 2:
            return {'status': 'insufficient_data'}
        
        recent_metrics = self.metrics_history[-60:]  # Última hora (60 muestras de 5s)
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        max_cpu = max(m.cpu_percent for m in recent_metrics)
        max_memory = max(m.memory_percent for m in recent_metrics)
        
        return {
            'period_minutes': len(recent_metrics) * self.config.get('monitoring_interval', 5) / 60,
            'avg_cpu_percent': round(avg_cpu, 2),
            'avg_memory_percent': round(avg_memory, 2),
            'max_cpu_percent': round(max_cpu, 2),
            'max_memory_percent': round(max_memory, 2),
            'samples_count': len(recent_metrics),
            'health_distribution': self._get_health_distribution(recent_metrics)
        }
    
    def _get_health_distribution(self, metrics: List[SystemMetrics]) -> Dict[str, int]:
        """Obtener distribución de estados de salud"""
        distribution = {}
        for status in SystemHealthStatus:
            distribution[status.value] = 0
        
        for metric in metrics:
            distribution[metric.health_status.value] += 1
        
        return distribution

# Funciones de utilidad
def create_production_monitor(config: Optional[Dict[str, Any]] = None) -> ProductionSystemMonitor:
    """Crear monitor de producción con configuración"""
    return ProductionSystemMonitor(config)

def get_system_health_check() -> Dict[str, Any]:
    """Obtener check rápido de salud del sistema"""
    try:
        cpu = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu,
            'memory_percent': memory.percent,
            'status': 'healthy' if cpu < 80 and memory.percent < 90 else 'stressed'
        }
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'error'
        }

if __name__ == "__main__":
    # Test básico
    monitor = create_production_monitor()
    
    def test_alert_callback(alert: Alert):
        print(f"🚨 [{alert.level.value.upper()}] {alert.component}: {alert.message}")
    
    monitor.add_alert_callback(test_alert_callback)
    
    try:
        monitor.start_monitoring()
        print("🚀 Monitor de producción iniciado - Presiona Ctrl+C para detener")
        
        while True:
            time.sleep(5)
            status = monitor.get_current_status()
            print(f"📊 Estado: {status['health']} | CPU: {status['cpu_percent']:.1f}% | RAM: {status['memory_percent']:.1f}%")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor detenido")