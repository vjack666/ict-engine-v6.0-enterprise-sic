#!/usr/bin/env python3
"""
⏱️ LATENCY WATCHDOG - ICT ENGINE v6.0 ENTERPRISE
================================================
Medidor ligero de latencia agregada.

Simula mediciones externas (p.ej. ping al broker o diferencia timestamp tick) mediante
un callback inyectable. Aplica suavizado exponencial y expondrá get_current_latency_ms().
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
import time
from datetime import datetime

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

@dataclass
class WatchdogConfig:
    sample_interval_seconds: float = 2.0
    ema_alpha: float = 0.3
    max_samples_store: int = 50

class LatencyWatchdog:
    def __init__(self, sampler: Callable[[], float], config: Optional[WatchdogConfig] = None):
        self.sampler = sampler
        self.config = config or WatchdogConfig()
        self.logger = create_safe_logger("LatencyWatchdog")
        self._ema_latency_ms: Optional[float] = None
        self._last_sample_time: Optional[float] = None
        self._last_raw: Optional[float] = None
        self._samples: list[float] = []

    def tick(self) -> None:
        now = time.time()
        if self._last_sample_time and (now - self._last_sample_time) < self.config.sample_interval_seconds:
            return
        try:
            raw = float(self.sampler())
            if raw < 0:
                return
            self._last_raw = raw
            if self._ema_latency_ms is None:
                self._ema_latency_ms = raw
            else:
                a = self.config.ema_alpha
                self._ema_latency_ms = (a * raw) + (1 - a) * self._ema_latency_ms
            self._samples.append(raw)
            if len(self._samples) > self.config.max_samples_store:
                self._samples.pop(0)
            self._last_sample_time = now
        except Exception as e:
            self.logger.warning(f"Sampler error: {e}", "LATENCY")

    def get_current_latency_ms(self) -> float:
        self.tick()  # intentar muestrear si corresponde
        if self._ema_latency_ms is not None:
            return float(self._ema_latency_ms)
        return 0.0

    def get_stats(self) -> dict:
        if not self._samples:
            return {"count": 0}
        return {
            'count': len(self._samples),
            'last_raw': self._last_raw,
            'ema': self._ema_latency_ms,
            'min': min(self._samples),
            'max': max(self._samples),
            'avg': sum(self._samples)/len(self._samples),
            'updated': datetime.utcnow().isoformat()
        }

__all__ = ['LatencyWatchdog', 'WatchdogConfig']
