"""
MT5 Health Monitoring - Black Box Logger v6.0 Enterprise
Sistema de logging tipo "caja negra" para análisis completo de health monitoring

Estructura de logs:
- 05-LOGS/health_monitoring/daily/         -> Logs diarios de health checks
- 05-LOGS/health_monitoring/alerts/        -> Logs de alertas y eventos críticos
- 05-LOGS/health_monitoring/performance/   -> Métricas de performance detalladas
- 05-LOGS/health_monitoring/connections/   -> Eventos de conexión/desconexión
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict
import threading

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

class MT5BlackBoxLogger:
    """
    🔍 Sistema de logging tipo caja negra para MT5 Health Monitoring
    Registra todos los eventos, métricas y estados para análisis posterior
    """
    
    def __init__(self, base_log_dir: Optional[str] = None):
        """
        Inicializar el logger de caja negra
        
        Args:
            base_log_dir: Directorio base para logs (default: 05-LOGS/health_monitoring)
        """
        if base_log_dir:
            self.base_log_dir = Path(base_log_dir)
        else:
            # Detectar automáticamente el directorio del proyecto
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            self.base_log_dir = project_root / "05-LOGS" / "health_monitoring"
        
        # Crear directorios si no existen
        self.daily_dir = self.base_log_dir / "daily"
        self.alerts_dir = self.base_log_dir / "alerts"
        self.performance_dir = self.base_log_dir / "performance"
        self.connections_dir = self.base_log_dir / "connections"
        
        for dir_path in [self.daily_dir, self.alerts_dir, self.performance_dir, self.connections_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Lock para thread-safety
        self._lock = threading.Lock()
        
        # Configurar loggers específicos
        self._setup_loggers()
        
        # Estadísticas de logging
        self.log_stats = {
            'health_checks_logged': 0,
            'alerts_logged': 0,
            'performance_entries': 0,
            'connection_events': 0,
            'start_time': datetime.now()
        }
        
    def _setup_loggers(self):
        """Configurar loggers específicos para cada tipo de evento"""
        
        # Logger para health checks diarios
        self.health_logger = logging.getLogger('MT5Health.Daily')
        self.health_logger.setLevel(logging.INFO)
        
        # Logger para alertas
        self.alert_logger = logging.getLogger('MT5Health.Alerts')
        self.alert_logger.setLevel(logging.WARNING)
        
        # Logger para performance
        self.performance_logger = logging.getLogger('MT5Health.Performance')
        self.performance_logger.setLevel(logging.INFO)
        
        # Logger para conexiones
        self.connection_logger = logging.getLogger('MT5Health.Connections')
        self.connection_logger.setLevel(logging.INFO)
        
        # Evitar duplicación de handlers
        for logger in [self.health_logger, self.alert_logger, self.performance_logger, self.connection_logger]:
            logger.handlers.clear()
            logger.propagate = False
        
    def log_health_check(self, metrics_data: Dict[str, Any]) -> None:
        """
        Registrar un health check completo
        
        Args:
            metrics_data: Datos de métricas del health check
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                
                # Preparar datos para logging
                log_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'HEALTH_CHECK',
                    'metrics': metrics_data,
                    'session_id': self._get_session_id()
                }
                
                # Log a archivo diario
                daily_file = self.daily_dir / f"health_checks_{date_str}.json"
                self._append_json_log(daily_file, log_entry)
                
                # Log formato legible
                readable_file = self.daily_dir / f"health_checks_{date_str}.log"
                readable_msg = self._format_health_check_readable(log_entry)
                self._append_text_log(readable_file, readable_msg)
                
                self.log_stats['health_checks_logged'] += 1
                
            except Exception as e:
                # Fallback logging en caso de error
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging health check: {e}")
                
    def log_alert(self, alert_type: str, metrics_data: Dict[str, Any], severity: str = "WARNING") -> None:
        """
        Registrar una alerta o evento crítico
        
        Args:
            alert_type: Tipo de alerta (WARNING, CRITICAL, RECONNECTION, etc.)
            metrics_data: Datos asociados con la alerta
            severity: Severidad del evento
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                
                alert_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'ALERT',
                    'alert_type': alert_type,
                    'severity': severity,
                    'metrics': metrics_data,
                    'session_id': self._get_session_id()
                }
                
                # Log a archivo de alertas
                alert_file = self.alerts_dir / f"alerts_{date_str}.json"
                self._append_json_log(alert_file, alert_entry)
                
                # Log formato legible para alertas críticas
                if severity in ['CRITICAL', 'ERROR']:
                    critical_file = self.alerts_dir / f"critical_alerts_{date_str}.log"
                    critical_msg = self._format_alert_readable(alert_entry)
                    self._append_text_log(critical_file, critical_msg)
                
                self.log_stats['alerts_logged'] += 1
                
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging alert: {e}")
                
    def log_performance_metrics(self, response_time: float, throughput: float, 
                              system_metrics: Dict[str, Any]) -> None:
        """
        Registrar métricas de performance detalladas
        
        Args:
            response_time: Tiempo de respuesta en ms
            throughput: Throughput de operaciones
            system_metrics: Métricas del sistema (CPU, memoria, etc.)
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                hour_str = timestamp.strftime('%H')
                
                perf_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'PERFORMANCE',
                    'response_time_ms': response_time,
                    'throughput': throughput,
                    'system_metrics': system_metrics,
                    'session_id': self._get_session_id()
                }
                
                # Log por hora para análisis granular
                perf_file = self.performance_dir / f"performance_{date_str}_{hour_str}h.json"
                self._append_json_log(perf_file, perf_entry)
                
                # Log resumen diario
                daily_perf_file = self.performance_dir / f"performance_daily_{date_str}.log"
                perf_msg = f"{timestamp.isoformat()} | Response: {response_time:.1f}ms | Throughput: {throughput:.2f} | CPU: {system_metrics.get('cpu_percent', 0):.1f}% | Memory: {system_metrics.get('memory_gb', 0):.2f}GB"
                self._append_text_log(daily_perf_file, perf_msg)
                
                self.log_stats['performance_entries'] += 1
                
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging performance: {e}")
                
    def log_connection_event(self, event_type: str, connection_data: Dict[str, Any]) -> None:
        """
        Registrar eventos de conexión/desconexión
        
        Args:
            event_type: Tipo de evento (CONNECT, DISCONNECT, RECONNECT, FAIL)
            connection_data: Datos de la conexión
        """
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                
                conn_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'CONNECTION',
                    'connection_event': event_type,
                    'connection_data': connection_data,
                    'session_id': self._get_session_id()
                }
                
                # Log de conexiones
                conn_file = self.connections_dir / f"connections_{date_str}.json"
                self._append_json_log(conn_file, conn_entry)
                
                # Log readable para eventos importantes
                if event_type in ['CONNECT', 'DISCONNECT', 'FAIL']:
                    readable_file = self.connections_dir / f"connections_{date_str}.log"
                    readable_msg = self._format_connection_readable(conn_entry)
                    self._append_text_log(readable_file, readable_msg)
                
                self.log_stats['connection_events'] += 1
                
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging connection: {e}")
                
    def log_system_startup(self, startup_data: Dict[str, Any]) -> None:
        """Registrar inicio del sistema de monitoring"""
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                
                startup_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'SYSTEM_STARTUP',
                    'startup_data': startup_data,
                    'session_id': self._get_session_id()
                }
                
                # Log en todos los directorios para marca de tiempo
                for log_dir in [self.daily_dir, self.alerts_dir, self.performance_dir, self.connections_dir]:
                    startup_file = log_dir / f"system_startup_{date_str}.json"
                    self._append_json_log(startup_file, startup_entry)
                
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging startup: {e}")
                
    def log_system_shutdown(self, shutdown_data: Dict[str, Any]) -> None:
        """Registrar cierre del sistema de monitoring"""
        with self._lock:
            try:
                timestamp = datetime.now()
                date_str = timestamp.strftime('%Y-%m-%d')
                
                # Agregar estadísticas finales
                final_stats = {
                    **shutdown_data,
                    'final_statistics': self.log_stats,
                    'session_duration': str(timestamp - self.log_stats['start_time'])
                }
                
                shutdown_entry = {
                    'timestamp': timestamp.isoformat(),
                    'event_type': 'SYSTEM_SHUTDOWN',
                    'shutdown_data': final_stats,
                    'session_id': self._get_session_id()
                }
                
                # Log en todos los directorios
                for log_dir in [self.daily_dir, self.alerts_dir, self.performance_dir, self.connections_dir]:
                    shutdown_file = log_dir / f"system_shutdown_{date_str}.json"
                    self._append_json_log(shutdown_file, shutdown_entry)
                
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{timestamp.isoformat()}: Error logging shutdown: {e}")
                
    def get_logging_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de logging"""
        uptime = datetime.now() - self.log_stats['start_time']
        
        return {
            **self.log_stats,
            'uptime': str(uptime),
            'uptime_seconds': uptime.total_seconds(),
            'logs_per_minute': self.log_stats['health_checks_logged'] / max(uptime.total_seconds() / 60, 1),
            'base_log_dir': str(self.base_log_dir)
        }
        
    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """
        Limpiar logs antiguos
        
        Args:
            days_to_keep: Días de logs a conservar
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_dir in [self.daily_dir, self.alerts_dir, self.performance_dir, self.connections_dir]:
            try:
                for file_path in log_dir.glob("*"):
                    if file_path.is_file():
                        # Extraer fecha del nombre del archivo
                        try:
                            date_part = file_path.stem.split('_')[-1]
                            if len(date_part) == 10 and date_part.count('-') == 2:  # YYYY-MM-DD
                                file_date = datetime.strptime(date_part, '%Y-%m-%d')
                                if file_date < cutoff_date:
                                    file_path.unlink()
                        except (ValueError, IndexError):
                            continue  # Skip files with non-standard names
                            
            except Exception as e:
                fallback_file = self.base_log_dir / "logging_errors.log"
                self._append_text_log(fallback_file, f"{datetime.now().isoformat()}: Error cleaning logs: {e}")
                
    def _append_json_log(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Agregar entrada JSON a un archivo de log"""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
                f.write('\\n')
        except Exception as e:
            # Fallback si no se puede escribir
            pass
            
    def _append_text_log(self, file_path: Path, message: str) -> None:
        """Agregar línea de texto a un archivo de log"""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{message}\\n")
        except Exception as e:
            # Fallback si no se puede escribir
            pass
            
    def _format_health_check_readable(self, log_entry: Dict[str, Any]) -> str:
        """Formatear health check para lectura humana"""
        metrics = log_entry.get('metrics', {})
        timestamp = log_entry.get('timestamp', 'N/A')
        
        status = metrics.get('status', 'UNKNOWN')
        response_time = metrics.get('response_time_ms', 0)
        connection = metrics.get('connection_active', False)
        failed_checks = metrics.get('failed_checks_count', 0)
        
        return f"{timestamp} | STATUS: {status} | Connection: {'✅' if connection else '❌'} | Response: {response_time:.1f}ms | Failed: {failed_checks}"
        
    def _format_alert_readable(self, alert_entry: Dict[str, Any]) -> str:
        """Formatear alerta para lectura humana"""
        timestamp = alert_entry.get('timestamp', 'N/A')
        alert_type = alert_entry.get('alert_type', 'UNKNOWN')
        severity = alert_entry.get('severity', 'INFO')
        
        return f"{timestamp} | 🚨 {severity} ALERT: {alert_type} | Metrics: {alert_entry.get('metrics', {})}"
        
    def _format_connection_readable(self, conn_entry: Dict[str, Any]) -> str:
        """Formatear evento de conexión para lectura humana"""
        timestamp = conn_entry.get('timestamp', 'N/A')
        event = conn_entry.get('connection_event', 'UNKNOWN')
        conn_data = conn_entry.get('connection_data', {})
        
        server = conn_data.get('server', 'N/A')
        account = conn_data.get('account', 'N/A')
        
        return f"{timestamp} | CONNECTION {event} | Server: {server} | Account: {account}"
        
    def _get_session_id(self) -> str:
        """Obtener ID de sesión único"""
        return f"MT5Health_{self.log_stats['start_time'].strftime('%Y%m%d_%H%M%S')}"

# Función de utilidad para integración fácil
def create_black_box_logger(base_log_dir: Optional[str] = None) -> MT5BlackBoxLogger:
    """Factory function para crear un logger de caja negra"""
    return MT5BlackBoxLogger(base_log_dir)

if __name__ == "__main__":
    # Ejemplo de uso del logger
    logger = create_black_box_logger()
    
    # Log de ejemplo
    sample_metrics = {
        'status': 'HEALTHY',
        'connection_active': True,
        'response_time_ms': 150.5,
        'failed_checks_count': 0,
        'account_balance': 1000.0
    }
    
    logger.log_health_check(sample_metrics)
    logger.log_alert('CONNECTION_WARNING', sample_metrics, 'WARNING')
    
    stats = logger.get_logging_statistics()
    print(f"Logging statistics: {stats}")
