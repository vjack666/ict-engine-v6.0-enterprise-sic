#!/usr/bin/env python3
"""Heartbeat Monitor - detecta servicios con latido atrasado."""
from __future__ import annotations
from typing import Dict, Any, Optional
import threading
import time

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

class HeartbeatMonitor:
    def __init__(self, 
                 stale_threshold: float = 10.0,
                 logger=None):
        self._beats: Dict[str, float] = {}
        self._lock = threading.RLock()
        self.stale_threshold = stale_threshold
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = create_safe_logger("HeartbeatMonitor", log_level=getattr(LogLevel, 'INFO', None))

    def beat(self, service: str) -> None:
        if not service:
            return
        with self._lock:
            self._beats[service] = time.time()

    def stale(self) -> Dict[str, float]:
        now = time.time()
        out: Dict[str, float] = {}
        with self._lock:
            for svc, ts in self._beats.items():
                delta = now - ts
                if delta > self.stale_threshold:
                    out[svc] = delta
        return out

    def report(self) -> Dict[str, Any]:
        s = self.stale()
        if s:
            self.logger.warning(f"Servicios stale: {s}", "HEARTBEAT")
        return {
            'total_services': len(self._beats),
            'stale': s,
            'stale_count': len(s)
        }

__all__ = ["HeartbeatMonitor"]
