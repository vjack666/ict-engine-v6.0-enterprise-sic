from pathlib import Path
import time
import sys
import importlib.util

# Repo root
ROOT = Path(__file__).resolve().parents[1]
# Ensure core packages (protocols, monitoring) resolve
CORE = ROOT / "01-CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

def load_module_from_path(name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load core implementations directly from 01-CORE to avoid shim shadowing
perf_mod = load_module_from_path(
    "core_perf_agg",
    ROOT / "01-CORE" / "monitoring" / "performance_metrics_aggregator.py",
)
export_mod = load_module_from_path(
    "core_metrics_exporter",
    ROOT / "01-CORE" / "monitoring" / "metrics_json_exporter.py",
)

PerformanceMetricsAggregator = getattr(perf_mod, "PerformanceMetricsAggregator")
MetricsJSONExporter = getattr(export_mod, "MetricsJSONExporter")


def main():
    out = Path('04-DATA/metrics/smoke')
    agg = PerformanceMetricsAggregator()

    # Emit some metrics
    agg.incr('signals_processed', 3)
    agg.incr('risk_rejections', 1)
    agg.set_gauge('last_latency_ms', 12.7)
    agg.snapshot()

    exporter = MetricsJSONExporter(agg, out, interval_sec=1.0)
    exporter.start()

    # Update a bit more and let exporter write
    time.sleep(1.2)
    agg.incr('signals_processed', 2)
    agg.set_gauge('last_latency_ms', 9.3)
    agg.snapshot()
    time.sleep(1.2)

    exporter.stop()
    print(f'Exported metrics JSONs to {out.resolve()}')


if __name__ == '__main__':
    main()
