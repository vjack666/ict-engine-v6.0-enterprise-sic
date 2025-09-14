"""Metrics Collector
===================
Agrega métricas operativas y de trading para reporting centralizado.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
import threading


@dataclass
class MetricPoint:
    name: str
    value: float
    timestamp: datetime


class MetricsCollector:
    def __init__(self, max_points: int = 5000) -> None:
        self.max_points = max_points
        self._metrics: Dict[str, list[MetricPoint]] = {}
        self._lock = threading.Lock()

    def record(self, name: str, value: float) -> None:
        with self._lock:
            lst = self._metrics.setdefault(name, [])
            lst.append(MetricPoint(name=name, value=value, timestamp=datetime.utcnow()))
            if len(lst) > self.max_points:
                lst.pop(0)

    def get_latest(self, name: str) -> float:
        with self._lock:
            lst = self._metrics.get(name)
            if not lst:
                return 0.0
            return lst[-1].value

    def export_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            out: Dict[str, Any] = {}
            for name, points in self._metrics.items():
                if not points:
                    continue
                values = [p.value for p in points]
                out[name] = {
                    "count": len(values),
                    "avg": sum(values)/len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1],
                    "last_timestamp": points[-1].timestamp
                }
            return out


__all__ = ["MetricsCollector", "MetricPoint"]
