"""PerformanceMetricsAggregator
Agrega métricas en memoria de diferentes componentes.
Fuente prevista: risk pipeline, ordenes, validadores, latencia.
"""
from __future__ import annotations
from typing import Dict, Any
from threading import RLock
from datetime import datetime

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):
        class _Mini:
            def info(self, m: str, c: str): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str): print(f"[ERROR][{c}] {m}")
            def debug(self, m: str, c: str): print(f"[DEBUG][{c}] {m}")
        return _Mini()

class PerformanceMetricsAggregator:
    def __init__(self):
        self.logger = create_safe_logger("PerformanceMetricsAggregator")
        self._lock = RLock()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._last_snapshot: Dict[str, Any] = {}

    def incr(self, key: str, value: int = 1) -> None:
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def set_gauge(self, key: str, value: float) -> None:
        with self._lock:
            self._gauges[key] = float(value)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snap = {
                'timestamp': datetime.utcnow().isoformat(),
                'counters': dict(self._counters),
                'gauges': dict(self._gauges)
            }
            self._last_snapshot = snap
            return snap

    def last_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._last_snapshot)

__all__ = ["PerformanceMetricsAggregator"]
