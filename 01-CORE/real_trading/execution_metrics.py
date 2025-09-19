#!/usr/bin/env python3
"""Execution Metrics Recorder
=============================
Componente desacoplado para registrar métricas de ejecución de órdenes.
Puede reutilizarse fuera de ExecutionRouter y facilita test unitarios.

Responsabilidades:
- Registrar tiempos de inicio/fin y computar latencias.
- Mantener contadores (total, ok, fail) y muestras de latencia con límite.
- Persistir archivos live / summary / cumulative siguiendo convención.
- Calcular percentiles sin depender de numpy (interpolación lineal).

Diseño eficiente:
- Operaciones O(1) sobre contadores.
- Percentiles calculados solo en persistencia (no en cada muestra).
- Límite de muestras configurable para controlar memoria.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from pathlib import Path
import json, time, os
from datetime import datetime, timezone

@runtime_checkable
class _LoggerProto(Protocol):
    def info(self, message: str, category: str) -> None: ...
    def warning(self, message: str, category: str) -> None: ...
    def error(self, message: str, category: str) -> None: ...

try:
    from protocols.logging_protocol import create_enterprise_logger as _central_logger_factory
    def create_enterprise_logger(component_name: str, prefer_smart_logger: bool = True, **kwargs) -> _LoggerProto:  # type: ignore[override]
        return _central_logger_factory(component_name, prefer_smart_logger=prefer_smart_logger, **kwargs)  # type: ignore[return-value]
except Exception:  # fallback reducido
    def create_enterprise_logger(component_name: str, prefer_smart_logger: bool = True, **kwargs) -> _LoggerProto:  # type: ignore[override]
        class _M:
            def info(self, message: str, category: str) -> None: pass
            def warning(self, message: str, category: str) -> None: pass
            def error(self, message: str, category: str) -> None: pass
        return _M()

@dataclass
class ExecutionMetricsConfig:
    metrics_dir: str
    history_limit: int = 100
    latency_samples_limit: int = 500
    cumulative_filename: str = "metrics_cumulative.json"
    live_filename: str = "metrics_live.json"
    summary_filename: str = "metrics_summary.json"

@dataclass
class ExecutionMetricsRecorder:
    config: ExecutionMetricsConfig
    logger: Any = field(init=False)
    _latency_samples: List[float] = field(default_factory=list)
    _history: List[Dict[str, Any]] = field(default_factory=list)
    _orders_total: int = 0
    _orders_ok: int = 0
    _orders_failed: int = 0
    _last_persist: float = 0.0
    _cumulative: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        Path(self.config.metrics_dir).mkdir(parents=True, exist_ok=True)
        self.logger = create_enterprise_logger("ExecMetrics")
        self._load_cumulative()

    # ------------- Registro básico -------------
    def record_order(self, success: bool, latency_ms: float) -> None:
        self._orders_total += 1
        if success:
            self._orders_ok += 1
        else:
            self._orders_failed += 1
        if latency_ms >= 0:
            self._latency_samples.append(latency_ms)
            if len(self._latency_samples) > self.config.latency_samples_limit:
                self._latency_samples.pop(0)

    # ------------- Persistencia -------------
    def maybe_persist(self, interval_seconds: float = 30.0) -> None:
        now = time.time()
        if (now - self._last_persist) < interval_seconds:
            return
        self._last_persist = now
        self._persist_live_and_summary()

    def force_persist(self) -> None:
        self._persist_live_and_summary()

    # ------------- Cumulative -------------
    def _cumulative_path(self) -> Path:
        return Path(self.config.metrics_dir) / self.config.cumulative_filename

    def _load_cumulative(self) -> None:
        path = self._cumulative_path()
        if not path.exists():
            self._cumulative = {"orders_total":0, "orders_ok":0, "orders_failed":0, "sessions":0, "last_update":None}
        else:
            try:
                self._cumulative = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self._cumulative = {"orders_total":0, "orders_ok":0, "orders_failed":0, "sessions":0, "last_update":None}
        # Normalizar estructura para compatibilidad
        if not isinstance(self._cumulative, dict):
            self._cumulative = {}
        if 'orders_total' not in self._cumulative or not isinstance(self._cumulative.get('orders_total'), (int, float)):
            self._cumulative['orders_total'] = 0
        if 'orders_ok' not in self._cumulative or not isinstance(self._cumulative.get('orders_ok'), (int, float)):
            self._cumulative['orders_ok'] = 0
        if 'orders_failed' not in self._cumulative or not isinstance(self._cumulative.get('orders_failed'), (int, float)):
            self._cumulative['orders_failed'] = 0
        if 'sessions' not in self._cumulative or not isinstance(self._cumulative.get('sessions'), (int, float)):
            self._cumulative['sessions'] = 0
        self._cumulative["sessions"] = int(self._cumulative.get("sessions",0)) + 1

    # ------------- Percentiles -------------
    def _percentile(self, sorted_list: List[float], p: float) -> float:
        if not sorted_list:
            return 0.0
        k = (len(sorted_list)-1) * p
        f = int(k)
        c = min(f+1, len(sorted_list)-1)
        if f == c:
            return float(sorted_list[f])
        d0 = sorted_list[f] * (c - k)
        d1 = sorted_list[c] * (k - f)
        return float(d0 + d1)

    def _compute_stats(self) -> Dict[str, Any]:
        lat = list(self._latency_samples)
        lat_sorted = sorted(lat)
        avg = sum(lat_sorted)/len(lat_sorted) if lat_sorted else 0.0
        pct = {k:self._percentile(lat_sorted, v) for k,v in {
            'p50':0.50,'p75':0.75,'p90':0.90,'p95':0.95,'p99':0.99}.items()}
        return {"avg": avg, "percentiles": pct, "count": len(lat_sorted)}

    def _persist_live_and_summary(self) -> None:
        stats = self._compute_stats()
        live = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "orders_total": self._orders_total,
            "orders_ok": self._orders_ok,
            "orders_failed": self._orders_failed,
            "avg_latency_ms": stats["avg"],
            "latency_samples_count": stats["count"],
            "latency_percentiles": stats["percentiles"],
        }
        summary = {
            "generated": live["timestamp"],
            "orders_total": self._orders_total,
            "orders_ok": self._orders_ok,
            "orders_failed": self._orders_failed,
            "latency_avg_ms": stats["avg"],
            "latency_percentiles": stats["percentiles"],
            "history": self._history[-50:]
        }
        self._history.append({"t": live["timestamp"], "total": self._orders_total, "ok": self._orders_ok, "fail": self._orders_failed, "lat": stats["avg"]})
        if len(self._history) > self.config.history_limit:
            self._history.pop(0)
        self._atomic_write(self.config.live_filename, live)
        self._atomic_write(self.config.summary_filename, summary)

    def persist_cumulative(self) -> None:
        # Garantizar claves mínimas
        if 'orders_total' not in self._cumulative or not isinstance(self._cumulative.get('orders_total'), (int, float)):
            self._cumulative['orders_total'] = 0
        if 'orders_ok' not in self._cumulative or not isinstance(self._cumulative.get('orders_ok'), (int, float)):
            self._cumulative['orders_ok'] = 0
        if 'orders_failed' not in self._cumulative or not isinstance(self._cumulative.get('orders_failed'), (int, float)):
            self._cumulative['orders_failed'] = 0
        self._cumulative["orders_total"] = int(self._cumulative.get("orders_total", 0)) + int(self._orders_total)
        self._cumulative["orders_ok"] = int(self._cumulative.get("orders_ok", 0)) + int(self._orders_ok)
        self._cumulative["orders_failed"] = int(self._cumulative.get("orders_failed", 0)) + int(self._orders_failed)
        self._cumulative["last_update"] = datetime.now(timezone.utc).isoformat()
        self._atomic_write(self.config.cumulative_filename, self._cumulative)
        self.force_persist()

    # ------------- Utilidades -------------
    def _atomic_write(self, filename: str, data: Dict[str, Any]) -> None:
        path = Path(self.config.metrics_dir) / filename
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(path)
        except Exception:
            pass

__all__ = ["ExecutionMetricsConfig", "ExecutionMetricsRecorder"]
