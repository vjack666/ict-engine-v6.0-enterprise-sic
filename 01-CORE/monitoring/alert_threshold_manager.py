#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📢 ALERT THRESHOLD MANAGER - ICT Engine v6.0 Enterprise
======================================================

Gestión centralizada de umbrales de alertas y evaluación de breaches.
Lee configuración de alerts.yaml y evalúa métricas contra umbrales.

Características:
✅ Carga umbrales desde alerts.yaml
✅ Evaluación de breaches con cooldowns
✅ Generación de alertas estructuradas
✅ Integración con alert_integration_system
✅ Cache de configuración con hot-reload

Autor: ICT Engine v6.0 Team
Fecha: 19 Septiembre 2025
"""

import yaml
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("AlertThresholdManager", LogLevel.INFO)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AlertThresholdManager")

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class AlertCategory(Enum):
    """Categorías de alertas"""
    SYSTEM_RESOURCES = "SYSTEM_RESOURCES"
    PERFORMANCE = "PERFORMANCE"  
    TRADING_PERFORMANCE = "TRADING_PERFORMANCE"
    MT5_CONNECTION = "MT5_CONNECTION"
    INTERNET = "INTERNET"
    MARKET_DATA = "MARKET_DATA"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    ORDER_PROCESSING = "ORDER_PROCESSING"
    PATTERN_DETECTION = "PATTERN_DETECTION"

@dataclass
class AlertThreshold:
    """Definición de umbral de alerta"""
    alert_type: str
    category: AlertCategory
    warning_value: Optional[float] = None
    critical_value: Optional[float] = None
    emergency_value: Optional[float] = None
    evaluation_window_seconds: int = 60
    cooldown_minutes: int = 5
    enabled: bool = True
    comparison_operator: str = ">"  # >, <, ==, !=
    unit: str = ""

@dataclass
class AlertBreach:
    """Breach de umbral detectado"""
    alert_id: str
    alert_type: str
    category: AlertCategory
    level: AlertLevel
    threshold_value: float
    actual_value: float
    timestamp: datetime
    component: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class AlertThresholdManager:
    """
    Gestor de umbrales de alertas con evaluación automática
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("01-CORE/config/alerts.yaml")
        self.thresholds: Dict[str, AlertThreshold] = {}
        self.config: Dict[str, Any] = {}
        
        # Tracking de breaches y cooldowns
        self.last_breach_times: Dict[str, datetime] = {}
        self.breach_history: deque = deque(maxlen=1000)
        self.active_cooldowns: Set[str] = set()
        
        # Threading para hot-reload
        self._lock = threading.RLock()
        self.last_config_load = datetime.min
        self.config_check_interval = 30  # segundos
        
        # Cargar configuración inicial
        self._load_config()
        
        logger.info("AlertThresholdManager initialized", "INIT")
    
    def _load_config(self) -> bool:
        """Cargar configuración desde YAML"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Alert config not found: {self.config_path}", "CONFIG")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self._parse_thresholds()
            self.last_config_load = datetime.now()
            
            logger.info(f"Alert configuration loaded: {len(self.thresholds)} thresholds", "CONFIG")
            return True
            
        except Exception as e:
            logger.error(f"Error loading alert config: {e}", "CONFIG")
            return False
    
    def _parse_thresholds(self) -> None:
        """Parsear umbrales desde la configuración"""
        self.thresholds.clear()
        
        # Performance alerts
        if "performance_alerts" in self.config:
            self._parse_section("performance_alerts", AlertCategory.PERFORMANCE)
        
        # Trading alerts
        if "trading_alerts" in self.config:
            self._parse_section("trading_alerts", AlertCategory.TRADING_PERFORMANCE)
        
        # Connectivity alerts
        if "connectivity_alerts" in self.config:
            self._parse_connectivity_alerts()
        
        # Engine alerts
        if "engine_alerts" in self.config:
            self._parse_section("engine_alerts", AlertCategory.ORDER_PROCESSING)
        
        # Risk alerts
        if "risk_alerts" in self.config:
            self._parse_section("risk_alerts", AlertCategory.RISK_MANAGEMENT)
    
    def _parse_section(self, section_name: str, default_category: AlertCategory) -> None:
        """Parsear una sección de alertas"""
        section = self.config.get(section_name, {})
        
        for alert_type, config in section.items():
            if not isinstance(config, dict):
                continue
            
            # Determinar categoría
            category = default_category
            if alert_type == "system_resources":
                category = AlertCategory.SYSTEM_RESOURCES
            elif alert_type in ["mt5_connection"]:
                category = AlertCategory.MT5_CONNECTION
            elif alert_type in ["market_data_staleness"]:
                category = AlertCategory.MARKET_DATA
            elif alert_type == "pattern_detection":
                category = AlertCategory.PATTERN_DETECTION
            
            # Determinar operador de comparación
            comparison_op = ">"
            if alert_type in ["fill_rate", "pattern_detection", "margin_level"]:
                comparison_op = "<"  # Alertar cuando el valor está DEBAJO del umbral
            
            threshold = AlertThreshold(
                alert_type=alert_type,
                category=category,
                warning_value=self._extract_threshold_value(config, "warning"),
                critical_value=self._extract_threshold_value(config, "critical"),
                emergency_value=self._extract_threshold_value(config, "emergency"),
                evaluation_window_seconds=config.get("evaluation_window_seconds", 60),
                cooldown_minutes=config.get("cooldown_minutes", 5),
                enabled=config.get("enabled", True),
                comparison_operator=comparison_op,
                unit=self._get_unit(alert_type)
            )
            
            self.thresholds[alert_type] = threshold
    
    def _parse_connectivity_alerts(self) -> None:
        """Parsear alertas de conectividad con lógica especial"""
        section = self.config.get("connectivity_alerts", {})
        
        for alert_type, config in section.items():
            category = AlertCategory.INTERNET
            if alert_type == "mt5_connection":
                category = AlertCategory.MT5_CONNECTION
            elif alert_type == "market_data_staleness":
                category = AlertCategory.MARKET_DATA
            
            threshold = AlertThreshold(
                alert_type=alert_type,
                category=category,
                warning_value=self._extract_threshold_value(config, "warning"),
                critical_value=self._extract_threshold_value(config, "critical"), 
                emergency_value=self._extract_threshold_value(config, "emergency"),
                evaluation_window_seconds=config.get("evaluation_window_seconds", 60),
                cooldown_minutes=config.get("cooldown_minutes", 5),
                enabled=config.get("enabled", True),
                comparison_operator=">",  # Tiempo de desconexión
                unit="seconds" if "seconds" in str(config) else "minutes"
            )
            
            self.thresholds[alert_type] = threshold
    
    def _extract_threshold_value(self, config: Dict[str, Any], level: str) -> Optional[float]:
        """Extraer valor de umbral para un nivel específico"""
        # Buscar patrones comunes
        patterns = [
            f"{level}_ms",
            f"{level}_percent", 
            f"{level}_pips",
            f"{level}_seconds",
            f"{level}_minutes",
            f"{level}_ops_per_second",
            f"{level}_items",
            f"{level}_per_hour",
            f"{level}_delay_ms",
            f"{level}_accuracy_percent"
        ]
        
        for pattern in patterns:
            if pattern in config:
                return float(config[pattern])
        
        # Fallback directo
        if level in config:
            return float(config[level])
        
        return None
    
    def _get_unit(self, alert_type: str) -> str:
        """Obtener unidad para tipo de alerta"""
        unit_map = {
            "system_latency": "ms",
            "error_rate": "%",
            "throughput": "ops/sec",
            "system_resources": "%",
            "drawdown": "%",
            "slippage": "pips",
            "fill_rate": "%",
            "pnl_rate": "USD/h",
            "mt5_connection": "s",
            "market_data_staleness": "min",
            "internet_connectivity": "s",
            "order_processing": "ms",
            "pattern_detection": "%",
            "processing_backlog": "items",
            "margin_level": "%",
            "position_exposure": "%",
            "daily_loss_limit": "%"
        }
        return unit_map.get(alert_type, "")
    
    def check_and_reload_config(self) -> bool:
        """Verificar y recargar configuración si ha cambiado"""
        try:
            if not self.config_path.exists():
                return False
            
            file_mtime = datetime.fromtimestamp(self.config_path.stat().st_mtime)
            if file_mtime > self.last_config_load:
                logger.info("Alert config file changed, reloading...", "CONFIG")
                return self._load_config()
                
        except Exception as e:
            logger.error(f"Error checking config file: {e}", "CONFIG")
        
        return False
    
    def evaluate_metric(self, alert_type: str, value: float, component: str = "System", 
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[AlertBreach]:
        """
        Evaluar métrica contra umbrales y generar breach si aplica
        
        Args:
            alert_type: Tipo de alerta a evaluar
            value: Valor actual de la métrica
            component: Componente que genera la métrica
            metadata: Metadatos adicionales
            
        Returns:
            AlertBreach si se detecta breach, None si no
        """
        with self._lock:
            # Hot-reload config si es necesario
            if (datetime.now() - self.last_config_load).seconds > self.config_check_interval:
                self.check_and_reload_config()
            
            threshold = self.thresholds.get(alert_type)
            if not threshold or not threshold.enabled:
                return None
            
            # Verificar cooldown
            cooldown_key = f"{alert_type}_{component}"
            if cooldown_key in self.active_cooldowns:
                return None
            
            # Evaluar breach
            breach = self._evaluate_threshold(threshold, value, component, metadata or {})
            
            if breach:
                # Aplicar cooldown
                self._apply_cooldown(cooldown_key, threshold.cooldown_minutes)
                
                # Guardar en historial
                self.breach_history.append(breach)
                self.last_breach_times[cooldown_key] = breach.timestamp
                
                logger.warning(f"Alert breach: {breach.alert_type} {breach.level.value} - {breach.message}", "BREACH")
            
            return breach
    
    def _evaluate_threshold(self, threshold: AlertThreshold, value: float, 
                          component: str, metadata: Dict[str, Any]) -> Optional[AlertBreach]:
        """Evaluar si un valor rompe los umbrales"""
        level = None
        threshold_value = None
        
        # Evaluar en orden de severidad
        if threshold.emergency_value is not None:
            if self._compare_value(value, threshold.emergency_value, threshold.comparison_operator):
                level = AlertLevel.EMERGENCY
                threshold_value = threshold.emergency_value
        
        if level is None and threshold.critical_value is not None:
            if self._compare_value(value, threshold.critical_value, threshold.comparison_operator):
                level = AlertLevel.CRITICAL
                threshold_value = threshold.critical_value
        
        if level is None and threshold.warning_value is not None:
            if self._compare_value(value, threshold.warning_value, threshold.comparison_operator):
                level = AlertLevel.WARNING
                threshold_value = threshold.warning_value
        
        if level is None:
            return None
        
        # Generar mensaje descriptivo  
        message = self._generate_breach_message(threshold, level, value, threshold_value or 0.0)
        
        return AlertBreach(
            alert_id=f"{threshold.alert_type}_{component}_{int(time.time())}",
            alert_type=threshold.alert_type,
            category=threshold.category,
            level=level,
            threshold_value=threshold_value or 0.0,
            actual_value=value,
            timestamp=datetime.now(),
            component=component,
            message=message,
            metadata=metadata
        )
    
    def _compare_value(self, actual: float, threshold: float, operator: str) -> bool:
        """Comparar valor actual contra umbral"""
        if operator == ">":
            return actual > threshold
        elif operator == "<":
            return actual < threshold
        elif operator == "==":
            return abs(actual - threshold) < 0.001
        elif operator == "!=":
            return abs(actual - threshold) >= 0.001
        return False
    
    def _generate_breach_message(self, threshold: AlertThreshold, level: AlertLevel, 
                                actual_value: float, threshold_value: float) -> str:
        """Generar mensaje descriptivo para el breach"""
        unit = threshold.unit
        op_desc = "excedió" if threshold.comparison_operator == ">" else "cayó por debajo de"
        
        return f"{threshold.alert_type} {op_desc} el umbral {level.value}: {actual_value:.2f}{unit} vs {threshold_value:.2f}{unit}"
    
    def _apply_cooldown(self, key: str, minutes: int) -> None:
        """Aplicar cooldown para evitar spam de alertas"""
        self.active_cooldowns.add(key)
        
        def remove_cooldown():
            time.sleep(minutes * 60)
            self.active_cooldowns.discard(key)
        
        threading.Thread(target=remove_cooldown, daemon=True).start()
    
    def get_threshold_config(self, alert_type: str) -> Optional[Dict[str, Any]]:
        """Obtener configuración de umbral para tipo específico"""
        threshold = self.thresholds.get(alert_type)
        if not threshold:
            return None
        
        return {
            "alert_type": threshold.alert_type,
            "category": threshold.category.value,
            "warning_value": threshold.warning_value,
            "critical_value": threshold.critical_value,
            "emergency_value": threshold.emergency_value,
            "evaluation_window_seconds": threshold.evaluation_window_seconds,
            "cooldown_minutes": threshold.cooldown_minutes,
            "enabled": threshold.enabled,
            "comparison_operator": threshold.comparison_operator,
            "unit": threshold.unit
        }
    
    def get_all_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Obtener todas las configuraciones de umbrales"""
        result = {}
        for alert_type in self.thresholds.keys():
            config = self.get_threshold_config(alert_type)
            if config is not None:
                result[alert_type] = config
        return result
    
    def get_recent_breaches(self, limit: int = 100, 
                          level_filter: Optional[AlertLevel] = None) -> List[Dict[str, Any]]:
        """Obtener breaches recientes"""
        breaches = list(self.breach_history)
        
        if level_filter:
            breaches = [b for b in breaches if b.level == level_filter]
        
        # Ordenar por timestamp descendente
        breaches.sort(key=lambda b: b.timestamp, reverse=True)
        
        # Convertir a dict para serialización
        return [
            {
                "alert_id": b.alert_id,
                "alert_type": b.alert_type,
                "category": b.category.value,
                "level": b.level.value,
                "threshold_value": b.threshold_value,
                "actual_value": b.actual_value,
                "timestamp": b.timestamp.isoformat(),
                "component": b.component,
                "message": b.message,
                "metadata": b.metadata
            }
            for b in breaches[:limit]
        ]

# Global instance
_threshold_manager: Optional[AlertThresholdManager] = None

def get_alert_threshold_manager() -> AlertThresholdManager:
    """Obtener instancia global del threshold manager"""
    global _threshold_manager
    if _threshold_manager is None:
        _threshold_manager = AlertThresholdManager()
    return _threshold_manager