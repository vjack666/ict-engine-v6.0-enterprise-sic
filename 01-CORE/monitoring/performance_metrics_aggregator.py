"""PerformanceMetricsAggregator
Agrega métricas en memoria de diferentes componentes.
Fuente prevista: risk pipeline, ordenes, validadores, latencia.
"""
from __future__ import annotations
from typing import Dict, Any
from threading import RLock
from datetime import datetime, timezone

from protocols.unified_logging import get_unified_logger

class PerformanceMetricsAggregator:
    def __init__(self):
        self.logger = get_unified_logger("PerformanceMetricsAggregator")
        self._lock = RLock()
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._last_snapshot: Dict[str, Any] = {}
        self.last_update: datetime | None = None

    def incr(self, key: str, value: int = 1) -> None:
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value

    def set_gauge(self, key: str, value: float) -> None:
        with self._lock:
            self._gauges[key] = float(value)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snap = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'counters': dict(self._counters),
                'gauges': dict(self._gauges)
            }
            self._last_snapshot = snap
            self.last_update = datetime.now(timezone.utc)
            return snap

    def last_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._last_snapshot)

    # Accessors para API
    def get_live_metrics(self) -> Dict[str, Any]:
        """Retorna un subconjunto rápido de métricas para monitoreo en vivo."""
        snap = self.snapshot()
        return {
            'timestamp': snap['timestamp'],
            'counters': snap.get('counters', {}),
            'gauges': snap.get('gauges', {}),
        }

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Retorna un resumen agregable (igual al snapshot actual)."""
        return self.snapshot()

    def get_cumulative_metrics(self) -> Dict[str, Any]:
        """Retorna métricas acumuladas. En esta versión coincide con summary."""
        return self.snapshot()

__all__ = ["PerformanceMetricsAggregator"]
