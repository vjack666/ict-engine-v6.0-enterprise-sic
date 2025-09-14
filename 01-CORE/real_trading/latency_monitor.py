"""Latency Monitor
=================
Calcula métricas de latencia para diferentes etapas del pipeline
(señal -> validación -> ejecución) para optimización en producción.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import statistics


@dataclass
class LatencySample:
    stage: str
    started_at: datetime
    completed_at: datetime

    @property
    def duration_ms(self) -> float:
        return (self.completed_at - self.started_at).total_seconds() * 1000.0


class LatencyMonitor:
    def __init__(self, max_samples: int = 500) -> None:
        self.max_samples = max_samples
        self._samples: list[LatencySample] = []

    def record(self, stage: str, started_at: datetime, completed_at: Optional[datetime] = None) -> None:
        comp = completed_at or datetime.utcnow()
        sample = LatencySample(stage=stage, started_at=started_at, completed_at=comp)
        self._samples.append(sample)
        if len(self._samples) > self.max_samples:
            self._samples.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        if not self._samples:
            return {"samples": 0}
        durations = [s.duration_ms for s in self._samples]
        return {
            "samples": len(self._samples),
            "p50_ms": statistics.median(durations),
            "p95_ms": statistics.quantiles(durations, n=100)[94] if len(durations) >= 100 else max(durations),
            "avg_ms": sum(durations) / len(durations),
            "max_ms": max(durations),
            "by_stage": self._aggregate_by_stage()
        }

    def _aggregate_by_stage(self) -> Dict[str, Dict[str, float]]:
        stage_map: Dict[str, list[float]] = {}
        for s in self._samples:
            stage_map.setdefault(s.stage, []).append(s.duration_ms)
        return {
            stage: {
                "avg_ms": sum(vals)/len(vals),
                "max_ms": max(vals),
                "count": len(vals)
            } for stage, vals in stage_map.items()
        }


__all__ = ["LatencyMonitor", "LatencySample"]
