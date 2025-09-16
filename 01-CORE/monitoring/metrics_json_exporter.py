"""MetricsJSONExporter
Exporta periódicamente métricas del PerformanceMetricsAggregator a JSON.
No requiere servidor web. Pensado para dashboards o monitoreo externo.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, Optional
from threading import Thread, Event
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import time

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):
        class _Mini:
            def info(self, m: str, c: str = ""): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str = ""): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str = ""): print(f"[ERROR][{c}] {m}")
            def debug(self, m: str, c: str = ""): print(f"[DEBUG][{c}] {m}")
        return _Mini()


class MetricsJSONExporter:
    def __init__(self, aggregator: Any, out_dir: Path, interval_sec: float = 5.0):
        self.logger = get_unified_logger("MetricsJSONExporter")
        self.aggregator = aggregator
        self.out_dir = Path(out_dir)
        self.interval = max(0.5, float(interval_sec))
        self._thread: Optional[Thread] = None
        self._stop = Event()

        try:
            self.out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"No se pudo crear el directorio de métricas: {e}", "Metrics")

    def _atomic_write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, file_path)
        except Exception as e:
            try:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            self.logger.error(f"Error escribiendo {file_path.name}: {e}", "Metrics")

    def _collect(self) -> Dict[str, Any]:
        try:
            live = self.aggregator.get_live_metrics()
            summary = self.aggregator.get_summary_metrics()
            cumulative = self.aggregator.get_cumulative_metrics()
            ts = getattr(self.aggregator, 'last_update', None)
            return {
                'live': live,
                'summary': summary,
                'cumulative': cumulative,
                'timestamp': (ts.isoformat() if ts else datetime.now(timezone.utc).isoformat()),
            }
        except Exception as e:
            self.logger.error(f"Error recolectando métricas: {e}", "Metrics")
            return {}

    def _run(self) -> None:
        self.logger.info(f"Exportador de métricas iniciado cada {self.interval:.1f}s en {self.out_dir}", "Metrics")
        while not self._stop.is_set():
            data = self._collect()
            if data:
                try:
                    self._atomic_write_json(self.out_dir / 'metrics_live.json', data.get('live', {}))
                    self._atomic_write_json(self.out_dir / 'metrics_summary.json', data.get('summary', {}))
                    self._atomic_write_json(self.out_dir / 'metrics_cumulative.json', data.get('cumulative', {}))
                    # Archivo combinado
                    self._atomic_write_json(self.out_dir / 'metrics_all.json', data)
                except Exception as e:
                    self.logger.error(f"Error exportando métricas: {e}", "Metrics")
            self._stop.wait(self.interval)
        self.logger.info("Exportador de métricas detenido", "Metrics")

    def start(self) -> bool:
        if self._thread and self._thread.is_alive():
            return True
        if self.aggregator is None:
            self.logger.warning("No hay aggregator disponible para exportar", "Metrics")
            return False
        self._stop.clear()
        self._thread = Thread(target=self._run, name="MetricsJSONExporter", daemon=True)
        self._thread.start()
        return True

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)


__all__ = ["MetricsJSONExporter"]
