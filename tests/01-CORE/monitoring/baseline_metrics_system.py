# tests shim module that imports the real implementation
from pathlib import Path
import importlib.util
import sys

# Compute project root: tests/ -> project
this = Path(__file__).resolve()
project_root = this.parents[3]
core_impl = project_root / '01-CORE' / 'monitoring' / 'baseline_metrics_system.py'

spec = importlib.util.spec_from_file_location('_core_baseline_metrics_system', str(core_impl))
if spec is None or spec.loader is None:
    raise ImportError('Cannot load core baseline_metrics_system')
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)  # type: ignore[attr-defined]

# Export explicit API for type checkers
BaselineMetricsSystem = getattr(mod, 'BaselineMetricsSystem')
ComponentTimer = getattr(mod, 'ComponentTimer')
create_baseline_metrics_system = getattr(mod, 'create_baseline_metrics_system')

__all__ = [
    'BaselineMetricsSystem',
    'ComponentTimer',
    'create_baseline_metrics_system',
]
