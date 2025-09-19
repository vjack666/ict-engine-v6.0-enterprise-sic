"""Unified Metrics Collector (wrapper)
Bridges simple recording APIs into PerformanceMetricsAggregator without duplication.

Usage:
- record_counter("orders.executed")
- record_gauge("latency.ms", 12.3)
- with time_operation("analysis"): ...

Internals:
- Tries to reuse the aggregator created by main.get_performance_metrics_instance()
- Falls back to a local PerformanceMetricsAggregator if none is available
"""
from __future__ import annotations
from typing import Any, Optional, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

try:
    from .performance_metrics_aggregator import PerformanceMetricsAggregator
except Exception:  # pragma: no cover
    PerformanceMetricsAggregator = None  # type: ignore

_aggregator: Optional[Any] = None


def set_aggregator(aggregator: Any) -> None:
    """Explicitly set the underlying aggregator instance to use."""
    global _aggregator
    _aggregator = aggregator


def _get_aggregator() -> Any:
    """Return a usable aggregator instance, preferring the global from main."""
    global _aggregator
    if _aggregator is not None:
        return _aggregator
    # Try to reuse instance exposed by main
    try:
        import importlib
        _main = importlib.import_module('main')
        if hasattr(_main, 'get_performance_metrics_instance'):
            inst = _main.get_performance_metrics_instance()
            if inst is not None:
                _aggregator = inst
                return _aggregator
    except Exception:
        pass
    # Fallback: create a local aggregator if implementation is available
    if PerformanceMetricsAggregator is not None:
        _aggregator = PerformanceMetricsAggregator()
        return _aggregator
    # Last resort: minimal shim with no-ops
    class _NullAgg:
        def incr(self, *_: Any, **__: Any) -> None: ...
        def set_gauge(self, *_: Any, **__: Any) -> None: ...
        def snapshot(self) -> dict: return {'timestamp': datetime.now(timezone.utc).isoformat()}
        def get_live_metrics(self) -> dict: return {}
        def get_summary_metrics(self) -> dict: return {}
        def get_cumulative_metrics(self) -> dict: return {}
        last_update = None
    _aggregator = _NullAgg()
    return _aggregator


def record_counter(name: str, by: int = 1) -> None:
    """Increment a counter metric on the aggregator."""
    agg = _get_aggregator()
    try:
        agg.incr(name, by)
    except Exception:
        # Be resilient – metrics should never break flows
        pass


def record_gauge(name: str, value: float) -> None:
    """Set a gauge metric on the aggregator."""
    agg = _get_aggregator()
    try:
        agg.set_gauge(name, float(value))
    except Exception:
        pass


def record_metric(name: str, value: float, kind: str = 'gauge') -> None:
    """Generic record helper. kind in {'gauge','counter'}"""
    if kind == 'counter':
        record_counter(name, int(value))
    else:
        record_gauge(name, value)


@contextmanager
def time_operation(name: str) -> Iterator[None]:
    """Context manager to time a block and record latency + count.

    Records:
    - counter: f"ops.{name}"
    - gauge:   f"latency.{name}_ms"
    """
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        record_counter(f"ops.{name}", 1)
    record_gauge(f"latency.{name}_ms", elapsed_ms)


def export_snapshot() -> dict:
    """Return current aggregator snapshot for quick inspection/testing."""
    agg = _get_aggregator()
    try:
        return agg.snapshot()
    except Exception:
        return {}


__all__ = [
    'set_aggregator',
    'record_counter',
    'record_gauge',
    'record_metric',
    'time_operation',
    'export_snapshot',
]
