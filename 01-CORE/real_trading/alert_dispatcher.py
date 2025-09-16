#!/usr/bin/env python3
"""
🚨 ALERT DISPATCHER - ICT ENGINE v6.0 ENTERPRISE
===============================================
Canal unificado para eventos críticos del sistema de trading.

Centraliza alertas de circuit breaker, fallos de orden, bloqueos de riesgo,
y otros eventos que requieren atención inmediata.

Características:
- Rate limiting para evitar spam de alertas  
- Múltiples canales de salida (consola, archivo, callbacks)
- Filtrado por severidad y categoría
- Persistencia JSONL con rotación automática
- Historial en memoria para dashboard
- Shortcuts para eventos comunes
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, asdict
from threading import Lock

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
except Exception:
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:  # pragma: no cover
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

# Integración opcional con subsistema avanzado
get_advanced_alert_manager = None
AdvancedAlertManager = None

try:
    from alerting.manager import AdvancedAlertManager
    
    # Try to import the function
    try:
        from alerting.manager import get_advanced_alert_manager
        _ADV_ENABLED = True
    except ImportError:
        _ADV_ENABLED = False
    
    ALERT_SYSTEMS_AVAILABLE = True
except ImportError:
    _ADV_ENABLED = False
    get_advanced_alert_manager = None  # type: ignore
    ALERT_SYSTEMS_AVAILABLE = False


class AlertSeverity(Enum):
    """Severidad de la alerta."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Categoría del evento de alerta."""
    CIRCUIT_BREAKER = "circuit_breaker"
    ORDER_FAILURE = "order_failure"
    RISK_BLOCK = "risk_block"
    SYSTEM_HEALTH = "system_health"
    MARKET_DATA = "market_data"
    CONNECTIVITY = "connectivity"
    RATE_LIMIT = "rate_limit"

@dataclass
class AlertEvent:
    """Evento de alerta estructurado."""
    timestamp: float
    datetime: str
    category: str
    severity: str
    message: str
    symbol: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, 
               category: AlertCategory,
               severity: AlertSeverity,
               message: str,
               symbol: Optional[str] = None,
               details: Optional[Dict[str, Any]] = None) -> 'AlertEvent':
        """Crea un nuevo evento de alerta."""
        return cls(
            timestamp=time.time(),
            datetime=datetime.now().isoformat(),
            category=category.value,
            severity=severity.value,
            message=message,
            symbol=symbol,
            details=details or {}
        )


@dataclass
class AlertDispatcherConfig:
    """Configuración del dispatcher de alertas."""
    max_alerts_per_minute: int = 60
    alert_history_size: int = 1000
    log_file_path: str = "05-LOGS/alerts/alerts.jsonl"
    enable_console_output: bool = True
    min_severity_console: AlertSeverity = AlertSeverity.MEDIUM
    min_severity_file: AlertSeverity = AlertSeverity.LOW
    max_file_size: int = 512_000


class AlertDispatcher:
    """
    Dispatcher central de alertas para eventos críticos del sistema.
    
    Funcionalidades mejoradas:
    - Rate limiting para evitar spam de alertas
    - Múltiples canales de salida (consola, archivo, callbacks)
    - Filtrado por severidad y categoría
    - Persistencia JSONL con rotación automática
    - Historial en memoria para dashboard
    - Shortcuts para eventos comunes del trading
    """
    
    def __init__(self, config: Optional[AlertDispatcherConfig] = None, logger=None):
        self.config = config or AlertDispatcherConfig()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = create_safe_logger("AlertDispatcher", log_level=getattr(LogLevel, 'INFO', None))
        
        # Setup paths
        self.base_dir = Path(self.config.log_file_path).parent
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = Path(self.config.log_file_path)
        
        # Control de rate limiting
        self._alert_timestamps: List[float] = []
        self._lock = Lock()
        
        # Historial en memoria
        self._alert_history: List[AlertEvent] = []
        
        # Callbacks externos
        self._callbacks: List[Callable[[AlertEvent], None]] = []
        
        self.logger.info("AlertDispatcher initialized", "INIT")
    
    def add_callback(self, callback: Callable[[AlertEvent], None]) -> None:
        """Registra un callback para recibir eventos de alerta."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            self.logger.info("Alert callback registered", "CALLBACK")
    
    def remove_callback(self, callback: Callable[[AlertEvent], None]) -> None:
        """Remueve un callback registrado."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            self.logger.info("Alert callback removed", "CALLBACK")
    
    def dispatch_alert(self, 
                      category: AlertCategory,
                      severity: AlertSeverity,
                      message: str,
                      symbol: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Despacha una alerta a través del sistema.
        
        Returns:
            bool: True si la alerta fue procesada, False si fue rate limited
        """
        # Verificar rate limiting
        if not self._check_rate_limit():
            self.logger.warning(f"Alert rate limited: {message}", "RATE_LIMIT")
            return False
        
        # Crear evento
        event = AlertEvent.create(category, severity, message, symbol, details)
        
        with self._lock:
            # Agregar al historial
            self._add_to_history(event)
            
            # Procesar según severidad
            self._process_alert(event)
        
        # Llamar callbacks (fuera del lock)
        self._notify_callbacks(event)
        
        return True
    
    # Shortcuts para eventos comunes
    def dispatch_circuit_breaker(self, symbol: str, failure_count: int) -> bool:
        """Shortcut para alertas de circuit breaker."""
        return self.dispatch_alert(
            AlertCategory.CIRCUIT_BREAKER,
            AlertSeverity.HIGH,
            f"Circuit breaker activated for {symbol}",
            symbol=symbol,
            details={"failure_count": failure_count}
        )
    
    def dispatch_order_failure(self, symbol: str, error: str, details: Dict[str, Any]) -> bool:
        """Shortcut para fallos de orden."""
        return self.dispatch_alert(
            AlertCategory.ORDER_FAILURE,
            AlertSeverity.MEDIUM,
            f"Order failed for {symbol}: {error}",
            symbol=symbol,
            details=details
        )
    
    def dispatch_risk_block(self, symbol: str, reason: str, risk_metrics: Dict[str, Any]) -> bool:
        """Shortcut para bloqueos de riesgo."""
        return self.dispatch_alert(
            AlertCategory.RISK_BLOCK,
            AlertSeverity.HIGH,
            f"Risk block activated for {symbol}: {reason}",
            symbol=symbol,
            details=risk_metrics
        )
    
    def dispatch_system_health(self, component: str, status: str, metrics: Dict[str, Any]) -> bool:
        """Shortcut para alertas de salud del sistema."""
        severity = AlertSeverity.CRITICAL if status == "down" else AlertSeverity.MEDIUM
        return self.dispatch_alert(
            AlertCategory.SYSTEM_HEALTH,
            severity,
            f"System health alert for {component}: {status}",
            details={**metrics, "component": component}
        )
    
    def dispatch_rate_limit_hit(self, symbol: str, limit_type: str) -> bool:
        """Shortcut para límites de velocidad alcanzados."""
        return self.dispatch_alert(
            AlertCategory.RATE_LIMIT,
            AlertSeverity.MEDIUM,
            f"Rate limit hit for {symbol}: {limit_type}",
            symbol=symbol,
            details={"limit_type": limit_type}
        )
    
    def get_alert_history(self, 
                         limit: Optional[int] = None,
                         category: Optional[AlertCategory] = None,
                         min_severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """
        Obtiene historial de alertas filtrado.
        
        Returns:
            Lista de alertas como diccionarios
        """
        with self._lock:
            alerts = self._alert_history.copy()
        
        # Filtrar por categoría
        if category:
            alerts = [a for a in alerts if a.category == category.value]
        
        # Filtrar por severidad mínima
        if min_severity:
            severity_values = ["low", "medium", "high", "critical"]
            min_idx = severity_values.index(min_severity.value)
            alerts = [a for a in alerts if severity_values.index(a.severity) >= min_idx]
        
        # Limitar resultados
        if limit:
            alerts = alerts[-limit:]
        
        return [asdict(alert) for alert in alerts]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de alertas recientes."""
        now = time.time()
        last_hour = now - 3600
        last_24h = now - 86400
        
        with self._lock:
            recent_alerts = [a for a in self._alert_history if a.timestamp >= last_hour]
            daily_alerts = [a for a in self._alert_history if a.timestamp >= last_24h]
        
        # Contar por severidad
        severity_counts = {}
        category_counts = {}
        
        for alert in recent_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
            category_counts[alert.category] = category_counts.get(alert.category, 0) + 1
        
        return {
            "total_alerts_1h": len(recent_alerts),
            "total_alerts_24h": len(daily_alerts),
            "severity_breakdown_1h": severity_counts,
            "category_breakdown_1h": category_counts,
            "last_alert": asdict(self._alert_history[-1]) if self._alert_history else None
        }
    
    def _check_rate_limit(self) -> bool:
        """Verifica si la alerta pasa el rate limit."""
        now = time.time()
        cutoff = now - 60  # ventana de 1 minuto
        
        # Limpiar timestamps antiguos
        self._alert_timestamps = [ts for ts in self._alert_timestamps if ts > cutoff]
        
        # Verificar límite
        if len(self._alert_timestamps) >= self.config.max_alerts_per_minute:
            return False
        
        # Agregar timestamp actual
        self._alert_timestamps.append(now)
        return True
    
    def _add_to_history(self, event: AlertEvent) -> None:
        """Agrega evento al historial en memoria."""
        self._alert_history.append(event)
        
        # Mantener límite de historial
        if len(self._alert_history) > self.config.alert_history_size:
            self._alert_history.pop(0)
    
    def _process_alert(self, event: AlertEvent) -> None:
        """Procesa una alerta según configuración."""
        # Salida a consola
        if (self.config.enable_console_output and 
            self._severity_meets_threshold(event.severity, self.config.min_severity_console.value)):
            self._output_to_console(event)
        
        # Salida a archivo
        if self._severity_meets_threshold(event.severity, self.config.min_severity_file.value):
            self._output_to_file(event)
    
    def _severity_meets_threshold(self, severity: str, threshold: str) -> bool:
        """Verifica si la severidad cumple el umbral."""
        severity_values = ["low", "medium", "high", "critical"]
        return severity_values.index(severity) >= severity_values.index(threshold)
    
    def _output_to_console(self, event: AlertEvent) -> None:
        """Salida de alerta a consola."""
        prefix = f"[{event.severity.upper()}] {event.category}"
        message = f"{prefix}: {event.message}"
        if event.symbol:
            message += f" ({event.symbol})"
        
        if event.severity in ["high", "critical"]:
            self.logger.error(message, "ALERT")
        elif event.severity == "medium":
            self.logger.warning(message, "ALERT")
        else:
            self.logger.info(message, "ALERT")
    
    def _output_to_file(self, event: AlertEvent) -> None:
        """Salida de alerta a archivo JSONL."""
        try:
            self._rotate_if_needed()
            with self.log_path.open('a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write alert to file: {e}", "FILE")
    
    def _rotate_if_needed(self):
        """Rota el archivo de log si excede el tamaño máximo."""
        try:
            if self.log_path.exists() and self.log_path.stat().st_size > self.config.max_file_size:
                ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                self.log_path.rename(self.base_dir / f"alerts_{ts}.jsonl")
        except Exception:
            pass
    
    def _notify_callbacks(self, event: AlertEvent) -> None:
        """Notifica a todos los callbacks registrados."""
        # Fan-out callbacks registrados
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}", "CALLBACK")
        # Fan-out opcional al AdvancedAlertManager (no duplica lógica de rate ni dedup aquí)
        if _ADV_ENABLED and get_advanced_alert_manager is not None:
            try:
                mgr = get_advanced_alert_manager()
                mgr.record_alert(
                    category=event.category,
                    severity=event.severity,
                    message=event.message,
                    symbol=event.symbol,
                    meta=event.details or {}
                )
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Advanced alert fan-out failed: {e}", "ADV_ALERT")
        elif ALERT_SYSTEMS_AVAILABLE and AdvancedAlertManager is not None:
            try:
                mgr = AdvancedAlertManager()
                if hasattr(mgr, 'record_alert'):
                    mgr.record_alert(
                        category=event.category,
                        severity=event.severity,
                        message=event.message,
                        symbol=event.symbol,
                        meta=event.details or {}
                    )
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Direct alert manager failed: {e}", "ADV_ALERT")
    
    # Legacy compatibility method
    def dispatch(self, severity: str, category: str, message: str, meta: Optional[Dict[str, Any]] = None) -> AlertEvent:
        """Método legacy para compatibilidad hacia atrás."""
        # Map legacy severities
        sev_map = {"INFO": AlertSeverity.LOW, "WARNING": AlertSeverity.MEDIUM, "CRITICAL": AlertSeverity.CRITICAL}
        severity_enum = sev_map.get(severity.upper(), AlertSeverity.MEDIUM)
        
        # Map legacy categories  
        cat_map = {"RISK": AlertCategory.RISK_BLOCK, "EXECUTION": AlertCategory.ORDER_FAILURE, 
                  "SYSTEM": AlertCategory.SYSTEM_HEALTH, "LATENCY": AlertCategory.SYSTEM_HEALTH}
        category_enum = cat_map.get(category.upper(), AlertCategory.SYSTEM_HEALTH)
        
        self.dispatch_alert(category_enum, severity_enum, message, details=meta)
        
        # Return legacy Alert-like object for compatibility
        return AlertEvent.create(category_enum, severity_enum, message, details=meta)


# Instancia global opcional para acceso simplificado
_global_dispatcher: Optional[AlertDispatcher] = None


def get_global_dispatcher() -> Optional[AlertDispatcher]:
    """Obtiene el dispatcher global si está configurado."""
    return _global_dispatcher


def set_global_dispatcher(dispatcher: AlertDispatcher) -> None:
    """Configura el dispatcher global."""
    global _global_dispatcher
    _global_dispatcher = dispatcher


def dispatch_alert_global(category: AlertCategory, severity: AlertSeverity, message: str, **kwargs) -> bool:
    """Función de conveniencia para usar el dispatcher global."""
    if _global_dispatcher:
        return _global_dispatcher.dispatch_alert(category, severity, message, **kwargs)
    return False


# Backward compatibility alias
Alert = AlertEvent

__all__ = ["AlertDispatcher", "AlertEvent", "Alert", "AlertSeverity", "AlertCategory", 
           "AlertDispatcherConfig", "get_global_dispatcher", "set_global_dispatcher", "dispatch_alert_global"]
