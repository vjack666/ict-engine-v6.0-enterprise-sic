#!/usr/bin/env python3
"""Composite Health Monitor - ICT Engine v6.0 Enterprise
======================================================
Agrega múltiples señales de salud en un punto único:
- Latencia (LatencyMonitorProtocol)
- Freshness de Market Data (func proveedor + edad máxima)
- Heartbeat externo (timestamp / callback booleano)

Objetivo: simplificar pre-check de ExecutionRouter y proveer razones estructuradas.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, Protocol
import time

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # fallback
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:
            def info(self, m, c=""): pass
            def warning(self, m, c=""): print(f"[WARN][{component_name}] {m}")
            def error(self, m, c=""): print(f"[ERR][{component_name}] {m}")
        return _L()

class LatencyMonitorProtocol(Protocol):  # repetir mínimo para no depender
    def get_current_latency_ms(self) -> float: ...

@dataclass
class CompositeHealthConfig:
    max_latency_ms: float = 900.0
    max_market_data_age_sec: int = 180
    max_heartbeat_age_sec: int = 90
    degrade_latency_ms: float = 700.0  # umbral de advertencia

class CompositeHealthMonitor:
    def __init__(self,
                 latency_monitor: Optional[LatencyMonitorProtocol] = None,
                 market_data_last_ts_provider: Optional[Callable[[], Optional[float]]] = None,
                 heartbeat_last_ts_provider: Optional[Callable[[], Optional[float]]] = None,
                 heartbeat_alive_check: Optional[Callable[[], bool]] = None,
                 config: Optional[CompositeHealthConfig] = None) -> None:
        self.latency_monitor = latency_monitor
        self.market_data_last_ts_provider = market_data_last_ts_provider
        self.heartbeat_last_ts_provider = heartbeat_last_ts_provider
        self.heartbeat_alive_check = heartbeat_alive_check
        self.config = config or CompositeHealthConfig()
        self.logger = create_safe_logger("CompositeHealth")
        self._last_eval: float = 0.0
        self._cache_result: bool = True
        self._cache_reasons: Dict[str, Any] = {}
        self._ttl_sec = 1.0  # cache muy corto para reducir coste

    def is_system_healthy(self) -> bool:
        now = time.time()
        if (now - self._last_eval) < self._ttl_sec:
            return self._cache_result
        reasons: Dict[str, Any] = {}
        healthy = True
        # Latencia
        if self.latency_monitor:
            try:
                lat = self.latency_monitor.get_current_latency_ms()
                if lat > self.config.max_latency_ms:
                    healthy = False
                    reasons['latency'] = f"high:{lat:.0f}ms"
                elif lat > self.config.degrade_latency_ms:
                    reasons['latency_warn'] = f"degraded:{lat:.0f}ms"
            except Exception as e:
                reasons['latency_error'] = str(e)
        # Market Data freshness
        if self.market_data_last_ts_provider:
            try:
                ts = self.market_data_last_ts_provider()
                if ts is not None:
                    age = now - ts
                    if age > self.config.max_market_data_age_sec:
                        healthy = False
                        reasons['market_data'] = f"stale:{int(age)}s"
                else:
                    reasons['market_data_warn'] = 'no_timestamp'
            except Exception as e:
                reasons['market_data_error'] = str(e)
        # Heartbeat
        if self.heartbeat_last_ts_provider:
            try:
                hb_ts = self.heartbeat_last_ts_provider()
                if hb_ts is not None:
                    age = now - hb_ts
                    if age > self.config.max_heartbeat_age_sec:
                        healthy = False
                        reasons['heartbeat'] = f"stale:{int(age)}s"
            except Exception:
                reasons['heartbeat_error'] = 'exception'
        if self.heartbeat_alive_check:
            try:
                if not self.heartbeat_alive_check():
                    healthy = False
                    reasons['heartbeat_alive'] = 'false'
            except Exception:
                reasons['heartbeat_alive_error'] = 'exception'
        self._last_eval = now
        self._cache_result = healthy
        self._cache_reasons = reasons
        if not healthy:
            try:
                self.logger.warning(f"Health degraded reasons={reasons}", "HEALTH")
            except Exception:
                pass
        return healthy

    def reasons(self) -> Dict[str, Any]:
        # forzar recalculo si caché vencida
        self.is_system_healthy()
        return dict(self._cache_reasons)

__all__ = ["CompositeHealthMonitor", "CompositeHealthConfig"]
