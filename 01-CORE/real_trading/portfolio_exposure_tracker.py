"""Portfolio Exposure Tracker

Responsable de mantener métricas agregadas de exposición por símbolo y total.
Se apoya en eventos de ejecuciones confirmadas. Persistencia opcional JSON.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, Optional
import json
import threading
import time
from pathlib import Path

try:
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore


class PortfolioExposureTracker:
    def __init__(self, persistence_path: Optional[str] = None, logger: Optional[Any] = None) -> None:
        self._lock = threading.RLock()
        self._exposure: Dict[str, float] = {}
        self._last_update = 0.0
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.logger = logger or (SmartTradingLogger("PortfolioExposure") if SmartTradingLogger else None)  # type: ignore
        self._load()

    def _log_info(self, msg: str) -> None:
        if self.logger:
            try:
                self.logger.info(msg, "portfolio_exposure")
            except Exception:  # pragma: no cover
                pass

    def _log_warn(self, msg: str) -> None:
        if self.logger:
            try:
                self.logger.warning(msg, "portfolio_exposure")
            except Exception:  # pragma: no cover
                pass

    def _load(self) -> None:
        if not self.persistence_path or not self.persistence_path.exists():
            return
        try:
            data = json.loads(self.persistence_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                with self._lock:
                    self._exposure = {k: float(v) for k, v in data.get("exposure", {}).items()}
        except Exception:  # pragma: no cover
            self._log_warn("No se pudo cargar exposición previa")

    def _persist(self) -> None:
        if not self.persistence_path:
            return
        try:
            payload = {"exposure": self._exposure, "ts": time.time()}
            tmp = self.persistence_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.persistence_path)
        except Exception:  # pragma: no cover
            self._log_warn("Persistencia exposición fallida")

    def apply_execution(self, symbol: str, volume: float, direction: str) -> None:
        if volume <= 0:
            return
        delta = volume if direction.upper() in ("BUY", "LONG") else -volume
        with self._lock:
            cur = self._exposure.get(symbol, 0.0) + delta
            if abs(cur) < 1e-9:
                self._exposure.pop(symbol, None)
            else:
                self._exposure[symbol] = cur
            self._last_update = time.time()
        self._persist()

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            total = sum(abs(v) for v in self._exposure.values())
            return {"by_symbol": dict(self._exposure), "total_abs": total, "last_update": self._last_update}

__all__ = ["PortfolioExposureTracker"]
