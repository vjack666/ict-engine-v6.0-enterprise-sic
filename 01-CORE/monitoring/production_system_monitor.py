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
class TradingConnectionMetrics:
    """Métricas de conexiones de trading"""
    timestamp: datetime
    mt5_connected: bool
    mt5_login_id: int
    mt5_server: str
    broker_ping_ms: float
    last_tick_age_ms: float
    account_balance: float
    account_equity: float
    margin_level: float
    open_positions: int
    internet_connected: bool = True
    
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
        self.trading_metrics: Optional[TradingConnectionMetrics] = None
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.trading_history: List[TradingConnectionMetrics] = []
        
        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.trading_monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks de alerta
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Persistencia
        self.metrics_file = Path(self.config.get('metrics_file', 'data/system_metrics.json'))
        self.alerts_file = Path(self.config.get('alerts_file', 'data/system_alerts.json'))
        self.trading_file = Path(self.config.get('trading_file', 'data/trading_metrics.json'))
        
        # Crear directorios
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        self.trading_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Auto-recovery state
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        
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
        
        # Iniciar hilo de monitoreo de sistema
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Iniciar hilo de monitoreo de trading
        self.trading_monitor_thread = threading.Thread(target=self._trading_monitor_loop, daemon=True)
        self.trading_monitor_thread.start()
        
        if LOGGING_AVAILABLE and logger:
            logger.info("Monitoreo del sistema y trading iniciado", "SystemMonitor")
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        # Esperar hilos
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
            
        if self.trading_monitor_thread and self.trading_monitor_thread.is_alive():
            self.trading_monitor_thread.join(timeout=5.0)
        
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

    def _trading_monitor_loop(self):
        """Loop de monitoreo de conexiones de trading"""
        while self.is_running and not self.stop_event.wait(10.0):  # Check every 10 seconds
            try:
                trading_metrics = self._collect_trading_metrics()
                self.trading_metrics = trading_metrics
                self.trading_history.append(trading_metrics)
                
                # Limitar historial
                if len(self.trading_history) > 500:
                    self.trading_history = self.trading_history[-500:]
                
                # Verificar alertas de trading
                self._check_trading_alerts(trading_metrics)
                
                # Auto-recovery si es necesario
                if self.config.get('auto_recovery_enabled', True):
                    self._attempt_auto_recovery(trading_metrics)
                
                # Persistir métricas de trading
                if self.config.get('persist_metrics', True):
                    self._persist_trading_metrics()
                    
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Error en trading monitor loop: {e}", "TradingMonitor")

    def _collect_trading_metrics(self) -> TradingConnectionMetrics:
        """Recopilar métricas de conexiones de trading"""
        metrics = TradingConnectionMetrics(
            timestamp=datetime.now(),
            mt5_connected=False,
            mt5_login_id=0,
            mt5_server="",
            broker_ping_ms=9999.0,
            last_tick_age_ms=9999.0,
            account_balance=0.0,
            account_equity=0.0,
            margin_level=0.0,
            open_positions=0,
            internet_connected=True
        )
        
        try:
            # Test internet connectivity
            import socket
            try:
                socket.create_connection(("8.8.8.8", 53), 3)
                metrics.internet_connected = True
            except OSError:
                metrics.internet_connected = False
            
            # Try to get MT5 info
            try:
                import MetaTrader5 as mt5  # type: ignore
                
                if mt5.initialize():  # type: ignore
                    metrics.mt5_connected = True
                    
                    # Account info
                    account_info = mt5.account_info()  # type: ignore
                    if account_info:
                        metrics.mt5_login_id = account_info.login
                        metrics.mt5_server = account_info.server
                        metrics.account_balance = account_info.balance
                        metrics.account_equity = account_info.equity
                        
                        # Calculate margin level
                        if hasattr(account_info, 'margin_level'):
                            metrics.margin_level = account_info.margin_level
                        elif account_info.margin > 0:
                            metrics.margin_level = (account_info.equity / account_info.margin) * 100
                    
                    # Get positions count
                    positions = mt5.positions_get()  # type: ignore
                    if positions is not None:
                        metrics.open_positions = len(positions)
                    
                    # Test ping (simplified - get symbol info response time)
                    start_time = time.time()
                    symbol_info = mt5.symbol_info("EURUSD")  # type: ignore
                    if symbol_info:
                        metrics.broker_ping_ms = (time.time() - start_time) * 1000
                        
                        # Check last tick age
                        if hasattr(symbol_info, 'time'):
                            current_time = time.time()
                            tick_age = current_time - symbol_info.time
                            metrics.last_tick_age_ms = tick_age * 1000
                    
                else:
                    metrics.mt5_connected = False
                    
            except ImportError:
                # MT5 not available
                pass
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error collecting trading metrics: {e}", "TradingMonitor")
        
        return metrics

    def _check_trading_alerts(self, metrics: TradingConnectionMetrics):
        """Verificar alertas específicas de trading"""
        # MT5 Connection
        if not metrics.mt5_connected:
            self._create_alert(
                AlertLevel.CRITICAL,
                "MT5Connection",
                "MT5 no está conectado",
                {"mt5_connected": False}
            )
        
        # Internet connectivity
        if not metrics.internet_connected:
            self._create_alert(
                AlertLevel.CRITICAL,
                "InternetConnection",
                "Sin conectividad a internet",
                {"internet_connected": False}
            )
        
        # High broker latency
        if metrics.broker_ping_ms > 5000:
            self._create_alert(
                AlertLevel.WARNING,
                "BrokerLatency",
                f"Alta latencia del broker: {metrics.broker_ping_ms:.0f}ms",
                {"broker_ping_ms": metrics.broker_ping_ms}
            )
        
        # Stale market data
        if metrics.last_tick_age_ms > 30000:  # 30 seconds
            self._create_alert(
                AlertLevel.WARNING,
                "StaleMarketData",
                f"Datos de mercado desactualizados: {metrics.last_tick_age_ms/1000:.1f}s",
                {"last_tick_age_ms": metrics.last_tick_age_ms}
            )
        
        # Low margin level
        if metrics.margin_level > 0 and metrics.margin_level < 150:
            level = AlertLevel.CRITICAL if metrics.margin_level < 120 else AlertLevel.WARNING
            self._create_alert(
                level,
                "MarginLevel",
                f"Nivel de margen bajo: {metrics.margin_level:.1f}%",
                {"margin_level": metrics.margin_level}
            )

    def _attempt_auto_recovery(self, metrics: TradingConnectionMetrics):
        """Intentar auto-recuperación para problemas comunes"""
        recovery_actions = []
        
        # MT5 reconnection
        if not metrics.mt5_connected:
            if self._should_attempt_recovery("mt5_reconnect"):
                recovery_actions.append(self._attempt_mt5_reconnect)
        
        # Clear memory if high usage
        if self.current_metrics and self.current_metrics.memory_percent > 85:
            if self._should_attempt_recovery("memory_cleanup"):
                recovery_actions.append(self._attempt_memory_cleanup)
        
        # Execute recovery actions
        for action in recovery_actions:
            try:
                action()
            except Exception as e:
                if LOGGING_AVAILABLE and logger:
                    logger.error(f"Recovery action failed: {e}", "AutoRecovery")

    def _should_attempt_recovery(self, recovery_type: str) -> bool:
        """Verificar si se debe intentar recuperación"""
        current_time = time.time()
        last_attempt = self.recovery_attempts.get(recovery_type, 0)
        
        # Wait at least 5 minutes between attempts
        if current_time - last_attempt < 300:
            return False
        
        # Limit total attempts
        attempt_count = self.recovery_attempts.get(f"{recovery_type}_count", 0)
        if attempt_count >= self.max_recovery_attempts:
            return False
        
        return True

    def _attempt_mt5_reconnect(self):
        """Intentar reconexión a MT5"""
        try:
            import MetaTrader5 as mt5  # type: ignore
            
            # Record attempt
            self.recovery_attempts["mt5_reconnect"] = time.time()
            count = self.recovery_attempts.get("mt5_reconnect_count", 0) + 1
            self.recovery_attempts["mt5_reconnect_count"] = count
            
            # Try to shutdown and reinitialize
            mt5.shutdown()  # type: ignore
            time.sleep(2)
            
            if mt5.initialize():  # type: ignore
                if LOGGING_AVAILABLE and logger:
                    logger.info("MT5 reconnection successful", "AutoRecovery")
                return True
            else:
                if LOGGING_AVAILABLE and logger:
                    logger.warning("MT5 reconnection failed", "AutoRecovery")
                return False
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"MT5 reconnection error: {e}", "AutoRecovery")
            return False

    def _attempt_memory_cleanup(self):
        """Intentar limpieza de memoria"""
        try:
            import gc
            
            # Record attempt
            self.recovery_attempts["memory_cleanup"] = time.time()
            count = self.recovery_attempts.get("memory_cleanup_count", 0) + 1
            self.recovery_attempts["memory_cleanup_count"] = count
            
            # Force garbage collection
            collected = gc.collect()
            
            if LOGGING_AVAILABLE and logger:
                logger.info(f"Memory cleanup completed, collected {collected} objects", "AutoRecovery")
            
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Memory cleanup error: {e}", "AutoRecovery")

    def _persist_trading_metrics(self):
        """Persistir métricas de trading a disco"""
        try:
            if self.trading_metrics:
                trading_data = {
                    'timestamp': self.trading_metrics.timestamp.isoformat(),
                    'mt5_connected': self.trading_metrics.mt5_connected,
                    'mt5_login_id': self.trading_metrics.mt5_login_id,
                    'mt5_server': self.trading_metrics.mt5_server,
                    'broker_ping_ms': self.trading_metrics.broker_ping_ms,
                    'last_tick_age_ms': self.trading_metrics.last_tick_age_ms,
                    'account_balance': self.trading_metrics.account_balance,
                    'account_equity': self.trading_metrics.account_equity,
                    'margin_level': self.trading_metrics.margin_level,
                    'open_positions': self.trading_metrics.open_positions,
                    'internet_connected': self.trading_metrics.internet_connected
                }
                
                # Atomic write
                temp_file = self.trading_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(trading_data, f, indent=2)
                temp_file.replace(self.trading_file)
                
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error persistiendo métricas de trading: {e}", "SystemMonitor")

    def get_trading_status(self) -> Dict[str, Any]:
        """Obtener estado actual del trading"""
        if not self.trading_metrics:
            return {'status': 'no_data'}
        
        return {
            'timestamp': self.trading_metrics.timestamp.isoformat(),
            'mt5_connected': self.trading_metrics.mt5_connected,
            'mt5_server': self.trading_metrics.mt5_server,
            'account_balance': self.trading_metrics.account_balance,
            'account_equity': self.trading_metrics.account_equity,
            'margin_level': self.trading_metrics.margin_level,
            'open_positions': self.trading_metrics.open_positions,
            'broker_ping_ms': self.trading_metrics.broker_ping_ms,
            'internet_connected': self.trading_metrics.internet_connected,
            'status': 'connected' if self.trading_metrics.mt5_connected and self.trading_metrics.internet_connected else 'disconnected'
        }

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