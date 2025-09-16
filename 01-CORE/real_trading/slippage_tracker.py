#!/usr/bin/env python3
"""
Slippage Tracker - ICT Engine v6.0 Enterprise
===========================================

Registro ligero de slippage (precio esperado vs ejecutado) para enriquecer métricas.
Persistencia opcional: agrega snapshots al metrics recorder si está inyectado.

Uso:
    tracker = SlippageTracker()
    tracker.record(symbol, expected, executed)
    avg, p95 = tracker.current_stats()
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import List, Tuple, Optional, Dict, Any
from statistics import mean
from pathlib import Path
import json
from datetime import datetime, timezone

try:
    from protocols.logging_protocol import create_safe_logger, LogLevel  # type: ignore
except Exception:  # fallback
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:
            def info(self, m, c=""): print(f"[INFO][{component_name}]{c} {m}")
            def warning(self, m, c=""): print(f"[WARN][{component_name}]{c} {m}")
            def error(self, m, c=""): print(f"[ERR][{component_name}]{c} {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

class SlippageTracker:
    def __init__(self, max_samples: int = 1000, persist_dir: Optional[str] = None) -> None:
        self.max_samples = max_samples
        self.samples: List[float] = []  # en pips o unidades normalizadas
        self.persist_dir = Path(persist_dir) if persist_dir else None
        if self.persist_dir:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_unified_logger("SlippageTracker")

    def record(self, symbol: str, expected_price: float, executed_price: float, pip_factor: float = 0.0001) -> float:
        try:
            if pip_factor <= 0:
                pip_factor = 0.0001
            raw = executed_price - expected_price
            pips = raw / pip_factor
            self.samples.append(pips)
            if len(self.samples) > self.max_samples:
                self.samples.pop(0)
            return pips
        except Exception as e:
            self.logger.error(f"No se pudo registrar slippage: {e}")
            return 0.0

    def current_stats(self) -> Dict[str, float]:
        if not self.samples:
            return {"avg": 0.0, "p95": 0.0, "count": 0}
        arr = sorted(self.samples)
        avg_v = mean(arr)
        def _pct(p: float) -> float:
            if not arr:
                return 0.0
            k = (len(arr)-1) * p
            f = int(k)
            c = min(f+1, len(arr)-1)
            if f == c:
                return float(arr[f])
            d0 = arr[f] * (c - k)
            d1 = arr[c] * (k - f)
            return float(d0 + d1)
        return {"avg": avg_v, "p95": _pct(0.95), "count": len(arr)}

    def persist_snapshot(self) -> None:
        if not self.persist_dir:
            return
        snap = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stats': self.current_stats()
        }
        try:
            path = self.persist_dir / 'slippage_stats.json'
            path.write_text(json.dumps(snap, indent=2), encoding='utf-8')
        except Exception:
            pass

__all__ = ["SlippageTracker"]
