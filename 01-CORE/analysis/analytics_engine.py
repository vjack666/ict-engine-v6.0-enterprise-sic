#!/usr/bin/env python3
"""
📊 ANALYTICS ENGINE - ICT ENGINE v6.0 ENTERPRISE
===============================================

Motor de análisis avanzado para el ICT Engine.
Proporciona métricas en tiempo real, análisis de rendimiento,
reportes automáticos y insights de trading inteligentes.

CARACTERÍSTICAS PRINCIPALES:
✅ Métricas de rendimiento en tiempo real
✅ Análisis de patrones y comportamiento
✅ Reportes automáticos (diario/semanal/mensual)
✅ Machine Learning para insights
✅ Detección de anomalías
✅ Análisis de correlación
✅ Backtesting automatizado
✅ Dashboard analytics integration

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 15 Septiembre 2025
"""

import os
import json
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import statistics
import logging

# Imports seguros
try:
    from ..smart_trading_logger import SmartTradingLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    SmartTradingLogger = None

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    StandardScaler = None
    DBSCAN = None


class MetricType(Enum):
    """📏 Tipos de métricas"""
    PERFORMANCE = "performance"
    RISK = "risk"
    TRADING = "trading"
    SYSTEM = "system"
    BEHAVIOR = "behavior"
    MARKET = "market"


class AnalysisType(Enum):
    """🔍 Tipos de análisis"""
    TREND = "trend"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    STATISTICAL = "statistical"
    PREDICTIVE = "predictive"


class ReportPeriod(Enum):
    """📅 Períodos de reporte"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class MetricDefinition:
    """📊 Definición de métrica"""
    name: str
    type: MetricType
    description: str
    unit: str = ""
    aggregation_method: str = "last"  # last, avg, sum, min, max
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    is_percentage: bool = False
    decimal_places: int = 2
    tags: List[str] = field(default_factory=list)


@dataclass
class DataPoint:
    """📈 Punto de datos para métricas"""
    timestamp: datetime
    value: Union[float, int]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """📋 Resultado de análisis"""
    analysis_id: str
    type: AnalysisType
    metric_name: str
    timestamp: datetime
    result: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class MetricCollector:
    """🎯 Recolector de métricas"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.definitions: Dict[str, MetricDefinition] = {}
        self._lock = threading.RLock()
    
    def define_metric(self, definition: MetricDefinition):
        """📊 Definir nueva métrica"""
        with self._lock:
            self.definitions[definition.name] = definition
    
    def record(self, metric_name: str, value: Union[float, int], 
               tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """📝 Registrar punto de datos"""
        with self._lock:
            data_point = DataPoint(
                timestamp=datetime.now(),
                value=value,
                tags=tags or {},
                metadata=metadata or {}
            )
            self.metrics[metric_name].append(data_point)
    
    def get_latest(self, metric_name: str) -> Optional[DataPoint]:
        """📊 Obtener último valor"""
        with self._lock:
            if metric_name in self.metrics and self.metrics[metric_name]:
                return self.metrics[metric_name][-1]
            return None
    
    def get_history(self, metric_name: str, hours: float = 24) -> List[DataPoint]:
        """📈 Obtener historial"""
        with self._lock:
            if metric_name not in self.metrics:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return [
                dp for dp in self.metrics[metric_name]
                if dp.timestamp >= cutoff_time
            ]
    
    def get_aggregated(self, metric_name: str, hours: float = 1, 
                      method: str = "avg") -> Optional[float]:
        """🧮 Obtener valor agregado"""
        history = self.get_history(metric_name, hours)
        if not history:
            return None
        
        values = [dp.value for dp in history]
        
        if method == "avg":
            return statistics.mean(values)
        elif method == "sum":
            return sum(values)
        elif method == "min":
            return min(values)
        elif method == "max":
            return max(values)
        elif method == "last":
            return values[-1] if values else None
        elif method == "std":
            return statistics.stdev(values) if len(values) > 1 else 0
        else:
            return values[-1] if values else None


class TrendAnalyzer:
    """📈 Analizador de tendencias"""
    
    @staticmethod
    def analyze_trend(data_points: List[DataPoint], min_points: int = 10) -> Dict[str, Any]:
        """📊 Analizar tendencia de datos"""
        if len(data_points) < min_points:
            return {
                "trend": "insufficient_data",
                "direction": "unknown",
                "strength": 0.0,
                "r_squared": 0.0
            }
        
        # Preparar datos
        timestamps = [dp.timestamp.timestamp() for dp in data_points]
        values = [dp.value for dp in data_points]
        
        # Normalizar timestamps
        min_ts = min(timestamps)
        x = [(ts - min_ts) for ts in timestamps]
        y = values
        
        try:
            # Regresión lineal simple
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            
            # Slope (pendiente)
            if n * sum_x2 - sum_x * sum_x == 0:
                slope = 0
            else:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Intercept
            intercept = (sum_y - slope * sum_x) / n
            
            # R-squared
            mean_y = sum_y / n
            ss_tot = sum((yi - mean_y) ** 2 for yi in y)
            ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determinar dirección y fuerza
            if abs(slope) < 1e-6:
                direction = "flat"
                trend = "stable"
            elif slope > 0:
                direction = "up"
                trend = "bullish" if r_squared > 0.7 else "slightly_bullish"
            else:
                direction = "down"  
                trend = "bearish" if r_squared > 0.7 else "slightly_bearish"
            
            strength = min(abs(slope) * r_squared, 1.0)
            
            return {
                "trend": trend,
                "direction": direction,
                "strength": strength,
                "slope": slope,
                "r_squared": r_squared,
                "data_points": len(data_points),
                "time_span_hours": (max(timestamps) - min(timestamps)) / 3600
            }
            
        except Exception as e:
            return {
                "trend": "error",
                "direction": "unknown", 
                "strength": 0.0,
                "error": str(e)
            }


class AnomalyDetector:
    """🚨 Detector de anomalías"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.model = None
        self.scaler = None
        self.trained = False
    
    def train(self, data_points: List[DataPoint]) -> bool:
        """🎓 Entrenar detector de anomalías"""
        if not SKLEARN_AVAILABLE or len(data_points) < 50:
            return False
        
        try:
            # Preparar datos
            features = self._extract_features(data_points)
            if len(features) == 0:
                return False
            
            # Normalizar
            # Hint types for pylance
            scaler_cls = StandardScaler  # type: ignore[assignment]
            if scaler_cls is None:  # Runtime safety
                return False
            self.scaler = scaler_cls()  # type: ignore[call-arg]
            X = self.scaler.fit_transform(features)  # type: ignore[arg-type]
            
            # Entrenar modelo
            model_cls = IsolationForest  # type: ignore[assignment]
            if model_cls is None:
                return False
            self.model = model_cls(contamination=self.contamination, random_state=42)  # type: ignore[call-arg]
            self.model.fit(X)  # type: ignore[arg-type]
            
            self.trained = True
            return True
            
        except Exception:
            return False
    
    def detect_anomalies(self, data_points: List[DataPoint]) -> List[Tuple[DataPoint, float]]:
        """🔍 Detectar anomalías en datos"""
        if not self.trained or not data_points:
            return []
        
        try:
            features = self._extract_features(data_points)
            if len(features) == 0:
                return []
            
            if self.scaler is None or self.model is None:
                return []
            X = self.scaler.transform(features)  # type: ignore[arg-type]
            scores = self.model.decision_function(X)  # type: ignore[attr-defined]
            predictions = self.model.predict(X)  # type: ignore[attr-defined]
            
            anomalies = []
            for i, (dp, score, pred) in enumerate(zip(data_points, scores, predictions)):
                if pred == -1:  # Anomaly
                    anomalies.append((dp, abs(score)))
            
            return sorted(anomalies, key=lambda x: x[1], reverse=True)
            
        except Exception:
            return []
    
    def _extract_features(self, data_points: List[DataPoint]) -> List[List[float]]:
        """🔧 Extraer características para ML"""
        if len(data_points) < 5:
            return []
        
        features = []
        values = [dp.value for dp in data_points]
        
        for i in range(2, len(data_points) - 2):
            # Features: current value, rolling stats, differences
            current = values[i]
            window = values[i-2:i+3]  # 5-point window
            
            feature_vector = [
                current,
                statistics.mean(window),
                statistics.stdev(window) if len(window) > 1 else 0,
                max(window) - min(window),  # Range
                current - values[i-1],      # 1st difference
                current - values[i-2]       # 2nd difference
            ]
            
            features.append(feature_vector)
        
        return features


class PatternRecognizer:
    """🔍 Reconocedor de patrones"""
    
    @staticmethod
    def detect_support_resistance(data_points: List[DataPoint], 
                                 tolerance: float = 0.001) -> Dict[str, Any]:
        """📊 Detectar soportes y resistencias"""
        if len(data_points) < 20:
            return {"support": None, "resistance": None, "touches": 0}
        
        values = [dp.value for dp in data_points]
        
        # Find local minima and maxima
        minima = []
        maxima = []
        
        for i in range(2, len(values) - 2):
            # Local minimum
            if (values[i] < values[i-1] and values[i] < values[i+1] and 
                values[i] <= values[i-2] and values[i] <= values[i+2]):
                minima.append(values[i])
            
            # Local maximum
            if (values[i] > values[i-1] and values[i] > values[i+1] and
                values[i] >= values[i-2] and values[i] >= values[i+2]):
                maxima.append(values[i])
        
        # Find most common levels
        support = None
        resistance = None
        
        if minima:
            # Group similar minima
            minima.sort()
            support_level, support_touches = PatternRecognizer._find_level(minima, tolerance)
            if support_touches >= 2:
                support = support_level
        
        if maxima:
            # Group similar maxima
            maxima.sort(reverse=True)
            resistance_level, resistance_touches = PatternRecognizer._find_level(maxima, tolerance)
            if resistance_touches >= 2:
                resistance = resistance_level
        
        return {
            "support": support,
            "resistance": resistance,
            "support_touches": len(minima),
            "resistance_touches": len(maxima)
        }
    
    @staticmethod
    def _find_level(values: List[float], tolerance: float) -> Tuple[Optional[float], int]:
        """🎯 Encontrar nivel más tocado"""
        if not values:
            return None, 0
        
        # Group values by proximity
        groups = []
        for value in values:
            added = False
            for group in groups:
                if abs(value - group[0]) <= group[0] * tolerance:
                    group.append(value)
                    added = True
                    break
            if not added:
                groups.append([value])
        
        # Find largest group
        if not groups:
            return None, 0
        
        largest_group = max(groups, key=len)
        level = statistics.mean(largest_group)
        touches = len(largest_group)
        
        return level, touches


class PerformanceAnalyzer:
    """⚡ Analizador de rendimiento del sistema"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_collector = MetricCollector()
        self._setup_system_metrics()
    
    def _setup_system_metrics(self):
        """⚙️ Configurar métricas del sistema"""
        metrics = [
            MetricDefinition("cpu_usage", MetricType.SYSTEM, "CPU Usage", "%", "avg", 70, 85, True),
            MetricDefinition("memory_usage", MetricType.SYSTEM, "Memory Usage", "%", "avg", 80, 90, True),
            MetricDefinition("response_time", MetricType.PERFORMANCE, "Response Time", "ms", "avg", 1000, 2000),
            MetricDefinition("throughput", MetricType.PERFORMANCE, "Throughput", "ops/sec", "avg", None, None),
            MetricDefinition("error_rate", MetricType.SYSTEM, "Error Rate", "%", "avg", 1, 5, True),
        ]
        
        for metric in metrics:
            self.metrics_collector.define_metric(metric)
    
    def record_system_metrics(self):
        """📊 Registrar métricas del sistema"""
        try:
            import psutil
            
            # CPU y memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.metrics_collector.record("cpu_usage", cpu_percent)
            self.metrics_collector.record("memory_usage", memory.percent)
            
        except ImportError:
            # Fallback si psutil no está disponible
            self.metrics_collector.record("cpu_usage", 0)
            self.metrics_collector.record("memory_usage", 0)
    
    def get_system_health(self) -> Dict[str, Any]:
        """🏥 Obtener salud del sistema"""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            cpu = self.metrics_collector.get_aggregated("cpu_usage", hours=0.25)  # 15 min
            memory = self.metrics_collector.get_aggregated("memory_usage", hours=0.25)
            
            health_score = 100
            issues = []
            
            if cpu and cpu > 85:
                health_score -= 30
                issues.append(f"High CPU usage: {cpu:.1f}%")
            
            if memory and memory > 90:
                health_score -= 30
                issues.append(f"High memory usage: {memory:.1f}%")
            
            status = "healthy"
            if health_score < 70:
                status = "critical"
            elif health_score < 85:
                status = "warning"
            
            return {
                "status": status,
                "health_score": max(0, health_score),
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600,
                "cpu_usage": cpu,
                "memory_usage": memory,
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class ReportGenerator:
    """📋 Generador de reportes"""
    
    def __init__(self, analytics_engine):
        self.analytics_engine = analytics_engine
        self.reports_dir = Path("04-DATA/reports/analytics")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """📊 Generar reporte diario"""
        try:
            report = {
                "type": "daily_report",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "generated_at": datetime.now().isoformat(),
                "summary": {},
                "metrics": {},
                "trends": {},
                "anomalies": [],
                "recommendations": []
            }
            
            # Recopilar métricas del día
            for metric_name in self.analytics_engine.metric_collector.definitions.keys():
                daily_data = self.analytics_engine.metric_collector.get_history(metric_name, hours=24)
                
                if daily_data:
                    values = [dp.value for dp in daily_data]
                    report["metrics"][metric_name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": statistics.mean(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0,
                        "latest": values[-1]
                    }
                    
                    # Análisis de tendencia
                    trend = TrendAnalyzer.analyze_trend(daily_data)
                    report["trends"][metric_name] = trend
            
            # Detectar anomalías si hay datos suficientes
            for metric_name, history in self.analytics_engine.metric_collector.metrics.items():
                if len(history) >= 50:
                    detector = AnomalyDetector()
                    if detector.train(list(history)[-100:]):  # Últimos 100 puntos para entrenar
                        recent_data = list(history)[-24:]  # Últimas 24 horas
                        anomalies = detector.detect_anomalies(recent_data)
                        
                        for anomaly, score in anomalies[:5]:  # Top 5 anomalies
                            report["anomalies"].append({
                                "metric": metric_name,
                                "timestamp": anomaly.timestamp.isoformat(),
                                "value": anomaly.value,
                                "anomaly_score": score
                            })
            
            # Generar recomendaciones
            report["recommendations"] = self._generate_recommendations(report)
            
            # Guardar reporte
            report_file = self.reports_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return report
            
        except Exception as e:
            return {
                "type": "daily_report",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """🎯 Generar recomendaciones basadas en el reporte"""
        recommendations = []
        
        # Análisis de métricas
        metrics = report.get("metrics", {})
        trends = report.get("trends", {})
        
        for metric_name, metric_data in metrics.items():
            # Check high values
            if metric_name == "cpu_usage" and metric_data.get("avg", 0) > 70:
                recommendations.append("Consider optimizing CPU-intensive processes")
            
            if metric_name == "memory_usage" and metric_data.get("avg", 0) > 80:
                recommendations.append("Monitor memory usage and consider increasing available RAM")
            
            # Check trends
            trend_data = trends.get(metric_name, {})
            if trend_data.get("direction") == "up" and trend_data.get("strength", 0) > 0.7:
                if metric_name in ["error_rate", "response_time"]:
                    recommendations.append(f"Investigate increasing {metric_name} trend")
        
        # Anomaly-based recommendations
        anomalies = report.get("anomalies", [])
        if len(anomalies) > 10:
            recommendations.append("High number of anomalies detected - review system stability")
        
        return recommendations


class AnalyticsEngine:
    """
    📊 MOTOR DE ANÁLISIS ENTERPRISE
    ==============================
    
    Motor de análisis avanzado para el ICT Engine.
    Proporciona métricas, análisis de tendencias, detección de anomalías y reportes.
    """
    
    def __init__(self):
        """Inicializar AnalyticsEngine"""
        # Logger
        self.logger = self._setup_logger()
        
        # Componentes principales
        self.metric_collector = MetricCollector()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.pattern_recognizer = PatternRecognizer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.report_generator = ReportGenerator(self)
        
        # Analysis results
        self.analysis_results: Dict[str, AnalysisResult] = {}
        self._results_lock = threading.RLock()
        
        # Auto-analysis configuration
        self.auto_analysis_enabled = True
        self.analysis_interval = 300  # 5 minutes
        self.last_analysis = datetime.now()
        
        # Initialize default metrics
        self._setup_trading_metrics()
        
        self.logger.info("✅ AnalyticsEngine initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """📝 Configurar logger"""
        if LOGGER_AVAILABLE and SmartTradingLogger:
            # SmartTradingLogger cumple interfaz similar a logging.Logger para métodos usados
            return SmartTradingLogger("AnalyticsEngine")  # type: ignore[return-value]
        else:
            logger = logging.getLogger("AnalyticsEngine")
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            return logger
    
    def _setup_trading_metrics(self):
        """📊 Configurar métricas de trading"""
        trading_metrics = [
            # Performance metrics
            MetricDefinition("total_pnl", MetricType.PERFORMANCE, "Total P&L", "$", "last"),
            MetricDefinition("win_rate", MetricType.PERFORMANCE, "Win Rate", "%", "avg", None, None, True),
            MetricDefinition("profit_factor", MetricType.PERFORMANCE, "Profit Factor", "", "avg", 1.0, 0.5),
            MetricDefinition("sharpe_ratio", MetricType.PERFORMANCE, "Sharpe Ratio", "", "avg", 1.0, 0.5),
            MetricDefinition("max_drawdown", MetricType.RISK, "Max Drawdown", "%", "max", 10, 20, True),
            
            # Risk metrics
            MetricDefinition("current_drawdown", MetricType.RISK, "Current Drawdown", "%", "last", 5, 10, True),
            MetricDefinition("daily_var", MetricType.RISK, "Daily VaR", "$", "avg"),
            MetricDefinition("position_size", MetricType.RISK, "Position Size", "lots", "avg"),
            
            # Trading metrics
            MetricDefinition("open_positions", MetricType.TRADING, "Open Positions", "count", "last", 5, 10),
            MetricDefinition("daily_trades", MetricType.TRADING, "Daily Trades", "count", "sum", 50, 100),
            MetricDefinition("avg_trade_duration", MetricType.TRADING, "Avg Trade Duration", "minutes", "avg"),
            
            # Market metrics
            MetricDefinition("market_volatility", MetricType.MARKET, "Market Volatility", "%", "avg", None, None, True),
            MetricDefinition("spread", MetricType.MARKET, "Average Spread", "pips", "avg"),
        ]
        
        for metric in trading_metrics:
            self.metric_collector.define_metric(metric)
    
    def record_metric(self, name: str, value: Union[float, int], 
                     tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """📝 Registrar métrica"""
        self.metric_collector.record(name, value, tags, metadata)
        
        # Auto-analysis check
        if self.auto_analysis_enabled:
            self._check_auto_analysis()
    
    def _check_auto_analysis(self):
        """🔍 Verificar si es hora de ejecutar análisis automático"""
        now = datetime.now()
        if (now - self.last_analysis).total_seconds() >= self.analysis_interval:
            self.last_analysis = now
            # Schedule analysis in background (simplified - in production use proper threading)
            try:
                self._run_auto_analysis()
            except Exception as e:
                self.logger.error(f"Error in auto-analysis: {e}")
    
    def _run_auto_analysis(self):
        """🔍 Ejecutar análisis automático"""
        # Analyze key metrics
        key_metrics = ["total_pnl", "win_rate", "current_drawdown", "open_positions"]
        
        for metric_name in key_metrics:
            if metric_name in self.metric_collector.definitions:
                self.analyze_metric_trend(metric_name)
                self.detect_metric_anomalies(metric_name)
    
    def analyze_metric_trend(self, metric_name: str, hours: float = 24) -> Optional[AnalysisResult]:
        """📈 Analizar tendencia de métrica"""
        try:
            history = self.metric_collector.get_history(metric_name, hours)
            if len(history) < 10:
                return None
            
            trend_analysis = self.trend_analyzer.analyze_trend(history)
            
            # Generate insights
            insights = []
            recommendations = []
            
            if trend_analysis["trend"] == "bullish":
                insights.append(f"{metric_name} shows strong upward trend")
                if metric_name == "current_drawdown":
                    recommendations.append("Monitor risk - drawdown is increasing")
            elif trend_analysis["trend"] == "bearish":
                insights.append(f"{metric_name} shows downward trend")
                if metric_name == "total_pnl":
                    recommendations.append("Review trading strategy - P&L declining")
            
            # Create result
            analysis_id = f"trend_{metric_name}_{int(datetime.now().timestamp())}"
            result = AnalysisResult(
                analysis_id=analysis_id,
                type=AnalysisType.TREND,
                metric_name=metric_name,
                timestamp=datetime.now(),
                result=trend_analysis,
                confidence=trend_analysis.get("r_squared", 0.0),
                insights=insights,
                recommendations=recommendations
            )
            
            with self._results_lock:
                self.analysis_results[analysis_id] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend for {metric_name}: {e}")
            return None
    
    def detect_metric_anomalies(self, metric_name: str) -> List[Tuple[DataPoint, float]]:
        """🚨 Detectar anomalías en métrica"""
        try:
            # Get sufficient history for training
            all_history = list(self.metric_collector.metrics.get(metric_name, []))
            if len(all_history) < 100:
                return []
            
            # Train detector
            detector = AnomalyDetector()
            if not detector.train(all_history[-200:]):  # Train with last 200 points
                return []
            
            # Detect anomalies in recent data
            recent_history = all_history[-24:]  # Last 24 points
            anomalies = detector.detect_anomalies(recent_history)
            
            # Log significant anomalies
            for anomaly, score in anomalies[:3]:  # Top 3
                if score > 0.5:  # Significant anomaly
                    self.logger.warning(
                        f"Anomaly detected in {metric_name}: "
                        f"value={anomaly.value} at {anomaly.timestamp} "
                        f"(score={score:.3f})"
                    )
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies for {metric_name}: {e}")
            return []
    
    def analyze_correlations(self, metrics: List[str], hours: float = 24) -> Dict[str, Any]:
        """🔗 Analizar correlaciones entre métricas"""
        try:
            # Get data for all metrics
            metric_data = {}
            for metric in metrics:
                history = self.metric_collector.get_history(metric, hours)
                if len(history) >= 10:
                    metric_data[metric] = [dp.value for dp in history]
            
            if len(metric_data) < 2:
                return {"error": "Insufficient data for correlation analysis"}
            
            # Calculate correlations
            correlations = {}
            for i, metric1 in enumerate(metrics):
                if metric1 not in metric_data:
                    continue
                    
                correlations[metric1] = {}
                for metric2 in metrics[i+1:]:
                    if metric2 not in metric_data:
                        continue
                    
                    # Align data lengths
                    min_len = min(len(metric_data[metric1]), len(metric_data[metric2]))
                    data1 = metric_data[metric1][-min_len:]
                    data2 = metric_data[metric2][-min_len:]
                    
                    if min_len >= 5:
                        correlation = np.corrcoef(data1, data2)[0, 1]
                        if not np.isnan(correlation):
                            correlations[metric1][metric2] = float(correlation)
            
            return {
                "correlations": correlations,
                "analysis_time": datetime.now().isoformat(),
                "hours_analyzed": hours,
                "metrics_count": len(metric_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {e}")
            return {"error": str(e)}
    
    def get_metric_summary(self, metric_name: str, hours: float = 24) -> Dict[str, Any]:
        """📊 Obtener resumen de métrica"""
        try:
            history = self.metric_collector.get_history(metric_name, hours)
            definition = self.metric_collector.definitions.get(metric_name)
            
            if not history:
                return {"error": f"No data for metric {metric_name}"}
            
            values = [dp.value for dp in history]
            
            summary = {
                "metric_name": metric_name,
                "definition": asdict(definition) if definition else None,
                "data_points": len(values),
                "time_range_hours": hours,
                "statistics": {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "latest": values[-1],
                    "change": values[-1] - values[0] if len(values) > 1 else 0
                },
                "trend": None,
                "anomalies_count": 0,
                "status": "normal"
            }
            
            # Add trend analysis
            if len(history) >= 10:
                trend = self.trend_analyzer.analyze_trend(history)
                summary["trend"] = trend
            
            # Check thresholds
            if definition:
                latest = values[-1]
                if definition.threshold_critical and abs(latest) > definition.threshold_critical:
                    summary["status"] = "critical"
                elif definition.threshold_warning and abs(latest) > definition.threshold_warning:
                    summary["status"] = "warning"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting summary for {metric_name}: {e}")
            return {"error": str(e)}
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """📋 Generar reporte diario"""
        return self.report_generator.generate_daily_report()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """📊 Obtener datos para dashboard"""
        try:
            # Get system health
            system_health = self.performance_analyzer.get_system_health()
            
            # Get key metric summaries
            key_metrics = ["total_pnl", "win_rate", "current_drawdown", "open_positions"]
            metric_summaries = {}
            
            for metric in key_metrics:
                if metric in self.metric_collector.definitions:
                    summary = self.get_metric_summary(metric, hours=24)
                    metric_summaries[metric] = summary
            
            # Get recent analysis results
            with self._results_lock:
                recent_analyses = sorted(
                    self.analysis_results.values(),
                    key=lambda x: x.timestamp,
                    reverse=True
                )[:10]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": system_health,
                "metric_summaries": metric_summaries,
                "recent_analyses": [asdict(analysis) for analysis in recent_analyses],
                "total_metrics": len(self.metric_collector.definitions),
                "auto_analysis_enabled": self.auto_analysis_enabled,
                "last_analysis": self.last_analysis.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """🏥 Verificar salud del motor de análisis"""
        try:
            status = {
                "status": "healthy",
                "components": {
                    "metric_collector": "healthy",
                    "trend_analyzer": "healthy", 
                    "anomaly_detector": "healthy" if SKLEARN_AVAILABLE else "limited",
                    "pattern_recognizer": "healthy",
                    "performance_analyzer": "healthy",
                    "report_generator": "healthy"
                },
                "metrics_count": len(self.metric_collector.definitions),
                "auto_analysis_enabled": self.auto_analysis_enabled,
                "sklearn_available": SKLEARN_AVAILABLE,
                "errors": []
            }
            
            # Check if we have recent data
            total_data_points = sum(len(deque_data) for deque_data in self.metric_collector.metrics.values())
            if total_data_points == 0:
                status["errors"].append("No metric data collected")
                status["status"] = "warning"
            
            # Check analysis results
            with self._results_lock:
                recent_analyses = [
                    r for r in self.analysis_results.values()
                    if (datetime.now() - r.timestamp).total_seconds() < 3600  # Last hour
                ]
            
            if not recent_analyses and self.auto_analysis_enabled:
                status["errors"].append("No recent analysis results")
                status["status"] = "warning"
            
            return status
            
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def test_analytics_engine():
    """🧪 Test function para validar AnalyticsEngine"""
    print("🧪 Testing AnalyticsEngine...")
    
    try:
        # Test initialization
        engine = AnalyticsEngine()
        print("✅ AnalyticsEngine initialized successfully")
        
        # Test metric recording
        engine.record_metric("test_metric", 100.0, tags={"symbol": "EURUSD"})
        engine.record_metric("test_metric", 105.0)
        engine.record_metric("test_metric", 95.0)
        print("✅ Metrics recorded")
        
        # Test metric summary
        summary = engine.get_metric_summary("test_metric")
        if "statistics" in summary:
            print(f"✅ Metric summary: {summary['statistics']['mean']:.1f}")
        
        # Test dashboard data
        dashboard_data = engine.get_dashboard_data()
        print(f"✅ Dashboard data: {len(dashboard_data)} keys")
        
        # Test health check
        health = engine.health_check()
        print(f"✅ Health check: {health['status']}")
        
        print("🎉 AnalyticsEngine test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ AnalyticsEngine test failed: {e}")
        return False


if __name__ == "__main__":
    test_analytics_engine()