"""Baseline Calculator (wrapper)
Provides a very small facade over BaselineMetricsSystem to:
- get baseline summary
- compare current values against established baselines

No duplication of baseline logic; it delegates to BaselineMetricsSystem.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

try:
    from .baseline_metrics_system import BaselineMetricsSystem, create_baseline_metrics_system
except Exception:  # pragma: no cover
    BaselineMetricsSystem = None  # type: ignore[assignment]
    create_baseline_metrics_system = (lambda config=None: None)  # type: ignore[assignment]

_baseline_sys: Optional[Any] = None


def _get_system(config: Optional[Dict[str, Any]] = None) -> Any:
    global _baseline_sys
    if _baseline_sys is None:
        _baseline_sys = create_baseline_metrics_system(config)
    return _baseline_sys


def ensure_started(config: Optional[Dict[str, Any]] = None) -> bool:
    sys = _get_system(config)
    if sys is None:
        return False
    try:
        if not getattr(sys, 'is_monitoring', False):
            sys.start_monitoring()
        return True
    except Exception:
        return False


def baseline_summary() -> Dict[str, Any]:
    sys = _get_system(None)
    if sys is None:
        return {}
    try:
        return sys.get_baseline_summary()
    except Exception:
        return {}


def compare_metric(component: str, metric_name: str, current_value: float) -> Dict[str, Any]:
    """Compare a value with its baseline (if exists).

    Returns a dict with: exists, baseline_value, deviation_percent, status.
    """
    sys = _get_system(None)
    if sys is None:
        return {'exists': False}
    try:
        key = f"{component}_{metric_name}"
        baseline = sys.baseline_metrics.get(key)
        if not baseline:
            return {'exists': False}
        bval = baseline.baseline_value
        if bval == 0:
            dev = 0.0
        else:
            dev = ((current_value - bval) / bval) * 100.0
        status = sys._determine_status(dev, metric_name)  # reuse internal rule
        return {
            'exists': True,
            'baseline_value': bval,
            'current_value': current_value,
            'deviation_percent': dev,
            'status': status,
            'unit': baseline.unit,
        }
    except Exception:
        return {'exists': False}


__all__ = [
    'ensure_started',
    'baseline_summary',
    'compare_metric',
]

# Optional helper to stop monitoring gracefully from callers like main.py
def stop() -> bool:
    global _baseline_sys
    sys = _baseline_sys
    if sys is None:
        return False
    try:
        if getattr(sys, 'is_monitoring', False) and hasattr(sys, 'stop_monitoring'):
            sys.stop_monitoring()
        else:
            # If not monitoring, still persist what exists if supported
            if hasattr(sys, '_save_all_data'):
                try:
                    sys._save_all_data()  # type: ignore[attr-defined]
                except Exception:
                    pass
        return True
    except Exception:
        return False

