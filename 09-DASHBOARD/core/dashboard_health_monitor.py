#!/usr/bin/env python3
"""
🏥 DASHBOARD HEALTH CHECKS SYSTEM
=================================

Sistema completo de health checks para todos los componentes del Dashboard Enterprise.
Proporciona monitoreo detallado de salud y métricas para cada componente.

Características:
- ✅ Health checks de componentes web
- ✅ Monitoreo de data processors
- ✅ Validación de UI components
- ✅ Métricas detalladas de performance
- ✅ Reporting automático de salud
- ⚡ Checks rápidos <5 segundos

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 18 de Septiembre, 2025
Versión: v1.0-health-monitoring
"""

import sys
import os
import time
import threading
import psutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Configurar rutas
dashboard_dir = Path(__file__).parent.parent.absolute()
project_root = dashboard_dir.parent

# Agregar paths (01-CORE primero para evitar conflictos)
sys.path.extend([
    str(project_root / "01-CORE"),  # Prioridad al 01-CORE
    str(project_root),
    str(dashboard_dir),
    str(dashboard_dir / "core")
])

try:
    from smart_trading_logger import SmartTradingLogger
    _LOGGER_AVAILABLE = True
except ImportError:
    _LOGGER_AVAILABLE = False
    # Fallback para logging básico
    import logging
    
    class FallbackLogger:
        def __init__(self):
            self.logger = logging.getLogger("DashboardHealthChecks")
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        def info(self, message): self.logger.info(message)
        def warning(self, message): self.logger.warning(message)
        def error(self, message): self.logger.error(message)
        def critical(self, message): self.logger.critical(message)
    
    SmartTradingLogger = FallbackLogger

class HealthStatus(Enum):
    """Estados de salud de los componentes"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    OFFLINE = "offline"

@dataclass
class ComponentHealth:
    """Información de salud de un componente"""
    component_name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_count: int
    warning_count: int
    uptime_seconds: float
    custom_metrics: Dict[str, Any]
    details: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario serializable"""
        result = asdict(self)
        result['status'] = self.status.value
        result['last_check'] = self.last_check.isoformat()
        return result

@dataclass
class SystemHealth:
    """Salud completa del sistema dashboard"""
    overall_status: HealthStatus
    components: List[ComponentHealth]
    system_metrics: Dict[str, Any]
    check_timestamp: datetime
    check_duration_ms: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario serializable"""
        return {
            'overall_status': self.overall_status.value,
            'components': [comp.to_dict() for comp in self.components],
            'system_metrics': self.system_metrics,
            'check_timestamp': self.check_timestamp.isoformat(),
            'check_duration_ms': self.check_duration_ms,
            'recommendations': self.recommendations
        }

class ComponentHealthChecker:
    """Checker base para componentes"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.start_time = datetime.now()
        self.error_count = 0
        self.warning_count = 0
        
    def check_health(self) -> ComponentHealth:
        """Ejecutar health check del componente"""
        start_time = time.time()
        
        try:
            # Métricas básicas
            memory_usage = self._get_memory_usage()
            cpu_usage = self._get_cpu_usage()
            
            # Health check específico del componente
            status, details, custom_metrics = self._perform_specific_checks()
            
            # Calcular response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Calcular uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time_ms,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                error_count=self.error_count,
                warning_count=self.warning_count,
                uptime_seconds=uptime_seconds,
                custom_metrics=custom_metrics,
                details=details
            )
            
        except Exception as e:
            self.error_count += 1
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.CRITICAL,
                last_check=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                error_count=self.error_count,
                warning_count=self.warning_count,
                uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
                custom_metrics={},
                details=f"Health check failed: {e}"
            )
    
    def _get_memory_usage(self) -> float:
        """Obtener uso de memoria del componente"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Obtener uso de CPU del componente"""
        try:
            process = psutil.Process()
            return process.cpu_percent()
        except:
            return 0.0
    
    def _perform_specific_checks(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Implementar checks específicos del componente (override en subclases)"""
        return HealthStatus.HEALTHY, "Base health check passed", {}

class DataProcessorHealthChecker(ComponentHealthChecker):
    """Health checker para los procesadores de datos"""
    
    def __init__(self, data_collector=None):
        super().__init__("DataProcessor")
        self.data_collector = data_collector
    
    def _perform_specific_checks(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Health checks específicos del data processor"""
        try:
            metrics = {
                'data_collector_active': False,
                'data_sources_connected': 0,
                'last_data_update': None,
                'data_processing_rate': 0,
                'buffer_size': 0,
                'memory_buffers_count': 0
            }
            
            if not self.data_collector:
                return HealthStatus.WARNING, "No data collector instance available", metrics
            
            metrics['data_collector_active'] = True
            
            # Verificar si el data collector tiene métodos esperados
            if hasattr(self.data_collector, 'is_connected'):
                try:
                    connected = self.data_collector.is_connected()
                    metrics['data_sources_connected'] = 1 if connected else 0
                except:
                    metrics['data_sources_connected'] = 0
            
            # Verificar última actualización de datos
            if hasattr(self.data_collector, 'get_last_update'):
                try:
                    last_update = self.data_collector.get_last_update()
                    if last_update:
                        metrics['last_data_update'] = last_update.isoformat() if hasattr(last_update, 'isoformat') else str(last_update)
                        
                        # Verificar si los datos son recientes (< 5 minutos)
                        if isinstance(last_update, datetime):
                            age = (datetime.now() - last_update).total_seconds()
                            if age > 300:  # 5 minutos
                                return HealthStatus.WARNING, f"Data is stale ({age:.0f}s old)", metrics
                except:
                    pass
            
            # Verificar rate de procesamiento
            if hasattr(self.data_collector, 'get_processing_rate'):
                try:
                    rate = self.data_collector.get_processing_rate()
                    metrics['data_processing_rate'] = rate
                    
                    if rate < 1:  # Menos de 1 operación por segundo
                        self.warning_count += 1
                        return HealthStatus.WARNING, f"Low processing rate: {rate} ops/sec", metrics
                except:
                    pass
            
            # Verificar buffers de memoria
            if hasattr(self.data_collector, 'get_buffer_info'):
                try:
                    buffer_info = self.data_collector.get_buffer_info()
                    if isinstance(buffer_info, dict):
                        metrics.update(buffer_info)
                except:
                    pass
            
            # Determinar estado final
            if metrics['data_sources_connected'] == 0:
                return HealthStatus.CRITICAL, "No data sources connected", metrics
            else:
                return HealthStatus.HEALTHY, f"Data processor healthy, {metrics['data_sources_connected']} sources connected", metrics
            
        except Exception as e:
            self.error_count += 1
            return HealthStatus.CRITICAL, f"Data processor health check failed: {e}", {'error': str(e)}

class UIComponentsHealthChecker(ComponentHealthChecker):
    """Health checker para componentes de interfaz de usuario"""
    
    def __init__(self, dashboard_instance=None):
        super().__init__("UIComponents")
        self.dashboard_instance = dashboard_instance
    
    def _perform_specific_checks(self) -> Tuple[HealthStatus, str, Dict[str, Any]]:
        """Health checks específicos de los UI components"""
        try:
            metrics = {
                'dashboard_instance_available': False,
                'ui_components_count': 0,
                'active_tabs': 0,
                'widget_count': 0,
                'layout_status': 'unknown',
                'rendering_issues': 0
            }
            
            if not self.dashboard_instance:
                return HealthStatus.WARNING, "No dashboard instance available", metrics
            
            metrics['dashboard_instance_available'] = True
            
            # Verificar componentes disponibles
            component_methods = ['get_active_tabs', 'get_widget_count', 'get_layout_status', 'check_rendering']
            issues = 0
            
            for method_name in component_methods:
                if hasattr(self.dashboard_instance, method_name):
                    try:
                        method = getattr(self.dashboard_instance, method_name)
                        result = method()
                        
                        if method_name == 'get_active_tabs':
                            metrics['active_tabs'] = result if isinstance(result, int) else len(result) if result else 0
                        elif method_name == 'get_widget_count':
                            metrics['widget_count'] = result if isinstance(result, int) else 0
                        elif method_name == 'get_layout_status':
                            metrics['layout_status'] = str(result)
                        elif method_name == 'check_rendering':
                            if not result:
                                issues += 1
                                
                    except Exception as e:
                        issues += 1
                        continue
            
            metrics['rendering_issues'] = issues
            
            # Determinar estado de salud
            if issues > 2:
                return HealthStatus.CRITICAL, f"Multiple UI issues detected ({issues})", metrics
            elif issues > 0:
                return HealthStatus.WARNING, f"Minor UI issues detected ({issues})", metrics
            elif metrics['widget_count'] == 0 and metrics['active_tabs'] == 0:
                return HealthStatus.WARNING, "No active UI components detected", metrics
            else:
                return HealthStatus.HEALTHY, f"UI components healthy ({metrics['widget_count']} widgets, {metrics['active_tabs']} tabs)", metrics
            
        except Exception as e:
            self.error_count += 1
            return HealthStatus.CRITICAL, f"UI components health check failed: {e}", {'error': str(e)}

class DashboardHealthMonitor:
    """Monitor completo de salud del dashboard"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar monitor de salud del dashboard
        
        Args:
            config: Configuración del sistema de health checks
        """
        self.config = self._setup_default_config()
        if config:
            self.config.update(config)
        
        # Configurar logging
        self.logger = SmartTradingLogger()
        
        # Health checkers
        self.health_checkers: Dict[str, ComponentHealthChecker] = {}
        
        # Estado del monitoreo
        self.is_monitoring = False
        self.monitoring_thread = None
        self.last_health_check = None
        
        # Histórico de salud
        self.health_history: List[SystemHealth] = []
        self.max_history_size = self.config.get('max_history_size', 100)
        
        self.logger.info("🏥 Dashboard Health Monitor inicializado")
    
    def _setup_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del health monitor (optimizado, sin web server)"""
        return {
            'check_interval': 60,  # Check cada minuto
            'max_history_size': 100,
            'auto_recovery_threshold': 3,  # Failures consecutivos antes de recovery
            'health_report_file': str(dashboard_dir / 'logs' / 'health_reports.json'),
            'enable_detailed_logging': True,
            'performance_thresholds': {
                'max_response_time_ms': 3000,  # Reducido de 5000ms a 3000ms
                'max_memory_usage_mb': 512,    # Reducido de 1024MB a 512MB
                'max_cpu_usage_percent': 70    # Reducido de 80% a 70%
            }
        }
    
    def register_data_processor(self, data_collector=None):
        """Registrar health checker para el data processor"""
        self.health_checkers['data_processor'] = DataProcessorHealthChecker(data_collector)
        self.logger.info("✅ Data processor health checker registrado")
    
    def register_ui_components(self, dashboard_instance=None):
        """Registrar health checker para UI components"""
        self.health_checkers['ui_components'] = UIComponentsHealthChecker(dashboard_instance)
        self.logger.info("✅ UI components health checker registrado")
    
    def perform_health_check(self) -> SystemHealth:
        """Ejecutar health check completo del sistema"""
        start_time = time.time()
        
        self.logger.info("🏥 Ejecutando health check completo del dashboard...")
        
        # Ejecutar health checks de componentes
        component_healths = []
        
        for checker_name, checker in self.health_checkers.items():
            try:
                self.logger.info(f"   🔍 Checking {checker_name}...")
                health = checker.check_health()
                component_healths.append(health)
                
                status_emoji = {
                    HealthStatus.HEALTHY: "✅",
                    HealthStatus.WARNING: "⚠️",
                    HealthStatus.CRITICAL: "❌",
                    HealthStatus.OFFLINE: "🔴",
                    HealthStatus.UNKNOWN: "❓"
                }.get(health.status, "❓")
                
                self.logger.info(f"   {status_emoji} {checker_name}: {health.status.value} ({health.response_time_ms:.1f}ms)")
                
            except Exception as e:
                self.logger.error(f"❌ Error checking {checker_name}: {e}")
                # Crear health record para componente fallido
                error_health = ComponentHealth(
                    component_name=checker_name,
                    status=HealthStatus.CRITICAL,
                    last_check=datetime.now(),
                    response_time_ms=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    error_count=1,
                    warning_count=0,
                    uptime_seconds=0,
                    custom_metrics={},
                    details=f"Health check exception: {e}"
                )
                component_healths.append(error_health)
        
        # Calcular estado general
        overall_status = self._calculate_overall_status(component_healths)
        
        # Métricas del sistema
        system_metrics = self._collect_system_metrics()
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(component_healths, system_metrics)
        
        # Crear SystemHealth
        check_duration_ms = (time.time() - start_time) * 1000
        
        system_health = SystemHealth(
            overall_status=overall_status,
            components=component_healths,
            system_metrics=system_metrics,
            check_timestamp=datetime.now(),
            check_duration_ms=check_duration_ms,
            recommendations=recommendations
        )
        
        # Guardar en histórico
        self.health_history.append(system_health)
        if len(self.health_history) > self.max_history_size:
            self.health_history.pop(0)
        
        self.last_health_check = system_health
        
        # Log resultado general
        overall_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.CRITICAL: "🚨",
            HealthStatus.OFFLINE: "🔴",
            HealthStatus.UNKNOWN: "❓"
        }.get(overall_status, "❓")
        
        self.logger.info(f"{overall_emoji} Health check completado: {overall_status.value} ({check_duration_ms:.1f}ms)")
        
        # Guardar reporte si está configurado
        if self.config.get('health_report_file'):
            self._save_health_report(system_health)
        
        return system_health
    
    def _calculate_overall_status(self, component_healths: List[ComponentHealth]) -> HealthStatus:
        """Calcular estado general basado en componentes"""
        if not component_healths:
            return HealthStatus.UNKNOWN
        
        critical_count = sum(1 for h in component_healths if h.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for h in component_healths if h.status == HealthStatus.WARNING)
        offline_count = sum(1 for h in component_healths if h.status == HealthStatus.OFFLINE)
        
        if critical_count > 0 or offline_count > 0:
            return HealthStatus.CRITICAL
        elif warning_count > 0:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas generales del sistema"""
        try:
            # Métricas de memoria
            memory = psutil.virtual_memory()
            
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            
            # Métricas de red (si están disponibles)
            network = psutil.net_io_counters()
            
            return {
                'memory': {
                    'total_mb': memory.total / 1024 / 1024,
                    'used_mb': memory.used / 1024 / 1024,
                    'available_mb': memory.available / 1024 / 1024,
                    'percent_used': memory.percent
                },
                'cpu': {
                    'percent_used': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'disk': {
                    'total_gb': disk.total / 1024 / 1024 / 1024,
                    'used_gb': disk.used / 1024 / 1024 / 1024,
                    'free_gb': disk.free / 1024 / 1024 / 1024,
                    'percent_used': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_received': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_received': network.packets_recv
                } if network else {},
                'processes': len(psutil.pids()),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, component_healths: List[ComponentHealth], system_metrics: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en el estado de salud"""
        recommendations = []
        
        # Recomendaciones por componente
        for health in component_healths:
            if health.status == HealthStatus.CRITICAL:
                recommendations.append(f"🚨 {health.component_name}: {health.details}")
            elif health.status == HealthStatus.WARNING:
                recommendations.append(f"⚠️ {health.component_name}: {health.details}")
                
            # Recomendaciones por performance
            if health.response_time_ms > self.config['performance_thresholds']['max_response_time_ms']:
                recommendations.append(f"⚡ {health.component_name}: Optimize response time ({health.response_time_ms:.1f}ms)")
                
            if health.memory_usage_mb > self.config['performance_thresholds']['max_memory_usage_mb']:
                recommendations.append(f"🧠 {health.component_name}: Reduce memory usage ({health.memory_usage_mb:.1f}MB)")
                
            if health.cpu_usage_percent > self.config['performance_thresholds']['max_cpu_usage_percent']:
                recommendations.append(f"⚙️ {health.component_name}: Optimize CPU usage ({health.cpu_usage_percent:.1f}%)")
        
        # Recomendaciones del sistema
        if 'memory' in system_metrics and system_metrics['memory']['percent_used'] > 80:
            recommendations.append("🧠 System: High memory usage detected, consider reducing dashboard components")
            
        if 'cpu' in system_metrics and system_metrics['cpu']['percent_used'] > 85:
            recommendations.append("⚙️ System: High CPU usage detected, consider optimizing dashboard processes")
            
        # Recomendaciones generales
        if len([h for h in component_healths if h.status in [HealthStatus.CRITICAL, HealthStatus.OFFLINE]]) > 1:
            recommendations.append("🔄 Consider restarting dashboard to resolve multiple component issues")
        
        return recommendations
    
    def _save_health_report(self, system_health: SystemHealth):
        """Guardar reporte de salud en archivo"""
        try:
            report_file = Path(self.config['health_report_file'])
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar reportes existentes
            reports = []
            if report_file.exists():
                try:
                    with open(report_file, 'r') as f:
                        reports = json.load(f)
                except:
                    reports = []
            
            # Agregar nuevo reporte
            reports.append(system_health.to_dict())
            
            # Mantener solo los últimos N reportes
            if len(reports) > self.max_history_size:
                reports = reports[-self.max_history_size:]
            
            # Guardar
            with open(report_file, 'w') as f:
                json.dump(reports, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving health report: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado de salud actual"""
        if not self.last_health_check:
            return {'status': 'no_data', 'message': 'No health checks performed yet'}
        
        health = self.last_health_check
        
        return {
            'overall_status': health.overall_status.value,
            'check_timestamp': health.check_timestamp.isoformat(),
            'components_count': len(health.components),
            'healthy_components': len([c for c in health.components if c.status == HealthStatus.HEALTHY]),
            'warning_components': len([c for c in health.components if c.status == HealthStatus.WARNING]),
            'critical_components': len([c for c in health.components if c.status == HealthStatus.CRITICAL]),
            'recommendations_count': len(health.recommendations),
            'check_duration_ms': health.check_duration_ms,
            'system_memory_percent': health.system_metrics.get('memory', {}).get('percent_used', 0),
            'system_cpu_percent': health.system_metrics.get('cpu', {}).get('percent_used', 0)
        }


def main():
    """Función principal para testing del health monitoring system"""
    print("🏥 Dashboard Health Monitor - Test Mode")
    
    # Crear monitor de salud
    health_monitor = DashboardHealthMonitor()
    
    # Registrar checkers de prueba (sin web server)
    health_monitor.register_data_processor()
    health_monitor.register_ui_components()
    
    # Ejecutar health check
    print("🔍 Ejecutando health check completo...")
    system_health = health_monitor.perform_health_check()
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DEL HEALTH CHECK:")
    print(f"   Estado general: {system_health.overall_status.value}")
    print(f"   Componentes: {len(system_health.components)}")
    print(f"   Duración: {system_health.check_duration_ms:.1f}ms")
    print(f"   Recomendaciones: {len(system_health.recommendations)}")
    
    for component in system_health.components:
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.CRITICAL: "❌",
            HealthStatus.OFFLINE: "🔴"
        }.get(component.status, "❓")
        
        print(f"   {status_emoji} {component.component_name}: {component.status.value}")
        print(f"      Response: {component.response_time_ms:.1f}ms")
        print(f"      Memory: {component.memory_usage_mb:.1f}MB")
        print(f"      Details: {component.details}")
    
    if system_health.recommendations:
        print(f"\n💡 RECOMENDACIONES:")
        for rec in system_health.recommendations:
            print(f"   {rec}")
    
    # Mostrar resumen
    print(f"\n📋 RESUMEN:")
    summary = health_monitor.get_health_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()