"""Shim for monitoring.baseline_metrics_system

This forwards imports to the real implementation at
`01-CORE/monitoring/baseline_metrics_system.py`.
"""

from pathlib import Path
import importlib.util
import sys

root = Path(__file__).resolve().parent
project_root = root.parent
core_impl = project_root / '01-CORE' / 'monitoring' / 'baseline_metrics_system.py'

if not core_impl.exists():
    raise ImportError(f"Core baseline_metrics_system not found at {core_impl}")

spec = importlib.util.spec_from_file_location(
    "_core_baseline_metrics_system", str(core_impl)
)
if spec is None or spec.loader is None:
    raise ImportError("Unable to load core baseline_metrics_system module spec")

_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = _module
spec.loader.exec_module(_module)  # type: ignore[attr-defined]

# Re-export explicit API to satisfy type checkers
BaselineMetricsSystem = getattr(_module, 'BaselineMetricsSystem')
ComponentTimer = getattr(_module, 'ComponentTimer')
create_baseline_metrics_system = getattr(_module, 'create_baseline_metrics_system')

__all__ = [
    'BaselineMetricsSystem',
    'ComponentTimer',
    'create_baseline_metrics_system',
]
