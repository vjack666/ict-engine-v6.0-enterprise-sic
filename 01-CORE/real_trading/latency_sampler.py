#!/usr/bin/env python3
"""
⏳ LATENCY SAMPLER - ICT ENGINE v6.0 ENTERPRISE
=============================================
Estrategias para muestrear latencia real.
Implementaciones:
- StaticZeroLatencySampler (placeholder)
- RollingAverageSampler (ingesta externa)
Extensible a: MT5 ping, API REST RTT, feed de precios.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Optional
from threading import Lock
import time

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

class LatencySampler(ABC):
    @abstractmethod
    def sample(self) -> float:
        """Obtener latencia actual estimada (ms)."""
        raise NotImplementedError

class StaticZeroLatencySampler(LatencySampler):
    def sample(self) -> float:  # pragma: no cover
        return 0.0

class RollingAverageSampler(LatencySampler):
    def __init__(self, 
                 window_size: int = 50,
                 logger=None):
        self.window_size = window_size
        self._samples: Deque[float] = deque()
        self._lock = Lock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = create_safe_logger("RollingLatencySampler", log_level=getattr(LogLevel, 'INFO', None))

    def add_raw_latency_measurement(self, ms: float) -> None:
        if ms < 0:
            return
        with self._lock:
            self._samples.append(ms)
            if len(self._samples) > self.window_size:
                self._samples.popleft()

    def sample(self) -> float:
        with self._lock:
            if not self._samples:
                return 0.0
            return sum(self._samples) / len(self._samples) if self._samples else 0.0

# Export classes and factory
__all__ = ['LatencySampler', 'StaticZeroLatencySampler', 'RollingAverageSampler', 'create_default_latency_sampler']

def create_default_latency_sampler(logger=None, **kwargs):
    """Factory function that creates a RollingAverageSampler for compatibility"""
    return RollingAverageSampler(logger=logger, **kwargs)

__all__ = ["LatencySampler", "StaticZeroLatencySampler", "RollingAverageSampler"]
