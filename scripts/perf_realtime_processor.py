from __future__ import annotations
from pathlib import Path
import sys
import time
import statistics
from datetime import datetime
from typing import Optional

# Ensure core path
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / '01-CORE'
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

# Import processor directly by path to avoid shims
import importlib.util
import importlib

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

rt_mod = load_module('core_realtime_proc', CORE / 'production' / 'realtime_data_processor.py')
RealTimeDataProcessor = getattr(rt_mod, 'RealTimeDataProcessor')

# Metrics wiring: import monitoring package modules so instances align
perf_mod = importlib.import_module('monitoring.performance_metrics_aggregator')
collector_pkg = importlib.import_module('monitoring.metrics_collector')
exporter_pkg = importlib.import_module('monitoring.metrics_json_exporter')
PerformanceMetricsAggregator = getattr(perf_mod, 'PerformanceMetricsAggregator')
set_aggregator = getattr(collector_pkg, 'set_aggregator')
MetricsJSONExporter = getattr(exporter_pkg, 'MetricsJSONExporter')


def main(duration_sec: float = 12.0):
    cfg = {
        'tick_processing_interval': 0.05,  # 50ms target loop
        'shutdown_timeout': 2.0,
        'performance_log_interval': 3600,  # silence internal perf log
        'data_validation': True,
        # Enable internal perf metrics emission
        'debug_perf_metrics': True,
        'perf_emit_interval': 2.0,
    }
    symbols = ['EURUSD', 'GBPUSD']

    proc = RealTimeDataProcessor(symbols=symbols, config=cfg)

    # Set up shared aggregator + JSON exporter to smoke dir
    agg = PerformanceMetricsAggregator()
    set_aggregator(agg)
    smoke_dir = ROOT / '04-DATA' / 'metrics' / 'smoke'
    exporter = MetricsJSONExporter(agg, smoke_dir, interval_sec=2.0)
    exporter_started = exporter.start()

    # Hook to capture tick timestamps and compute inter-arrival/processing latency
    latencies_ms = []
    events = {
        'count': 0,
        'mt5_connected': False,
        'start_ts': time.perf_counter(),
    }

    def on_data(symbol, timeframe, tick):
        events['count'] += 1
        if tick is not None:
            # processing delay from tick timestamp to now (approx)
            delay_ms = (datetime.now() - tick.timestamp).total_seconds() * 1000
            latencies_ms.append(max(0.0, delay_ms))

    proc.add_callback(on_data)

    # Start and detect MT5 connectivity state
    proc.start()
    try:
        mt5 = getattr(proc, 'mt5_manager', None)
        events['mt5_connected'] = bool(mt5 and getattr(mt5, 'is_connected', lambda: False)())
    except Exception:
        events['mt5_connected'] = False

    time.sleep(duration_sec)
    proc.stop()

    # Stop exporter
    try:
        if exporter_started:
            exporter.stop()
    except Exception:
        pass

    # Compute stats
    count = events['count']
    lat = latencies_ms
    stats = {
        'duration_sec': duration_sec,
        'symbols': symbols,
        'events': count,
        'events_per_sec': round(count / duration_sec, 2),
        'mt5_connected': events['mt5_connected'],
        'latency_ms': {
            'samples': len(lat),
            'avg': round(statistics.mean(lat), 2) if lat else 0.0,
            'p50': round(statistics.median(lat), 2) if lat else 0.0,
            'p95': round(sorted(lat)[int(0.95 * len(lat)) - 1], 2) if len(lat) >= 2 else (lat[0] if lat else 0.0),
            'max': round(max(lat), 2) if lat else 0.0,
        }
    }

    print('--- RealTimeDataProcessor Performance ---')
    for k, v in stats.items():
        print(f"{k}: {v}")


if __name__ == '__main__':
    dur = 12.0
    if len(sys.argv) > 1:
        try:
            dur = float(sys.argv[1])
        except Exception:
            pass
    main(dur)
