#!/usr/bin/env python3
"""
📊 BASELINE METRICS SYSTEM v6.0 ENTERPRISE
==========================================

Sistema de métricas baseline para medir mejoras de rendimiento del ICT Engine.
Establece KPIs de referencia y tracking de performance a lo largo del tiempo.

Funcionalidades:
- Medición de latencia de componentes clave
- Tracking de uso de memoria y CPU
- Métricas de rendimiento de trading
- Análisis comparativo de rendimiento
- Alertas de degradación de performance
- Reports automáticos de mejora/degradación

Autor: ICT Engine v6.0 Enterprise Team
Fecha: Septiembre 17, 2025
"""

import time
import json
import psutil
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import threading
import statistics
import gc

try:
    from protocols.unified_logging import get_unified_logger
    logger = get_unified_logger("BaselineMetrics")
except ImportError:
    import logging
    logger = logging.getLogger("BaselineMetrics")


class MetricCategory(Enum):
    """Categorías de métricas del sistema"""
    SYSTEM_PERFORMANCE = "system_performance"
    MEMORY_USAGE = "memory_usage"
    COMPONENT_LATENCY = "component_latency"
    TRADING_PERFORMANCE = "trading_performance"
    DATA_PROCESSING = "data_processing"
    NETWORK_LATENCY = "network_latency"


@dataclass
class MetricSnapshot:
    """Snapshot de una métrica en un punto específico del tiempo"""
    timestamp: datetime
    category: MetricCategory
    metric_name: str
    value: float
    unit: str
    component: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BaselineMetric:
    """Métrica baseline establecida"""
    metric_name: str
    category: MetricCategory
    baseline_value: float
    unit: str
    tolerance_percent: float  # % acceptable de desviación
    samples_count: int
    established_at: datetime
    last_updated: datetime
    min_value: float
    max_value: float
    avg_value: float
    std_deviation: float
    component: str


@dataclass
class PerformanceReport:
    """Reporte de performance comparado con baseline"""
    timestamp: datetime
    component: str
    metric_name: str
    current_value: float
    baseline_value: float
    deviation_percent: float
    status: str  # "improved", "degraded", "stable", "critical"
    impact_level: str  # "low", "medium", "high", "critical"
    recommendation: str


class BaselineMetricsSystem:
    """
    Sistema de métricas baseline para tracking de rendimiento del ICT Engine
    
    Establece baselines automáticamente durante los primeros días de operación
    y luego trackea desviaciones para identificar mejoras o degradaciones.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el sistema de métricas baseline
        
        Args:
            config: Configuración del sistema (opcional)
        """
        self.config = config or self._get_default_config()
        self.is_monitoring = False
        self.baseline_metrics: Dict[str, BaselineMetric] = {}
        self.metric_snapshots: List[MetricSnapshot] = []
        self.performance_reports: List[PerformanceReport] = []
        
        # Threading
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        
        # Paths
        self.data_dir = Path(self.config['data_directory'])
        self.baseline_file = self.data_dir / "baseline_metrics.json"
        self.snapshots_file = self.data_dir / "metric_snapshots.json"
        self.reports_file = self.data_dir / "performance_reports.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_baseline_metrics()
        self._load_snapshots()
        
        # Component timers for latency measurement
        self._component_timers: Dict[str, float] = {}
        self._lock = threading.Lock()
        
        logger.info("BaselineMetricsSystem initialized")
        logger.info(f"Monitoring {len(self.baseline_metrics)} baseline metrics")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del sistema"""
        return {
            'data_directory': '04-DATA/metrics/baseline',
            'monitoring_interval': 30.0,  # seconds
            'baseline_establishment_period': 7,  # days
            'min_samples_for_baseline': 100,
            'performance_tolerance': 20.0,  # % degradation threshold
            'critical_tolerance': 50.0,  # % critical degradation
            'snapshot_retention_days': 30,
            'auto_baseline_update': True,
            'components_to_monitor': [
                'mt5_data_manager',
                'smart_money_analyzer', 
                'pattern_detector',
                'unified_memory_system',
                'production_system_monitor'
            ]
        }
    
    def start_monitoring(self):
        """Inicia el monitoreo automático de métricas"""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.is_monitoring = True
        self._stop_event.clear()
        
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name="BaselineMetrics-Monitor"
        )
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
        
        logger.info("BaselineMetrics monitoring started")
    
    def stop_monitoring(self):
        """Detiene el monitoreo automático"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self._stop_event.set()
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)
        
        self._save_all_data()
        logger.info("BaselineMetrics monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        while not self._stop_event.wait(self.config['monitoring_interval']):
            try:
                self._collect_system_metrics()
                self._collect_component_metrics()
                self._analyze_performance()
                self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
        
        logger.info("Monitoring loop stopped")
    
    def _collect_system_metrics(self):
        """Recopila métricas del sistema operativo"""
        timestamp = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1.0)
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.SYSTEM_PERFORMANCE,
            metric_name="cpu_usage_percent",
            value=cpu_percent,
            unit="percent",
            component="system"
        )
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.MEMORY_USAGE,
            metric_name="memory_usage_percent",
            value=memory.percent,
            unit="percent",
            component="system"
        )
        
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.MEMORY_USAGE,
            metric_name="memory_available_gb",
            value=memory.available / (1024**3),
            unit="gb",
            component="system"
        )
        
        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self._record_metric(
                    timestamp=timestamp,
                    category=MetricCategory.SYSTEM_PERFORMANCE,
                    metric_name="disk_read_mb_per_sec",
                    value=disk_io.read_bytes / (1024**2),
                    unit="mb_per_sec",
                    component="system"
                )
        except Exception as e:
            logger.debug(f"Could not collect disk metrics: {e}")
    
    def _collect_component_metrics(self):
        """Recopila métricas de componentes ICT específicos"""
        timestamp = datetime.now()
        
        # Python garbage collection metrics
        gc_stats = gc.get_stats()
        if gc_stats:
            for i, stats in enumerate(gc_stats):
                self._record_metric(
                    timestamp=timestamp,
                    category=MetricCategory.MEMORY_USAGE,
                    metric_name=f"gc_generation_{i}_collections",
                    value=stats['collections'],
                    unit="count",
                    component="python_gc"
                )
        
        # Process-specific metrics
        current_process = psutil.Process()
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.MEMORY_USAGE,
            metric_name="process_memory_mb",
            value=current_process.memory_info().rss / (1024**2),
            unit="mb",
            component="ict_process"
        )
        
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.SYSTEM_PERFORMANCE,
            metric_name="process_cpu_percent",
            value=current_process.cpu_percent(),
            unit="percent",
            component="ict_process"
        )
        
        # Thread count
        self._record_metric(
            timestamp=timestamp,
            category=MetricCategory.SYSTEM_PERFORMANCE,
            metric_name="thread_count",
            value=current_process.num_threads(),
            unit="count",
            component="ict_process"
        )
    
    def _record_metric(self, timestamp: datetime, category: MetricCategory,
                      metric_name: str, value: float, unit: str, component: str,
                      metadata: Optional[Dict[str, Any]] = None):
        """Registra una nueva métrica"""
        snapshot = MetricSnapshot(
            timestamp=timestamp,
            category=category,
            metric_name=metric_name,
            value=value,
            unit=unit,
            component=component,
            metadata=metadata or {}
        )
        
        self.metric_snapshots.append(snapshot)
        
        # Try to establish or update baseline
        self._update_baseline(snapshot)
    
    def _update_baseline(self, snapshot: MetricSnapshot):
        """Actualiza o establece baseline para una métrica"""
        key = f"{snapshot.component}_{snapshot.metric_name}"
        
        if key in self.baseline_metrics:
            # Update existing baseline if configured
            if self.config['auto_baseline_update']:
                baseline = self.baseline_metrics[key]
                
                # Calculate new statistics
                recent_snapshots = [
                    s for s in self.metric_snapshots
                    if (s.component == snapshot.component and
                        s.metric_name == snapshot.metric_name and
                        s.timestamp > datetime.now() - timedelta(days=7))
                ]
                
                if len(recent_snapshots) >= 50:  # Enough data for update
                    values = [s.value for s in recent_snapshots]
                    
                    baseline.avg_value = statistics.mean(values)
                    baseline.min_value = min(values)
                    baseline.max_value = max(values)
                    baseline.std_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
                    baseline.samples_count = len(values)
                    baseline.last_updated = snapshot.timestamp
                    
        else:
            # Try to establish new baseline
            component_snapshots = [
                s for s in self.metric_snapshots
                if (s.component == snapshot.component and
                    s.metric_name == snapshot.metric_name)
            ]
            
            min_samples = self.config['min_samples_for_baseline']
            if len(component_snapshots) >= min_samples:
                values = [s.value for s in component_snapshots]
                
                # Establish new baseline
                baseline = BaselineMetric(
                    metric_name=snapshot.metric_name,
                    category=snapshot.category,
                    baseline_value=statistics.median(values),  # Use median as more robust
                    unit=snapshot.unit,
                    tolerance_percent=self.config['performance_tolerance'],
                    samples_count=len(values),
                    established_at=snapshot.timestamp,
                    last_updated=snapshot.timestamp,
                    min_value=min(values),
                    max_value=max(values),
                    avg_value=statistics.mean(values),
                    std_deviation=statistics.stdev(values) if len(values) > 1 else 0.0,
                    component=snapshot.component
                )
                
                self.baseline_metrics[key] = baseline
                logger.info(f"✅ Established baseline for {key}: {baseline.baseline_value:.2f} {baseline.unit}")
    
    def _analyze_performance(self):
        """Analiza el rendimiento actual vs baseline"""
        if not self.baseline_metrics:
            return
        
        current_time = datetime.now()
        
        for key, baseline in self.baseline_metrics.items():
            # Get recent snapshots for this metric
            recent_snapshots = [
                s for s in self.metric_snapshots
                if (s.component == baseline.component and
                    s.metric_name == baseline.metric_name and
                    s.timestamp > current_time - timedelta(minutes=10))
            ]
            
            if not recent_snapshots:
                continue
            
            # Calculate current performance
            recent_values = [s.value for s in recent_snapshots]
            current_value = statistics.mean(recent_values)
            
            # Calculate deviation
            deviation_percent = ((current_value - baseline.baseline_value) / baseline.baseline_value) * 100
            
            # Determine status
            status = self._determine_status(deviation_percent, baseline.metric_name)
            impact_level = self._determine_impact_level(abs(deviation_percent))
            recommendation = self._generate_recommendation(baseline.metric_name, deviation_percent, status)
            
            # Create performance report
            report = PerformanceReport(
                timestamp=current_time,
                component=baseline.component,
                metric_name=baseline.metric_name,
                current_value=current_value,
                baseline_value=baseline.baseline_value,
                deviation_percent=deviation_percent,
                status=status,
                impact_level=impact_level,
                recommendation=recommendation
            )
            
            # Only log significant deviations
            if abs(deviation_percent) > baseline.tolerance_percent:
                logger.warning(f"📊 Performance deviation detected: {key}")
                logger.warning(f"   Current: {current_value:.2f} {baseline.unit}")
                logger.warning(f"   Baseline: {baseline.baseline_value:.2f} {baseline.unit}")
                logger.warning(f"   Deviation: {deviation_percent:+.1f}%")
                logger.warning(f"   Status: {status}")
            
            self.performance_reports.append(report)
    
    def _determine_status(self, deviation_percent: float, metric_name: str) -> str:
        """Determina el status basado en la desviación"""
        abs_deviation = abs(deviation_percent)
        
        # For metrics where lower is better (latency, CPU, memory usage)
        lower_is_better = any(keyword in metric_name.lower() 
                            for keyword in ['latency', 'usage', 'cpu', 'memory', 'response_time'])
        
        if abs_deviation <= self.config['performance_tolerance']:
            return "stable"
        elif abs_deviation <= self.config['critical_tolerance']:
            if lower_is_better:
                return "degraded" if deviation_percent > 0 else "improved"
            else:
                return "improved" if deviation_percent > 0 else "degraded"
        else:
            return "critical"
    
    def _determine_impact_level(self, abs_deviation: float) -> str:
        """Determina el nivel de impacto"""
        if abs_deviation <= 10:
            return "low"
        elif abs_deviation <= 25:
            return "medium"
        elif abs_deviation <= 50:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendation(self, metric_name: str, deviation_percent: float, status: str) -> str:
        """Genera recomendación basada en la métrica y desviación"""
        recommendations = {
            ("cpu_usage_percent", "degraded"): "Consider optimizing CPU-intensive operations or increasing system resources",
            ("memory_usage_percent", "degraded"): "Investigate memory leaks or consider increasing available RAM",
            ("memory_available_gb", "degraded"): "Free up memory or increase system RAM",
            ("latency", "degraded"): "Optimize data processing pipeline or check network connectivity",
            ("response_time", "degraded"): "Profile and optimize slow components",
        }
        
        # Generic recommendations
        if status == "improved":
            return f"Performance improved by {abs(deviation_percent):.1f}% - monitor to ensure stability"
        elif status == "critical":
            return f"Critical performance degradation ({deviation_percent:+.1f}%) - immediate investigation required"
        
        # Specific recommendations
        for (metric_pattern, status_pattern), recommendation in recommendations.items():
            if metric_pattern in metric_name.lower() and status_pattern == status:
                return recommendation
        
        # Default
        return f"Monitor {metric_name} performance - deviation: {deviation_percent:+.1f}%"
    
    def _cleanup_old_data(self):
        """Limpia datos antiguos según la configuración"""
        cutoff_date = datetime.now() - timedelta(days=self.config['snapshot_retention_days'])
        
        # Clean snapshots
        original_count = len(self.metric_snapshots)
        self.metric_snapshots = [
            s for s in self.metric_snapshots
            if s.timestamp > cutoff_date
        ]
        cleaned_count = original_count - len(self.metric_snapshots)
        
        if cleaned_count > 0:
            logger.info(f"Cleaned {cleaned_count} old metric snapshots")
        
        # Clean performance reports
        original_reports = len(self.performance_reports)
        self.performance_reports = [
            r for r in self.performance_reports
            if r.timestamp > cutoff_date
        ]
        cleaned_reports = original_reports - len(self.performance_reports)
        
        if cleaned_reports > 0:
            logger.info(f"Cleaned {cleaned_reports} old performance reports")
    
    def get_baseline_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de todas las baselines establecidas"""
        return {
            'established_baselines': len(self.baseline_metrics),
            'total_snapshots': len(self.metric_snapshots),
            'recent_reports': len([
                r for r in self.performance_reports
                if r.timestamp > datetime.now() - timedelta(hours=24)
            ]),
            'categories': list(set(b.category.value for b in self.baseline_metrics.values())),
            'components': list(set(b.component for b in self.baseline_metrics.values())),
            'baselines': {
                key: {
                    'metric_name': baseline.metric_name,
                    'baseline_value': baseline.baseline_value,
                    'unit': baseline.unit,
                    'established_at': baseline.established_at.isoformat(),
                    'samples_count': baseline.samples_count
                }
                for key, baseline in self.baseline_metrics.items()
            }
        }
    
    def get_performance_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Genera reporte de performance de las últimas horas"""
        cutoff = datetime.now() - timedelta(hours=hours_back)
        recent_reports = [r for r in self.performance_reports if r.timestamp > cutoff]
        
        if not recent_reports:
            return {'message': 'No performance reports available for the specified period'}
        
        # Aggregate by status
        status_counts = {}
        impact_counts = {}
        
        for report in recent_reports:
            status_counts[report.status] = status_counts.get(report.status, 0) + 1
            impact_counts[report.impact_level] = impact_counts.get(report.impact_level, 0) + 1
        
        # Find critical issues
        critical_issues = [r for r in recent_reports if r.status == 'critical']
        improvements = [r for r in recent_reports if r.status == 'improved']
        
        return {
            'report_period_hours': hours_back,
            'total_reports': len(recent_reports),
            'status_distribution': status_counts,
            'impact_distribution': impact_counts,
            'critical_issues': len(critical_issues),
            'improvements_detected': len(improvements),
            'critical_details': [
                {
                    'component': r.component,
                    'metric': r.metric_name,
                    'deviation': f"{r.deviation_percent:+.1f}%",
                    'recommendation': r.recommendation
                }
                for r in critical_issues[:5]  # Top 5 critical issues
            ],
            'improvements_details': [
                {
                    'component': r.component,
                    'metric': r.metric_name,
                    'improvement': f"{abs(r.deviation_percent):.1f}%"
                }
                for r in improvements[:5]  # Top 5 improvements
            ]
        }
    
    # Context manager methods for component timing
    def start_component_timer(self, component: str) -> str:
        """Inicia timer para medir latencia de componente"""
        timer_id = f"{component}_{int(time.time() * 1000)}"
        with self._lock:
            self._component_timers[timer_id] = time.perf_counter()
        return timer_id
    
    def stop_component_timer(self, timer_id: str, component: str, operation: str = "general"):
        """Detiene timer y registra latencia"""
        with self._lock:
            start_time = self._component_timers.pop(timer_id, None)
        
        if start_time is None:
            logger.warning(f"Timer {timer_id} not found")
            return
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        self._record_metric(
            timestamp=datetime.now(),
            category=MetricCategory.COMPONENT_LATENCY,
            metric_name=f"{operation}_latency_ms",
            value=latency_ms,
            unit="ms",
            component=component,
            metadata={'operation': operation}
        )
    
    def _save_all_data(self):
        """Guarda todos los datos a disco"""
        try:
            # Save baselines
            baselines_data = {
                key: {
                    'metric_name': baseline.metric_name,
                    'category': baseline.category.value,
                    'baseline_value': baseline.baseline_value,
                    'unit': baseline.unit,
                    'tolerance_percent': baseline.tolerance_percent,
                    'samples_count': baseline.samples_count,
                    'established_at': baseline.established_at.isoformat(),
                    'last_updated': baseline.last_updated.isoformat(),
                    'min_value': baseline.min_value,
                    'max_value': baseline.max_value,
                    'avg_value': baseline.avg_value,
                    'std_deviation': baseline.std_deviation,
                    'component': baseline.component
                }
                for key, baseline in self.baseline_metrics.items()
            }
            
            with open(self.baseline_file, 'w') as f:
                json.dump(baselines_data, f, indent=2)
            
            logger.info(f"Saved {len(baselines_data)} baseline metrics")
            
        except Exception as e:
            logger.error(f"Error saving baseline data: {e}")
    
    def _load_baseline_metrics(self):
        """Carga métricas baseline desde disco"""
        if not self.baseline_file.exists():
            return
        
        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)
            
            for key, baseline_data in data.items():
                baseline = BaselineMetric(
                    metric_name=baseline_data['metric_name'],
                    category=MetricCategory(baseline_data['category']),
                    baseline_value=baseline_data['baseline_value'],
                    unit=baseline_data['unit'],
                    tolerance_percent=baseline_data['tolerance_percent'],
                    samples_count=baseline_data['samples_count'],
                    established_at=datetime.fromisoformat(baseline_data['established_at']),
                    last_updated=datetime.fromisoformat(baseline_data['last_updated']),
                    min_value=baseline_data['min_value'],
                    max_value=baseline_data['max_value'],
                    avg_value=baseline_data['avg_value'],
                    std_deviation=baseline_data['std_deviation'],
                    component=baseline_data['component']
                )
                self.baseline_metrics[key] = baseline
            
            logger.info(f"Loaded {len(self.baseline_metrics)} baseline metrics from disk")
            
        except Exception as e:
            logger.error(f"Error loading baseline metrics: {e}")
    
    def _load_snapshots(self):
        """Carga snapshots recientes desde disco"""
        if not self.snapshots_file.exists():
            return
        
        try:
            with open(self.snapshots_file, 'r') as f:
                data = json.load(f)
            
            cutoff = datetime.now() - timedelta(days=1)  # Only load recent snapshots
            
            for snapshot_data in data:
                timestamp = datetime.fromisoformat(snapshot_data['timestamp'])
                if timestamp > cutoff:
                    snapshot = MetricSnapshot(
                        timestamp=timestamp,
                        category=MetricCategory(snapshot_data['category']),
                        metric_name=snapshot_data['metric_name'],
                        value=snapshot_data['value'],
                        unit=snapshot_data['unit'],
                        component=snapshot_data['component'],
                        metadata=snapshot_data.get('metadata', {})
                    )
                    self.metric_snapshots.append(snapshot)
            
            logger.info(f"Loaded {len(self.metric_snapshots)} recent metric snapshots")
            
        except Exception as e:
            logger.error(f"Error loading metric snapshots: {e}")


# Factory function
def create_baseline_metrics_system(config: Optional[Dict[str, Any]] = None) -> BaselineMetricsSystem:
    """Factory para crear sistema de métricas baseline"""
    return BaselineMetricsSystem(config)


# Context manager for easy component timing
class ComponentTimer:
    """Context manager para medir latencia de componentes fácilmente"""
    
    def __init__(self, metrics_system: BaselineMetricsSystem, component: str, operation: str = "general"):
        self.metrics_system = metrics_system
        self.component = component
        self.operation = operation
        self.timer_id = None
    
    def __enter__(self):
        self.timer_id = self.metrics_system.start_component_timer(self.component)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer_id:
            self.metrics_system.stop_component_timer(self.timer_id, self.component, self.operation)


if __name__ == "__main__":
    # Test básico
    metrics_system = create_baseline_metrics_system()
    
    try:
        metrics_system.start_monitoring()
        logger.info("🚀 Baseline Metrics System started - Monitoring performance...")
        
        # Simulate some component work
        with ComponentTimer(metrics_system, "test_component", "data_processing"):
            time.sleep(0.1)  # Simulate work
        
        time.sleep(5)  # Let it collect some metrics
        
        # Get reports
        summary = metrics_system.get_baseline_summary()
        print("📊 Baseline Summary:")
        print(json.dumps(summary, indent=2))
        
        performance_report = metrics_system.get_performance_report(hours_back=1)
        print("\n📈 Performance Report:")
        print(json.dumps(performance_report, indent=2))
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping metrics system...")
    finally:
        metrics_system.stop_monitoring()
        logger.info("✅ Baseline Metrics System stopped")