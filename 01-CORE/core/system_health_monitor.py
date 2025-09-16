#!/usr/bin/env python3
"""
🩺 SYSTEM HEALTH MONITOR - ICT ENGINE v6.0 ENTERPRISE
=====================================================
Monitoreo ligero de salud del sistema.

Checks incluidos:
- Latencia reciente (si hay watchdog)
- Actividad de data_collector
- Número de errores recientes (si logger avanzado expone canal)
- Estado de memoria (umbral simple)

La clase expone is_system_healthy() usada por ExecutionRouter.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import psutil

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except ImportError:  # fallback
    from smart_trading_logger import enviar_senal_log as _compat_log  # type: ignore
    class _MiniLogger:
        def info(self,m,c): _compat_log("INFO",m,c)
        def warning(self,m,c): _compat_log("WARNING",m,c)
        def error(self,m,c): _compat_log("ERROR",m,c)
        def debug(self,m,c): _compat_log("DEBUG",m,c)
    def create_safe_logger(component_name: str, **_): return _MiniLogger()  # type: ignore

class LatencyProvider(Protocol):
    def get_current_latency_ms(self) -> float: ...

class DataCollectorLike(Protocol):
    last_update: datetime
    def is_active(self) -> bool: ...

@dataclass
class HealthConfig:
    max_latency_ms: float = 900.0
    max_memory_percent: float = 85.0
    max_silence_seconds: int = 25
    degrade_latency_ms: float = 750.0  # marca de advertencia

class SystemHealthMonitor:
    def __init__(self,
                 latency_provider: Optional[LatencyProvider] = None,
                 data_collector: Optional[DataCollectorLike] = None,
                 config: Optional[HealthConfig] = None):
        self.latency_provider = latency_provider
        self.data_collector = data_collector
        self.config = config or HealthConfig()
        self.logger = get_unified_logger("SystemHealthMonitor")
        self._last_status: Dict[str, Any] = {}

    def _check_latency(self) -> Dict[str, Any]:
        if not self.latency_provider:
            return {"available": False}
        try:
            lat = self.latency_provider.get_current_latency_ms()
        except Exception as e:
            self.logger.warning(f"Latency provider error: {e}", "HEALTH")
            return {"available": True, "error": str(e)}
        status = "ok"
        if lat >= self.config.degrade_latency_ms:
            status = "degraded"
        if lat >= self.config.max_latency_ms:
            status = "critical"
        return {"available": True, "latency_ms": lat, "status": status}

    def _check_data_collector(self) -> Dict[str, Any]:
        if not self.data_collector:
            return {"available": False}
        try:
            last = getattr(self.data_collector, 'last_update', None)
            active = self.data_collector.is_active() if hasattr(self.data_collector, 'is_active') else True
            silence = None
            if isinstance(last, datetime):
                silence = (datetime.now(timezone.utc) - last).total_seconds()
            status = "ok"
            if silence is not None and silence > self.config.max_silence_seconds:
                status = "stale"
            if not active:
                status = "inactive"
            return {"available": True, "status": status, "silence_seconds": silence}
        except Exception as e:
            self.logger.warning(f"DataCollector check error: {e}", "HEALTH")
            return {"available": True, "error": str(e)}

    def _check_memory(self) -> Dict[str, Any]:
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_percent()
            status = "ok"
            if mem_info >= self.config.max_memory_percent:
                status = "critical"
            return {"percent": mem_info, "status": status}
        except Exception as e:
            return {"error": str(e)}

    def evaluate(self) -> Dict[str, Any]:
        latency = self._check_latency()
        data_feed = self._check_data_collector()
        memory = self._check_memory()
        healthy = True
        reasons = []
        if latency.get("status") == "critical":
            healthy = False
            reasons.append("latency")
        if data_feed.get("status") in {"stale", "inactive"}:
            healthy = False
            reasons.append("data_feed")
        if memory.get("status") == "critical":
            healthy = False
            reasons.append("memory")
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'healthy': healthy,
            'reasons': reasons,
            'latency': latency,
            'data_feed': data_feed,
            'memory': memory
        }
        self._last_status = result
        return result

    def is_system_healthy(self) -> bool:
        status = self.evaluate()
        if not status['healthy']:
            self.logger.warning(f"System unhealthy reasons={status['reasons']}", "HEALTH")
        return status['healthy']

__all__ = ['SystemHealthMonitor', 'HealthConfig']
