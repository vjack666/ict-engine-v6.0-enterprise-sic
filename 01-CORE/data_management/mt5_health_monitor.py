"""
MT5 Health Monitoring System v6.0 Enterprise
Sistema de monitoreo de salud automático para conexiones MT5 con FTMO

Features:
- Health check continuo de conexión MT5
- Alertas automáticas por desconexión
- Reconexión automática inteligente
- Métricas de performance en tiempo real
- Integration con SmartTradingLogger
"""

import time
import threading
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Resolver imports
def _resolve_imports():
    """Resolver imports con path absoluto"""
    current_dir = Path(__file__).parent
    core_dir = current_dir.parent
    project_root = core_dir.parent
    
    paths_to_add = [str(project_root), str(core_dir), str(current_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

_resolve_imports()

# Imports
try:
    from mt5_connection_manager import MT5ConnectionManager
    from mt5_black_box_logger import MT5BlackBoxLogger, create_black_box_logger
    from smart_trading_logger import get_smart_logger
    logger = get_smart_logger("MT5HealthMonitor")
    BLACK_BOX_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Import warning: {e}")
    BLACK_BOX_AVAILABLE = False
    MT5BlackBoxLogger = None

class HealthStatus(Enum):
    """Estados de salud del sistema"""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"

@dataclass
class HealthMetrics:
    """Métricas de salud del sistema"""
    timestamp: datetime
    status: HealthStatus
    connection_active: bool
    response_time_ms: float
    last_successful_check: datetime
    failed_checks_count: int
    reconnection_attempts: int
    account_balance: Optional[float] = None
    server_name: Optional[str] = None
    error_message: Optional[str] = None

class MT5HealthMonitor:
    """
    🔍 Monitor de salud MT5 con alertas automáticas y reconexión inteligente
    """
    
    def __init__(self, mt5_manager: Optional[MT5ConnectionManager] = None, 
                 check_interval: int = 30, max_failed_checks: int = 3):
        """
        Inicializar el monitor de salud
        
        Args:
            mt5_manager: Instancia del MT5ConnectionManager
            check_interval: Intervalo entre checks en segundos (default: 30s)
            max_failed_checks: Máximo número de checks fallidos antes de alerta crítica
        """
        self.logger = logger
        self.mt5_manager = mt5_manager or MT5ConnectionManager()
        self.check_interval = check_interval
        self.max_failed_checks = max_failed_checks
        
        # Inicializar Black Box Logger
        if BLACK_BOX_AVAILABLE:
            self.black_box_logger = create_black_box_logger()
            self.logger.info("✅ Black Box Logger inicializado")
        else:
            self.black_box_logger = None
            self.logger.warning("⚠️ Black Box Logger no disponible")
        
        # Estado del monitor
        self.monitoring_active = False
        self.monitoring_thread = None
        self._lock = threading.Lock()
        
        # Métricas y estado
        self.current_status = HealthStatus.DISCONNECTED
        self.metrics_history: List[HealthMetrics] = []
        self.last_successful_check = None
        self.failed_checks_count = 0
        self.reconnection_attempts = 0
        
        # Callbacks para alertas
        self.alert_callbacks: List[Callable[[HealthMetrics], None]] = []
        
        # Configuración de alertas
        self.alert_config = {
            'warning_threshold': 2,    # Alertas después de 2 checks fallidos
            'critical_threshold': 5,   # Crítico después de 5 checks fallidos
            'response_time_warning': 5000,  # Warning si response > 5s
            'response_time_critical': 15000  # Crítico si response > 15s
        }
        
        # Log de startup en la caja negra
        if self.black_box_logger:
            startup_data = {
                'check_interval': check_interval,
                'max_failed_checks': max_failed_checks,
                'alert_config': self.alert_config,
                'mt5_manager_available': mt5_manager is not None
            }
            self.black_box_logger.log_system_startup(startup_data)
        
        self.logger.info("✅ MT5 Health Monitor inicializado")
        
    def start_monitoring(self) -> bool:
        """
        Iniciar el monitoreo de salud continuo
        
        Returns:
            bool: True si el monitoreo se inició correctamente
        """
        with self._lock:
            if self.monitoring_active:
                self.logger.warning("⚠️ Monitor ya está activo")
                return True
                
            try:
                self.monitoring_active = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    name="MT5HealthMonitor",
                    daemon=True
                )
                self.monitoring_thread.start()
                
                self.logger.info("🔄 MT5 Health Monitoring iniciado")
                self.logger.info(f"   Check interval: {self.check_interval}s")
                self.logger.info(f"   Max failed checks: {self.max_failed_checks}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Error iniciando monitoring: {e}")
                self.monitoring_active = False
                return False
                
    def stop_monitoring(self) -> None:
        """🛑 Detener el monitoreo de salud con optimización de velocidad"""
        with self._lock:
            if not self.monitoring_active:
                return
                
            print("🛑 Deteniendo MT5 Health Monitor...")
            start_time = time.time()
            
            self.monitoring_active = False
            
            # === SHUTDOWN OPTIMIZADO ===
            shutdown_tasks = []
            
            # 1. Log shutdown en background (no bloquear)
            if self.black_box_logger:
                def log_shutdown():
                    try:
                        shutdown_data = {
                            'final_status': self.current_status.value,
                            'total_checks_performed': len(self.metrics_history),
                            'final_failed_checks': self.failed_checks_count,
                            'final_reconnection_attempts': self.reconnection_attempts
                        }
                        self.black_box_logger.log_system_shutdown(shutdown_data)  # type: ignore
                        print("   ✅ Shutdown logged")
                    except Exception as e:
                        print(f"   ⚠️ Error logging shutdown: {e}")
                
                log_thread = threading.Thread(target=log_shutdown, daemon=True)
                log_thread.start()
                shutdown_tasks.append(('Logger', log_thread))
            
            # 2. Detener monitoring thread con timeout reducido
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                def stop_monitor_thread():
                    try:
                        self.monitoring_thread.join(timeout=5)  # type: ignore # Reducido de 10 a 5 segundos
                        if self.monitoring_thread.is_alive():  # type: ignore
                            print("   ⚠️ Monitor thread timeout - forzando")
                        else:
                            print("   ✅ Monitor thread detenido")
                    except Exception as e:
                        print(f"   ❌ Error deteniendo monitor thread: {e}")
                
                monitor_stop_thread = threading.Thread(target=stop_monitor_thread, daemon=True)
                monitor_stop_thread.start()
                shutdown_tasks.append(('Monitor', monitor_stop_thread))
            
            # === ESPERAR COMPLETAR CON TIMEOUT ===
            for task_name, thread in shutdown_tasks:
                try:
                    thread.join(timeout=2.0)  # 2 segundos máximo por tarea
                    if thread.is_alive():
                        print(f"   ⚠️ {task_name}: Timeout - continuando")
                except Exception as e:
                    print(f"   ❌ {task_name}: Error - {e}")
            
            stop_time = time.time() - start_time
            self.logger.info(f"🛑 MT5 Health Monitoring detenido en {stop_time:.2f}s")
            
            # Cleanup final
            self.monitoring_thread = None
            
    def _monitoring_loop(self) -> None:
        """Loop principal de monitoreo"""
        self.logger.info("🔄 Iniciando loop de monitoreo de salud...")
        
        while self.monitoring_active:
            try:
                # Ejecutar health check
                metrics = self._perform_health_check()
                
                # Almacenar métricas
                self._store_metrics(metrics)
                
                # Log en la caja negra
                if self.black_box_logger:
                    metrics_dict = asdict(metrics)
                    self.black_box_logger.log_health_check(metrics_dict)
                
                # Evaluar estado y generar alertas si es necesario
                self._evaluate_health_status(metrics)
                
                # Ejecutar acciones automáticas si es necesario
                self._handle_automatic_actions(metrics)
                
            except Exception as e:
                self.logger.error(f"❌ Error en monitoring loop: {e}")
                
            # Esperar hasta el próximo check
            time.sleep(self.check_interval)
            
    def _perform_health_check(self) -> HealthMetrics:
        """
        Realizar check completo de salud
        
        Returns:
            HealthMetrics: Métricas del check actual
        """
        start_time = time.time()
        timestamp = datetime.now()
        
        try:
            # Test 1: Verificar estado de conexión
            connection_status = self.mt5_manager.get_connection_status()
            connection_active = connection_status.get('connected', False)
            
            # Test 2: Medir tiempo de respuesta
            response_start = time.time()
            account_info = self.mt5_manager.get_account_info()
            response_time_ms = (time.time() - response_start) * 1000
            
            # Test 3: Validar datos de cuenta
            account_balance = None
            server_name = None
            if account_info:
                account_balance = account_info.get('balance')
                server_name = account_info.get('server')
            
            # Determinar estado basado en los tests
            if connection_active and account_info and response_time_ms < self.alert_config['response_time_warning']:
                status = HealthStatus.HEALTHY
                self.failed_checks_count = 0
                self.last_successful_check = timestamp
                error_message = None
            elif connection_active and response_time_ms < self.alert_config['response_time_critical']:
                status = HealthStatus.WARNING
                self.failed_checks_count += 1
                error_message = f"Respuesta lenta: {response_time_ms:.1f}ms"
            else:
                status = HealthStatus.CRITICAL if connection_active else HealthStatus.DISCONNECTED
                self.failed_checks_count += 1
                error_message = "Conexión perdida o respuesta crítica"
                
        except Exception as e:
            # Error en el health check
            status = HealthStatus.CRITICAL
            connection_active = False
            response_time_ms = -1
            account_balance = None
            server_name = None
            error_message = f"Health check error: {str(e)}"
            self.failed_checks_count += 1
            
        # Crear métricas
        metrics = HealthMetrics(
            timestamp=timestamp,
            status=status,
            connection_active=connection_active,
            response_time_ms=response_time_ms,
            last_successful_check=self.last_successful_check or timestamp,
            failed_checks_count=self.failed_checks_count,
            reconnection_attempts=self.reconnection_attempts,
            account_balance=account_balance,
            server_name=server_name,
            error_message=error_message
        )
        
        return metrics
        
    def _store_metrics(self, metrics: HealthMetrics) -> None:
        """Almacenar métricas en historial"""
        self.metrics_history.append(metrics)
        self.current_status = metrics.status
        
        # Mantener solo las últimas 1000 métricas (aprox 8 horas con check cada 30s)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
            
        # Log métricas de performance en la caja negra
        if self.black_box_logger and metrics.response_time_ms > 0:
            import psutil
            try:
                system_metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory_gb': psutil.virtual_memory().used / (1024**3),
                    'memory_percent': psutil.virtual_memory().percent
                }
                
                # Calcular throughput (checks por minuto)
                if len(self.metrics_history) >= 2:
                    time_diff = (metrics.timestamp - self.metrics_history[-2].timestamp).total_seconds()
                    throughput = 60.0 / max(time_diff, 1)  # checks per minute
                else:
                    throughput = 0.0
                
                self.black_box_logger.log_performance_metrics(
                    response_time=metrics.response_time_ms,
                    throughput=throughput,
                    system_metrics=system_metrics
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Error logging performance metrics: {e}")
            
    def _evaluate_health_status(self, metrics: HealthMetrics) -> None:
        """Evaluar estado de salud y generar alertas"""
        
        # Log del estado actual
        if metrics.status == HealthStatus.HEALTHY:
            self.logger.info(f"✅ MT5 Health: HEALTHY - Response: {metrics.response_time_ms:.1f}ms")
        elif metrics.status == HealthStatus.WARNING:
            self.logger.warning(f"⚠️ MT5 Health: WARNING - {metrics.error_message}")
        elif metrics.status == HealthStatus.CRITICAL:
            self.logger.error(f"🚨 MT5 Health: CRITICAL - {metrics.error_message}")
        elif metrics.status == HealthStatus.DISCONNECTED:
            self.logger.error(f"❌ MT5 Health: DISCONNECTED - {metrics.error_message}")
            
        # Generar alertas basadas en umbrales
        if (metrics.failed_checks_count >= self.alert_config['warning_threshold'] and 
            metrics.failed_checks_count < self.alert_config['critical_threshold']):
            self._trigger_alert(metrics, "WARNING")
            
        elif metrics.failed_checks_count >= self.alert_config['critical_threshold']:
            self._trigger_alert(metrics, "CRITICAL")
            
        # Alerta por tiempo de respuesta
        if (metrics.response_time_ms > self.alert_config['response_time_critical'] and 
            metrics.connection_active):
            self._trigger_alert(metrics, "PERFORMANCE_CRITICAL")
            
    def _handle_automatic_actions(self, metrics: HealthMetrics) -> None:
        """Manejar acciones automáticas basadas en el estado"""
        
        # Reconexión automática para estados críticos
        if (metrics.status in [HealthStatus.CRITICAL, HealthStatus.DISCONNECTED] and 
            metrics.failed_checks_count >= self.alert_config['critical_threshold']):
            
            self._attempt_automatic_reconnection()
            
    def _attempt_automatic_reconnection(self) -> bool:
        """
        Intentar reconexión automática
        
        Returns:
            bool: True si la reconexión fue exitosa
        """
        if self.reconnection_attempts >= 5:  # Máximo 5 intentos de reconexión
            self.logger.error("🚨 Máximo de intentos de reconexión alcanzado")
            return False
            
        self.reconnection_attempts += 1
        self.current_status = HealthStatus.RECONNECTING
        
        self.logger.info(f"🔄 Intento de reconexión automática #{self.reconnection_attempts}")
        
        # Log evento de reconexión en la caja negra
        if self.black_box_logger:
            reconnection_data = {
                'attempt_number': self.reconnection_attempts,
                'failed_checks_count': self.failed_checks_count,
                'current_status': self.current_status.value
            }
            self.black_box_logger.log_connection_event('RECONNECT_ATTEMPT', reconnection_data)
        
        try:
            if self.mt5_manager.reconnect():
                self.logger.info("✅ Reconexión automática exitosa")
                
                # Log reconexión exitosa
                if self.black_box_logger:
                    success_data = {
                        'attempt_number': self.reconnection_attempts,
                        'success': True,
                        'connection_restored': True
                    }
                    self.black_box_logger.log_connection_event('RECONNECT_SUCCESS', success_data)
                
                self.reconnection_attempts = 0
                self.failed_checks_count = 0
                return True
            else:
                self.logger.error(f"❌ Reconexión automática fallida (intento #{self.reconnection_attempts})")
                
                # Log reconexión fallida
                if self.black_box_logger:
                    failure_data = {
                        'attempt_number': self.reconnection_attempts,
                        'success': False,
                        'max_attempts_reached': self.reconnection_attempts >= 5
                    }
                    self.black_box_logger.log_connection_event('RECONNECT_FAIL', failure_data)
                    
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error en reconexión automática: {e}")
            return False
            
    def _trigger_alert(self, metrics: HealthMetrics, alert_type: str) -> None:
        """Disparar alerta y ejecutar callbacks"""
        alert_msg = f"🚨 MT5 HEALTH ALERT [{alert_type}]: {metrics.error_message}"
        self.logger.error(alert_msg)
        
        # Log en la caja negra
        if self.black_box_logger:
            metrics_dict = asdict(metrics)
            severity = "CRITICAL" if alert_type in ["CRITICAL", "PERFORMANCE_CRITICAL"] else "WARNING"
            self.black_box_logger.log_alert(alert_type, metrics_dict, severity)
        
        # Ejecutar callbacks de alerta
        for callback in self.alert_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self.logger.error(f"❌ Error en callback de alerta: {e}")
                
    def add_alert_callback(self, callback: Callable[[HealthMetrics], None]) -> None:
        """Agregar callback para alertas"""
        self.alert_callbacks.append(callback)
        
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del estado de salud
        
        Returns:
            dict: Resumen completo del estado
        """
        if not self.metrics_history:
            return {'status': 'NO_DATA', 'message': 'No hay datos de monitoreo disponibles'}
            
        latest = self.metrics_history[-1]
        
        # Calcular estadísticas de las últimas 24 horas
        last_24h = [m for m in self.metrics_history 
                   if m.timestamp > datetime.now() - timedelta(hours=24)]
        
        if last_24h:
            avg_response_time = sum(m.response_time_ms for m in last_24h if m.response_time_ms > 0) / len(last_24h)
            uptime_percentage = (len([m for m in last_24h if m.status == HealthStatus.HEALTHY]) / len(last_24h)) * 100
        else:
            avg_response_time = latest.response_time_ms
            uptime_percentage = 100 if latest.status == HealthStatus.HEALTHY else 0
            
        return {
            'current_status': latest.status.value,
            'connection_active': latest.connection_active,
            'last_check': latest.timestamp.isoformat(),
            'response_time_ms': latest.response_time_ms,
            'failed_checks_count': latest.failed_checks_count,
            'reconnection_attempts': latest.reconnection_attempts,
            'account_balance': latest.account_balance,
            'server_name': latest.server_name,
            'error_message': latest.error_message,
            'statistics_24h': {
                'avg_response_time_ms': avg_response_time,
                'uptime_percentage': uptime_percentage,
                'total_checks': len(last_24h)
            },
            'monitoring_active': self.monitoring_active
        }
        
    def force_health_check(self) -> HealthMetrics:
        """Forzar un health check inmediato"""
        self.logger.info("🔍 Ejecutando health check manual...")
        metrics = self._perform_health_check()
        self._store_metrics(metrics)
        self._evaluate_health_status(metrics)
        return metrics

# Funciones de utilidad para integración
def create_health_monitor(mt5_manager: Optional[MT5ConnectionManager] = None) -> MT5HealthMonitor:
    """Factory function para crear un monitor de salud"""
    return MT5HealthMonitor(mt5_manager)

def setup_basic_health_monitoring() -> MT5HealthMonitor:
    """Setup básico de monitoreo de salud con configuración por defecto"""
    logger.info("🔧 Configurando monitoreo básico de salud MT5...")
    
    # Crear manager y monitor
    mt5_manager = MT5ConnectionManager()
    health_monitor = MT5HealthMonitor(mt5_manager, check_interval=30)
    
    # Callback de ejemplo para alertas críticas
    def critical_alert_callback(metrics: HealthMetrics):
        if metrics.status in [HealthStatus.CRITICAL, HealthStatus.DISCONNECTED]:
            logger.error(f"🚨 CRITICAL ALERT: {metrics.error_message}")
            # Aquí se pueden agregar acciones adicionales como enviar emails, SMS, etc.
    
    health_monitor.add_alert_callback(critical_alert_callback)
    
    # Iniciar monitoreo
    if health_monitor.start_monitoring():
        logger.info("✅ Monitoreo de salud MT5 configurado y activo")
        return health_monitor
    else:
        logger.error("❌ Error configurando monitoreo de salud")
        return health_monitor

if __name__ == "__main__":
    # Test del sistema de monitoreo
    print("🔧 Testing MT5 Health Monitoring System...")
    
    try:
        monitor = setup_basic_health_monitoring()
        
        # Ejecutar un health check manual
        metrics = monitor.force_health_check()
        print(f"✅ Health check: {metrics.status.value}")
        
        # Mostrar resumen
        summary = monitor.get_health_summary()
        print(f"📊 Health summary: {summary}")
        
        print("✅ MT5 Health Monitoring System: OPERATIONAL")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
